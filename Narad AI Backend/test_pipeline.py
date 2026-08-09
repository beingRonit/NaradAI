from app.agent.engine import PersonaEngine
from app.pipeline import EditorialPipeline


def main():

    # ==========================================================
    # PERSONA
    # ==========================================================

    engine = PersonaEngine()

    engine.create_default_persona()

    engine.add_interest(
        topic="LLMs",
        weight=95,
        confidence=0.90
    )

    engine.add_interest(
        topic="Open Source",
        weight=90,
        confidence=0.80
    )

    engine.add_interest(
        topic="Cybersecurity",
        weight=85,
        confidence=0.80
    )

    engine.add_editorial_rule(
        name="Avoid Hype",
        description="Never exaggerate AI news.",
        priority=10
    )

    # ==========================================================
    # PIPELINE
    # ==========================================================

    pipeline = EditorialPipeline(
        persona_engine=engine
    )

    results = pipeline.run(
        top_count=5
    )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    print("\n========== PIPELINE SUMMARY ==========")

    print(
        "Discovered:",
        len(results["topics_discovered"])
    )

    print(
        "Verified:",
        len(results["topics_verified"])
    )

    print(
        "Evaluated:",
        len(results["evaluation_results"])
    )

    print(
        "Ranked:",
        len(results["ranked_results"])
    )

    print(
        "Top:",
        len(results["top_results"])
    )

    # ==========================================================
    # FINAL RANKING
    # ==========================================================

    print("\n========== FINAL RANKING ==========")

    for position, result in enumerate(
        results["top_results"],
        start=1
    ):

        print(
            f"{position}. "
            f"{result.topic_title} "
            f"→ {result.overall_score}/100"
        )

        print(
            f"   Publish: {result.publish}"
        )

        print(
            f"   Reason: {result.reason}"
        )


if __name__ == "__main__":
    main()