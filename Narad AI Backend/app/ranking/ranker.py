"""
Editorial Ranking Engine

This module takes evaluated Topics and ranks them
according to their overall editorial score.

The Ranker has one responsibility:
ranking and filtering evaluated articles.
"""

from app.agent.models import EvaluationResult


class TopicRanker:
    """
    Ranks evaluated news Topics.
    """

    # ==========================================================
    # RANK
    # ==========================================================

    def rank(
        self,
        results: list[EvaluationResult]
    ) -> list[EvaluationResult]:
        """
        Return all results sorted from highest score
        to lowest score.

        The original list is not modified.
        """

        if not results:
            return []

        return sorted(
            results,
            key=lambda result: result.overall_score,
            reverse=True
        )

    # ==========================================================
    # TOP N
    # ==========================================================

    def top(
        self,
        results: list[EvaluationResult],
        count: int = 5
    ) -> list[EvaluationResult]:
        """
        Return the top N results.
        """

        if count <= 0:
            return []

        ranked_results = self.rank(results)

        return ranked_results[:count]

    # ==========================================================
    # PUBLISHABLE
    # ==========================================================

    def publishable(
        self,
        results: list[EvaluationResult]
    ) -> list[EvaluationResult]:
        """
        Return only results marked as publishable.
        """

        publishable_results = [
            result
            for result in results
            if result.publish
        ]

        return self.rank(
            publishable_results
        )

    # ==========================================================
    # TOP PUBLISHABLE
    # ==========================================================

    def top_publishable(
        self,
        results: list[EvaluationResult],
        count: int = 5
    ) -> list[EvaluationResult]:
        """
        Return the highest-ranked publishable results.
        """

        return self.publishable(
            results
        )[:count]
        