"""
Verification Engine

Stage 1 reliability assessment.

The verifier currently evaluates:

    1. Source credibility
    2. Evidence quality
    3. Specificity / verifiability
    4. Temporal consistency
    5. Metadata completeness

IMPORTANT:

This is PROVISIONAL verification.

At this stage we do NOT yet have:

    - cross-source verification
    - story clustering
    - claim comparison
    - contradiction detection

Those are handled by later pipeline stages.

IMPORTANT:

Failure to verify does NOT mean the article is false.

Therefore:

    VERIFIED
        = sufficient evidence currently available

    NOT VERIFIED
        = insufficient evidence currently available

The Topic remains DISCOVERED when verification
requirements are not met.
"""

from datetime import datetime, timezone
from urllib.parse import urlparse
import re

from app.agent.models import (
    Topic,
    TopicStatus,
    VerificationResult,
)


class VerificationEngine:
    """
    Performs Stage 1 provisional reliability assessment.
    """

    # ==========================================================
    # TRUSTED SOURCES
    # ==========================================================

    TRUSTED_SOURCES = {

        # ------------------------------------------------------
        # NEWS ORGANIZATIONS
        # ------------------------------------------------------

        "reuters": 95,

        "associated press": 95,

        "bbc": 90,

        "the guardian": 85,

        "the verge": 85,

        "techcrunch": 85,

        "arstechnica": 85,

        "wired": 85,

        "mit technology review": 90,

        "the wall street journal": 90,

        "new york times": 90,

        "bloomberg": 90,

        # ------------------------------------------------------
        # OFFICIAL TECHNOLOGY SOURCES
        # ------------------------------------------------------

        "openai": 95,

        "anthropic": 95,

        "google": 95,

        "microsoft": 95,

        "nvidia": 95,

        "meta": 95,

        "apple": 95,

        "amazon": 95,
    }

    # ==========================================================
    # SOURCE ALIASES
    # ==========================================================

    SOURCE_ALIASES = {

        "techcrunch ai":
            "techcrunch",

        "the verge ai":
            "the verge",

        "ars technica":
            "arstechnica",

        "ap news":
            "associated press",

        "associated press news":
            "associated press",
    }

    # ==========================================================
    # THRESHOLDS
    # ==========================================================

    # ----------------------------------------------------------
    # Stage 1 provisional verification threshold.
    #
    # This is deliberately lower than the old 70 threshold
    # because Stage 1 is NOT final verification.
    # ----------------------------------------------------------

    VERIFICATION_THRESHOLD = 55.0

    # ----------------------------------------------------------
    # Minimum evidence for ordinary sources.
    # ----------------------------------------------------------

    MIN_EVIDENCE_FOR_VERIFICATION = 45.0

    # ----------------------------------------------------------
    # Highly trusted sources can pass with weaker evidence
    # because source credibility itself is strong evidence.
    # ----------------------------------------------------------

    PRIMARY_SOURCE_THRESHOLD = 90.0

    # ----------------------------------------------------------
    # Minimum metadata completeness.
    # ----------------------------------------------------------

    MIN_COMPLETENESS = 60.0

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):

        self.verification_count = 0

        self.verified_count = 0

        self.pending_count = 0

    # ==========================================================
    # MAIN VERIFICATION
    # ==========================================================

    def verify(
        self,
        topic: Topic
    ) -> VerificationResult:
        """
        Perform Stage 1 provisional reliability assessment.
        """

        # ------------------------------------------------------
        # CALCULATE COMPONENTS
        # ------------------------------------------------------

        source_score = self._source_score(
            topic
        )

        evidence_score = self._evidence_score(
            topic
        )

        specificity_score = self._specificity_score(
            topic
        )

        temporal_score = self._temporal_consistency_score(
            topic
        )

        completeness_score = self._completeness_score(
            topic
        )

        # ------------------------------------------------------
        # CALCULATE PROVISIONAL RELIABILITY
        # ------------------------------------------------------

        reliability_score = self._calculate_reliability(
            source_score=source_score,
            evidence_score=evidence_score,
            specificity_score=specificity_score,
            temporal_score=temporal_score
        )

        # ------------------------------------------------------
        # VERIFICATION DECISION
        # ------------------------------------------------------

        verified = self._verification_decision(
            reliability_score=reliability_score,
            source_score=source_score,
            evidence_score=evidence_score,
            completeness_score=completeness_score
        )

        # ------------------------------------------------------
        # GENERATE REASON
        # ------------------------------------------------------

        reason = self._generate_reason(
            topic=topic,
            source_score=source_score,
            evidence_score=evidence_score,
            specificity_score=specificity_score,
            temporal_score=temporal_score,
            completeness_score=completeness_score,
            reliability_score=reliability_score,
            verified=verified
        )

        # ------------------------------------------------------
        # UPDATE TOPIC
        # ------------------------------------------------------

        topic.reliability_score = (
            reliability_score
        )

        if verified:

            topic.status = (
                TopicStatus.VERIFIED
            )

        else:

            # IMPORTANT:
            #
            # Do NOT mark the topic as REJECTED.
            #
            # We simply don't have enough evidence yet.
            #
            # Keep its existing status.

            self.pending_count += 1

        # ------------------------------------------------------
        # UPDATE COUNTERS
        # ------------------------------------------------------

        self.verification_count += 1

        if verified:

            self.verified_count += 1

        # ------------------------------------------------------
        # RETURN RESULT
        # ------------------------------------------------------

        return VerificationResult(

            topic_id=topic.id,

            topic_title=topic.title,

            source_score=source_score,

            content_score=evidence_score,

            evidence_score=evidence_score,

            completeness_score=completeness_score,

            reliability_score=reliability_score,

            verified=verified,

            reason=reason
        )

    # ==========================================================
    # SOURCE IDENTITY / PRIMARY SOURCE HELPERS
    # ==========================================================

    @classmethod
    def normalize_source(cls, source: str) -> str:
        """Canonical identity used for independent-source counting."""
        value = " ".join((source or "").strip().lower().split())
        aliases = {
            "ars technica": "arstechnica",
            "ars technica ai": "arstechnica",
            "techcrunch ai": "techcrunch",
            "the verge ai": "the verge",
            "ap news": "associated press",
            "associated press news": "associated press",
        }
        return aliases.get(value, value)

    @classmethod
    def source_score(cls, source: str) -> float:
        normalized = cls.normalize_source(source)
        if normalized in cls.TRUSTED_SOURCES:
            return float(cls.TRUSTED_SOURCES[normalized])
        for trusted, score in cls.TRUSTED_SOURCES.items():
            if trusted in normalized:
                return float(score)
        return 40.0

    @classmethod
    def is_primary_source(cls, source_or_topic) -> bool:
        """Detect official publisher identity from source name and URL domain."""
        source = getattr(source_or_topic, "source", source_or_topic) or ""
        normalized = cls.normalize_source(source)
        official_names = {"openai", "anthropic", "google", "microsoft", "nvidia", "meta", "apple", "amazon"}
        if normalized in official_names:
            return True
        url = getattr(source_or_topic, "url", "") or ""
        host = (urlparse(url).hostname or "").lower().removeprefix("www.")
        official_domains = {
            "openai.com": "openai", "anthropic.com": "anthropic",
            "blog.google": "google", "google.com": "google",
            "microsoft.com": "microsoft", "blogs.microsoft.com": "microsoft",
            "nvidia.com": "nvidia", "blogs.nvidia.com": "nvidia",
            "about.fb.com": "meta", "meta.com": "meta",
            "apple.com": "apple", "amazon.com": "amazon",
        }
        return host in official_domains or any(host.endswith("." + d) for d in official_domains)

    # ==========================================================
    # SOURCE CREDIBILITY
    # ==========================================================

    def _source_score(
        self,
        topic: Topic
    ) -> float:
        """
        Calculate the credibility baseline of the source.

        This is only one component of reliability.
        """

        return self.source_score(topic.source)

    # ==========================================================
    # EVIDENCE QUALITY
    # ==========================================================

    def _evidence_score(
        self,
        topic: Topic
    ) -> float:
        """
        Estimate evidence quality from the available article
        text.

        This is NOT cross-source verification.

        The score considers:

            - primary source indicators
            - attribution
            - supporting material
            - quotations
            - referenced URLs/documents
        """

        title = topic.title or ""

        summary = topic.summary or ""

        content = topic.content or ""

        text = " ".join(
            [
                title,
                summary,
                content
            ]
        ).lower()

        # ------------------------------------------------------
        # BASE SCORE
        # ------------------------------------------------------

        score = 20.0

        # ------------------------------------------------------
        # PRIMARY SOURCE INDICATORS
        # ------------------------------------------------------

        primary_indicators = [

            "official announcement",

            "official statement",

            "official blog",

            "official documentation",

            "company blog",

            "research paper",

            "technical paper",

            "white paper",

            "preprint",

            "published paper",

            "court filing",

            "court documents",

            "regulatory filing",

            "government report",

            "security advisory",
        ]

        primary_matches = sum(
            1
            for indicator in primary_indicators
            if indicator in text
        )

        score += min(
            primary_matches * 15,
            30
        )

        # ------------------------------------------------------
        # ATTRIBUTION
        # ------------------------------------------------------

        attribution_indicators = [

            "according to",

            "said",

            "says",

            "told",

            "spokesperson",

            "researcher",

            "researchers",

            "professor",

            "scientist",

            "chief executive",

            "ceo",

            "security researcher",

            "company representative",
        ]

        attribution_matches = sum(
            1
            for indicator in attribution_indicators
            if indicator in text
        )

        score += min(
            attribution_matches * 5,
            20
        )

        # ------------------------------------------------------
        # SUPPORTING MATERIAL
        # ------------------------------------------------------

        supporting_indicators = [

            "report",

            "study",

            "analysis",

            "findings",

            "data",

            "documents",

            "documentation",

            "benchmark",

            "testing",

            "tests",

            "experiment",

            "experiments",

            "research",
        ]

        supporting_matches = sum(
            1
            for indicator in supporting_indicators
            if indicator in text
        )

        score += min(
            supporting_matches * 4,
            20
        )

        # ------------------------------------------------------
        # DIRECT QUOTATIONS
        # ------------------------------------------------------

        quote_count = (
            text.count('"')
            // 2
        )

        score += min(
            quote_count * 3,
            10
        )

        # ------------------------------------------------------
        # URL REFERENCES
        # ------------------------------------------------------

        url_count = len(
            re.findall(
                r"https?://",
                text
            )
        )

        score += min(
            url_count * 5,
            10
        )

        # ------------------------------------------------------
        # FINAL SCORE
        # ------------------------------------------------------

        return round(
            min(
                score,
                100.0
            ),
            2
        )

    # ==========================================================
    # SPECIFICITY
    # ==========================================================

    def _specificity_score(
        self,
        topic: Topic
    ) -> float:
        """
        Measure how concrete and verifiable the article's
        claims appear to be.
        """

        text = " ".join(
            [
                topic.title or "",
                topic.summary or "",
                topic.content or ""
            ]
        )

        if not text.strip():

            return 0.0

        score = 20.0

        # ------------------------------------------------------
        # NUMBERS
        # ------------------------------------------------------

        numbers = re.findall(
            r"\b\d+(?:\.\d+)?\b",
            text
        )

        score += min(
            len(numbers) * 5,
            20
        )

        # ------------------------------------------------------
        # PERCENTAGES
        # ------------------------------------------------------

        percentages = re.findall(
            r"\b\d+(?:\.\d+)?\s*%",
            text
        )

        score += min(
            len(percentages) * 5,
            10
        )

        # ------------------------------------------------------
        # MONEY
        # ------------------------------------------------------

        money_patterns = [

            r"\$\s?\d+",

            r"€\s?\d+",

            r"£\s?\d+",

            r"\b\d+\s*(?:million|billion|trillion)\b",
        ]

        money_matches = 0

        for pattern in money_patterns:

            money_matches += len(
                re.findall(
                    pattern,
                    text,
                    flags=re.IGNORECASE
                )
            )

        score += min(
            money_matches * 5,
            15
        )

        # ------------------------------------------------------
        # YEARS
        # ------------------------------------------------------

        years = re.findall(
            r"\b20\d{2}\b",
            text
        )

        score += min(
            len(years) * 3,
            9
        )

        # ------------------------------------------------------
        # KNOWN ENTITIES
        # ------------------------------------------------------

        known_entities = [

            "OpenAI",

            "Anthropic",

            "Google",

            "Microsoft",

            "Meta",

            "NVIDIA",

            "Apple",

            "Amazon",

            "Cloudflare",

            "ChatGPT",

            "Claude",

            "Gemini",

            "GPT",
        ]

        entity_matches = sum(

            1

            for entity in known_entities

            if entity.lower()
            in text.lower()
        )

        score += min(
            entity_matches * 4,
            16
        )

        return round(
            min(
                score,
                100.0
            ),
            2
        )

    # ==========================================================
    # TEMPORAL CONSISTENCY
    # ==========================================================

    def _temporal_consistency_score(
        self,
        topic: Topic
    ) -> float:
        """
        Evaluate whether publication and discovery timestamps
        are internally sensible.

        This is NOT freshness.
        """

        published_at = (
            topic.published_at
        )

        discovered_at = (
            topic.discovered_at
        )

        if published_at is None:

            return 20.0

        if discovered_at is None:

            return 70.0

        # ------------------------------------------------------
        # NORMALIZE TIMEZONES
        # ------------------------------------------------------

        if published_at.tzinfo is None:

            published_at = (
                published_at.replace(
                    tzinfo=timezone.utc
                )
            )

        if discovered_at.tzinfo is None:

            discovered_at = (
                discovered_at.replace(
                    tzinfo=timezone.utc
                )
            )

        now = datetime.now(
            timezone.utc
        )

        # ------------------------------------------------------
        # FUTURE PUBLICATION
        # ------------------------------------------------------

        future_seconds = (
            published_at - now
        ).total_seconds()

        if future_seconds > 3600:

            return 20.0

        # ------------------------------------------------------
        # DISCOVERED BEFORE PUBLICATION
        # ------------------------------------------------------

        if published_at > discovered_at:

            difference = (
                published_at
                - discovered_at
            ).total_seconds()

            if difference <= 3600:

                return 90.0

            return 60.0

        # ------------------------------------------------------
        # DISCOVERY AFTER PUBLICATION
        # ------------------------------------------------------

        delay = (
            discovered_at
            - published_at
        ).total_seconds()

        if delay < 0:

            return 50.0

        if delay <= 3600:

            return 100.0

        if delay <= 21600:

            return 95.0

        if delay <= 86400:

            return 90.0

        if delay <= 172800:

            return 80.0

        if delay <= 604800:

            return 65.0

        return 50.0

    # ==========================================================
    # COMPLETENESS
    # ==========================================================

    def _completeness_score(
        self,
        topic: Topic
    ) -> float:
        """
        Calculate metadata completeness.

        Completeness is a gate, not a reliability component.
        """

        fields = [

            topic.title,

            topic.summary,

            topic.content,

            topic.source,

            topic.url,
        ]

        completed = sum(

            1

            for field in fields

            if field
            and str(field).strip()
        )

        return round(
            (
                completed
                /
                len(fields)
            )
            * 100,
            2
        )

    # ==========================================================
    # RELIABILITY FORMULA
    # ==========================================================

    def _calculate_reliability(
        self,
        source_score: float,
        evidence_score: float,
        specificity_score: float,
        temporal_score: float
    ) -> float:
        """
        Calculate Stage 1 provisional reliability.

        V5 calibration formula:

            Source credibility       35%
            Evidence quality         30%
            Specificity               20%
            Temporal consistency      10%
            Baseline completeness     5%

        This keeps a strong publisher/primary source meaningful without
        allowing source reputation alone to manufacture reliability.
        """

        score = (
            source_score * 0.35
            + evidence_score * 0.30
            + specificity_score * 0.20
            + temporal_score * 0.10
            + 100.0 * 0.05
        )

        return round(
            min(
                max(
                    score,
                    0.0
                ),
                100.0
            ),
            2
        )

    # ==========================================================
    # VERIFICATION DECISION
    # ==========================================================

    def _verification_decision(
        self,
        reliability_score: float,
        source_score: float,
        evidence_score: float,
        completeness_score: float
    ) -> bool:
        """
        Determine whether Stage 1 verification has enough
        evidence.

        IMPORTANT:

        Failure means "not verified yet".

        It does NOT mean "false".

        Trusted publishers receive a controlled provisional
        path because Stage 1 is not the final verification
        layer.
        """

        # ------------------------------------------------------
        # COMPLETENESS GATE
        # ------------------------------------------------------

        if (
            completeness_score
            < self.MIN_COMPLETENESS
        ):

            return False

        # ------------------------------------------------------
        # TRUSTED PUBLISHER PATH
        # ------------------------------------------------------

        if (
            source_score >= 80.0
            and
            reliability_score
            >= self.VERIFICATION_THRESHOLD
            and
            evidence_score >= 30.0
        ):

            return True

        # ------------------------------------------------------
        # NORMAL SOURCE PATH
        # ------------------------------------------------------

        if (
            reliability_score
            >= self.VERIFICATION_THRESHOLD
            and
            evidence_score
            >= self.MIN_EVIDENCE_FOR_VERIFICATION
        ):

            return True

        # ------------------------------------------------------
        # PRIMARY SOURCE FALLBACK
        # ------------------------------------------------------

        if (
            source_score
            >= self.PRIMARY_SOURCE_THRESHOLD
            and
            completeness_score
            >= self.MIN_COMPLETENESS
            and
            reliability_score >= 50.0
        ):

            return True

        return False

    # ==========================================================
    # EXPLANATION
    # ==========================================================

    def _generate_reason(
        self,
        topic: Topic,
        source_score: float,
        evidence_score: float,
        specificity_score: float,
        temporal_score: float,
        completeness_score: float,
        reliability_score: float,
        verified: bool
    ) -> str:
        """
        Generate an explainable verification reason.
        """

        reasons = []

        # ------------------------------------------------------
        # SOURCE
        # ------------------------------------------------------

        if source_score >= 90:

            reasons.append(
                "high source credibility"
            )

        elif source_score >= 80:

            reasons.append(
                "good source credibility"
            )

        elif source_score >= 60:

            reasons.append(
                "moderate source credibility"
            )

        else:

            reasons.append(
                "limited source credibility"
            )

        # ------------------------------------------------------
        # EVIDENCE
        # ------------------------------------------------------

        if evidence_score >= 80:

            reasons.append(
                "strong evidence indicators"
            )

        elif evidence_score >= 60:

            reasons.append(
                "reasonable evidence indicators"
            )

        elif evidence_score >= 40:

            reasons.append(
                "limited evidence indicators"
            )

        else:

            reasons.append(
                "weak evidence indicators"
            )

        # ------------------------------------------------------
        # SPECIFICITY
        # ------------------------------------------------------

        if specificity_score >= 80:

            reasons.append(
                "highly specific claims"
            )

        elif specificity_score >= 60:

            reasons.append(
                "reasonably specific claims"
            )

        elif specificity_score >= 40:

            reasons.append(
                "limited claim specificity"
            )

        else:

            reasons.append(
                "low claim specificity"
            )

        # ------------------------------------------------------
        # TEMPORAL
        # ------------------------------------------------------

        if temporal_score >= 90:

            reasons.append(
                "consistent timestamps"
            )

        elif temporal_score >= 70:

            reasons.append(
                "mostly consistent timestamps"
            )

        else:

            reasons.append(
                "temporal inconsistencies"
            )

        # ------------------------------------------------------
        # COMPLETENESS
        # ------------------------------------------------------

        if completeness_score >= 90:

            reasons.append(
                "complete metadata"
            )

        elif completeness_score >= 80:

            reasons.append(
                "adequate metadata"
            )

        elif completeness_score >= 60:

            reasons.append(
                "sufficient metadata for provisional verification"
            )

        else:

            reasons.append(
                "incomplete metadata"
            )

        # ------------------------------------------------------
        # FINAL MESSAGE
        # ------------------------------------------------------

        if verified:

            return (
                f"{topic.title} received a provisional "
                f"reliability score of "
                f"{reliability_score}/100 and passed "
                f"Stage 1 verification because it has "
                + ", ".join(reasons)
                + "."
            )

        return (
            f"{topic.title} received a provisional "
            f"reliability score of "
            f"{reliability_score}/100 but is not "
            f"verified yet because it has "
            + ", ".join(reasons)
            + ". More evidence or cross-source "
            f"confirmation is required."
        )

    # ==========================================================
    # ENGINE STATUS
    # ==========================================================

    def get_status(self) -> dict:
        """
        Return verification statistics.
        """

        return {

            "processed":
                self.verification_count,

            "verified":
                self.verified_count,

            "pending":
                self.pending_count,
        }