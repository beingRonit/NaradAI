from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.agent.models import Topic
from app.verification.verifier import VerificationEngine


@dataclass
class StoryCluster:
    """
    Represents one underlying news event/story.

    A cluster can contain multiple articles from different
    sources covering the same event.
    """

    cluster_id: str

    topics: List[Topic] = field(default_factory=list)

    canonical_title: Optional[str] = None

    first_seen: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    best_topic: Optional[Topic] = None

    confidence: float = 0.0

    status: str = "ACTIVE"

    def add_topic(
        self,
        topic: Topic,
    ) -> None:

        # A feed can legitimately return the same URL in later
        # cycles. Treat URL/ID as article identity so a retry does
        # not inflate the story with duplicate evidence.
        duplicate = any(
            existing.id == topic.id
            or (
                existing.url
                and topic.url
                and existing.url == topic.url
            )
            for existing in self.topics
        )

        if not duplicate:
            self.topics.append(topic)

        now = (
            topic.discovered_at
            or topic.published_at
            or datetime.now()
        )

        if self.first_seen is None:
            self.first_seen = now

        if (
            self.last_updated is None
            or now > self.last_updated
        ):
            self.last_updated = now

        self._update_canonical_title()

    def _update_canonical_title(self) -> None:

        if not self.topics:
            return

        # For now the first article becomes the
        # canonical title.
        #
        # We'll later replace this with a proper
        # representative-topic selector using
        # reliability + editorial score.

        if self.canonical_title is None:
            self.canonical_title = (
                self.topics[0].title
            )

    @property
    def article_count(self) -> int:
        return len(self.topics)

    @property
    def sources(self) -> List[str]:

        return sorted(
            {
                VerificationEngine.normalize_source(topic.source)
                for topic in self.topics
                if topic.source
            }
        )

    @property
    def topic_ids(self) -> List[str]:

        return [
            topic.id
            for topic in self.topics
        ]


    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def independent_sources(self) -> List[str]:
        return self.sources

    def verified_topics(self) -> List[Topic]:
        return [
            topic
            for topic in self.topics
            if topic.reliability_score is not None
            and topic.reliability_score >= 55.0
        ]

    def corroboration_score(self) -> float:
        """Diminishing-return score for distinct source corroboration."""
        count = self.source_count
        if count <= 1:
            return 0.0
        if count == 2:
            return 0.65
        if count == 3:
            return 0.82
        if count == 4:
            return 0.91
        return 0.95

    def update_best_topic(self) -> None:

        if not self.topics:
            self.best_topic = None
            return

        def topic_score(
            topic: Topic,
        ) -> float:

            reliability = (
                topic.reliability_score
                or 0.0
            )

            evaluation = (
                topic.evaluation_score
                or 0.0
            )

            return (
                reliability * 0.40
                +
                evaluation * 0.60
            )

        self.best_topic = max(
            self.topics,
            key=topic_score,
        )

        self.confidence = round(
            topic_score(
                self.best_topic
            ),
            2,
        )