from fastapi import APIRouter, HTTPException, status

from app.models.interview import (
    AnswerClassification,
    AnswerQuality,
    AnswerRequest,
    AnswerResponse,
    DifficultyTier,
    FinishRequest,
    FinishResponse,
    GapType,
    StartInterviewRequest,
)

from app.services.candidate_analyzer import CandidateAnalyzer
from app.services.curriculum_loader import CurriculumLoader
from app.services.gemini_service import GeminiService
from app.services.interview_engine import InterviewEngine
from app.services.prompt_builder import PromptBuilder
from app.services.scoring import ScoringService


router = APIRouter()

analyzer = CandidateAnalyzer()
loader = CurriculumLoader()
builder = PromptBuilder()
gemini = GeminiService()
engine = InterviewEngine(
    analyzer=analyzer,
    loader=loader,
)
scoring = ScoringService()


@router.post("/interview/start")
def start_interview(
    request: StartInterviewRequest
):

    candidate_analysis = analyzer.analyze(
        request.candidate_id
    )

    if candidate_analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    try:

        session = engine.start_session(
            candidate_id=request.candidate_id,
            preferred_day=request.day,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    selected_day = session.current_day

    if selected_day is None:
        raise HTTPException(
            status_code=500,
            detail="Interview engine did not select a curriculum day",
        )

    lesson = loader.get_day(selected_day)

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail=f"Curriculum day {selected_day} not found",
        )

    try:

        prompt = builder.build_prompt(
            candidate_analysis,
            lesson,
        )

        question = gemini.ask(prompt)

        session = engine.record_question(
            session_id=session.session_id,
            question=question,
            day=selected_day,
        )

    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):

            raise HTTPException(
                status_code=503,
                detail="Gemini quota is temporarily unavailable.",
                headers={
                    "Retry-After": "60"
                },
            )

        raise HTTPException(
            status_code=502,
            detail=f"Could not generate question: {error}",
        )

    return {
        "session_id": session.session_id,
        "candidate": candidate_analysis[
            "candidate"
        ]["name"],
        "candidate_id": candidate_analysis[
            "candidate"
        ]["id"],
        "day": selected_day,
        "topic": lesson["title"],
        "question": question,
        "question_number": session.question_count,
        "distinct_days_asked": len(
            set(session.asked_days)
        ),
        "ready_to_finish": (
            session.readiness.ready_to_finish
        ),
    }


@router.post(
    "/interview/answer",
    response_model=AnswerResponse,
)
def submit_answer(
    request: AnswerRequest
):

    session = engine.get_session(
        request.session_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found",
        )

    if not session.transcript:
        raise HTTPException(
            status_code=400,
            detail="Interview has no question",
        )

    current_entry = session.transcript[-1]

    if current_entry.answer is not None:
        raise HTTPException(
            status_code=400,
            detail="Current question is already answered",
        )

    try:

        session = engine.record_answer(
            session_id=request.session_id,
            answer_text=request.answer_text,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    answered_entry = session.transcript[-1]

    lesson = loader.get_day(
        answered_entry.day
    )

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Curriculum lesson not found",
        )

    try:

        classification_data = (
            gemini.generate_json(
                builder.build_answer_classification_prompt(
                    question=answered_entry.question,
                    answer=answered_entry.answer,
                    lesson=lesson,
                    difficulty=session.current_difficulty.value,
                )
            )
        )

        quality = AnswerQuality(
            classification_data.get(
                "quality",
                "PARTIAL"
            ).upper()
        )

        gap_value = classification_data.get(
            "gap_type"
        )

        gap_type = None

        if gap_value:
            try:
                gap_type = GapType(
                    gap_value.upper()
                )
            except ValueError:
                gap_type = None

        classification = AnswerClassification(
            transcript_index=answered_entry.index,
            day=answered_entry.day,
            quality=quality,
            gap_type=gap_type,
            rationale=classification_data.get(
                "rationale"
            ),
        )

        session.answer_classifications.append(
            classification
        )

        if quality == AnswerQuality.STRONG:

            session.difficulty_by_day[
                answered_entry.day
            ] = DifficultyTier.L3_SYSTEM

        elif quality == AnswerQuality.WEAK:

            session.difficulty_by_day[
                answered_entry.day
            ] = DifficultyTier.L1_RECALL

        session = engine.store.save(session)

    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):

            raise HTTPException(
                status_code=503,
                detail="Gemini quota is temporarily unavailable.",
                headers={
                    "Retry-After": "60"
                },
            )

        raise HTTPException(
            status_code=502,
            detail=f"Could not evaluate answer: {error}",
        )

    if session.readiness.ready_to_finish:

        return AnswerResponse(
            session_id=session.session_id,
            question=(
                "Interview is ready to finish. "
                "Click Finish Interview."
            ),
            day=answered_entry.day,
            topic=answered_entry.topic,
            is_followup=False,
            question_number=session.question_count,
            distinct_days_asked=len(
                set(session.asked_days)
            ),
            ready_to_finish=True,
        )

    followup_count = session.follow_up_counts.get(
        answered_entry.day,
        0,
    )

    is_followup = (
        quality in {
            AnswerQuality.PARTIAL,
            AnswerQuality.WEAK,
        }
        and followup_count < 2
    )

    if is_followup:

        next_day = answered_entry.day

        session.follow_up_counts[
            next_day
        ] = followup_count + 1

    else:

        next_day = engine.choose_next_day(
            session
        )

    session = engine.store.save(session)

    next_lesson = loader.get_day(
        next_day
    )

    if next_lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Next curriculum day not found",
        )

    candidate_analysis = analyzer.analyze(
        session.candidate_id
    )

    next_difficulty = engine._difficulty_for_day(
        session,
        next_day,
    )

    try:

        prompt = builder.build_next_question_prompt(
            candidate=candidate_analysis[
                "candidate"
            ],
            lesson=next_lesson,
            difficulty=next_difficulty.value,
            transcript=[
                entry.model_dump(mode="json")
                for entry in session.transcript
            ],
            is_followup=is_followup,
            gap_type=(
                gap_type.value
                if gap_type
                else None
            ),
        )

        question = gemini.ask(prompt)

        session = engine.record_question(
            session_id=session.session_id,
            question=question,
            day=next_day,
            is_followup=is_followup,
        )

    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):

            raise HTTPException(
                status_code=503,
                detail="Gemini quota is temporarily unavailable.",
                headers={
                    "Retry-After": "60"
                },
            )

        raise HTTPException(
            status_code=502,
            detail=f"Could not generate next question: {error}",
        )

    return AnswerResponse(
        session_id=session.session_id,
        question=question,
        day=next_day,
        topic=next_lesson["title"],
        is_followup=is_followup,
        question_number=session.question_count,
        distinct_days_asked=len(
            set(session.asked_days)
        ),
        ready_to_finish=session.readiness.ready_to_finish,
    )


@router.post(
    "/interview/finish",
    response_model=FinishResponse,
)
def finish_interview(
    request: FinishRequest
):

    try:

        session = engine.finish_session(
            request.session_id
        )

    except ValueError as error:

        detail = str(error)

        raise HTTPException(
            status_code=(
                404
                if detail ==
                "Interview session not found"
                else 400
            ),
            detail=detail,
        )

    return scoring.build_scorecard(
        session
    )