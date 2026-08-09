from app.agent.engine import PersonaEngine
from app.discovery.collector import NewsCollector
from app.agent.evaluator import EditorialEvaluator


def main():

    # ==========================================================
    # CREATE PERSONA
    # ==========================================================

    engine = PersonaEngine()

    engine.create_default_persona()

    # Give the Persona interests.

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

    # Add editorial rule.

    engine.add_editorial_rule(
        name="Avoid Hype",
        description="Never exaggerate AI news.",
        priority=10
    )

    # ==========================================================
    # COLLECT NEWS
    # ==========================================================

    collector = NewsCollector()

    topics = collector.collect()

    # ==========================================================
    # CREATE EVALUATOR
    # ==========================================================

    evaluator = EditorialEvaluator(
        engine
    )

    # ==========================================================
    # EVALUATE ARTICLES
    # ==========================================================

    results = []

    for topic in topics:

        result = evaluator.evaluate(
            topic
        )

        results.append(result)

    # ==========================================================
    # PRINT RESULTS
    # ==========================================================

    print("\n========== EDITORIAL EVALUATION ==========")

    for result in results:

        print("\n----------------------------------------")

        print(
            "Title:",
            result.topic_title
        )

        print(
            "Interest:",
            result.interest_score
        )

        print(
            "Technical:",
            result.technical_score
        )

        print(
            "Reliability:",
            result.reliability_score
        )

        print(
            "Freshness:",
            result.freshness_score
        )

        print(
            "Memory:",
            result.memory_score
        )

        print(
            "Editorial:",
            result.editorial_score
        )

        print(
            "OVERALL:",
            result.overall_score
        )

        print(
            "Publish:",
            result.publish
        )

        print(
            "Reason:",
            result.reason
        )

    # ==========================================================
    # RANK
    # ==========================================================

    results.sort(
        key=lambda result: result.overall_score,
        reverse=True
    )

    print("\n========== RANKING ==========")

    for position, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{position}. "
            f"{result.topic_title} "
            f"→ {result.overall_score}/100"
        )


if __name__ == "__main__":
    main()
