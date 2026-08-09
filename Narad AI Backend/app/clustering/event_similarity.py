"""
Event Similarity Engine V3.1

Determines whether two articles describe the same underlying
news event rather than merely sharing the same company or topic.

V3.1 improvements:
    - stronger event-concept weighting
    - concept-based paraphrase detection
    - entity-aware event matching
    - time-aware event matching
    - protection against same-company false positives
    - explainable scoring
"""

from dataclasses import dataclass, field
from typing import List, Set
from difflib import SequenceMatcher
import re

from app.agent.models import Topic


# ==========================================================
# RESULT
# ==========================================================

@dataclass
class EventSimilarityResult:

    score: float

    # Individual diagnostic scores
    title_score: float
    action_score: float
    event_score: float
    entity_score: float
    distinctive_score: float
    content_score: float
    time_score: float

    # Evidence
    shared_entities: List[str] = field(
        default_factory=list
    )

    shared_actions: List[str] = field(
        default_factory=list
    )

    shared_event_terms: List[str] = field(
        default_factory=list
    )

    shared_distinctive_terms: List[str] = field(
        default_factory=list
    )

    reasons: List[str] = field(
        default_factory=list
    )

    decision: str = "DIFFERENT_EVENT"


# ==========================================================
# ENGINE
# ==========================================================

class EventSimilarityEngine:

    # ------------------------------------------------------
    # FINAL SCORE WEIGHTS
    # ------------------------------------------------------

    TITLE_WEIGHT = 0.30
    EVENT_WEIGHT = 0.25
    ENTITY_WEIGHT = 0.15
    DISTINCTIVE_WEIGHT = 0.15
    CONTENT_WEIGHT = 0.10
    TIME_WEIGHT = 0.05

    # ------------------------------------------------------
    # DECISION THRESHOLDS
    # ------------------------------------------------------

    SAME_EVENT_THRESHOLD = 0.55
    POSSIBLE_EVENT_THRESHOLD = 0.38

    # ======================================================
    # STOP WORDS
    # ======================================================

    STOP_WORDS = {
        "the",
        "and",
        "for",
        "that",
        "this",
        "with",
        "from",
        "into",
        "about",
        "after",
        "before",
        "over",
        "under",
        "their",
        "they",
        "them",
        "have",
        "has",
        "had",
        "will",
        "would",
        "could",
        "should",
        "been",
        "being",
        "were",
        "was",
        "are",
        "is",
        "its",
        "you",
        "your",
        "our",
        "what",
        "when",
        "where",
        "which",
        "while",
        "than",
        "also",
        "more",
        "most",
        "some",
        "just",
        "news",
        "says",
        "said",
        "according",
        "reportedly",
        "new",
        "latest",
        "big",
        "first",
        "one",
        "two",
        "three",

        # Generic technology terms
        "ai",
        "artificial",
        "intelligence",
        "model",
        "models",
        "technology",
        "tech",
        "company",
        "companies",
        "system",
        "systems",
        "software",
        "platform",
        "service",
        "services",
    }

    # ======================================================
    # ACTION NORMALIZATION
    # ======================================================

    ACTION_CANONICAL = {

        # Announcements
        "announce": "announce",
        "announces": "announce",
        "announced": "announce",
        "announcement": "announce",

        # Launch
        "launch": "launch",
        "launches": "launch",
        "launched": "launch",
        "launching": "launch",

        # Release
        "release": "release",
        "releases": "release",
        "released": "release",
        "releasing": "release",

        # Development
        "develop": "develop",
        "develops": "develop",
        "developed": "develop",
        "developing": "develop",
        "development": "develop",

        # Delay
        "delay": "delay",
        "delays": "delay",
        "delayed": "delay",
        "delaying": "delay",

        # Slowdown
        "slow": "slow",
        "slows": "slow",
        "slowed": "slow",
        "slowing": "slow",

        # Pause
        "pause": "pause",
        "pauses": "pause",
        "paused": "pause",

        # Stop
        "stop": "stop",
        "stops": "stop",
        "stopped": "stop",
        "stopping": "stop",

        # Acquisition
        "acquire": "acquire",
        "acquires": "acquire",
        "acquired": "acquire",
        "acquisition": "acquire",

        # Funding
        "raise": "funding",
        "raises": "funding",
        "raised": "funding",
        "funding": "funding",

        # Investment
        "invest": "invest",
        "invests": "invest",
        "invested": "invest",
        "investment": "invest",

        # Legal
        "sue": "lawsuit",
        "sues": "lawsuit",
        "sued": "lawsuit",
        "lawsuit": "lawsuit",

        "order": "court_order",
        "orders": "court_order",
        "ordered": "court_order",

        "accuse": "accuse",
        "accuses": "accuse",
        "accused": "accuse",

        # Investigation
        "investigate": "investigate",
        "investigates": "investigate",
        "investigated": "investigate",

        # Product changes
        "watermark": "watermark",
        "watermarks": "watermark",
        "watermarking": "watermark",

        "give": "give",
        "gives": "give",
        "giving": "give",
        "gave": "give",

        "introduce": "introduce",
        "introduces": "introduce",
        "introduced": "introduce",

        "expand": "expand",
        "expands": "expand",
        "expanded": "expand",

        # Partnership
        "partner": "partnership",
        "partners": "partnership",
        "partnered": "partnership",
        "partnership": "partnership",

        # Restrictions
        "ban": "ban",
        "bans": "ban",
        "banned": "ban",

        "allow": "allow",
        "allows": "allow",
        "allowed": "allow",

        # Reporting
        "report": "report",
        "reports": "report",
        "reported": "report",
        "reporting": "report",
    }

    # ======================================================
    # EVENT CONCEPT GROUPS
    # ======================================================

    EVENT_CONCEPTS = {

        # --------------------------------------------------
        # Google organizational change
        # --------------------------------------------------

        "org_shakeup": {
            "shake",
            "shakeup",
            "reshuffle",
            "reorg",
            "reorganization",
            "restructure",
            "restructuring",
            "leadership",
            "politics",
            "changes",
            "change",
            "departure",
            "departures",
        },

        # --------------------------------------------------
        # Smart speaker
        # --------------------------------------------------

        "smart_speaker": {
            "speaker",
            "speakers",
            "smart",
            "puck",
            "device",
            "audio",
            "sound",
            "hockey",
            "hockeypuck",
        },

        # --------------------------------------------------
        # AI music watermarking
        # --------------------------------------------------

        "music_watermarking": {
            "watermark",
            "watermarks",
            "watermarking",
            "music",
            "song",
            "songs",
            "generated",
            "generation",
            "audio",
        },

        # --------------------------------------------------
        # ChatGPT free access
        # --------------------------------------------------

        "chatgpt_access": {
            "chatgpt",
            "chat",
            "chats",
            "free",
            "unlimited",
            "users",
            "text",
            "access",
        },

        # --------------------------------------------------
        # AI security
        # --------------------------------------------------

        "ai_security": {
            "security",
            "secure",
            "safety",
            "threat",
            "risk",
            "risks",
            "concern",
            "concerns",
            "danger",
            "dangerous",
            "powerful",
            "capability",
            "capabilities",
        },

        # --------------------------------------------------
        # Product pricing
        # --------------------------------------------------

        "product_pricing": {
            "price",
            "pricing",
            "cost",
            "costs",
            "sell",
            "selling",
            "dollar",
            "dollars",
        },

        # --------------------------------------------------
        # Food ordering
        # --------------------------------------------------

        "food_ordering": {
            "food",
            "restaurant",
            "restaurants",
            "order",
            "ordering",
            "delivery",
        },

        # --------------------------------------------------
        # Hotel booking
        # --------------------------------------------------

        "hotel_booking": {
            "hotel",
            "hotels",
            "booking",
            "bookings",
            "reservation",
            "reservations",
        },

        # --------------------------------------------------
        # Researchers leaving company
        # --------------------------------------------------

        "researcher_departure": {
            "researcher",
            "researchers",
            "scientist",
            "scientists",
            "leave",
            "leaving",
            "left",
            "departure",
            "departures",
            "startup",
        },
    }

    # ======================================================
    # KNOWN ENTITIES
    # ======================================================

    KNOWN_ENTITIES = {
        "openai",
        "anthropic",
        "google",
        "microsoft",
        "meta",
        "nvidia",
        "apple",
        "amazon",
        "cloudflare",
        "suno",
        "softbank",
        "spotify",
        "shopify",
        "airbnb",
        "chatgpt",
        "claude",
        "gemini",
        "deepmind",
    }

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(
        self,
        same_event_threshold=(
            SAME_EVENT_THRESHOLD
        ),
        possible_event_threshold=(
            POSSIBLE_EVENT_THRESHOLD
        ),
    ):

        self.same_event_threshold = (
            same_event_threshold
        )

        self.possible_event_threshold = (
            possible_event_threshold
        )

    # ======================================================
    # PUBLIC COMPARE
    # ======================================================

    def compare(
        self,
        topic_a: Topic,
        topic_b: Topic,
    ) -> EventSimilarityResult:

        title_a = self._normalize(
            topic_a.title or ""
        )

        title_b = self._normalize(
            topic_b.title or ""
        )

        content_a = self._normalize(
            topic_a.content or ""
        )

        content_b = self._normalize(
            topic_b.content or ""
        )

        # --------------------------------------------------
        # Extract actions
        # --------------------------------------------------

        actions_a = self._extract_actions(
            title_a
        )

        actions_b = self._extract_actions(
            title_b
        )

        # --------------------------------------------------
        # Extract normalized concepts
        # --------------------------------------------------

        concepts_a = (
            self._extract_concepts(
                title_a
            )
        )

        concepts_b = (
            self._extract_concepts(
                title_b
            )
        )

        # --------------------------------------------------
        # Extract event terms
        # --------------------------------------------------

        event_terms_a = (
            self._extract_event_terms(
                title_a
            )
        )

        event_terms_b = (
            self._extract_event_terms(
                title_b
            )
        )

        # --------------------------------------------------
        # Extract entities
        # --------------------------------------------------

        entities_a = (
            self._extract_entities(
                topic_a
            )
        )

        entities_b = (
            self._extract_entities(
                topic_b
            )
        )

        # --------------------------------------------------
        # Extract distinctive terms
        # --------------------------------------------------

        distinctive_a = (
            self._extract_distinctive_terms(
                title_a
            )
        )

        distinctive_b = (
            self._extract_distinctive_terms(
                title_b
            )
        )

        # ==================================================
        # INDIVIDUAL SCORES
        # ==================================================

        title_score = (
            self._title_similarity(
                title_a,
                title_b,
            )
        )

        action_score = (
            self._set_similarity(
                actions_a,
                actions_b,
            )
        )

        raw_event_score = (
            self._set_similarity(
                event_terms_a,
                event_terms_b,
            )
        )

        concept_score = (
            self._set_similarity(
                concepts_a,
                concepts_b,
            )
        )

        # --------------------------------------------------
        # V3.1 CHANGE
        #
        # Event concepts are now the strongest part of the
        # event score.
        # --------------------------------------------------

        event_score = (
            0.20 * action_score
            +
            0.25 * raw_event_score
            +
            0.55 * concept_score
        )

        entity_score = (
            self._set_similarity(
                entities_a,
                entities_b,
            )
        )

        distinctive_score = (
            self._set_similarity(
                distinctive_a,
                distinctive_b,
            )
        )

        content_score = (
            self._content_similarity(
                content_a,
                content_b,
            )
        )

        time_score = (
            self._time_similarity(
                topic_a,
                topic_b,
            )
        )

        # ==================================================
        # FINAL WEIGHTED SCORE
        # ==================================================

        score = (

            self.TITLE_WEIGHT
            * title_score

            +

            self.EVENT_WEIGHT
            * event_score

            +

            self.ENTITY_WEIGHT
            * entity_score

            +

            self.DISTINCTIVE_WEIGHT
            * distinctive_score

            +

            self.CONTENT_WEIGHT
            * content_score

            +

            self.TIME_WEIGHT
            * time_score
        )

        # ==================================================
        # SHARED EVIDENCE
        # ==================================================

        shared_entities = sorted(
            entities_a
            &
            entities_b
        )

        shared_actions = sorted(
            actions_a
            &
            actions_b
        )

        shared_event_terms = sorted(
            event_terms_a
            &
            event_terms_b
        )

        shared_distinctive_terms = sorted(
            distinctive_a
            &
            distinctive_b
        )

        shared_concepts = sorted(
            concepts_a
            &
            concepts_b
        )

        # ==================================================
        # REASONS
        # ==================================================

        reasons = []

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        if title_score >= 0.70:

            reasons.append(
                "very strong title similarity"
            )

        elif title_score >= 0.50:

            reasons.append(
                "strong title similarity"
            )

        elif title_score >= 0.30:

            reasons.append(
                "moderate title similarity"
            )

        # --------------------------------------------------
        # Actions
        # --------------------------------------------------

        if shared_actions:

            reasons.append(
                "shared event actions: "
                +
                ", ".join(
                    shared_actions
                )
            )

        # --------------------------------------------------
        # Concepts
        # --------------------------------------------------

        if shared_concepts:

            reasons.append(
                "shared event concepts: "
                +
                ", ".join(
                    shared_concepts
                )
            )

        # --------------------------------------------------
        # Event terms
        # --------------------------------------------------

        if len(
            shared_event_terms
        ) >= 2:

            reasons.append(
                "shared event terms: "
                +
                ", ".join(
                    shared_event_terms[:10]
                )
            )

        # --------------------------------------------------
        # Entities
        # --------------------------------------------------

        if shared_entities:

            reasons.append(
                "shared entities: "
                +
                ", ".join(
                    shared_entities
                )
            )

        # --------------------------------------------------
        # Distinctive terms
        # --------------------------------------------------

        if len(
            shared_distinctive_terms
        ) >= 2:

            reasons.append(
                "shared distinctive terms: "
                +
                ", ".join(
                    shared_distinctive_terms[:10]
                )
            )

        # --------------------------------------------------
        # Time
        # --------------------------------------------------

        if time_score >= 0.80:

            reasons.append(
                "published very close together"
            )

        elif time_score >= 0.50:

            reasons.append(
                "published within a similar time window"
            )

        # ==================================================
        # SAFETY RULE
        # ==================================================

        # Same entity alone must NEVER be enough.

        if (
            entity_score > 0
            and
            title_score < 0.20
            and
            event_score < 0.20
            and
            distinctive_score < 0.20
        ):

            score *= 0.60

            reasons.append(
                "shared entity but weak event evidence"
            )

        # ==================================================
        # STRONG HEADLINE / ENTITY / TIME
        # ==================================================

        if (
            title_score >= 0.60
            and
            entity_score >= 0.50
            and
            time_score >= 0.50
        ):

            score = max(
                score,
                0.56
            )

            reasons.append(
                "strong headline/entity/time agreement"
            )

        # ==================================================
        # V3.1 CONCEPT MATCH
        # ==================================================

        if (
            concept_score >= 0.40
            and
            entity_score >= 0.30
            and
            time_score >= 0.40
        ):

            score = max(
                score,
                0.56
            )

            reasons.append(
                "strong event-concept/time agreement"
            )

        # ==================================================
        # VERY STRONG CONCEPT MATCH
        # ==================================================

        if (
            concept_score >= 0.75
            and
            entity_score >= 0.50
            and
            time_score >= 0.50
        ):

            score = max(
                score,
                0.62
            )

            reasons.append(
                "very strong event-concept/entity/time agreement"
            )

        # ==================================================
        # FINAL DECISION
        # ==================================================

        if (
            score
            >= self.same_event_threshold
        ):

            decision = (
                "SAME_EVENT"
            )

        elif (
            score
            >= self.possible_event_threshold
        ):

            decision = (
                "POSSIBLY_SAME_EVENT"
            )

        else:

            decision = (
                "DIFFERENT_EVENT"
            )

        # ==================================================
        # RETURN
        # ==================================================

        return EventSimilarityResult(

            score=round(
                score,
                4
            ),

            title_score=round(
                title_score,
                4
            ),

            action_score=round(
                action_score,
                4
            ),

            event_score=round(
                event_score,
                4
            ),

            entity_score=round(
                entity_score,
                4
            ),

            distinctive_score=round(
                distinctive_score,
                4
            ),

            content_score=round(
                content_score,
                4
            ),

            time_score=round(
                time_score,
                4
            ),

            shared_entities=(
                shared_entities
            ),

            shared_actions=(
                shared_actions
            ),

            shared_event_terms=(
                shared_event_terms
            ),

            shared_distinctive_terms=(
                shared_distinctive_terms
            ),

            reasons=reasons,

            decision=decision,
        )

    # ======================================================
    # TITLE SIMILARITY
    # ======================================================

    def _title_similarity(
        self,
        title_a: str,
        title_b: str,
    ) -> float:

        words_a = (
            self._important_words(
                title_a
            )
        )

        words_b = (
            self._important_words(
                title_b
            )
        )

        token_score = (
            self._set_similarity(
                words_a,
                words_b,
            )
        )

        char_score = (
            SequenceMatcher(
                None,
                title_a,
                title_b,
            ).ratio()
        )

        return (
            0.65 * token_score
            +
            0.35 * char_score
        )

    # ======================================================
    # ACTION EXTRACTION
    # ======================================================

    def _extract_actions(
        self,
        title: str,
    ) -> Set[str]:

        words = set(
            title.split()
        )

        actions = set()

        for word in words:

            canonical = (
                self.ACTION_CANONICAL.get(
                    word
                )
            )

            if canonical:

                actions.add(
                    canonical
                )

        return actions

    # ======================================================
    # CONCEPT EXTRACTION
    # ======================================================

    def _extract_concepts(
        self,
        title: str,
    ) -> Set[str]:

        words = set(
            self._important_words(
                title
            )
        )

        concepts = set()

        for concept_name, concept_words in (
            self.EVENT_CONCEPTS.items()
        ):

            overlap = (
                words
                &
                concept_words
            )

            if not overlap:

                continue

            # ------------------------------------------------
            # Normal concepts require at least two matching
            # terms.
            # ------------------------------------------------

            if len(overlap) >= 2:

                concepts.add(
                    concept_name
                )

                continue

            # ------------------------------------------------
            # Some concepts have highly distinctive words.
            # ------------------------------------------------

            distinctive_hits = {

                "speaker",
                "speakers",
                "puck",

                "watermark",
                "watermarks",
                "watermarking",

                "chatgpt",
                "unlimited",

                "shakeup",
                "shake",
            }

            if (
                overlap
                &
                distinctive_hits
            ):

                concepts.add(
                    concept_name
                )

        return concepts

    # ======================================================
    # EVENT TERM EXTRACTION
    # ======================================================

    def _extract_event_terms(
        self,
        title: str,
    ) -> Set[str]:

        words = set(
            self._important_words(
                title
            )
        )

        # Remove action vocabulary.
        words -= set(
            self.ACTION_CANONICAL.keys()
        )

        synonyms = {

            # Google organizational change
            "shake": "shakeup",
            "shakeup": "shakeup",
            "reshuffle": "shakeup",
            "reorg": "shakeup",
            "reorganization": "shakeup",
            "restructure": "shakeup",
            "restructuring": "shakeup",

            # Speaker
            "speaker": "speaker",
            "speakers": "speaker",

            # Music
            "song": "music",
            "songs": "music",

            # Watermark
            "watermarks": "watermark",
            "watermarking": "watermark",

            # ChatGPT
            "chats": "chat",
            "chatgpt": "chatgpt",

            # Security
            "concerns": "concern",
            "risks": "risk",
            "capabilities": "capability",
            "powerful": "capability",

            # Pricing
            "dollars": "dollar",
            "costs": "cost",

            # Hotel
            "hotels": "hotel",
            "bookings": "booking",

            # Researchers
            "researchers": "researcher",
            "scientists": "scientist",
        }

        normalized = set()

        for word in words:

            normalized.add(
                synonyms.get(
                    word,
                    word
                )
            )

        return normalized

    # ======================================================
    # DISTINCTIVE TERMS
    # ======================================================

    def _extract_distinctive_terms(
        self,
        title: str,
    ) -> Set[str]:

        words = (
            self._important_words(
                title
            )
        )

        words -= set(
            self.ACTION_CANONICAL.keys()
        )

        return words

    # ======================================================
    # ENTITY EXTRACTION
    # ======================================================

    def _extract_entities(
        self,
        topic: Topic,
    ) -> Set[str]:

        text = " ".join([
            topic.title or "",
            topic.summary or "",
            " ".join(
                topic.tags or []
            ),
        ]).lower()

        found = set()

        for entity in (
            self.KNOWN_ENTITIES
        ):

            if re.search(
                rf"\b{re.escape(entity)}\b",
                text,
            ):

                found.add(
                    entity
                )

        return found

    # ======================================================
    # IMPORTANT WORDS
    # ======================================================

    def _important_words(
        self,
        text: str,
    ) -> Set[str]:

        text = self._normalize(
            text
        )

        return {
            word
            for word in text.split()
            if (
                len(word) >= 3
                and
                word not in self.STOP_WORDS
            )
        }

    # ======================================================
    # NORMALIZATION
    # ======================================================

    def _normalize(
        self,
        text: str,
    ) -> str:

        text = text.lower()

        # Normalize hyphens.
        text = text.replace(
            "-",
            " "
        )

        # Remove punctuation.
        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text,
        )

        # Collapse whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ======================================================
    # SET SIMILARITY
    # ======================================================

    def _set_similarity(
        self,
        set_a: Set[str],
        set_b: Set[str],
    ) -> float:

        if not set_a or not set_b:

            return 0.0

        intersection = (
            set_a
            &
            set_b
        )

        union = (
            set_a
            |
            set_b
        )

        if not union:

            return 0.0

        return (
            len(intersection)
            /
            len(union)
        )

    # ======================================================
    # CONTENT SIMILARITY
    # ======================================================

    def _content_similarity(
        self,
        content_a: str,
        content_b: str,
    ) -> float:

        words_a = (
            self._important_words(
                content_a
            )
        )

        words_b = (
            self._important_words(
                content_b
            )
        )

        return self._set_similarity(
            words_a,
            words_b,
        )

    # ======================================================
    # TIME SIMILARITY
    # ======================================================

    def _time_similarity(
        self,
        topic_a: Topic,
        topic_b: Topic,
    ) -> float:

        date_a = (
            topic_a.published_at
            or topic_a.discovered_at
        )

        date_b = (
            topic_b.published_at
            or topic_b.discovered_at
        )

        if (
            not date_a
            or not date_b
        ):

            return 0.0

        hours = abs(
            (
                date_a - date_b
            ).total_seconds()
        ) / 3600.0

        if hours >= 48:

            return 0.0

        return (
            1.0
            -
            (
                hours / 48.0
            )
        )