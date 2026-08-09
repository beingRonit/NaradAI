"""
Test EventSimilarityEngine V2.

The test:

    1. Collects RSS articles
    2. Enriches them
    3. Finds known article pairs
    4. Compares them
    5. Prints all diagnostic signals
"""

from app.discovery.collector import NewsCollector

from app.enrichment.article_fetcher import (
    ArticleFetcher,
)

from app.clustering.event_similarity import (
    EventSimilarityEngine,
)


# ==========================================================
# RESULT PRINTER
# ==========================================================

def print_result(
    title_a,
    title_b,
    result,
):

    print(
        "\n========================================"
    )

    print(
        f"A: {title_a}"
    )

    print(
        f"B: {title_b}"
    )

    print(
        "\n---------- RESULT ----------"
    )

    print(
        f"Score: {result.score:.3f}"
    )

    print(
        f"Decision: {result.decision}"
    )

    print(
        "\nComponents:"
    )

    print(
        f"Title:       {result.title_score:.3f}"
    )

    print(
        f"Action:      {result.action_score:.3f}"
    )

    print(
        f"Event:       {result.event_score:.3f}"
    )

    print(
        f"Entity:      {result.entity_score:.3f}"
    )

    print(
        f"Distinctive: {result.distinctive_score:.3f}"
    )

    print(
        f"Content:     {result.content_score:.3f}"
    )

    print(
        f"Time:        {result.time_score:.3f}"
    )

    # ------------------------------------------------------
    # Shared entities
    # ------------------------------------------------------

    if result.shared_entities:

        print(
            "\nShared entities:"
        )

        print(
            ", ".join(
                result.shared_entities
            )
        )

    # ------------------------------------------------------
    # Shared actions
    # ------------------------------------------------------

    if result.shared_actions:

        print(
            "\nShared actions:"
        )

        print(
            ", ".join(
                result.shared_actions
            )
        )

    # ------------------------------------------------------
    # Shared event terms
    # ------------------------------------------------------

    if result.shared_event_terms:

        print(
            "\nShared event terms:"
        )

        print(
            ", ".join(
                result.shared_event_terms
            )
        )

    # ------------------------------------------------------
    # Shared distinctive terms
    # ------------------------------------------------------

    if result.shared_distinctive_terms:

        print(
            "\nShared distinctive terms:"
        )

        print(
            ", ".join(
                result.shared_distinctive_terms
            )
        )

    # ------------------------------------------------------
    # Reasons
    # ------------------------------------------------------

    if result.reasons:

        print(
            "\nReasons:"
        )

        for reason in result.reasons:

            print(
                f"- {reason}"
            )


# ==========================================================
# FIND ARTICLE
# ==========================================================

def find_article(
    topics,
    phrase,
):

    phrase = phrase.lower()

    for topic in topics:

        title = (
            topic.title or ""
        ).lower()

        if phrase in title:

            return topic

    return None


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
        # COLLECTION
        # ==================================================

        print(
            "\n========== COLLECTING =========="
        )

        topics = collector.collect()

        print(
            f"Articles: {len(topics)}"
        )

        # ==================================================
        # ENRICHMENT
        # ==================================================

        print(
            "\n========== ENRICHING =========="
        )

        successful = 0

        failed = 0

        cached = 0

        for topic in topics:

            result = fetcher.enrich(
                topic
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

        print(
            "\nEnrichment summary:"
        )

        print(
            f"Successful: {successful}"
        )

        print(
            f"Failed: {failed}"
        )

        print(
            f"Cached: {cached}"
        )

        # ==================================================
        # ENGINE
        # ==================================================

        engine = (
            EventSimilarityEngine()
        )

        # ==================================================
        # TEST PAIRS
        # ==================================================

        test_pairs = [

            (
                "ChatGPT brings unlimited",
                "OpenAI is giving ChatGPT",
            ),

            (
                "What’s behind the Google AI",
                "The messy politics behind Google",
            ),

            (
                "Suno hopes to go legit",
                "Amid legal battles, Suno",
            ),

            (
                "OpenAI’s expensive smart speaker",
                "OpenAI’s new AI smart speaker",
            ),

            (
                "OpenAI says it slowed Astra",
                "OpenAI puts the brakes",
            ),

            (
                "Google Maps adds agentic",
                "Jeff Dean and other top AI",
            ),
        ]

        # ==================================================
        # TESTS
        # ==================================================

        print(
            "\n========== EVENT SIMILARITY TESTS =========="
        )

        tested = 0

        skipped = 0

        for phrase_a, phrase_b in (
            test_pairs
        ):

            topic_a = find_article(
                topics,
                phrase_a,
            )

            topic_b = find_article(
                topics,
                phrase_b,
            )

            if topic_a is None:

                print(
                    "\nSKIP:"
                    f" Could not find '{phrase_a}'"
                )

                skipped += 1

                continue

            if topic_b is None:

                print(
                    "\nSKIP:"
                    f" Could not find '{phrase_b}'"
                )

                skipped += 1

                continue

            result = engine.compare(
                topic_a,
                topic_b,
            )

            print_result(
                topic_a.title,
                topic_b.title,
                result,
            )

            tested += 1

        # ==================================================
        # SUMMARY
        # ==================================================

        print(
            "\n========================================"
        )

        print(
            "EVENT SIMILARITY TEST SUMMARY"
        )

        print(
            "========================================"
        )

        print(
            f"Tests completed: {tested}"
        )

        print(
            f"Tests skipped:   {skipped}"
        )

        print(
            "========================================"
        )

    finally:

        fetcher.close()

        collector.close()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()