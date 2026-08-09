from datetime import datetime, timedelta, timezone

from app.agent.models import EvaluationResult, Topic
from app.cycle.manager import CycleManager
from app.publishing.policy import PublicationPolicy


def evaluation(score, reliability, editorial=80):
    return EvaluationResult(
        topic_id="topic",
        topic_title="Test story",
        interest_score=90,
        technical_score=20,
        reliability_score=reliability,
        freshness_score=90,
        memory_score=100,
        editorial_score=editorial,
        overall_score=score,
        publish=False,
        reason="test",
    )


def test_deadline_fallback_accepts_best_corroborated_candidate():
    policy = PublicationPolicy()

    decision = policy.decide_deadline_fallback(
        evaluation(67.22, 79.0),
        source_count=2,
        has_primary_source=False,
        corroboration=0.65,
    )

    assert decision.ready
    assert decision.path == "deadline_fallback_corroborated"


def test_deadline_fallback_rejects_weak_evidence():
    policy = PublicationPolicy()

    decision = policy.decide_deadline_fallback(
        evaluation(95.0, 50.0),
        source_count=1,
        has_primary_source=False,
        corroboration=0.0,
    )

    assert not decision.ready


def test_corroboration_boundary_is_not_rejected_by_float_precision():
    policy = PublicationPolicy()

    decision = policy.decide(
        evaluation(68.0, 65.0),
        source_count=2,
        has_primary_source=False,
        corroboration=0.65,
    )

    assert decision.ready
    assert decision.path == "corroborated"


def test_deadline_fallback_preserves_primary_source_overall_floor():
    policy = PublicationPolicy()

    decision = policy.decide_deadline_fallback(
        evaluation(69.9, 80.0, editorial=80),
        source_count=1,
        has_primary_source=True,
        corroboration=0.0,
    )

    assert not decision.ready

    decision = policy.decide_deadline_fallback(
        evaluation(70.0, 75.0, editorial=70),
        source_count=1,
        has_primary_source=True,
        corroboration=0.0,
    )

    assert decision.ready
    assert decision.path == "deadline_fallback_primary_source"


def test_deadline_fallback_preserves_trusted_single_source_overall_floor():
    policy = PublicationPolicy()

    decision = policy.decide_deadline_fallback(
        evaluation(77.9, 82.0, editorial=75),
        source_count=1,
        has_primary_source=False,
        corroboration=0.0,
        best_source_score=95,
    )

    assert not decision.ready

    decision = policy.decide_deadline_fallback(
        evaluation(78.0, 82.0, editorial=75),
        source_count=1,
        has_primary_source=False,
        corroboration=0.0,
        best_source_score=95,
    )

    assert decision.ready
    assert decision.path == "deadline_fallback_trusted_single_source"


def test_publication_opens_a_new_posting_window():
    now = datetime.now(timezone.utc)
    manager = CycleManager(
        posting_deadline=now + timedelta(hours=1),
        candidate_ttl_hours=6,
    )

    manager.start_cycle()
    old_deadline = manager.posting_deadline

    manager.reset_after_publication()

    assert manager.posting_deadline > old_deadline
    assert manager.posting_deadline > now + timedelta(hours=5)
    assert manager.current_cycle.posting_deadline == manager.posting_deadline
