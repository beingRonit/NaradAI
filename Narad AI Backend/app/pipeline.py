"""Complete autonomous editorial processing cycle.

The pipeline is deliberately story-centric:

    collect -> enrich new evidence -> verify -> cluster
    -> re-verify/re-evaluate active stories -> rank -> publish

A story that is not ready in one cycle is retained and reconsidered when
new evidence arrives in a later cycle.
"""
from __future__ import annotations

import os
import threading
from datetime import datetime, timezone 

from app.discovery.collector import NewsCollector
from app.enrichment.article_fetcher import ArticleFetcher
from app.verification.verifier import VerificationEngine
from app.agent.evaluator import EditorialEvaluator
from app.ranking.ranker import TopicRanker
from app.clustering.clusterer import StoryClusterer
from app.cycle.manager import CycleManager
from app.publishing.policy import PublicationPolicy


class EditorialPipeline:
    def __init__(
        self,
        persona_engine,
        posting_deadline=None,
        publisher=None,
        auto_publish=False,
    ):
        self.persona_engine = persona_engine
        self.collector = NewsCollector()
        self.fetcher = ArticleFetcher()
        self.verifier = VerificationEngine()
        self.evaluator = EditorialEvaluator(persona_engine)
        self.ranker = TopicRanker()
        self.clusterer = StoryClusterer()
        self.cycle_manager = CycleManager(posting_deadline=posting_deadline)
        self.publication_policy = PublicationPolicy()
        self.publisher = publisher
        self.auto_publish = auto_publish
        self.last_publication = None
        self._run_lock = threading.Lock()
        # Topic objects are reused across cycles by stable article ID/URL.
        # This preserves enrichment cache and retry state between RSS runs.
        self.topic_registry = {}

    # ==========================================================
    # RUN ONE EDITORIAL CYCLE
    # ==========================================================

    def run(self, top_count: int = 5, enrich: bool = False):
        """Run one editorial cycle; serialize scheduler/manual invocations."""
        with self._run_lock:
            return self._run(top_count=top_count, enrich=enrich)

    def _run(self, top_count: int = 5, enrich: bool = False):
        cycle_state = self.cycle_manager.start_cycle()

        print(
            f"\n==========================================\n"
            f"EDITORIAL CYCLE {cycle_state.cycle_id}\n"
            f"=========================================="
        )

        # ------------------------------------------------------
        # 1. DISCOVERY
        # ------------------------------------------------------

        print("\n========== RSS COLLECTION ==========")
        discovered_topics = self.collector.collect()
        topics = [self._reuse_topic_state(topic) for topic in discovered_topics]
        print(f"Articles discovered: {len(topics)}")
        self.cycle_manager.record_discovered(topics)

        # ------------------------------------------------------
        # 2. ENRICH ONLY CURRENTLY DISCOVERED ARTICLES
        # ------------------------------------------------------

        if enrich and topics:
            print("\n========== ARTICLE ENRICHMENT ==========")

            max_enrich = max(
                1,
                int(os.getenv("AUTONOMOUSAI_MAX_ENRICH", "15")),
            )

            # Statistics are cycle-local. Previously successful topics
            # are skipped by ArticleFetcher itself.
            self.fetcher.reset_cycle_stats()

            self.fetcher.enrich_many(
                topics[:max_enrich]
            )

            print(
                f"Enrichment: {self.fetcher.get_status()}"
            )

        # ------------------------------------------------------
        # 3. VERIFY NEW EVIDENCE
        # ------------------------------------------------------

        print("\n========== VERIFICATION ==========")

        verified_topics = []
        verification_results = []

        for topic in topics:
            result = self.verifier.verify(topic)

            verification_results.append(result)

            if result.verified:
                verified_topics.append(topic)

        print(
            f"Verified: {len(verified_topics)}"
        )

        self.cycle_manager.record_verified(
            verified_topics
        )

        # ------------------------------------------------------
        # 4. CLUSTER ALL DISCOVERED ARTICLES BEFORE FINAL VERIFICATION
        # ------------------------------------------------------
        # Event similarity answers "same event?". Verification answers
        # "safe/reliable enough?". Keeping these stages separate allows
        # a weak article to still contribute to event identification
        # without becoming publishable evidence.

        print("\n========== STORY CLUSTERING ==========")

        self.clusterer.cluster_topics(
            topics
        )

        clusters = (
            self.clusterer.get_active_clusters()
        )

        self.cycle_manager.record_clusters(
            clusters
        )

        for cluster in clusters:
            print(
                f"  {cluster.cluster_id} → "
                f"{cluster.article_count} articles"
            )

        print(
            f"Story clusters: {len(clusters)}"
        )

        # ------------------------------------------------------
        # 4B. PRIORITIZE ENRICHMENT FOR MULTI-SOURCE STORIES
        # ------------------------------------------------------
        # The initial enrichment pass is deliberately budgeted because
        # RSS feeds can return many articles. Once clustering identifies
        # a story covered by multiple independent sources, those sources
        # become high-value evidence and must get a chance to reach the
        # verifier with full article content. Otherwise a failed/unfetched
        # article can disappear from corroboration even though clustering
        # correctly identified it as the same event.
        self._enrich_multi_source_evidence(clusters)

        # ------------------------------------------------------
        # 5. RE-VERIFY AND RE-EVALUATE ACTIVE STORIES
        #
        # This is the important cross-cycle behavior.
        #
        # Every active story is reconstructed from all of its
        # known evidence, not merely from articles discovered
        # in the current cycle.
        # ------------------------------------------------------

        print(
            "\n========== ACTIVE STORY RE-EVALUATION =========="
        )

        story_evaluations = []
        evaluated_representatives = []
        story_topic_map = {}
        story_publication_context = {}

        for cluster in clusters:

            if not cluster.topics:
                continue

            # Once a story has been published, keep its cluster
            # for historical/duplicate detection but remove it from
            # the active editorial decision set.
            if self.cycle_manager.is_cluster_published(
                cluster.cluster_id
            ):
                continue

            # Re-verify all known evidence in the story.
            story_verified_topics = []

            for topic in cluster.topics:
                result = self.verifier.verify(topic)

                if result.verified:
                    story_verified_topics.append(topic)

            if not story_verified_topics:
                continue

            # Count distinct reporting sources, not article copies.
            source_identities = {
                self.verifier.normalize_source(topic.source)
                for topic in story_verified_topics
                if topic.source
            }
            source_count = len(source_identities)
            has_primary_source = any(
                self.verifier.is_primary_source(topic)
                for topic in story_verified_topics
            )
            best_source_score = max(
                (self.verifier.source_score(topic.source) for topic in story_verified_topics),
                default=0.0,
            )

            corroboration = self._corroboration_score(source_count)

            # Diminishing-return corroboration. Two independent sources
            # matter a lot; additional sources add progressively less.
            reliability_boost = self._corroboration_boost(corroboration)
            for topic in story_verified_topics:
                topic.reliability_score = min(
                    100.0,
                    (topic.reliability_score or 0.0) + reliability_boost,
                )

            # Pick the best evidence article as the representative
            # for editorial scoring.
            representative = self._select_representative(
                story_verified_topics
            )

            evaluation = (
                self.evaluator.evaluate(
                    representative
                )
            )

            representative.evaluation_score = (
                evaluation.overall_score
            )

            # Keep the complete story attached to the result so
            # publication can cite every corroborating source.
            story_topic_map[
                evaluation.topic_id
            ] = cluster
            story_publication_context[
                evaluation.topic_id
            ] = {
                "source_count": source_count,
                "has_primary_source": has_primary_source,
                "corroboration": corroboration,
                "best_source_score": best_source_score,
            }

            story_evaluations.append(
                evaluation
            )

            evaluated_representatives.append(
                representative
            )

            final_hour = self._is_final_hour()
            decision = self.publication_policy.decide(
                evaluation,
                source_count=source_count,
                has_primary_source=has_primary_source,
                corroboration=corroboration,
                final_hour=final_hour,
                best_source_score=best_source_score,
            )
            evaluation.publish = decision.ready
            evaluation.publication_path = decision.path
            evaluation.publication_blockers = list(decision.blockers)

            self.cycle_manager.upsert_candidate(
                cluster,
                evaluation,
                source_count=source_count,
                corroboration_score=corroboration,
                blocking_reasons=decision.blockers,
            )

            print(
                f"  {cluster.cluster_id} | "
                f"{'READY' if decision.ready else 'HOLD'} | "
                f"Score={evaluation.overall_score:.1f} | "
                f"Reliability={evaluation.reliability_score:.1f} | "
                f"Sources={source_count} | "
                f"Primary={'YES' if has_primary_source else 'NO'} | "
                f"Path={decision.path}"
            )
            print(
                "    Breakdown: "
                + ", ".join(
                    f"{k}={v:.1f}"
                    for k, v in evaluation.score_breakdown.items()
                )
            )
            if decision.blockers:
                print("    Blockers: " + "; ".join(decision.blockers))

        print(
            f"Evaluated stories: "
            f"{len(story_evaluations)}"
        )

        print("\n========== PUBLICATION CANDIDATES ==========")
        for candidate in self.cycle_manager.get_candidates(active_only=True)[:10]:
            decision = "READY" if candidate.status == "READY" else "HOLD"
            print(
                f"  {candidate.cluster_id} | {decision} | "
                f"Score={candidate.score:.1f} | "
                f"Reliability={candidate.reliability_score:.1f} | "
                f"Sources={candidate.independent_source_count} | "
                f"Corroboration={candidate.corroboration_score:.2f} | "
                f"Path={candidate.publication_path}"
            )
            if candidate.blocking_reasons:
                print("    Blockers: " + "; ".join(candidate.blocking_reasons))

        self.cycle_manager.record_evaluated(
            evaluated_representatives
        )

        # ------------------------------------------------------
        # 6. RANK STORIES
        # ------------------------------------------------------

        print("\n========== RANKING ==========")

        ranked_results = self.ranker.rank(
            story_evaluations
        )

        print(
            f"Ranked: {len(ranked_results)}"
        )

        self.cycle_manager.record_rankings(
            evaluated_representatives
        )

        top_results = ranked_results[
            : max(0, top_count)
        ]

        # ------------------------------------------------------
        # 7. EXPIRATION
        # ------------------------------------------------------

        self.cycle_manager.expire_candidates()

        # ------------------------------------------------------
        # 8. PUBLICATION DECISION
        # Normal policy-ready stories publish immediately. If the posting
        # deadline has arrived and none is ready, the highest-ranked eligible
        # verified story is selected by PublicationPolicy's deadline fallback.
        # ------------------------------------------------------

        published = None

        publishable = (
            self.ranker.top_publishable(
                ranked_results,
                count=1,
            )
        )

        deadline = (
            self.cycle_manager
            .is_posting_deadline_reached()
        )

        selected = publishable[0] if publishable else None

        # At the posting deadline, if no story passed the normal publication
        # policy, choose the highest-ranked story that still satisfies an
        # evidence/editorial eligibility path. This is a fallback selection,
        # not a new overall-score threshold. Verification is never bypassed.
        if selected is None and deadline:
            for candidate in ranked_results:
                context = story_publication_context.get(candidate.topic_id)
                if context is None:
                    continue

                fallback_decision = self.publication_policy.decide_deadline_fallback(
                    candidate,
                    source_count=context["source_count"],
                    has_primary_source=context["has_primary_source"],
                    corroboration=context["corroboration"],
                    best_source_score=context["best_source_score"],
                )
                if fallback_decision.ready:
                    candidate.publish = True
                    candidate.publication_path = fallback_decision.path
                    candidate.publication_blockers = []
                    selected = candidate
                    print(
                        f"Deadline fallback selected: {candidate.topic_title} "
                        f"(score={candidate.overall_score:.1f}, path={fallback_decision.path})"
                    )
                    break

        if (
            self.auto_publish
            and self.publisher
            and selected is not None
        ):

            cluster = story_topic_map.get(
                selected.topic_id
            )

            if cluster is not None:
                topic = self._topic_for_evaluation(
                    cluster,
                    selected.topic_id,
                )

                if topic is not None:
                    persona = (
                        self.persona_engine
                        .get_persona()
                    )

                    sources = (
                        cluster.sources
                        or [topic.url]
                    )

                    published = (
                        self.publisher.publish(
                            topic,
                            selected,
                            cluster.cluster_id,
                            sources,
                            persona=persona,
                        )
                    )

                    self.publisher.remember_publication(
                        persona,
                        topic,
                        selected.reason,
                        technologies=topic.tags,
                    )

                    self.last_publication = (
                        published
                    )

                    self.cycle_manager.mark_published(
                        cluster.cluster_id,
                        topic.id,
                    )

                    # Do not let unresolved stories from the old
                    # publication window immediately publish again.
                    self.cycle_manager.reset_after_publication()

        # ------------------------------------------------------
        # 9. COMPLETE CYCLE
        # ------------------------------------------------------

        completed_state = (
            self.cycle_manager.complete_cycle()
        )

        print(
            "\n========== CYCLE SUMMARY =========="
        )

        print(
            f"Cycle: {completed_state.cycle_id}"
        )

        print(
            f"Discovered: {len(topics)}"
        )

        print(
            f"Verified: {len(verified_topics)}"
        )

        print(
            f"Evaluated stories: "
            f"{len(story_evaluations)}"
        )

        print(
            f"Clusters: {len(clusters)}"
        )

        print(
            f"Ranked stories: "
            f"{len(ranked_results)}"
        )

        print(
            f"Top: {len(top_results)}"
        )

        if published:
            print(
                f"Published: {published.id}"
            )

        return {
            "cycle_id": completed_state.cycle_id,
            "cycle_state": completed_state,
            "topics_discovered": topics,
            "topics_verified": verified_topics,
            "verification_results": verification_results,
            "evaluated_topics": evaluated_representatives,
            "evaluation_results": story_evaluations,
            "story_clusters": clusters,
            "ranked_results": ranked_results,
            "top_results": top_results,
            "published_post": published,
            "summary": {
                "cycle_id": completed_state.cycle_id,
                "discovered": len(topics),
                "verified": len(verified_topics),
                "evaluated": len(story_evaluations),
                "clusters": len(clusters),
                "ranked": len(ranked_results),
                "top": len(top_results),
                "published": bool(published),
            },
        }

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _is_final_hour(self) -> bool:
        deadline = self.cycle_manager.posting_deadline
        if deadline is None:
            return False
        now = datetime.now(timezone.utc)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        remaining = (deadline - now).total_seconds()
        return 0 < remaining <= 3600


    def _enrich_multi_source_evidence(self, clusters):
        """Give multi-source stories a bounded evidence-enrichment pass.

        The first discovery enrichment pass is intentionally limited. That
        limit must not permanently prevent a corroborating source from being
        verified later in the same cycle. Only clusters with at least two
        distinct source identities are considered, and a small global budget
        keeps the cycle bounded. Cached successful enrichment is skipped by
        ArticleFetcher automatically.
        """
        candidates = []
        seen = set()

        for cluster in clusters:
            if len(cluster.sources) < 2:
                continue
            for topic in cluster.topics:
                if topic.id in seen:
                    continue
                seen.add(topic.id)
                if getattr(topic, "enrichment_status", None) is not None:
                    status = getattr(topic.enrichment_status, "value", topic.enrichment_status)
                    if str(status).upper() == "SUCCESS":
                        continue
                candidates.append(topic)

        budget = max(0, int(os.getenv("AUTONOMOUSAI_CORROBORATION_ENRICH", "12")))
        if not candidates or budget == 0:
            return

        for topic in candidates[:budget]:
            try:
                self.fetcher.enrich(topic, force=True)
            except Exception as exc:
                # Enrichment failure is evidence failure, not a cycle failure.
                topic.enrichment_error = str(exc)


    @staticmethod
    def _corroboration_score(source_count: int) -> float:
        if source_count <= 1:
            return 0.0
        if source_count == 2:
            return 0.65
        if source_count == 3:
            return 0.82
        if source_count == 4:
            return 0.91
        return 0.95

    @staticmethod
    def _corroboration_boost(score: float) -> float:
        return round(score * 15.0, 2)

    @staticmethod
    def _publication_blockers(evaluation, source_count: int) -> list[str]:
        blockers = []
        if evaluation.overall_score < 68:
            blockers.append(f"overall score {evaluation.overall_score:.1f} < 68")
        if evaluation.reliability_score < 65:
            blockers.append(f"reliability {evaluation.reliability_score:.1f} < 65")
        if source_count < 2:
            blockers.append("fewer than 2 independent sources")
        return blockers

    def _reuse_topic_state(self, incoming):
        """Merge a new RSS record into the persistent in-process topic object."""
        existing = self.topic_registry.get(incoming.id)
        if existing is None and incoming.url:
            for candidate in self.topic_registry.values():
                if candidate.url and candidate.url == incoming.url:
                    existing = candidate
                    break

        if existing is None:
            self.topic_registry[incoming.id] = incoming
            return incoming

        # Refresh feed metadata but preserve enrichment, retry, and
        # editorial state accumulated in previous cycles.
        existing.url = incoming.url or existing.url
        existing.title = incoming.title or existing.title
        existing.summary = incoming.summary or existing.summary
        existing.source = incoming.source or existing.source
        existing.author = incoming.author or existing.author
        existing.category = incoming.category or existing.category
        existing.tags = incoming.tags or existing.tags
        existing.image_url = incoming.image_url or existing.image_url
        existing.published_at = incoming.published_at or existing.published_at
        existing.discovered_at = incoming.discovered_at
        return existing

    @staticmethod
    def _select_representative(topics):
        """
        Select the strongest article for story-level editorial
        evaluation.

        Reliability is primary; freshness/content are used as
        deterministic tie-breakers.
        """

        def key(topic):
            reliability = (
                topic.reliability_score or 0.0
            )

            content_length = len(
                topic.content or ""
            )

            published_at = topic.published_at
            if published_at is None:
                published_rank = 0.0
            else:
                try:
                    published_rank = published_at.timestamp()
                except (AttributeError, OSError, ValueError):
                    published_rank = 0.0

            return (
                reliability,
                content_length,
                published_rank,
            )

        return max(
            topics,
            key=key,
        )

    @staticmethod
    def _topic_for_evaluation(
        cluster,
        topic_id,
    ):
        for topic in cluster.topics:
            if topic.id == topic_id:
                return topic

        return cluster.best_topic

    def get_cycle_state(self):
        return self.cycle_manager.get_current_state()

    def get_previous_cycle(self):
        return self.cycle_manager.get_previous_cycle()

    def get_story_clusters(self):
        return self.cycle_manager.get_story_clusters()

    def get_candidates(self, active_only: bool = True):
        return self.cycle_manager.get_candidates(active_only=active_only)


    def summary(self):
        return self.cycle_manager.summary()