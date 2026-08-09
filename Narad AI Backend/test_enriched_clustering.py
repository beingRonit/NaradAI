"""
Integration test:

    RSS Collector
        ↓
    Article Enrichment
        ↓
    Story Clustering V2

This test intentionally does NOT run verification.

The goal is to determine whether clustering improves when
the articles contain enriched/full article content.
"""

from app.discovery.collector import NewsCollector

from app.enrichment.article_fetcher import (
    ArticleFetcher,
)

from app.clustering.clusterer import (
    StoryClusterer,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

MAX_ARTICLES = 50

CLUSTER_THRESHOLD = 0.52

STRONG_CLUSTER_THRESHOLD = 0.68


# ==========================================================
# PRINT ARTICLE
# ==========================================================

def print_enrichment_result(
    index,
    topic,
    result,
):

    print(
        f"\n--- Article {index} ---"
    )

    print(
        f"Title: {topic.title}"
    )

    print(
        f"Source: {topic.source}"
    )

    print(
        f"Success: {result.success}"
    )

    print(
        f"HTTP Status: {result.status_code}"
    )

    print(
        f"Attempt: {result.attempt_number}"
    )

    print(
        f"Extractor: {result.extractor}"
    )

    print(
        f"Original Content: "
        f"{result.original_content_length}"
    )

    print(
        f"Enriched Content: "
        f"{result.enriched_content_length}"
    )

    if result.error:

        print(
            f"Error: {result.error}"
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
        f"Cluster: {cluster.cluster_id}"
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

    for index, topic_id in enumerate(
        cluster.topic_ids
    ):

        title = cluster.titles[
            index
        ]

        source = cluster.sources[
            index
        ]

        similarity = (
            cluster.similarity_scores.get(
                topic_id
            )
        )

        print(
            f"\n  {index + 1}. {title}"
        )

        print(
            f"     Source: {source}"
        )

        if similarity is not None:

            print(
                f"     Similarity: "
                f"{similarity:.3f}"
            )

    # ------------------------------------------------------
    # Relationship evidence
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
                f"    Decision: "
                f"{relation.decision}"
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

            if relation.shared_entities:

                print(
                    "    Shared entities: "
                    + ", ".join(
                        relation.shared_entities
                    )
                )

            if relation.shared_keywords:

                print(
                    "    Shared keywords: "
                    + ", ".join(
                        relation.shared_keywords[:10]
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
# PRINT RELATION
# ==========================================================

def print_relation(
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
        f"Score: {relation.score:.3f}"
    )

    print(
        f"Decision: {relation.decision}"
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

    fetcher = ArticleFetcher(
        timeout=20
    )

    try:

        # ==================================================
        # STEP 1 — RSS COLLECTION
        # ==================================================

        print(
            "\n========== RSS COLLECTION =========="
        )

        topics = collector.collect()

        if not topics:

            print(
                "No articles were collected."
            )

            return

        topics = topics[
            :MAX_ARTICLES
        ]

        print(
            f"Articles discovered: "
            f"{len(topics)}"
        )

        # ==================================================
        # STEP 2 — ARTICLE ENRICHMENT
        # ==================================================

        print(
            "\n========== ARTICLE ENRICHMENT =========="
        )

        enrichment_results = []

        successful = 0

        failed = 0

        cached = 0

        for index, topic in enumerate(
            topics,
            start=1,
        ):

            print(
                f"\nProcessing article "
                f"{index}/{len(topics)}..."
            )

            result = fetcher.enrich(
                topic
            )

            enrichment_results.append(
                result
            )

            if result.success:

                if (
                    result.extractor
                    == "cached"
                ):

                    cached += 1

                else:

                    successful += 1

            else:

                failed += 1

            print_enrichment_result(
                index,
                topic,
                result,
            )

        # ==================================================
        # ENRICHMENT SUMMARY
        # ==================================================

        print(
            "\n========== ENRICHMENT SUMMARY =========="
        )

        print(
            f"Successful: "
            f"{successful}"
        )

        print(
            f"Failed: "
            f"{failed}"
        )

        print(
            f"Cached: "
            f"{cached}"
        )

        # ==================================================
        # CONTENT STATISTICS
        # ==================================================

        total_content = sum(
            len(topic.content or "")
            for topic in topics
        )

        enriched_articles = sum(
            1
            for topic in topics
            if (
                getattr(
                    topic,
                    "enrichment_status",
                    None,
                )
                is not None
                and
                str(
                    topic.enrichment_status
                ).endswith(
                    "SUCCESS"
                )
            )
        )

        average_content = (
            total_content
            /
            max(
                len(topics),
                1,
            )
        )

        print(
            "\n========== CONTENT STATISTICS =========="
        )

        print(
            f"Total content characters: "
            f"{total_content}"
        )

        print(
            f"Average content/article: "
            f"{average_content:.0f}"
        )

        print(
            f"Articles with successful enrichment: "
            f"{enriched_articles}"
        )

        # ==================================================
        # STEP 3 — CLUSTERING
        # ==================================================

        print(
            "\n========== STORY CLUSTERING V2 =========="
        )

        clusterer = StoryClusterer(

            threshold=(
                CLUSTER_THRESHOLD
            ),

            strong_threshold=(
                STRONG_CLUSTER_THRESHOLD
            ),
        )

        result = clusterer.cluster(
            topics
        )

        # ==================================================
        # CLUSTER SUMMARY
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

        multi_article_clusters = [
            cluster
            for cluster in result.clusters
            if cluster.article_count > 1
        ]

        if not multi_article_clusters:

            print(
                "No multi-article clusters found."
            )

        else:

            for cluster in (
                multi_article_clusters
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
        # STRONGEST RELATIONSHIPS
        # ==================================================

        print(
            "\n========== STRONGEST RELATIONSHIPS =========="
        )

        topics_by_id = {
            topic.id: topic
            for topic in topics
        }

        strongest = sorted(
            result.relations,
            key=lambda relation:
                relation.score,
            reverse=True,
        )

        if not strongest:

            print(
                "No relationships generated."
            )

        else:

            for relation in strongest[:15]:

                print_relation(
                    relation,
                    topics_by_id,
                )

        # ==================================================
        # POSSIBLE RELATIONSHIPS
        # ==================================================

        print(
            "\n========== POSSIBLY RELATED =========="
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

        if not possible:

            print(
                "No possible relationships."
            )

        else:

            for relation in possible[:10]:

                print_relation(
                    relation,
                    topics_by_id,
                )

        # ==================================================
        # FINAL
        # ==================================================

        print(
            "\n=========================================="
        )

        print(
            "ENRICHED CLUSTERING TEST COMPLETE"
        )

        print(
            "=========================================="
        )

    finally:

        fetcher.close()

        collector.close()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()