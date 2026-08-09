"""
Persistent state representation for the autonomous news pipeline.

A CycleState represents the state of the system at a particular
processing cycle.

The state is intentionally independent of the actual pipeline
components so that it can later be persisted to PostgreSQL,
Redis, or another database.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from app.agent.models import Topic
from app.clustering.models import StoryCluster


@dataclass
class CycleState:
    """
    State maintained across autonomous processing cycles.
    """

    cycle_id: int

    started_at: datetime

    last_cycle_at: Optional[datetime] = None

    # ------------------------------------------------------
    # Article state
    # ------------------------------------------------------

    discovered_topics: List[Topic] = field(
        default_factory=list
    )

    verified_topics: List[Topic] = field(
        default_factory=list
    )

    evaluated_topics: List[Topic] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # Story state
    # ------------------------------------------------------

    story_clusters: Dict[
        str,
        StoryCluster,
    ] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Ranking state
    # ------------------------------------------------------

    current_rankings: List[Topic] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # Publication state
    # ------------------------------------------------------

    posting_deadline: Optional[datetime] = None

    published: bool = False

    published_cluster_id: Optional[str] = None

    published_topic_id: Optional[str] = None

    # ------------------------------------------------------
    # Cycle statistics
    # ------------------------------------------------------

    new_articles_count: int = 0

    verified_count: int = 0

    evaluated_count: int = 0

    cluster_count: int = 0

    # ======================================================
    # UPDATE HELPERS
    # ======================================================

    def update_discovered(
        self,
        topics: List[Topic],
    ) -> None:

        self.discovered_topics = topics

        self.new_articles_count = len(
            topics
        )

    def update_verified(
        self,
        topics: List[Topic],
    ) -> None:

        self.verified_topics = topics

        self.verified_count = len(
            topics
        )

    def update_evaluated(
        self,
        topics: List[Topic],
    ) -> None:

        self.evaluated_topics = topics

        self.evaluated_count = len(
            topics
        )

    def update_clusters(
        self,
        clusters: List[StoryCluster],
    ) -> None:

        self.story_clusters = {
            cluster.cluster_id: cluster
            for cluster in clusters
        }

        self.cluster_count = len(
            clusters
        )

    def update_rankings(
        self,
        topics: List[Topic],
    ) -> None:

        self.current_rankings = topics

    # ======================================================
    # PUBLICATION
    # ======================================================

    def mark_published(
        self,
        cluster_id: Optional[str] = None,
        topic_id: Optional[str] = None,
    ) -> None:

        self.published = True

        self.published_cluster_id = (
            cluster_id
        )

        self.published_topic_id = (
            topic_id
        )

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(self) -> dict:

        return {
            "cycle_id": self.cycle_id,
            "started_at": self.started_at,
            "last_cycle_at": self.last_cycle_at,

            "discovered": len(
                self.discovered_topics
            ),

            "verified": len(
                self.verified_topics
            ),

            "evaluated": len(
                self.evaluated_topics
            ),

            "clusters": len(
                self.story_clusters
            ),

            "ranked": len(
                self.current_rankings
            ),

            "published": self.published,

            "published_cluster_id": (
                self.published_cluster_id
            ),

            "published_topic_id": (
                self.published_topic_id
            ),

            "posting_deadline": (
                self.posting_deadline
            ),
        }