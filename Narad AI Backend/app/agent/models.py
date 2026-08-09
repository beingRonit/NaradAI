"""
Core data models for AutonomousAI.

This file contains the shared data structures used by:

    - Persona
    - Topic discovery
    - Article enrichment
    - Verification
    - Editorial evaluation
    - Ranking
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# ==========================================================
# AGENT STATUS
# ==========================================================

class AgentStatus(str, Enum):
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    VERIFYING = "VERIFYING"
    EVALUATING = "EVALUATING"
    RANKING = "RANKING"
    GENERATING = "GENERATING"
    PUBLISHING = "PUBLISHING"
    ERROR = "ERROR"


# ==========================================================
# TOPIC STATUS
# ==========================================================

class TopicStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    VERIFIED = "VERIFIED"
    EVALUATED = "EVALUATED"
    RANKED = "RANKED"
    SELECTED = "SELECTED"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


# ==========================================================
# ENRICHMENT STATUS
# ==========================================================

class EnrichmentStatus(str, Enum):
    """
    Tracks the state of article enrichment.

    NOT_ATTEMPTED:
        No enrichment attempt has been made.

    PENDING:
        An enrichment attempt is currently being processed.

    SUCCESS:
        Article content was successfully extracted.

    FAILED:
        Enrichment was attempted but failed.

    FAILED does NOT mean that the article is false.
    It only means that richer article content could not
    currently be retrieved.
    """

    NOT_ATTEMPTED = "NOT_ATTEMPTED"

    PENDING = "PENDING"

    SUCCESS = "SUCCESS"

    FAILED = "FAILED"


# ==========================================================
# INTEREST
# ==========================================================

@dataclass
class Interest:
    """
    Represents a topic that the persona is interested in.
    """

    topic: str

    weight: float = 50.0

    confidence: float = 0.5

    interactions: int = 0

    last_updated: datetime = field(
        default_factory=datetime.utcnow
    )


# ==========================================================
# EDITORIAL RULE
# ==========================================================

@dataclass
class EditorialRule:
    """
    Represents an editorial rule followed by the persona.
    """

    name: str

    description: str

    priority: int

    enabled: bool = True


# ==========================================================
# MEMORY
# ==========================================================

@dataclass
class MemoryEntry:
    """
    Represents a previously stored opinion or memory.
    """

    topic: str

    opinion: str

    keywords: List[str] = field(
        default_factory=list
    )

    companies: List[str] = field(
        default_factory=list
    )

    technologies: List[str] = field(
        default_factory=list
    )

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


# ==========================================================
# PERSONA PROFILE
# ==========================================================

@dataclass
class PersonaProfile:
    """
    Static identity information about the AI creator.
    """

    name: str

    bio: str

    tone: str

    writing_style: str

    posting_time: str

    timezone: str


# ==========================================================
# PERSONA STATE
# ==========================================================

@dataclass
class PersonaState:
    """
    Runtime state of the autonomous agent.
    """

    status: AgentStatus = AgentStatus.IDLE

    last_scan_time: Optional[datetime] = None

    last_post_time: Optional[datetime] = None

    next_post_time: Optional[datetime] = None

    articles_scanned_today: int = 0

    articles_queued: int = 0

    posts_published_today: int = 0

    last_error: Optional[str] = None


# ==========================================================
# PERSONA
# ==========================================================

@dataclass
class Persona:
    """
    Complete AI creator persona.
    """

    name: str

    bio: str

    tone: str

    writing_style: str

    posting_time: str

    timezone: str

    state: PersonaState = field(
        default_factory=PersonaState
    )

    interests: Dict[str, Interest] = field(
        default_factory=dict
    )

    editorial_rules: List[EditorialRule] = field(
        default_factory=list
    )

    memory: List[MemoryEntry] = field(
        default_factory=list
    )


# ==========================================================
# TOPIC
# ==========================================================

@dataclass
class Topic:
    """
    Represents a discovered news article.

    A Topic persists through multiple editorial cycles.
    """

    # ------------------------------------------------------
    # ARTICLE IDENTITY
    # ------------------------------------------------------

    id: str

    url: str

    title: str

    summary: str

    content: str

    source: str

    author: Optional[str] = None

    category: Optional[str] = None

    language: str = "en"

    tags: List[str] = field(
        default_factory=list
    )

    image_url: Optional[str] = None

    # ------------------------------------------------------
    # TIMESTAMPS
    # ------------------------------------------------------

    published_at: Optional[datetime] = None

    discovered_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # ------------------------------------------------------
    # PIPELINE STATE
    # ------------------------------------------------------

    status: TopicStatus = (
        TopicStatus.DISCOVERED
    )

    reliability_score: Optional[float] = None

    evaluation_score: Optional[float] = None

    # ------------------------------------------------------
    # ENRICHMENT STATE
    # ------------------------------------------------------

    enrichment_status: EnrichmentStatus = (
        EnrichmentStatus.NOT_ATTEMPTED
    )

    enrichment_attempts: int = 0

    last_enrichment_attempt: Optional[datetime] = None

    last_enrichment_success: Optional[datetime] = None

    enrichment_error: Optional[str] = None

    # Next permitted enrichment retry. This prevents repeated HTTP
    # requests on every autonomous cycle after a failure.
    next_enrichment_retry: Optional[datetime] = None

    enriched_content_length: int = 0


# ==========================================================
# VERIFICATION RESULT
# ==========================================================

@dataclass
class VerificationResult:
    """
    Result generated by the verification engine.
    """

    topic_id: str

    topic_title: str

    source_score: float

    content_score: float

    evidence_score: float

    completeness_score: float

    reliability_score: float

    verified: bool

    reason: str


# ==========================================================
# EVALUATION RESULT
# ==========================================================

@dataclass
class EvaluationResult:
    """
    Result generated by the editorial evaluator.
    """

    topic_id: str

    topic_title: str

    interest_score: float

    technical_score: float

    reliability_score: float

    freshness_score: float

    memory_score: float

    editorial_score: float

    overall_score: float

    publish: bool

    reason: str

    # V5: transparent editorial calibration / publication diagnostics.
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    publication_path: str = "standard"
    publication_blockers: List[str] = field(default_factory=list)


# ==========================================================
# RANKING RESULT
# ==========================================================

@dataclass
class RankingResult:
    """
    Represents one ranked article.
    """

    topic_id: str

    topic_title: str

    score: float

    rank: int

    publish: bool

    reason: str


# ==========================================================
# RANKING SUMMARY
# ==========================================================

@dataclass
class RankingSummary:
    """
    Summary produced by the ranking engine.
    """

    rankings: List[RankingResult] = field(
        default_factory=list
    )

    top_publishable: List[RankingResult] = field(
        default_factory=list
    )

    total_articles: int = 0

    publishable_articles: int = 0


# ==========================================================
# TOPIC SUMMARY
# ==========================================================

@dataclass
class TopicSummary:
    """
    Lightweight representation of a Topic.
    """

    id: str

    title: str

    source: str

    score: Optional[float] = None

    status: TopicStatus = (
        TopicStatus.DISCOVERED
    )
# ==========================================================
# PUBLICATION CANDIDATE
# ==========================================================

@dataclass
class PublicationCandidate:
    """A story kept alive across cycles until it can be published or expires."""

    cluster_id: str
    topic_id: str
    title: str
    score: float
    reliability_score: float
    first_seen_at: datetime = field(default_factory=datetime.utcnow)
    last_seen_at: datetime = field(default_factory=datetime.utcnow)
    last_evaluated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "ACTIVE"  # ACTIVE, READY, PUBLISHED, EXPIRED, DROPPED
    attempts: int = 0
    source_count: int = 1
    reason: str = ""
    independent_source_count: int = 1
    corroboration_score: float = 0.0
    blocking_reasons: List[str] = field(default_factory=list)
    publication_path: str = "standard"
