from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Shared constants
#
# These are referenced by the (not-yet-built) InterviewEngine, but live here
# alongside the session model since they define the shape of "readiness"
# rather than any particular piece of orchestration logic.
# ---------------------------------------------------------------------------

MIN_QUESTIONS = 8
MIN_DISTINCT_DAYS = 4
MAX_FOLLOWUPS_PER_DAY = 2


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SessionStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class PriorTier(str, Enum):
    """
    Attempts-based confidence prior for a PASSED mission, matching the
    values produced by candidate_analyzer._classify_prior().
    """
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
    """
    The five follow-up trigger categories from the interview design.
    Optional on a classification — only set when quality is PARTIAL/WEAK.
    """
    SURFACE_NO_DEPTH = "SURFACE_NO_DEPTH"
    NO_TRADEOFF_AWARENESS = "NO_TRADEOFF_AWARENESS"
    NO_IMPLEMENTATION_GROUNDING = "NO_IMPLEMENTATION_GROUNDING"
    HEDGING_PARTIAL = "HEDGING_PARTIAL"
    CONFIDENTLY_WRONG = "CONFIDENTLY_WRONG"


# ---------------------------------------------------------------------------
# Existing request model — preserved unchanged for compatibility.
#
# interview.py's /interview/start currently reads request.day directly, so
# this field is kept as-is for now. Removing client-supplied day selection
# is a change that belongs to the interview.py + interview_engine.py update,
# not this batch.
# ---------------------------------------------------------------------------

class StartInterviewRequest(BaseModel):
    candidate_id: str
    day: int


# ---------------------------------------------------------------------------
# Building blocks for InterviewSession
# ---------------------------------------------------------------------------

class EligibleDay(BaseModel):
    """One PASSED curriculum day this candidate can legitimately be asked
    about, carrying the attempts-based prior used to seed difficulty."""
    day: int
    title: str
    attempts: int
    prior: PriorTier
    domain: Optional[str] = None  # populated once domain mapping exists


class TranscriptEntry(BaseModel):
    """A single question turn in the interview, with its answer once given."""
    index: int
    day: int
    topic: str
    question: str
    is_followup: bool = False
    answer: Optional[str] = None
    asked_at: datetime = Field(default_factory=datetime.utcnow)
    answered_at: Optional[datetime] = None


class AnswerClassification(BaseModel):
    """The structured judgment produced for one answered transcript entry."""
    transcript_index: int
    day: int
    quality: AnswerQuality
    gap_type: Optional[GapType] = None
    rationale: Optional[str] = None


class ReadinessState(BaseModel):
    """
    Whether the interview has met the hackathon's minimum bar and can be
    safely finished. Tracked as a small structured object rather than a
    single flag so a client can see *why* it isn't ready yet.
    """
    question_count_met: bool = False
    day_diversity_met: bool = False
    ready_to_finish: bool = False


# ---------------------------------------------------------------------------
# InterviewSession — the full in-memory session object
# ---------------------------------------------------------------------------

class InterviewSession(BaseModel):
    session_id: str
    candidate_id: str
    status: SessionStatus = SessionStatus.IN_PROGRESS

    eligible_days: List[EligibleDay] = Field(default_factory=list)
    asked_days: List[int] = Field(default_factory=list)
    question_count: int = 0

    current_day: Optional[int] = None
    current_topic: Optional[str] = None
    current_difficulty: DifficultyTier = DifficultyTier.L2_APPLIED
    difficulty_by_day: Dict[int, DifficultyTier] = Field(default_factory=dict)

    transcript: List[TranscriptEntry] = Field(default_factory=list)
    answer_classifications: List[AnswerClassification] = Field(default_factory=list)
    follow_up_counts: Dict[int, int] = Field(default_factory=dict)

    readiness: ReadinessState = Field(default_factory=ReadinessState)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def recompute_readiness(self) -> ReadinessState:
        """
        Recompute (and store) whether the session has hit the hackathon's
        minimum bar: >= MIN_QUESTIONS questions and >= MIN_DISTINCT_DAYS
        distinct days asked. Pure/deterministic — no side effects beyond
        updating this session's own readiness field. Not wired into the
        answer loop yet; the InterviewEngine will call this once built.
        """
        distinct_days = len(set(self.asked_days))

        question_count_met = self.question_count >= MIN_QUESTIONS
        day_diversity_met = distinct_days >= MIN_DISTINCT_DAYS

        self.readiness = ReadinessState(
            question_count_met=question_count_met,
            day_diversity_met=day_diversity_met,
            ready_to_finish=question_count_met and day_diversity_met,
        )
        return self.readiness

    @classmethod
    def new(cls, session_id: str, candidate_id: str,
            eligible_days: List[EligibleDay]) -> "InterviewSession":
        """Convenience factory for creating a fresh session from an
        analyzer result's eligible days."""
        return cls(
            session_id=session_id,
            candidate_id=candidate_id,
            eligible_days=eligible_days,
        )


# ---------------------------------------------------------------------------
# Request/response models for the upcoming /interview/answer and
# /interview/finish endpoints. Defined now so the route handlers can be
# built against a stable contract; the routes themselves are not modified
# in this batch.
# ---------------------------------------------------------------------------

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
    confidence: str  # "CONFIRMED" or "FLAGGED", per the weak-concept fusion design
    reason: str


class CoverageGap(BaseModel):
    day: int
    title: str
    reason: str  # e.g. "SKIPPED" or "NOT_ATTEMPTED"


class DomainOrDayScore(BaseModel):
    day: int
    topic: str
    score: float
    quality_breakdown: Dict[str, int] = Field(default_factory=dict)


class FinishResponse(BaseModel):
    session_id: str
    status: SessionStatus
    partial: bool  # true if /finish was called before readiness was met
    scores: List[DomainOrDayScore] = Field(default_factory=list)
    weak_concepts: List[WeakConcept] = Field(default_factory=list)
    coverage_gaps: List[CoverageGap] = Field(default_factory=list)
    narrative_feedback: Optional[str] = None
    recommendation: Optional[str] = None