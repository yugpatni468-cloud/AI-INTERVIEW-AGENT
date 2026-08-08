from collections import defaultdict
from typing import Dict, List

from app.models.interview import (
    AnswerClassification,
    AnswerQuality,
    CoverageGap,
    DomainOrDayScore,
    FinishResponse,
    InterviewSession,
    WeakConcept,
)


class ScoringService:
    """
    Produces a deterministic scorecard from the session transcript and
    Gemini's stored answer classifications.
    """

    QUALITY_POINTS = {
        AnswerQuality.STRONG: 1.0,
        AnswerQuality.PARTIAL: 0.55,
        AnswerQuality.WEAK: 0.20,
    }

    def build_scorecard(self, session: InterviewSession) -> FinishResponse:
        classifications_by_index = {
            classification.transcript_index: classification
            for classification in session.answer_classifications
        }

        entries_by_day: Dict[int, list] = defaultdict(list)

        for entry in session.transcript:
            entries_by_day[entry.day].append(entry)

        scores = self._build_day_scores(
            session=session,
            entries_by_day=entries_by_day,
            classifications_by_index=classifications_by_index,
        )

        weak_concepts = self._build_weak_concepts(
            session=session,
            classifications_by_index=classifications_by_index,
        )

        coverage_gaps = self._build_coverage_gaps(session)
        average_score = self._average_score(scores)
        partial = not session.readiness.ready_to_finish

        return FinishResponse(
            session_id=session.session_id,
            status=session.status,
            partial=partial,
            scores=scores,
            weak_concepts=weak_concepts,
            coverage_gaps=coverage_gaps,
            narrative_feedback=self._narrative_feedback(
                average_score=average_score,
                weak_concepts=weak_concepts,
                coverage_gaps=coverage_gaps,
            ),
            recommendation=self._recommendation(
                average_score=average_score,
                partial=partial,
            ),
        )

    def _build_day_scores(
        self,
        session: InterviewSession,
        entries_by_day: Dict[int, list],
        classifications_by_index: Dict[int, AnswerClassification],
    ) -> List[DomainOrDayScore]:
        scores = []

        for day, entries in sorted(entries_by_day.items()):
            topic = next(
                eligible_day.title
                for eligible_day in session.eligible_days
                if eligible_day.day == day
            )

            quality_breakdown = {
                AnswerQuality.STRONG.value: 0,
                AnswerQuality.PARTIAL.value: 0,
                AnswerQuality.WEAK.value: 0,
            }

            points = []

            for entry in entries:
                classification = classifications_by_index.get(entry.index)

                if classification is None:
                    continue

                quality_breakdown[classification.quality.value] += 1
                points.append(self.QUALITY_POINTS[classification.quality])

            score = round((sum(points) / len(points)) * 100, 1) if points else 0.0

            scores.append(
                DomainOrDayScore(
                    day=day,
                    topic=topic,
                    score=score,
                    quality_breakdown=quality_breakdown,
                )
            )

        return scores

    def _build_weak_concepts(
        self,
        session: InterviewSession,
        classifications_by_index: Dict[int, AnswerClassification],
    ) -> List[WeakConcept]:
        weak_concepts = []
        seen = set()

        for entry in session.transcript:
            classification = classifications_by_index.get(entry.index)

            if (
                classification is None
                or classification.quality == AnswerQuality.STRONG
            ):
                continue

            key = (entry.day, classification.gap_type)

            if key in seen:
                continue

            seen.add(key)

            reason = classification.rationale or (
                classification.gap_type.value
                if classification.gap_type
                else "The answer needs deeper technical grounding."
            )

            weak_concepts.append(
                WeakConcept(
                    day=entry.day,
                    topic=entry.topic,
                    confidence=(
                        "CONFIRMED"
                        if classification.quality == AnswerQuality.WEAK
                        else "FLAGGED"
                    ),
                    reason=reason,
                )
            )

        return weak_concepts

    @staticmethod
    def _build_coverage_gaps(session: InterviewSession) -> List[CoverageGap]:
        asked_day_set = set(session.asked_days)

        return [
            CoverageGap(
                day=eligible_day.day,
                title=eligible_day.title,
                reason="NOT_INTERVIEWED",
            )
            for eligible_day in session.eligible_days
            if eligible_day.day not in asked_day_set
        ]

    @staticmethod
    def _average_score(scores: List[DomainOrDayScore]) -> float:
        if not scores:
            return 0.0

        return sum(score.score for score in scores) / len(scores)

    @staticmethod
    def _recommendation(average_score: float, partial: bool) -> str:
        if partial:
            return "INCOMPLETE: finish more questions across additional topics."

        if average_score >= 80:
            return "READY: demonstrates strong technical readiness."
        if average_score >= 60:
            return "PROMISING: strengthen the flagged concepts and reassess."

        return "NEEDS_FOUNDATION: revisit core concepts before reassessment."

    @staticmethod
    def _narrative_feedback(
        average_score: float,
        weak_concepts: List[WeakConcept],
        coverage_gaps: List[CoverageGap],
    ) -> str:
        feedback = f"Average evaluated score: {average_score:.1f}/100."

        if weak_concepts:
            feedback += (
                " Focus improvement on: "
                + ", ".join(item.topic for item in weak_concepts[:3])
                + "."
            )

        if coverage_gaps:
            feedback += (
                f" {len(coverage_gaps)} eligible topic(s) were not covered."
            )

        return feedback