from app.agent.engine import PersonaEngine
from app.agent.evaluator import EditorialEvaluator
from app.discovery.collector import NewsCollector
from app.ranking.ranker import TopicRanker


def main():

    # ==========================================================
    # CREATE PERSONA
    # ==========================================================

    engine = PersonaEngine()

    engine.create_default_persona()

    # Add Persona interests

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

    # Add editorial rule

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

    print("\n========== COLLECTION ==========")

    print(
        "Articles collected:",
        len(topics)
    )

    # ==========================================================
    # CREATE EVALUATOR
    # ==========================================================

    evaluator = EditorialEvaluator(
        engine
    )

    # ==========================================================
    # EVALUATE ARTICLES
    # ==========================================================

    evaluation_results = []

    for topic in topics:

        result = evaluator.evaluate(
            topic
        )

        evaluation_results.append(
            result
        )

    # ==========================================================
    # CREATE RANKER
    # ==========================================================

    ranker = TopicRanker()

    # ==========================================================
    # RANK ALL ARTICLES
    # ==========================================================

    ranked_results = ranker.rank(
        evaluation_results
    )

    print("\n========== ALL RANKINGS ==========")

    for position, result in enumerate(
        ranked_results,
        start=1
    ):

        print(
            f"{position}. "
            f"{result.topic_title} "
            f"→ {result.overall_score}/100 "
            f"| Publish: {result.publish}"
        )

    # ==========================================================
    # GET TOP 5
    # ==========================================================

    top_results = ranker.top(
        evaluation_results,
        count=5
    )

    print("\n========== TOP 5 ==========")

    for position, result in enumerate(
        top_results,
        start=1
    ):

        print(
            f"{position}. "
            f"{result.topic_title} "
            f"→ {result.overall_score}/100"
        )

    # ==========================================================
    # GET TOP PUBLISHABLE ARTICLES
    # ==========================================================

    top_publishable = ranker.top_publishable(
        evaluation_results,
        count=5
    )

    print("\n========== TOP PUBLISHABLE ==========")

    for position, result in enumerate(
        top_publishable,
        start=1
    ):

        print(
            f"{position}. "
            f"{result.topic_title} "
            f"→ {result.overall_score}/100"
        )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    print("\n========== RANKER SUMMARY ==========")

    print(
        "Articles evaluated:",
        len(evaluation_results)
    )

    print(
        "Articles ranked:",
        len(ranked_results)
    )

    print(
        "Articles publishable:",
        len(top_publishable)
    )


if __name__ == "__main__":
    main()