from app.discovery.collector import NewsCollector
from app.verification.verifier import VerificationEngine


def main():

    collector = NewsCollector()

    try:

        # ======================================================
        # COLLECTION
        # ======================================================

        print(
            "\n========== COLLECTING =========="
        )

        topics = collector.collect()

        print(
            f"Discovered: {len(topics)}"
        )

        # ======================================================
        # VERIFICATION ENGINE
        # ======================================================

        verifier = VerificationEngine()

        results = []

        # ======================================================
        # VERIFICATION
        # ======================================================

        print(
            "\n========== VERIFICATION RESULTS =========="
        )

        for topic in topics:

            result = verifier.verify(
                topic
            )

            results.append(
                result
            )

            specificity_score = (
                verifier._specificity_score(
                    topic
                )
            )

            temporal_score = (
                verifier._temporal_consistency_score(
                    topic
                )
            )

            print("\n---")

            print(
                f"Title: {topic.title}"
            )

            print(
                f"Source: {topic.source}"
            )

            print(
                f"Source Score: "
                f"{result.source_score}"
            )

            print(
                f"Evidence Score: "
                f"{result.evidence_score}"
            )

            print(
                f"Specificity Score: "
                f"{specificity_score}"
            )

            print(
                f"Temporal Score: "
                f"{temporal_score}"
            )

            print(
                f"Completeness: "
                f"{result.completeness_score}"
            )

            print(
                f"Reliability: "
                f"{result.reliability_score}"
            )

            # --------------------------------------------------
            # IMPORTANT STATUS
            # --------------------------------------------------

            if result.verified:

                verification_status = (
                    "VERIFIED"
                )

            else:

                verification_status = (
                    "NOT VERIFIED YET"
                )

            print(
                f"Verification: "
                f"{verification_status}"
            )

            print(
                f"Topic Status: "
                f"{topic.status}"
            )

            print(
                f"Reason: "
                f"{result.reason}"
            )

        # ======================================================
        # SUMMARY
        # ======================================================

        status = verifier.get_status()

        print(
            "\n========== VERIFICATION SUMMARY =========="
        )

        print(
            f"Processed: "
            f"{status['processed']}"
        )

        print(
            f"Verified: "
            f"{status['verified']}"
        )

        print(
            f"Not Verified Yet: "
            f"{status['pending']}"
        )

        # ======================================================
        # SCORE DISTRIBUTION
        # ======================================================

        if results:

            reliability_scores = [

                result.reliability_score

                for result in results
            ]

            highest = max(
                reliability_scores
            )

            lowest = min(
                reliability_scores
            )

            average = (
                sum(reliability_scores)
                /
                len(reliability_scores)
            )

            print(
                "\n========== SCORE DISTRIBUTION =========="
            )

            print(
                f"Highest Reliability: "
                f"{highest:.2f}"
            )

            print(
                f"Lowest Reliability: "
                f"{lowest:.2f}"
            )

            print(
                f"Average Reliability: "
                f"{average:.2f}"
            )

    finally:

        collector.close()


if __name__ == "__main__":

    main()