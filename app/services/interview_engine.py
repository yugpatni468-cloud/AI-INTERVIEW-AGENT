from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from app.models.interview import (
    DifficultyTier,
    EligibleDay,
    InterviewSession,
    PriorTier,
    SessionStatus,
    TranscriptEntry,
)
from app.services.candidate_analyzer import CandidateAnalyzer
from app.services.curriculum_loader import CurriculumLoader
from app.services.session_store import SessionStore


class InterviewEngine:
    """
    Owns session state and deterministic question scheduling.

    Gemini generates question text later. This service decides which eligible
    curriculum day should be discussed and records the interview transcript.
    """

    def __init__(
        self,
        analyzer: Optional[CandidateAnalyzer] = None,
        loader: Optional[CurriculumLoader] = None,
        store: Optional[SessionStore] = None,
    ) -> None:
        self.analyzer = analyzer or CandidateAnalyzer()
        self.loader = loader or CurriculumLoader()
        self.store = store or SessionStore()

    def start_session(
        self,
        candidate_id: str,
        preferred_day: Optional[int] = None,
    ) -> InterviewSession:
        analysis = self.analyzer.analyze(candidate_id)

        if analysis is None:
            raise ValueError("Candidate not found")

        eligible_days = self._build_eligible_days(analysis["passed_missions"])

        if not eligible_days:
            raise ValueError("Candidate has no passed curriculum days to interview on")

        if preferred_day is not None:
            eligible_day_numbers = {item.day for item in eligible_days}
            if preferred_day not in eligible_day_numbers:
                raise ValueError(
                    "The selected day is not eligible because the candidate has not passed it"
                )

        session = InterviewSession.new(
            session_id=str(uuid4()),
            candidate_id=candidate_id,
            eligible_days=eligible_days,
        )

        if preferred_day is not None:
            session.current_day = preferred_day
            session.current_topic = self._topic_for_day(session, preferred_day)
            session.current_difficulty = self._difficulty_for_day(
                session, preferred_day
            )

        return self.store.create(session)

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.store.get(session_id)

    def choose_next_day(self, session: InterviewSession) -> int:
        """
        Prefer coverage of a new eligible day. If every day has already been
        covered, return the day with the fewest questions so far.
        """
        unseen_days = [
            item for item in session.eligible_days if item.day not in session.asked_days
        ]

        candidates = unseen_days or session.eligible_days

        question_counts = {
            item.day: session.asked_days.count(item.day) for item in candidates
        }

        # Fragile topics are checked earlier; then moderate; then strong.
        prior_rank = {
            PriorTier.FRAGILE: 0,
            PriorTier.MODERATE: 1,
            PriorTier.STRONG: 2,
        }

        selected = min(
            candidates,
            key=lambda item: (question_counts[item.day], prior_rank[item.prior], item.day),
        )
        return selected.day

    def record_question(
        self,
        session_id: str,
        question: str,
        *,
        day: Optional[int] = None,
        is_followup: bool = False,
    ) -> InterviewSession:
        session = self._require_active_session(session_id)

        if session.transcript and session.transcript[-1].answer is None:
            raise ValueError("Answer the current question before asking another one")

        selected_day = day or session.current_day or self.choose_next_day(session)
        topic = self._topic_for_day(session, selected_day)

        entry = TranscriptEntry(
            index=len(session.transcript) + 1,
            day=selected_day,
            topic=topic,
            question=question,
            is_followup=is_followup,
        )

        session.transcript.append(entry)
        session.asked_days.append(selected_day)
        session.question_count += 1
        session.current_day = selected_day
        session.current_topic = topic
        session.current_difficulty = self._difficulty_for_day(session, selected_day)
        session.recompute_readiness()

        return self.store.save(session)

    def record_answer(self, session_id: str, answer_text: str) -> InterviewSession:
        if not answer_text.strip():
            raise ValueError("Answer text cannot be empty")

        session = self._require_active_session(session_id)

        if not session.transcript or session.transcript[-1].answer is not None:
            raise ValueError("There is no unanswered interview question")

        session.transcript[-1].answer = answer_text.strip()
        session.transcript[-1].answered_at = datetime.utcnow()

        return self.store.save(session)

    def finish_session(self, session_id: str) -> InterviewSession:
        session = self._require_active_session(session_id)

        if session.transcript and session.transcript[-1].answer is None:
            raise ValueError("Answer the current question before finishing the interview")

        session.recompute_readiness()
        session.status = SessionStatus.FINISHED

        return self.store.save(session)

    def _build_eligible_days(self, passed_missions: List[dict]) -> List[EligibleDay]:
        eligible_days = []

        for mission in passed_missions:
            lesson = self.loader.get_day(mission["day"])
            if lesson is None:
                continue

            eligible_days.append(
                EligibleDay(
                    day=lesson["day"],
                    title=lesson["title"],
                    attempts=mission.get("attempts", 1),
                    prior=PriorTier(mission["prior"]),
                    domain=lesson.get("type"),
                )
            )

        return eligible_days

    @staticmethod
    def _topic_for_day(session: InterviewSession, day: int) -> str:
        for item in session.eligible_days:
            if item.day == day:
                return item.title
        raise ValueError(f"Day {day} is not eligible for this interview")

    @staticmethod
    def _difficulty_for_day(
        session: InterviewSession, day: int
    ) -> DifficultyTier:
        if day in session.difficulty_by_day:
            return session.difficulty_by_day[day]

        eligible_day = next(item for item in session.eligible_days if item.day == day)

        if eligible_day.prior == PriorTier.STRONG:
            difficulty = DifficultyTier.L3_SYSTEM
        elif eligible_day.prior == PriorTier.FRAGILE:
            difficulty = DifficultyTier.L1_RECALL
        else:
            difficulty = DifficultyTier.L2_APPLIED

        session.difficulty_by_day[day] = difficulty
        return difficulty

    def _require_active_session(self, session_id: str) -> InterviewSession:
        session = self.store.get(session_id)

        if session is None:
            raise ValueError("Interview session not found")

        if session.status != SessionStatus.IN_PROGRESS:
            raise ValueError("Interview session has already finished")

        return session