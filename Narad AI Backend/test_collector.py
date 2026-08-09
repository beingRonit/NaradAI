from app.discovery.collector import NewsCollector


def main():

    collector = NewsCollector()

    try:

        print(
            "\n========== STARTING COLLECTION =========="
        )

        topics = collector.collect()

        print(
            "Articles collected:",
            len(topics)
        )

        print(
            "Collection time:",
            collector.last_collection_time
        )

        print(
            "\n========== ARTICLES =========="
        )

        for index, topic in enumerate(
            topics,
            start=1
        ):

            print(
                f"\n--- Article {index} ---"
            )

            print(
                "ID:",
                topic.id
            )

            print(
                "Title:",
                topic.title
            )

            print(
                "Source:",
                topic.source
            )

            print(
                "Category:",
                topic.category
            )

            print(
                "Tags:",
                topic.tags
            )

            print(
                "Published:",
                topic.published_at
            )

            print(
                "Image:",
                topic.image_url
            )

    finally:

        collector.close()

    # ==========================================================
    # STATUS
    # ==========================================================

    status = collector.get_status()

    print(
        "\n========== COLLECTOR STATUS =========="
    )

    print(
        "Before deduplication:",
        status[
            "total_before_deduplication"
        ]
    )

    print(
        "After deduplication:",
        status[
            "total_collected"
        ]
    )

    print(
        "\nFeed statistics:"
    )

    for source, stats in status[
        "feeds"
    ].items():

        print(
            f"{source}: {stats}"
        )

    print(
        "\nErrors:",
        status["errors"]
    )


if __name__ == "__main__":
    main()