"""Cycle and publication-candidate lifecycle manager.

The manager keeps stories alive across cycles. Publication candidates are
story-level objects, not one-shot article objects.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.agent.models import Topic, PublicationCandidate
from app.clustering.models import StoryCluster
from app.cycle.state import CycleState


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class CycleManager:
    def __init__(
        self,
        posting_deadline: Optional[datetime] = None,
        candidate_ttl_hours: float = 6.0,
    ):
        self.posting_deadline = _as_utc(posting_deadline)
        self.candidate_ttl_hours = max(
            0.25,
            float(candidate_ttl_hours),
        )

        self.current_cycle: Optional[CycleState] = None
        self.story_clusters: Dict[str, StoryCluster] = {}
        self.history: List[CycleState] = []
        self.next_cycle_id = 1
        self.candidates: Dict[str, PublicationCandidate] = {}

    def start_cycle(self) -> CycleState:
        now = _utc_now()
        previous = self.current_cycle

        if self.posting_deadline is None:
            self.posting_deadline = (
                now
                + timedelta(
                    hours=self.candidate_ttl_hours
                )
            )

        state = CycleState(
            cycle_id=self.next_cycle_id,
            started_at=now,
            last_cycle_at=(
                previous.started_at
                if previous
                else None
            ),
            posting_deadline=self.posting_deadline,
        )

        state.story_clusters = self.story_clusters.copy()
        self.current_cycle = state
        self.next_cycle_id += 1

        # Expiration is checked at the start of every cycle so
        # candidates cannot survive indefinitely.
        self.expire_candidates(now)

        return state

    def complete_cycle(self) -> CycleState:
        self._require_active_cycle()

        self.story_clusters = (
            self.current_cycle.story_clusters.copy()
        )

        self.history.append(
            self.current_cycle
        )

        return self.current_cycle

    def record_discovered(self, topics: List[Topic]):
        self._require_active_cycle()
        self.current_cycle.update_discovered(topics)

    def record_verified(self, topics: List[Topic]):
        self._require_active_cycle()
        self.current_cycle.update_verified(topics)

    def record_evaluated(self, topics: List[Topic]):
        self._require_active_cycle()
        self.current_cycle.update_evaluated(topics)

    def record_clusters(self, clusters: List[StoryCluster]):
        self._require_active_cycle()

        self.current_cycle.update_clusters(
            clusters
        )

        self.story_clusters = {
            c.cluster_id: c
            for c in clusters
        }

    def record_rankings(self, topics):
        self._require_active_cycle()
        self.current_cycle.update_rankings(topics)

    def mark_published(
        self,
        cluster_id=None,
        topic_id=None,
    ):
        self._require_active_cycle()

        self.current_cycle.mark_published(
            cluster_id,
            topic_id,
        )

        if cluster_id in self.candidates:
            self.candidates[
                cluster_id
            ].status = "PUBLISHED"

    def upsert_candidate(
        self,
        cluster: StoryCluster,
        evaluation,
        source_count: int | None = None,
        corroboration_score: float = 0.0,
        blocking_reasons: Optional[List[str]] = None,
    ):
        now = _utc_now()

        existing = self.candidates.get(
            cluster.cluster_id
        )

        # A published story is permanently ineligible for
        # another publication during this runtime.
        if existing and existing.status == "PUBLISHED":
            return existing

        # Never create/revive a candidate after the posting
        # deadline has passed.
        if (
            self.posting_deadline is not None
            and now >= self.posting_deadline
        ):
            if existing:
                existing.status = "EXPIRED"
                return existing

            candidate = PublicationCandidate(
                cluster_id=cluster.cluster_id,
                topic_id=evaluation.topic_id,
                title=evaluation.topic_title,
                score=evaluation.overall_score,
                reliability_score=evaluation.reliability_score,
                first_seen_at=now,
                last_seen_at=now,
                last_evaluated_at=now,
                status="EXPIRED",
                attempts=1,
                source_count=(
                    source_count
                    or len(cluster.sources)
                    or 1
                ),
                reason=evaluation.reason,
                independent_source_count=source_count or len(cluster.sources) or 1,
                corroboration_score=corroboration_score,
                blocking_reasons=list(blocking_reasons or []),
                publication_path=getattr(evaluation, "publication_path", "standard"),
            )

            self.candidates[
                cluster.cluster_id
            ] = candidate

            return candidate

        status = (
            "READY"
            if evaluation.publish
            else "ACTIVE"
        )

        if existing:
            existing.topic_id = evaluation.topic_id
            existing.title = evaluation.topic_title
            existing.score = evaluation.overall_score
            existing.reliability_score = (
                evaluation.reliability_score
            )
            existing.last_seen_at = now
            existing.last_evaluated_at = now
            existing.attempts += 1
            existing.source_count = (
                source_count
                or len(cluster.sources)
                or 1
            )
            existing.reason = evaluation.reason
            existing.independent_source_count = (
                source_count or len(cluster.sources) or 1
            )
            existing.corroboration_score = corroboration_score
            existing.blocking_reasons = list(blocking_reasons or [])
            existing.publication_path = getattr(evaluation, "publication_path", "standard")
            existing.status = status
            return existing

        candidate = PublicationCandidate(
            cluster_id=cluster.cluster_id,
            topic_id=evaluation.topic_id,
            title=evaluation.topic_title,
            score=evaluation.overall_score,
            reliability_score=evaluation.reliability_score,
            first_seen_at=now,
            last_seen_at=now,
            last_evaluated_at=now,
            status=status,
            attempts=1,
            source_count=(
                source_count
                or len(cluster.sources)
                or 1
            ),
            reason=evaluation.reason,
            independent_source_count=source_count or len(cluster.sources) or 1,
            corroboration_score=corroboration_score,
            blocking_reasons=list(blocking_reasons or []),
            publication_path=getattr(evaluation, "publication_path", "standard"),
        )

        self.candidates[
            cluster.cluster_id
        ] = candidate

        return candidate

    def get_candidate(
        self,
        cluster_id: str,
    ):
        return self.candidates.get(
            cluster_id
        )

    def get_candidates(
        self,
        active_only: bool = False,
    ):
        values = list(
            self.candidates.values()
        )

        if active_only:
            values = [
                c
                for c in values
                if c.status in {
                    "ACTIVE",
                    "READY",
                }
            ]

        return sorted(
            values,
            key=lambda c: c.score,
            reverse=True,
        )

    def is_cluster_published(
        self,
        cluster_id: str,
    ) -> bool:
        candidate = self.candidates.get(
            cluster_id
        )

        return bool(
            candidate
            and candidate.status == "PUBLISHED"
        )

    def expire_candidates(
        self,
        now: Optional[datetime] = None,
    ):
        current = _as_utc(now) or _utc_now()
        deadline = _as_utc(
            self.posting_deadline
        )

        if deadline and current >= deadline:
            for candidate in self.candidates.values():
                if candidate.status in {
                    "ACTIVE",
                    "READY",
                }:
                    candidate.status = "EXPIRED"

    def get_current_state(self):
        return self.current_cycle

    def get_previous_cycle(self):
        return (
            self.history[-1]
            if self.history
            else None
        )

    def get_history(self):
        return list(self.history)

    def get_story_clusters(self):
        return list(
            self.story_clusters.values()
        )

    def is_posting_deadline_reached(
        self,
        now: Optional[datetime] = None,
    ) -> bool:
        deadline = _as_utc(
            self.posting_deadline
        )

        if deadline is None:
            return False

        current = (
            _as_utc(now)
            or _utc_now()
        )

        return current >= deadline

    def reset_after_publication(self):
        # The published candidate remains PUBLISHED so the story
        # cannot be republished. Other unresolved candidates are
        # dropped because the publication window has been consumed.
        for candidate in self.candidates.values():
            if candidate.status in {
                "ACTIVE",
                "READY",
            }:
                candidate.status = "DROPPED"

        # A publication consumes the current posting window. Start a fresh
        # window so the autonomous scheduler can publish again later instead
        # of remaining permanently past the old deadline.
        self.posting_deadline = (
            _utc_now()
            + timedelta(hours=self.candidate_ttl_hours)
        )

        if self.current_cycle:
            self.current_cycle.story_clusters = (
                self.story_clusters.copy()
            )
            self.current_cycle.posting_deadline = self.posting_deadline

    def summary(self) -> dict:
        current = self.current_cycle

        return {
            "current_cycle": (
                current.cycle_id
                if current
                else None
            ),
            "historical_cycles": len(
                self.history
            ),
            "persistent_clusters": len(
                self.story_clusters
            ),
            "posting_deadline": (
                self.posting_deadline
            ),
            "published": (
                current.published
                if current
                else False
            ),
            "active_candidates": len(
                self.get_candidates(
                    active_only=True
                )
            ),
            "candidates": len(
                self.candidates
            ),
        }

    def _require_active_cycle(self):
        if self.current_cycle is None:
            raise RuntimeError(
                "No active cycle. "
                "Call start_cycle() first."
            )
