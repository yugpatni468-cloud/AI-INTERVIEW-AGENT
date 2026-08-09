from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


MIN_QUESTIONS = 8
MIN_DISTINCT_DAYS = 4
MAX_FOLLOWUPS_PER_DAY = 2


class SessionStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class PriorTier(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    FRAGILE = "FRAGILE"


class DifficultyTier(str, Enum):
    L1_RECALL = "L1_RECALL"
    L2_APPLIED = "L2_APPLIED"
    L3_SYSTEM = "L3_SYSTEM"


class AnswerQuality(str, Enum):
    STRONG = "STRONG"
    PARTIAL = "PARTIAL"
    WEAK = "WEAK"


class GapType(str, Enum):
    SURFACE_NO_DEPTH = "SURFACE_NO_DEPTH"
    NO_TRADEOFF_AWARENESS = "NO_TRADEOFF_AWARENESS"
    NO_IMPLEMENTATION_GROUNDING = "NO_IMPLEMENTATION_GROUNDING"
    HEDGING_PARTIAL = "HEDGING_PARTIAL"
    CONFIDENTLY_WRONG = "CONFIDENTLY_WRONG"


class StartInterviewRequest(BaseModel):
    candidate_id: str
    day: Optional[int] = None


class EligibleDay(BaseModel):
    day: int
    title: str
    attempts: int
    prior: PriorTier
    domain: Optional[str] = None


class TranscriptEntry(BaseModel):
    index: int
    day: int
    topic: str
    question: str
    is_followup: bool = False
    answer: Optional[str] = None
    asked_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    answered_at: Optional[datetime] = None


class AnswerClassification(BaseModel):
    transcript_index: int
    day: int
    quality: AnswerQuality
    gap_type: Optional[GapType] = None
    rationale: Optional[str] = None


class ReadinessState(BaseModel):
    question_count_met: bool = False
    day_diversity_met: bool = False
    ready_to_finish: bool = False


class InterviewSession(BaseModel):

    session_id: str
    candidate_id: str

    status: SessionStatus = SessionStatus.IN_PROGRESS

    eligible_days: List[EligibleDay] = Field(
        default_factory=list
    )

    asked_days: List[int] = Field(
        default_factory=list
    )

    question_count: int = 0

    current_day: Optional[int] = None
    current_topic: Optional[str] = None

    current_difficulty: DifficultyTier = (
        DifficultyTier.L2_APPLIED
    )

    difficulty_by_day: Dict[
        int,
        DifficultyTier
    ] = Field(default_factory=dict)

    transcript: List[TranscriptEntry] = Field(
        default_factory=list
    )

    answer_classifications: List[
        AnswerClassification
    ] = Field(default_factory=list)

    follow_up_counts: Dict[
        int,
        int
    ] = Field(default_factory=dict)

    readiness: ReadinessState = Field(
        default_factory=ReadinessState
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    def recompute_readiness(self):

        distinct_days = len(
            set(self.asked_days)
        )

        question_count_met = (
            self.question_count >= MIN_QUESTIONS
        )

        day_diversity_met = (
            distinct_days >= MIN_DISTINCT_DAYS
        )

        self.readiness = ReadinessState(
            question_count_met=question_count_met,
            day_diversity_met=day_diversity_met,
            ready_to_finish=(
                question_count_met
                and day_diversity_met
            ),
        )

        return self.readiness

    @classmethod
    def new(
        cls,
        session_id: str,
        candidate_id: str,
        eligible_days: List[EligibleDay],
    ):

        return cls(
            session_id=session_id,
            candidate_id=candidate_id,
            eligible_days=eligible_days,
        )


class AnswerRequest(BaseModel):
    session_id: str
    answer_text: str


class AnswerResponse(BaseModel):
    session_id: str
    question: str
    day: int
    topic: str
    is_followup: bool
    question_number: int
    distinct_days_asked: int
    ready_to_finish: bool


class FinishRequest(BaseModel):
    session_id: str


class WeakConcept(BaseModel):
    day: int
    topic: str
    confidence: str
    reason: str


class CoverageGap(BaseModel):
    day: int
    title: str
    reason: str


class DomainOrDayScore(BaseModel):
    day: int
    topic: str
    score: float
    quality_breakdown: Dict[str, int] = Field(
        default_factory=dict
    )


class FinishResponse(BaseModel):
    session_id: str
    status: SessionStatus
    partial: bool
    scores: List[DomainOrDayScore] = Field(
        default_factory=list
    )
    weak_concepts: List[WeakConcept] = Field(
        default_factory=list
    )
    coverage_gaps: List[CoverageGap] = Field(
        default_factory=list
    )
    narrative_feedback: Optional[str] = None
    recommendation: Optional[str] = None