"""
Editorial Evaluator

Evaluates news Topics according to the current Persona.

The evaluator considers:

    - Persona interest
    - Technical value
    - Reliability
    - Freshness
    - Memory / novelty
    - Editorial rules

The evaluator does NOT:

    - collect news
    - verify external sources
    - rank articles
    - publish content
"""

from datetime import datetime, timezone

from app.agent.models import (
    Persona,
    Topic,
    TopicStatus,
    EvaluationResult,
)


class EditorialEvaluator:
    """
    Evaluates a Topic according to the current Persona.
    """

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self, persona_engine):
        """
        Store the PersonaEngine.
        """

        self.engine = persona_engine

    # ==========================================================
    # MAIN EVALUATION
    # ==========================================================

    def evaluate(
        self,
        topic: Topic
    ) -> EvaluationResult:
        """
        Evaluate one Topic.
        """

        persona = self.engine.get_persona()

        if persona is None:
            raise ValueError(
                "No Persona is loaded."
            )

        # ------------------------------------------------------
        # INDIVIDUAL SCORES
        # ------------------------------------------------------

        interest_score = self._interest_score(
            topic,
            persona
        )

        technical_score = self._technical_score(
            topic
        )

        reliability_score = self._reliability_score(
            topic
        )

        freshness_score = self._freshness_score(
            topic
        )

        memory_score = self._memory_score(
            topic,
            persona
        )

        editorial_score = self._editorial_score(
            topic,
            persona
        )

        # ------------------------------------------------------
        # OVERALL SCORE
        # ------------------------------------------------------

        overall_score = self._calculate_overall_score(
            interest_score,
            technical_score,
            reliability_score,
            freshness_score,
            memory_score,
            editorial_score
        )

        # ------------------------------------------------------
        # V5 PROVISIONAL PUBLISHABILITY
        # ------------------------------------------------------
        # The final story-level policy is applied by PublicationPolicy.
        # This flag remains useful for legacy callers and single-article tests.
        # V5 deliberately keeps this conservative.
        publish = (
            overall_score >= 78
            and reliability_score >= 72
            and editorial_score >= 80
        )

        score_breakdown = {
            "interest": round(interest_score, 2),
            "technical": round(technical_score, 2),
            "reliability": round(reliability_score, 2),
            "freshness": round(freshness_score, 2),
            "memory": round(memory_score, 2),
            "editorial": round(editorial_score, 2),
            "overall": round(overall_score, 2),
        }

        # ------------------------------------------------------
        # EXPLANATION
        # ------------------------------------------------------

        reason = self._generate_reason(
            topic,
            interest_score,
            technical_score,
            reliability_score,
            freshness_score,
            memory_score,
            editorial_score,
            overall_score
        )

        # ------------------------------------------------------
        # UPDATE TOPIC
        # ------------------------------------------------------

        topic.evaluation_score = overall_score

        topic.status = TopicStatus.EVALUATED

        # ------------------------------------------------------
        # RETURN RESULT
        # ------------------------------------------------------

        return EvaluationResult(
            topic_id=topic.id,
            topic_title=topic.title,

            interest_score=interest_score,

            technical_score=technical_score,

            reliability_score=reliability_score,

            freshness_score=freshness_score,

            memory_score=memory_score,

            editorial_score=editorial_score,

            overall_score=overall_score,

            publish=publish,

            reason=reason,
            score_breakdown=score_breakdown,
        )

    # ==========================================================
    # INTEREST SCORE
    # ==========================================================

    def _interest_score(
        self,
        topic: Topic,
        persona: Persona
    ) -> float:
        """
        Calculate how strongly a Topic matches
        the Persona's interests.

        Uses aliases to understand related concepts.

        Example:

            Persona interest:
                LLMs

            Can match:
                GPT
                Claude
                Gemini
                foundation model
                language model
                inference
        """

        if not persona.interests:
            return 0.0

        # ------------------------------------------------------
        # BUILD SEARCHABLE ARTICLE TEXT
        # ------------------------------------------------------

        searchable_text = " ".join(
            [
                topic.title,
                topic.summary,
                topic.category,
                " ".join(topic.tags)
            ]
        ).lower()

        # ------------------------------------------------------
        # INTEREST ALIASES
        # ------------------------------------------------------

        interest_aliases = {

            "llm": [
                "llm",
                "llms",
                "language model",
                "language models",
                "large language model",
                "large language models",
                "foundation model",
                "foundation models",
                "generative ai",
                "gpt",
                "claude",
                "gemini",
                "inference",
                "transformer",
                "chatbot",
                "chatbots",
            ],

            "open source": [
                "open source",
                "open-source",
                "open model",
                "open models",
                "open weights",
                "open-weight",
                "open source model",
                "open-source model",
            ],

            "cybersecurity": [
                "cybersecurity",
                "cyber security",
                "security vulnerability",
                "vulnerability",
                "vulnerabilities",
                "exploit",
                "exploits",
                "malware",
                "ransomware",
                "zero-day",
                "zero day",
                "security breach",
                "data breach",
            ],

            "artificial intelligence": [
                "artificial intelligence",
                "artificial intelligence",
                " ai ",
                "generative ai",
                "machine learning",
                "deep learning",
                "foundation model",
                "ai model",
                "ai models",
                "ai agent",
                "ai agents",
            ],

            "machine learning": [
                "machine learning",
                "deep learning",
                "neural network",
                "neural networks",
                "training",
                "inference",
                "model",
                "models",
            ],

            "robotics": [
                "robot",
                "robots",
                "robotics",
                "humanoid",
                "humanoids",
                "autonomous robot",
            ],

            "cloud": [
                "cloud",
                "cloud computing",
                "cloud infrastructure",
                "aws",
                "azure",
                "google cloud",
            ],

            "developer": [
                "developer",
                "developers",
                "programming",
                "software development",
                "github",
                "api",
                "sdk",
            ],
        }

        # ------------------------------------------------------
        # FIND BEST INTEREST MATCH
        # ------------------------------------------------------

        best_score = 0.0

        for interest in persona.interests.values():

            interest_name = (
                interest.topic
                .strip()
                .lower()
            )

            aliases = interest_aliases.get(
                interest_name,
                [interest_name]
            )

            matched_aliases = []

            for alias in aliases:

                if alias in searchable_text:

                    matched_aliases.append(
                        alias
                    )

            if not matched_aliases:
                continue

            # --------------------------------------------------
            # COVERAGE
            # --------------------------------------------------
            #
            # More matching concepts means stronger evidence
            # that the article is genuinely related.
            #
            # Maximum useful coverage = 3 aliases.
            #
            # --------------------------------------------------

            coverage = min(
                len(matched_aliases) / 3,
                1.0
            )

            score = (
                interest.weight
                * interest.confidence
                * (
                    0.70
                    + (0.30 * coverage)
                )
            )

            best_score = max(
                best_score,
                score
            )

        return round(
            min(best_score, 100.0),
            2
        )

    # ==========================================================
    # TECHNICAL SCORE
    # ==========================================================

    def _technical_score(
        self,
        topic: Topic
    ) -> float:
        """Score concrete technical substance, not keyword volume."""
        text = " ".join([topic.title or "", topic.summary or "", topic.content or "", topic.category or "", " ".join(topic.tags)]).lower()

        signals = {
            "research": ("research paper", "technical paper", "preprint", "benchmark", "evaluation results"),
            "architecture": ("architecture", "inference architecture", "system design", "model architecture"),
            "security": ("vulnerability", "zero-day", "exploit", "security advisory", "security flaw", "breach"),
            "developer": ("api", "sdk", "developer platform", "developer tools", "open source"),
            "performance": ("latency", "throughput", "inference speed", "accuracy", "performance", "benchmark"),
            "infrastructure": ("gpu", "data center", "datacenter", "infrastructure", "cloud infrastructure", "semiconductor", "chip"),
            "release": ("launches", "released", "release", "announces", "available", "ships"),
            "robotics": ("robotics", "humanoid", "autonomous robot", "robot fleet"),
        }
        weights = {
            "research": 18, "architecture": 18, "security": 20, "developer": 12,
            "performance": 14, "infrastructure": 14, "release": 6, "robotics": 12,
        }

        score = 0.0
        for name, terms in signals.items():
            if any(term in text for term in terms):
                score += weights[name]

        # Quantitative claims and concrete technical nouns are useful, but
        # never allowed to overwhelm the actual substance signals.
        import re
        if re.search(r"\b\d+(?:\.\d+)?%", text):
            score += 8
        if re.search(r"\b(?:latency|throughput|tokens|parameters|fps|teraflops)\b", text):
            score += 6

        return round(min(score, 100.0), 2)

    # ==========================================================
    # RELIABILITY SCORE
    # ==========================================================

    def _reliability_score(
        self,
        topic: Topic
    ) -> float:
        """
        Use the reliability score produced
        by the VerificationEngine.
        """

        if topic.reliability_score is not None:

            return float(
                topic.reliability_score
            )

        # Fallback when verification has not
        # happened yet.

        return 50.0

    # ==========================================================
    # FRESHNESS SCORE
    # ==========================================================

    def _freshness_score(
        self,
        topic: Topic
    ) -> float:
        """
        Calculate freshness based on publication time.

        All timestamps are treated as UTC-aware.
        """

        now = datetime.now(
            timezone.utc
        )

        published_at = topic.published_at

        if published_at is None:
            return 35.0

        # ------------------------------------------------------
        # SAFETY FOR OLD NAIVE DATETIME OBJECTS
        # ------------------------------------------------------

        if published_at.tzinfo is None:

            published_at = published_at.replace(
                tzinfo=timezone.utc
            )

        # ------------------------------------------------------
        # AGE
        # ------------------------------------------------------

        age_hours = (
            now - published_at
        ).total_seconds() / 3600

        # Prevent negative values caused by
        # slightly incorrect future timestamps.

        age_hours = max(
            age_hours,
            0
        )

        # ------------------------------------------------------
        # SCORE
        # ------------------------------------------------------

        if age_hours < 1:
            return 100.0

        if age_hours < 3:
            return 90.0

        if age_hours < 6:
            return 80.0

        if age_hours < 12:
            return 65.0

        if age_hours < 24:
            return 50.0

        if age_hours < 48:
            return 30.0

        return 10.0

    # ==========================================================
    # MEMORY / NOVELTY SCORE
    # ==========================================================

    def _memory_score(
        self,
        topic: Topic,
        persona: Persona
    ) -> float:
        """Return novelty score using normalized tokens and entity overlap."""
        if not persona.memory:
            return 100.0

        import re
        def tokens(text):
            return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}

        topic_tokens = tokens(" ".join([topic.title or "", topic.summary or "", " ".join(topic.tags)]))
        if not topic_tokens:
            return 100.0

        best_overlap = 0.0
        for memory in persona.memory:
            memory_tokens = tokens(" ".join([memory.topic, memory.opinion, " ".join(memory.keywords), " ".join(memory.companies), " ".join(memory.technologies)]))
            if not memory_tokens:
                continue
            overlap = len(topic_tokens & memory_tokens) / max(1, len(topic_tokens))
            best_overlap = max(best_overlap, overlap)

        if best_overlap >= 0.60:
            return 10.0
        if best_overlap >= 0.40:
            return 30.0
        if best_overlap >= 0.25:
            return 55.0
        if best_overlap >= 0.15:
            return 75.0
        return 100.0

    # ==========================================================
    # EDITORIAL SCORE
    # ==========================================================

    def _editorial_score(
        self,
        topic: Topic,
        persona: Persona
    ) -> float:
        """
        Check compliance with Persona editorial rules.
        """

        if not persona.editorial_rules:

            return 100.0

        score = 100.0

        text = " ".join(
            [
                topic.title,
                topic.summary,
                topic.category,
                " ".join(topic.tags)
            ]
        ).lower()

        for rule in persona.editorial_rules:

            if not rule.enabled:

                continue

            rule_name = (
                rule.name
                .lower()
            )

            # --------------------------------------------------
            # AVOID HYPE
            # --------------------------------------------------

            if "avoid hype" in rule_name:

                hype_words = [
                    "shocking",
                    "insane",
                    "revolutionary",
                    "unbelievable",
                    "world-changing",
                    "game-changing",
                    "game changing",
                    "groundbreaking",
                    "mind-blowing",
                    "mind blowing",
                ]

                hype_found = any(
                    word in text
                    for word in hype_words
                )

                if hype_found:

                    penalty = min(
                        rule.priority * 2,
                        30
                    )

                    score -= penalty

        return round(
            max(score, 0.0),
            2
        )

    # ==========================================================
    # OVERALL SCORE
    # ==========================================================

    def _calculate_overall_score(
        self,
        interest_score: float,
        technical_score: float,
        reliability_score: float,
        freshness_score: float,
        memory_score: float,
        editorial_score: float
    ) -> float:
        """
        Calculate the final editorial score.

        Interest:       30%
        Technical:      15%
        Reliability:    25%
        Freshness:      15%
        Memory:         10%
        Editorial:       5%
        """

        score = (

            interest_score * 0.30

            + technical_score * 0.15

            + reliability_score * 0.25

            + freshness_score * 0.15

            + memory_score * 0.10

            + editorial_score * 0.05
        )

        return round(
            score,
            2
        )

    # ==========================================================
    # EXPLANATION
    # ==========================================================

    def _generate_reason(
        self,
        topic: Topic,
        interest_score: float,
        technical_score: float,
        reliability_score: float,
        freshness_score: float,
        memory_score: float,
        editorial_score: float,
        overall_score: float
    ) -> str:
        """
        Generate an explainable evaluation reason.
        """

        strengths = []

        # ------------------------------------------------------
        # INTEREST
        # ------------------------------------------------------

        if interest_score >= 80:

            strengths.append(
                "strongly matches persona interests"
            )

        elif interest_score >= 50:

            strengths.append(
                "matches persona interests"
            )

        elif interest_score >= 25:

            strengths.append(
                "partially matches persona interests"
            )

        # ------------------------------------------------------
        # TECHNICAL
        # ------------------------------------------------------

        if technical_score >= 70:

            strengths.append(
                "has high technical value"
            )

        elif technical_score >= 40:

            strengths.append(
                "has moderate technical value"
            )

        # ------------------------------------------------------
        # RELIABILITY
        # ------------------------------------------------------

        if reliability_score >= 85:

            strengths.append(
                "has high reliability"
            )

        elif reliability_score >= 70:

            strengths.append(
                "has acceptable reliability"
            )

        elif reliability_score >= 50:

            strengths.append(
                "has moderate reliability"
            )

        else:

            strengths.append(
                "has low reliability"
            )

        # ------------------------------------------------------
        # FRESHNESS
        # ------------------------------------------------------

        if freshness_score >= 80:

            strengths.append(
                "is highly recent"
            )

        elif freshness_score >= 50:

            strengths.append(
                "is relatively recent"
            )

        # ------------------------------------------------------
        # MEMORY
        # ------------------------------------------------------

        if memory_score >= 80:

            strengths.append(
                "provides novel information"
            )

        elif memory_score >= 50:

            strengths.append(
                "contains some novel information"
            )

        # ------------------------------------------------------
        # EDITORIAL
        # ------------------------------------------------------

        if editorial_score >= 80:

            strengths.append(
                "fits the editorial rules"
            )

        else:

            strengths.append(
                "has editorial concerns"
            )

        # ------------------------------------------------------
        # FINAL REASON
        # ------------------------------------------------------

        return (
            f"{topic.title} scored "
            f"{overall_score}/100 because it "
            + ", ".join(strengths)
            + "."
        )