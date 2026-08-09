"""
Persistent Story Clusterer

Groups articles that describe the same underlying event.

Important:
    Same company/topic != same event.

The EventSimilarityEngine is responsible for deciding
whether two articles represent the same event.

The clusterer is responsible for maintaining the
collection of persistent story clusters.
"""

from typing import Dict, List, Optional

from app.agent.models import Topic

from app.clustering.models import StoryCluster

from app.clustering.event_similarity import (
    EventSimilarityEngine,
)


class StoryClusterer:

    def __init__(
        self,
        similarity_engine: Optional[
            EventSimilarityEngine
        ] = None,
    ):

        self.similarity_engine = (
            similarity_engine
            or EventSimilarityEngine()
        )

        # Persistent in-memory cluster store.
        #
        # Later this can be replaced by PostgreSQL,
        # Redis, or another persistence layer without
        # changing the clustering logic.
        self.clusters: Dict[
            str,
            StoryCluster,
        ] = {}

        self._next_cluster_id = 1

    # ======================================================
    # PUBLIC API
    # ======================================================

    def cluster_topics(
        self,
        topics: List[Topic],
    ) -> List[StoryCluster]:

        for topic in topics:

            self.add_topic(
                topic
            )

        return self.get_clusters()

    # ======================================================
    # ADD SINGLE TOPIC
    # ======================================================

    def add_topic(
        self,
        topic: Topic,
    ) -> StoryCluster:

        # --------------------------------------------------
        # Find the best existing cluster.
        # --------------------------------------------------

        best_cluster = None
        best_score = 0.0

        for cluster in (
            self.clusters.values()
        ):

            if cluster.status != "ACTIVE":
                continue

            similarity = (
                self._best_cluster_similarity(
                    topic,
                    cluster,
                )
            )

            if similarity > best_score:

                best_score = similarity
                best_cluster = cluster

        # --------------------------------------------------
        # SAME_EVENT
        # --------------------------------------------------

        if (
            best_cluster is not None
            and
            best_score
            >= self.similarity_engine
            .same_event_threshold
        ):

            best_cluster.add_topic(
                topic
            )

            best_cluster.update_best_topic()

            return best_cluster

        # --------------------------------------------------
        # POSSIBLY_SAME_EVENT
        #
        # We intentionally DO NOT merge these yet.
        #
        # This prevents uncertain matches from polluting
        # clusters.
        # --------------------------------------------------

        # --------------------------------------------------
        # Create a new cluster.
        # --------------------------------------------------

        return self._create_cluster(
            topic
        )

    # ======================================================
    # COMPARE TOPIC AGAINST CLUSTER
    # ======================================================

    def _best_cluster_similarity(
        self,
        topic: Topic,
        cluster: StoryCluster,
    ) -> float:

        best_score = 0.0

        for existing_topic in (
            cluster.topics
        ):

            result = (
                self.similarity_engine.compare(
                    topic,
                    existing_topic,
                )
            )

            if result.score > best_score:

                best_score = result.score

        return best_score

    # ======================================================
    # CREATE CLUSTER
    # ======================================================

    def _create_cluster(
        self,
        topic: Topic,
    ) -> StoryCluster:

        cluster_id = (
            f"cluster-{self._next_cluster_id:04d}"
        )

        self._next_cluster_id += 1

        cluster = StoryCluster(
            cluster_id=cluster_id
        )

        cluster.add_topic(
            topic
        )

        cluster.update_best_topic()

        self.clusters[
            cluster_id
        ] = cluster

        return cluster

    # ======================================================
    # GET CLUSTERS
    # ======================================================

    def get_clusters(
        self,
    ) -> List[StoryCluster]:

        return list(
            self.clusters.values()
        )

    # ======================================================
    # ACTIVE CLUSTERS
    # ======================================================

    def get_active_clusters(
        self,
    ) -> List[StoryCluster]:

        return [
            cluster
            for cluster in (
                self.clusters.values()
            )
            if cluster.status == "ACTIVE"
        ]

    # ======================================================
    # FIND CLUSTER
    # ======================================================

    def get_cluster(
        self,
        cluster_id: str,
    ) -> Optional[StoryCluster]:

        return self.clusters.get(
            cluster_id
        )

    # ======================================================
    # CLOSE CLUSTER
    # ======================================================

    def close_cluster(
        self,
        cluster_id: str,
    ) -> bool:

        cluster = (
            self.clusters.get(
                cluster_id
            )
        )

        if cluster is None:
            return False

        cluster.status = "CLOSED"

        return True

    # ======================================================
    # REMOVE CLOSED CLUSTERS
    # ======================================================

    def remove_closed_clusters(
        self,
    ) -> None:

        closed_ids = [
            cluster_id
            for cluster_id, cluster
            in self.clusters.items()
            if cluster.status == "CLOSED"
        ]

        for cluster_id in closed_ids:

            del self.clusters[
                cluster_id
            ]

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(self) -> dict:

        clusters = (
            self.get_clusters()
        )

        active = [
            cluster
            for cluster in clusters
            if cluster.status == "ACTIVE"
        ]

        closed = [
            cluster
            for cluster in clusters
            if cluster.status == "CLOSED"
        ]

        return {
            "clusters": len(clusters),
            "active": len(active),
            "closed": len(closed),
            "articles": sum(
                cluster.article_count
                for cluster in clusters
            ),
        }