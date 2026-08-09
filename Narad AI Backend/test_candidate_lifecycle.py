"""Deterministic tests for cross-cycle candidate lifecycle."""

from datetime import datetime, timedelta, timezone

from app.agent.models import EvaluationResult, Topic
from app.clustering.clusterer import StoryClusterer
from app.cycle.manager import CycleManager


def topic(i, title, source):
    return Topic(
        id=i,
        url=f"https://example.com/{i}",
        title=title,
        summary=title,
        content=title + " details",
        source=source,
        published_at=datetime.now(timezone.utc),
    )


def evaluation(t, score, reliability, publish=False):
    return EvaluationResult(
        topic_id=t.id,
        topic_title=t.title,
        interest_score=80,
        technical_score=80,
        reliability_score=reliability,
        freshness_score=90,
        memory_score=90,
        editorial_score=90,
        overall_score=score,
        publish=publish,
        reason="deterministic test",
    )


def main():
    manager = CycleManager(
        posting_deadline=datetime.now(timezone.utc) + timedelta(hours=1)
    )

    a = topic("a", "OpenAI announces a new model", "Source A")
    b = topic("b", "OpenAI announces its new model", "Source B")

    clusterer = StoryClusterer()

    # Cycle 1: one source, not ready.
    manager.start_cycle()
    c1 = clusterer.add_topic(a)
    held = manager.upsert_candidate(
        c1,
        evaluation(a, 70, 68, False),
        source_count=1,
    )

    assert held.status == "ACTIVE"

    # Cycle 2: corroborating source joins the existing story.
    manager.start_cycle()
    c2 = clusterer.add_topic(b)

    assert c2.cluster_id == c1.cluster_id
    assert c2.article_count == 2

    ready = manager.upsert_candidate(
        c2,
        evaluation(b, 84, 82, True),
        source_count=2,
    )

    assert ready.status == "READY"
    assert ready.source_count == 2

    # Publication locks the story.
    manager.mark_published(
        c2.cluster_id,
        b.id,
    )

    assert manager.is_cluster_published(
        c2.cluster_id
    )

    # A later cycle must not revive it.
    manager.start_cycle()
    still_published = manager.upsert_candidate(
        c2,
        evaluation(b, 90, 90, True),
        source_count=2,
    )

    assert still_published.status == "PUBLISHED"

    print("PASS: Story remained ACTIVE after first HOLD.")
    print("PASS: Second source merged into persistent cluster.")
    print("PASS: Story became READY after corroboration.")
    print("PASS: Published story cannot be revived.")
    print("PASS: Cross-cycle candidate lifecycle works.")


if __name__ == "__main__":
    main()
