"""Final story-level publication policy.

The evaluator scores editorial quality. This module decides whether a story
has enough evidence to enter the publisher. It deliberately avoids a simple
"score > X" rule and exposes the reason/path for every decision.
"""

from dataclasses import dataclass
from typing import List

from app.agent.models import EvaluationResult


@dataclass(frozen=True)
class PublicationDecision:
    ready: bool
    path: str
    blockers: List[str]


class PublicationPolicy:
    # Corroborated reporting: strong enough to publish when two independent
    # sources agree, without requiring an artificially high overall score.
    MIN_CORROBORATED_OVERALL = 68.0
    MIN_CORROBORATED_RELIABILITY = 65.0
    MIN_CORROBORATED_EDITORIAL = 70.0

    # Official/primary-source reporting: one official source is acceptable
    # when the story itself scores strongly.
    MIN_PRIMARY_OVERALL = 70.0
    MIN_PRIMARY_RELIABILITY = 75.0
    MIN_PRIMARY_EDITORIAL = 70.0

    # Very strong trusted single-source path for breaking announcements.
    MIN_TRUSTED_SINGLE_OVERALL = 78.0
    MIN_TRUSTED_SINGLE_RELIABILITY = 82.0
    MIN_TRUSTED_SINGLE_EDITORIAL = 75.0

    # Final-hour mode never removes verification; it only relaxes the score
    # slightly for already-corroborated stories.
    MIN_FINAL_OVERALL = 65.0
    MIN_FINAL_RELIABILITY = 65.0

    # Deadline fallback minimums.
    # Ranking still determines which story is selected.
    MIN_DEADLINE_RELIABILITY = 55.0
    MIN_DEADLINE_EDITORIAL = 70.0

    def decide(
        self,
        evaluation: EvaluationResult,
        source_count: int,
        has_primary_source: bool = False,
        corroboration: float = 0.0,
        final_hour: bool = False,
        best_source_score: float = 0.0,
    ) -> PublicationDecision:

        blockers = []

        editorial_ok = (
            evaluation.editorial_score >= self.MIN_CORROBORATED_EDITORIAL
        )

        primary_ok = (
            has_primary_source
            and evaluation.overall_score >= self.MIN_PRIMARY_OVERALL
            and evaluation.reliability_score >= self.MIN_PRIMARY_RELIABILITY
            and evaluation.editorial_score >= self.MIN_PRIMARY_EDITORIAL
        )

        trusted_single_ok = (
            source_count == 1
            and best_source_score >= 90
            and evaluation.overall_score >= self.MIN_TRUSTED_SINGLE_OVERALL
            and evaluation.reliability_score >= self.MIN_TRUSTED_SINGLE_RELIABILITY
            and evaluation.editorial_score >= self.MIN_TRUSTED_SINGLE_EDITORIAL
        )

        if source_count >= 2:
            overall_min = (
                self.MIN_FINAL_OVERALL
                if final_hour
                else self.MIN_CORROBORATED_OVERALL
            )

            reliability_min = (
                self.MIN_FINAL_RELIABILITY
                if final_hour
                else self.MIN_CORROBORATED_RELIABILITY
            )

            corroborated_ok = (
                corroboration + 1e-9 >= 0.65
                and evaluation.overall_score >= overall_min
                and evaluation.reliability_score >= reliability_min
                and editorial_ok
            )
        else:
            corroborated_ok = False

        if primary_ok:
            return PublicationDecision(
                True,
                "primary_source",
                [],
            )

        if trusted_single_ok:
            return PublicationDecision(
                True,
                "trusted_single_source",
                [],
            )

        if corroborated_ok:
            return PublicationDecision(
                True,
                "corroborated",
                [],
            )

        if evaluation.overall_score < 68:
            blockers.append(
                f"overall score {evaluation.overall_score:.1f} < 68"
            )

        if evaluation.reliability_score < 65:
            blockers.append(
                f"reliability {evaluation.reliability_score:.1f} < 65"
            )

        if not editorial_ok:
            blockers.append(
                f"editorial score {evaluation.editorial_score:.1f} < 70"
            )

        if source_count < 2:
            if has_primary_source:
                blockers.append(
                    f"primary source path requires reliability >= "
                    f"{self.MIN_PRIMARY_RELIABILITY:.0f}"
                )
            elif best_source_score >= 90:
                blockers.append(
                    f"trusted single-source path requires overall >= "
                    f"{self.MIN_TRUSTED_SINGLE_OVERALL:.0f} and reliability >= "
                    f"{self.MIN_TRUSTED_SINGLE_RELIABILITY:.0f}"
                )
            else:
                blockers.append("fewer than 2 independent sources")
        else:
            if corroboration + 1e-9 < 0.65:
                blockers.append(
                    f"corroboration={corroboration:.2f} < 0.65"
                )

        return PublicationDecision(
            False,
            "standard",
            blockers,
        )

    def decide_deadline_fallback(
        self,
        evaluation: EvaluationResult,
        source_count: int,
        has_primary_source: bool = False,
        corroboration: float = 0.0,
        best_source_score: float = 0.0,
    ) -> PublicationDecision:
        """Select the best verified story when the posting deadline is reached.

        Normal publication remains strict.

        At the deadline, ranking determines the preferred story. The fallback
        still requires minimum reliability and editorial quality, but does not
        require two independent sources or the normal 68-point score threshold.
        """

        blockers = []

        if (
            evaluation.reliability_score
            < self.MIN_DEADLINE_RELIABILITY
        ):
            blockers.append(
                f"reliability {evaluation.reliability_score:.1f} < "
                f"{self.MIN_DEADLINE_RELIABILITY:.0f}"
            )

        if (
            evaluation.editorial_score
            < self.MIN_DEADLINE_EDITORIAL
        ):
            blockers.append(
                f"editorial score {evaluation.editorial_score:.1f} < "
                f"{self.MIN_DEADLINE_EDITORIAL:.0f}"
            )

        if blockers:
            return PublicationDecision(
                False,
                "deadline_fallback",
                blockers,
            )

        return PublicationDecision(
            True,
            "deadline_fallback_ranked",
            [],
        )