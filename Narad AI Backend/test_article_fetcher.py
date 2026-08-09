"""
Test Story Clustering V2.

Runs against the real RSS collector and prints:

    - overall clustering statistics
    - multi-article clusters
    - multi-source clusters
    - possible relationships
    - strongest article relationships
"""

from app.discovery.collector import NewsCollector

from app.clustering.clusterer import (
    StoryClusterer,
)


# ==========================================================
# PRINT CLUSTER
# ==========================================================

def print_cluster(
    cluster
):

    print(
        "\n----------------------------------------"
    )

    print(
        f"{cluster.cluster_id}"
    )

    print(
        f"Articles: {cluster.article_count}"
    )

    print(
        f"Sources: {cluster.source_count}"
    )

    print(
        f"Multi-source: "
        f"{cluster.is_multi_source}"
    )

    for index, title in enumerate(
        cluster.titles
    ):

        source = cluster.sources[
            index
        ]

        topic_id = cluster.topic_ids[
            index
        ]

        score = (
            cluster.similarity_scores.get(
                topic_id,
                1.0
            )
        )

        print(
            f"\n  {index + 1}. {title}"
        )

        print(
            f"     Source: {source}"
        )

        print(
            f"     Similarity: {score:.3f}"
        )

    # ------------------------------------------------------
    # Explain relationships.
    # ------------------------------------------------------

    if cluster.relations:

        print(
            "\n  Evidence:"
        )

        for relation in (
            cluster.relations
        ):

            print(
                f"\n    Score: "
                f"{relation.score:.3f}"
            )

            print(
                f"    Title: "
                f"{relation.title_score:.3f}"
            )

            print(
                f"    Entity: "
                f"{relation.entity_score:.3f}"
            )

            print(
                f"    Keywords: "
                f"{relation.keyword_score:.3f}"
            )

            print(
                f"    Content: "
                f"{relation.content_score:.3f}"
            )

            print(
                f"    Time: "
                f"{relation.time_score:.3f}"
            )

            print(
                f"    Decision: "
                f"{relation.decision}"
            )

            if relation.shared_entities:

                print(
                    "    Shared entities: "
                    + ", ".join(
                        relation.shared_entities
                    )
                )

            if relation.reasons:

                print(
                    "    Reasons: "
                    + "; ".join(
                        relation.reasons
                    )
                )


# ==========================================================
# PRINT CANDIDATE
# ==========================================================

def print_candidate(
    relation,
    topics_by_id,
):

    topic_a = topics_by_id[
        relation.topic_a
    ]

    topic_b = topics_by_id[
        relation.topic_b
    ]

    print(
        "\n----------------------------------------"
    )

    print(
        f"Score: "
        f"{relation.score:.3f}"
    )

    print(
        f"Decision: "
        f"{relation.decision}"
    )

    print(
        f"\nA: {topic_a.title}"
    )

    print(
        f"   Source: {topic_a.source}"
    )

    print(
        f"\nB: {topic_b.title}"
    )

    print(
        f"   Source: {topic_b.source}"
    )

    print(
        "\nComponents:"
    )

    print(
        f"  Title: "
        f"{relation.title_score:.3f}"
    )

    print(
        f"  Entity: "
        f"{relation.entity_score:.3f}"
    )

    print(
        f"  Keywords: "
        f"{relation.keyword_score:.3f}"
    )

    print(
        f"  Content: "
        f"{relation.content_score:.3f}"
    )

    print(
        f"  Time: "
        f"{relation.time_score:.3f}"
    )

    if relation.shared_entities:

        print(
            "Shared entities: "
            + ", ".join(
                relation.shared_entities
            )
        )

    if relation.shared_keywords:

        print(
            "Shared keywords: "
            + ", ".join(
                relation.shared_keywords[:10]
            )
        )

    if relation.reasons:

        print(
            "Reasons: "
            + "; ".join(
                relation.reasons
            )
        )


# ==========================================================
# MAIN
# ==========================================================

def main():

    collector = NewsCollector()

    try:

        # ==================================================
        # RSS
        # ==================================================

        print(
            "\n========== RSS COLLECTION =========="
        )

        topics = collector.collect()

        print(
            f"Articles discovered: "
            f"{len(topics)}"
        )

        if not topics:

            print(
                "No articles discovered."
            )

            return

        # ==================================================
        # CLUSTER
        # ==================================================

        print(
            "\n========== STORY CLUSTERING V2 =========="
        )

        clusterer = StoryClusterer(
            threshold=0.52,
            strong_threshold=0.68,
        )

        result = clusterer.cluster(
            topics
        )

        # ==================================================
        # SUMMARY
        # ==================================================

        print(
            "\n========== CLUSTER SUMMARY =========="
        )

        print(
            f"Articles: "
            f"{result.total_articles}"
        )

        print(
            f"Clusters: "
            f"{result.total_clusters}"
        )

        print(
            f"Multi-article clusters: "
            f"{result.multi_article_clusters}"
        )

        print(
            f"Multi-source clusters: "
            f"{result.multi_source_clusters}"
        )

        print(
            f"Singleton articles: "
            f"{result.singleton_articles}"
        )

        # ==================================================
        # MULTI-ARTICLE CLUSTERS
        # ==================================================

        print(
            "\n========== MULTI-ARTICLE CLUSTERS =========="
        )

        multi_clusters = [
            cluster
            for cluster in result.clusters
            if cluster.article_count > 1
        ]

        if not multi_clusters:

            print(
                "No multi-article clusters found."
            )

        else:

            for cluster in (
                multi_clusters
            ):

                print_cluster(
                    cluster
                )

        # ==================================================
        # MULTI-SOURCE CLUSTERS
        # ==================================================

        print(
            "\n========== MULTI-SOURCE CLUSTERS =========="
        )

        multi_source_clusters = [
            cluster
            for cluster in result.clusters
            if cluster.is_multi_source
        ]

        if not multi_source_clusters:

            print(
                "No multi-source clusters found."
            )

        else:

            for cluster in (
                multi_source_clusters
            ):

                print_cluster(
                    cluster
                )

        # ==================================================
        # POSSIBLE RELATIONSHIPS
        # ==================================================

        print(
            "\n========== POSSIBLE RELATIONSHIPS =========="
        )

        possible = [
            relation
            for relation in result.relations
            if relation.decision
            == "POSSIBLY_RELATED"
        ]

        possible.sort(
            key=lambda relation:
                relation.score,
            reverse=True,
        )

        topics_by_id = {
            topic.id: topic
            for topic in topics
        }

        if not possible:

            print(
                "No possible relationships found."
            )

        else:

            for relation in possible[:15]:

                print_candidate(
                    relation,
                    topics_by_id,
                )

        # ==================================================
        # STRONGEST RELATIONSHIPS
        # ==================================================

        print(
            "\n========== STRONGEST RELATIONSHIPS =========="
        )

        strongest = sorted(
            result.relations,
            key=lambda relation:
                relation.score,
            reverse=True,
        )

        for relation in strongest[:15]:

            print_candidate(
                relation,
                topics_by_id,
            )

        # ==================================================
        # COMPLETE
        # ==================================================

        print(
            "\n========== CLUSTERING COMPLETE =========="
        )

    finally:

        collector.close()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()