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
engine = InterviewEngine()
scoring = ScoringService()


@router.post("/interview/start")
def start_interview(request: StartInterviewRequest):
    candidate_analysis = analyzer.analyze(request.candidate_id)

    if candidate_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    lesson = loader.get_day(request.day)

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curriculum day not found",
        )

    try:
        session = engine.start_session(
            candidate_id=request.candidate_id,
            preferred_day=request.day,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    try:
        prompt = builder.build_prompt(candidate_analysis, lesson)
        question = gemini.ask(prompt)

        session = engine.record_question(
            session_id=session.session_id,
            question=question,
            day=request.day,
        )

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not generate interview question: {error}",
        ) from error

    return {
        "session_id": session.session_id,
        "candidate": candidate_analysis["candidate"]["name"],
        "candidate_id": candidate_analysis["candidate"]["id"],
        "day": lesson["day"],
        "topic": lesson["title"],
        "question": question,
        "question_number": session.question_count,
    }


@router.post("/interview/answer", response_model=AnswerResponse)
def submit_answer(request: AnswerRequest):
    session = engine.get_session(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found",
        )

    if not session.transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The interview has no question to answer",
        )

    answered_entry = session.transcript[-1]

    existing_classification = next(
        (
            item
            for item in session.answer_classifications
            if item.transcript_index == answered_entry.index
        ),
        None,
    )

    # First submission: save the answer.
    # Retry after Gemini failure: reuse the already-saved answer.
    if answered_entry.answer is None:
        try:
            session = engine.record_answer(
                session_id=request.session_id,
                answer_text=request.answer_text,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error

        answered_entry = session.transcript[-1]

    lesson = loader.get_day(answered_entry.day)

    # Evaluate only if this answer has not already been classified.
    if existing_classification is None:
        try:
            classification_data = gemini.generate_json(
                builder.build_answer_classification_prompt(
                    question=answered_entry.question,
                    answer=answered_entry.answer,
                    lesson=lesson,
                    difficulty=session.current_difficulty.value,
                )
            )

            quality = AnswerQuality(classification_data["quality"].upper())

            gap_value = classification_data.get("gap_type")
            gap_type = GapType(gap_value.upper()) if gap_value else None

            classification = AnswerClassification(
                transcript_index=answered_entry.index,
                day=answered_entry.day,
                quality=quality,
                gap_type=gap_type,
                rationale=classification_data.get("rationale"),
            )

            session.answer_classifications.append(classification)

            if quality == AnswerQuality.STRONG:
                session.difficulty_by_day[answered_entry.day] = (
                    DifficultyTier.L3_SYSTEM
                )
            elif quality == AnswerQuality.WEAK:
                session.difficulty_by_day[answered_entry.day] = (
                    DifficultyTier.L1_RECALL
                )

            session = engine.store.save(session)

        except Exception as error:
            is_quota_error = (
                "429" in str(error)
                or "RESOURCE_EXHAUSTED" in str(error)
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                    if is_quota_error
                    else status.HTTP_502_BAD_GATEWAY
                ),
                detail=(
                    "Gemini quota is temporarily unavailable. "
                    "Wait about one minute, then submit the same answer again."
                    if is_quota_error
                    else f"Could not evaluate the answer: {error}"
                ),
                headers={"Retry-After": "60"} if is_quota_error else None,
            ) from error

    else:
        classification = existing_classification
        quality = classification.quality
        gap_type = classification.gap_type

    # The final answer has been evaluated, so no new question is created.
    if session.readiness.ready_to_finish:
        return AnswerResponse(
            session_id=session.session_id,
            question=(
                "Interview is ready to finish. Submit /interview/finish "
                "to view the scorecard."
            ),
            day=answered_entry.day,
            topic=answered_entry.topic,
            is_followup=False,
            question_number=session.question_count,
            distinct_days_asked=len(set(session.asked_days)),
            ready_to_finish=True,
        )

    followup_count = session.follow_up_counts.get(answered_entry.day, 0)

    is_followup = (
        quality in {AnswerQuality.PARTIAL, AnswerQuality.WEAK}
        and followup_count < 2
    )

    next_day = answered_entry.day if is_followup else engine.choose_next_day(session)

    if is_followup:
        session.follow_up_counts[next_day] = followup_count + 1
        session = engine.store.save(session)

    next_lesson = loader.get_day(next_day)
    candidate_analysis = analyzer.analyze(session.candidate_id)

    if candidate_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    next_difficulty = engine._difficulty_for_day(session, next_day)

    try:
        prompt = builder.build_next_question_prompt(
            candidate=candidate_analysis["candidate"],
            lesson=next_lesson,
            difficulty=next_difficulty.value,
            transcript=[
                entry.model_dump(mode="json")
                for entry in session.transcript
            ],
            is_followup=is_followup,
            gap_type=gap_type.value if gap_type else None,
        )

        question = gemini.ask(prompt)

        session = engine.record_question(
            session_id=session.session_id,
            question=question,
            day=next_day,
            is_followup=is_followup,
        )

    except Exception as error:
        is_quota_error = (
            "429" in str(error)
            or "RESOURCE_EXHAUSTED" in str(error)
        )

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
                if is_quota_error
                else status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Gemini quota is temporarily unavailable. "
                "Wait about one minute, then submit the same answer again."
                if is_quota_error
                else f"Could not generate the next question: {error}"
            ),
            headers={"Retry-After": "60"} if is_quota_error else None,
        ) from error

    return AnswerResponse(
        session_id=session.session_id,
        question=question,
        day=next_day,
        topic=next_lesson["title"],
        is_followup=is_followup,
        question_number=session.question_count,
        distinct_days_asked=len(set(session.asked_days)),
        ready_to_finish=session.readiness.ready_to_finish,
    )


@router.post("/interview/finish", response_model=FinishResponse)
def finish_interview(request: FinishRequest):
    try:
        session = engine.finish_session(request.session_id)

    except ValueError as error:
        detail = str(error)

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
                if detail == "Interview session not found"
                else status.HTTP_400_BAD_REQUEST
            ),
            detail=detail,
        ) from error

    return scoring.build_scorecard(session)