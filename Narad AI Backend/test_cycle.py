from datetime import datetime, timedelta

from app.agent.models import Topic

from app.clustering.models import StoryCluster

from app.cycle.manager import CycleManager


# ==========================================================
# TOPIC FACTORY
# ==========================================================

def make_topic(
    topic_id,
    title,
    source,
):

    now = datetime.now()

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
            f"Test article content."
        ),
        source=source,
        author="Test Author",
        category="Artificial Intelligence",
        language="en",
        tags=["AI"],
        image_url=None,
        published_at=now,
        discovered_at=now,
    )


# ==========================================================
# TEST 1
# ==========================================================

def test_first_cycle():

    print()
    print(
        "========== TEST 1: FIRST CYCLE =========="
    )

    manager = CycleManager()

    state = manager.start_cycle()

    assert state.cycle_id == 1

    assert (
        state.last_cycle_at
        is None
    )

    print(
        f"Cycle ID: {state.cycle_id}"
    )

    print(
        "PASS: First cycle created correctly."
    )


# ==========================================================
# TEST 2
# ==========================================================

def test_record_pipeline_state():

    print()
    print(
        "========== TEST 2: PIPELINE STATE =========="
    )

    manager = CycleManager()

    manager.start_cycle()

    topics = [

        make_topic(
            "topic-001",
            "OpenAI releases new AI model",
            "Example AI News",
        ),

        make_topic(
            "topic-002",
            "NVIDIA announces new GPU",
            "Example Tech News",
        ),
    ]

    manager.record_discovered(
        topics
    )

    manager.record_verified(
        topics
    )

    manager.record_evaluated(
        topics
    )

    state = (
        manager.get_current_state()
    )

    assert state is not None

    assert (
        len(
            state.discovered_topics
        )
        == 2
    )

    assert (
        len(
            state.verified_topics
        )
        == 2
    )

    assert (
        len(
            state.evaluated_topics
        )
        == 2
    )

    print(
        "Discovered:",
        len(
            state.discovered_topics
        ),
    )

    print(
        "Verified:",
        len(
            state.verified_topics
        ),
    )

    print(
        "Evaluated:",
        len(
            state.evaluated_topics
        ),
    )

    print(
        "PASS: Pipeline state recorded correctly."
    )


# ==========================================================
# TEST 3
# ==========================================================

def test_cycle_persistence():

    print()
    print(
        "========== TEST 3: CYCLE PERSISTENCE =========="
    )

    manager = CycleManager()

    # ------------------------------------------------------
    # Cycle 1
    # ------------------------------------------------------

    cycle_1 = (
        manager.start_cycle()
    )

    topic = make_topic(
        "topic-003",
        "OpenAI launches a new AI system",
        "Example AI News",
    )

    manager.record_discovered(
        [topic]
    )

    manager.complete_cycle()

    # ------------------------------------------------------
    # Cycle 2
    # ------------------------------------------------------

    cycle_2 = (
        manager.start_cycle()
    )

    assert (
        cycle_2.cycle_id
        == 2
    )

    assert (
        cycle_2.last_cycle_at
        ==
        cycle_1.started_at
    )

    print(
        "Cycle 1:",
        cycle_1.cycle_id,
    )

    print(
        "Cycle 2:",
        cycle_2.cycle_id,
    )

    print(
        "Previous cycle timestamp:",
        cycle_2.last_cycle_at,
    )

    print(
        "PASS: Cycle state persisted correctly."
    )


# ==========================================================
# TEST 4
# ==========================================================

def test_cluster_persistence():

    print()
    print(
        "========== TEST 4: CLUSTER PERSISTENCE =========="
    )

    manager = CycleManager()

    manager.start_cycle()

    cluster = StoryCluster(
        cluster_id="cluster-0001"
    )

    topic = make_topic(
        "topic-004",
        "Google announces new AI features",
        "Example AI News",
    )

    cluster.add_topic(
        topic
    )

    manager.record_clusters(
        [cluster]
    )

    manager.complete_cycle()

    # ------------------------------------------------------
    # Start second cycle
    # ------------------------------------------------------

    second_cycle = (
        manager.start_cycle()
    )

    clusters = (
        manager.get_story_clusters()
    )

    assert len(clusters) == 1

    assert (
        clusters[0].cluster_id
        == "cluster-0001"
    )

    assert (
        "cluster-0001"
        in
        second_cycle.story_clusters
    )

    print(
        "Persistent clusters:",
        len(clusters),
    )

    print(
        "Cluster ID:",
        clusters[0].cluster_id,
    )

    print(
        "PASS: Story cluster survived cycle transition."
    )


# ==========================================================
# TEST 5
# ==========================================================

def test_rankings():

    print()
    print(
        "========== TEST 5: RANKING STATE =========="
    )

    manager = CycleManager()

    manager.start_cycle()

    topics = [

        make_topic(
            "topic-005",
            "Major cybersecurity vulnerability discovered",
            "Security News",
        ),

        make_topic(
            "topic-006",
            "New open source AI model released",
            "AI News",
        ),
    ]

    manager.record_rankings(
        topics
    )

    state = (
        manager.get_current_state()
    )

    assert (
        len(
            state.current_rankings
        )
        == 2
    )

    assert (
        state.current_rankings[0].id
        ==
        "topic-005"
    )

    print(
        "Ranked articles:",
        len(
            state.current_rankings
        ),
    )

    print(
        "Top article:",
        state.current_rankings[0].title,
    )

    print(
        "PASS: Ranking state recorded correctly."
    )


# ==========================================================
# TEST 6
# ==========================================================

def test_publication_state():

    print()
    print(
        "========== TEST 6: PUBLICATION STATE =========="
    )

    manager = CycleManager()

    manager.start_cycle()

    manager.mark_published(
        cluster_id="cluster-0001",
        topic_id="topic-001",
    )

    state = (
        manager.get_current_state()
    )

    assert state.published is True

    assert (
        state.published_cluster_id
        ==
        "cluster-0001"
    )

    assert (
        state.published_topic_id
        ==
        "topic-001"
    )

    print(
        "Published:",
        state.published,
    )

    print(
        "Published cluster:",
        state.published_cluster_id,
    )

    print(
        "Published topic:",
        state.published_topic_id,
    )

    print(
        "PASS: Publication state recorded correctly."
    )


# ==========================================================
# TEST 7
# ==========================================================

def test_summary():

    print()
    print(
        "========== TEST 7: SUMMARY =========="
    )

    manager = CycleManager()

    manager.start_cycle()

    topic = make_topic(
        "topic-007",
        "New AI security research published",
        "Security News",
    )

    manager.record_discovered(
        [topic]
    )

    manager.record_verified(
        [topic]
    )

    manager.record_evaluated(
        [topic]
    )

    summary = (
        manager.summary()
    )

    print(
        "Summary:"
    )

    for key, value in (
        summary.items()
    ):

        print(
            f"  {key}: {value}"
        )

    assert (
        summary["current_cycle"]
        == 1
    )

    assert (
        summary["historical_cycles"]
        == 0
    )

    print(
        "PASS: Summary generated correctly."
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
        "          CYCLE MANAGER TEST SUITE"
    )

    print(
        "############################################"
    )

    test_first_cycle()

    test_record_pipeline_state()

    test_cycle_persistence()

    test_cluster_persistence()

    test_rankings()

    test_publication_state()

    test_summary()

    print()
    print(
        "############################################"
    )

    print(
        "       ALL CYCLE TESTS PASSED"
    )

    print(
        "############################################"
    )


if __name__ == "__main__":
    main()