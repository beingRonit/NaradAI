from datetime import datetime, timedelta

from app.agent.models import Topic

from app.clustering.clusterer import (
    StoryClusterer,
)


# ==========================================================
# HELPERS
# ==========================================================

def make_topic(
    topic_id,
    title,
    source,
    hours_ago=0,
    tags=None,
):

    now = datetime.now()

    published = (
        now
        -
        timedelta(
            hours=hours_ago
        )
    )

    return Topic(
        id=topic_id,
        url=(
            f"https://example.com/"
            f"{topic_id}"
        ),
        title=title,
        summary=title,
        content=(
            f"{title}. "
            f"This is test article content."
        ),
        source=source,
        author="Test Author",
        category="Artificial Intelligence",
        language="en",
        tags=tags or [],
        image_url=None,
        published_at=published,
        discovered_at=published,
    )


# ==========================================================
# PRINT CLUSTERS
# ==========================================================

def print_clusters(
    clusterer,
    heading,
):

    print()
    print(
        "=" * 70
    )

    print(
        heading
    )

    print(
        "=" * 70
    )

    for cluster in (
        clusterer.get_clusters()
    ):

        print()
        print(
            f"Cluster: "
            f"{cluster.cluster_id}"
        )

        print(
            f"Canonical Title: "
            f"{cluster.canonical_title}"
        )

        print(
            f"Articles: "
            f"{cluster.article_count}"
        )

        print(
            f"Sources: "
            f"{cluster.sources}"
        )

        print(
            f"Status: "
            f"{cluster.status}"
        )

        print(
            f"Confidence: "
            f"{cluster.confidence}"
        )

        for topic in (
            cluster.topics
        ):

            print(
                f"   - {topic.title}"
            )


# ==========================================================
# TEST 1
# ==========================================================

def test_same_event():

    print()
    print(
        "========== TEST 1: SAME EVENT =========="
    )

    clusterer = StoryClusterer()

    a = make_topic(
        "topic-001",
        "ChatGPT brings unlimited text chats to free users",
        "Ars Technica",
        hours_ago=1,
        tags=[
            "OpenAI",
            "ChatGPT",
        ],
    )

    b = make_topic(
        "topic-002",
        "OpenAI is giving ChatGPT free users unlimited text chats",
        "TechCrunch",
        hours_ago=2,
        tags=[
            "OpenAI",
            "ChatGPT",
        ],
    )

    clusterer.add_topic(a)

    clusterer.add_topic(b)

    print_clusters(
        clusterer,
        "AFTER ADDING TWO RELATED ARTICLES",
    )

    clusters = (
        clusterer.get_clusters()
    )

    assert len(clusters) == 1

    assert (
        clusters[0].article_count
        == 2
    )

    print()
    print(
        "PASS: Related articles merged."
    )


# ==========================================================
# TEST 2
# ==========================================================

def test_different_event():

    print()
    print(
        "========== TEST 2: DIFFERENT EVENT =========="
    )

    clusterer = StoryClusterer()

    a = make_topic(
        "topic-003",
        "OpenAI releases a new smart speaker",
        "Example AI News",
        hours_ago=1,
        tags=[
            "OpenAI",
            "Hardware",
        ],
    )

    b = make_topic(
        "topic-004",
        "OpenAI slows Astra model development over security concerns",
        "Example Security News",
        hours_ago=2,
        tags=[
            "OpenAI",
            "Security",
        ],
    )

    clusterer.add_topic(a)

    clusterer.add_topic(b)

    print_clusters(
        clusterer,
        "AFTER ADDING UNRELATED OPENAI ARTICLES",
    )

    clusters = (
        clusterer.get_clusters()
    )

    assert len(clusters) == 2

    print()
    print(
        "PASS: Different events remained separate."
    )


# ==========================================================
# TEST 3
# ==========================================================

def test_three_article_story():

    print()
    print(
        "========== TEST 3: THREE ARTICLE STORY =========="
    )

    clusterer = StoryClusterer()

    articles = [

        make_topic(
            "topic-005",
            "Suno hopes to go legit with watermarks for AI-generated music",
            "Ars Technica",
            hours_ago=1,
            tags=["Suno"],
        ),

        make_topic(
            "topic-006",
            "Amid legal battles, Suno says it will start watermarking songs",
            "TechCrunch",
            hours_ago=2,
            tags=["Suno"],
        ),

        make_topic(
            "topic-007",
            "Suno plans watermarking system for AI-generated songs",
            "The Verge",
            hours_ago=3,
            tags=["Suno"],
        ),
    ]

    for article in articles:

        clusterer.add_topic(
            article
        )

    print_clusters(
        clusterer,
        "THREE RELATED ARTICLES",
    )

    clusters = (
        clusterer.get_clusters()
    )

    assert len(clusters) == 1

    assert (
        clusters[0].article_count
        == 3
    )

    print()
    print(
        "PASS: Three related articles merged into one story."
    )


# ==========================================================
# TEST 4
# ==========================================================

def test_persistent_cycle():

    print()
    print(
        "========== TEST 4: PERSISTENT CYCLES =========="
    )

    clusterer = StoryClusterer()

    # ------------------------------------------------------
    # Cycle 1
    # ------------------------------------------------------

    first_article = make_topic(
        "topic-008",
        "Google AI shake-up creates uncertainty among researchers",
        "Ars Technica",
        hours_ago=5,
        tags=["Google"],
    )

    clusterer.add_topic(
        first_article
    )

    print_clusters(
        clusterer,
        "AFTER CYCLE 1",
    )

    assert (
        len(
            clusterer.get_clusters()
        )
        == 1
    )

    original_cluster_id = (
        clusterer.get_clusters()[0]
        .cluster_id
    )

    # ------------------------------------------------------
    # Cycle 2
    # ------------------------------------------------------

    second_article = make_topic(
        "topic-009",
        "The messy politics behind Google's big AI shakeup",
        "TechCrunch",
        hours_ago=2,
        tags=["Google"],
    )

    clusterer.add_topic(
        second_article
    )

    print_clusters(
        clusterer,
        "AFTER CYCLE 2",
    )

    clusters = (
        clusterer.get_clusters()
    )

    assert len(clusters) == 1

    assert (
        clusters[0].cluster_id
        ==
        original_cluster_id
    )

    assert (
        clusters[0].article_count
        == 2
    )

    print()
    print(
        "PASS: Existing cluster survived across cycles."
    )


# ==========================================================
# TEST 5
# ==========================================================

def test_google_separate_events():

    print()
    print(
        "========== TEST 5: SAME COMPANY, DIFFERENT EVENTS =========="
    )

    clusterer = StoryClusterer()

    maps_article = make_topic(
        "topic-010",
        "Google Maps adds agentic features including food ordering and hotel bookings",
        "Ars Technica",
        hours_ago=1,
        tags=["Google"],
    )

    researchers_article = make_topic(
        "topic-011",
        "Jeff Dean and other top AI researchers are leaving Google to launch their own startup",
        "TechCrunch",
        hours_ago=2,
        tags=["Google"],
    )

    clusterer.add_topic(
        maps_article
    )

    clusterer.add_topic(
        researchers_article
    )

    print_clusters(
        clusterer,
        "GOOGLE ARTICLES",
    )

    clusters = (
        clusterer.get_clusters()
    )

    assert len(clusters) == 2

    print()
    print(
        "PASS: Same-company stories remained separate."
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print()
    print(
        "############################################"
    )

    print(
        "       STORY CLUSTERER TEST SUITE"
    )

    print(
        "############################################"
    )

    test_same_event()

    test_different_event()

    test_three_article_story()

    test_persistent_cycle()

    test_google_separate_events()

    print()
    print(
        "############################################"
    )

    print(
        "ALL CLUSTERER TESTS PASSED"
    )

    print(
        "############################################"
    )


if __name__ == "__main__":
    main()