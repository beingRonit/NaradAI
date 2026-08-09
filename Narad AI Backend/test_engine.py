from app.agent.engine import PersonaEngine


def main():

    engine = PersonaEngine()

    engine.create_default_persona()

    engine.add_interest("LLMs", 95)

    engine.add_interest("Open Source", 90)

    engine.add_editorial_rule(
        "Avoid Hype",
        "Never exaggerate AI news.",
        10
    )

    engine.add_memory(
        topic="Claude 5",
        opinion="Inference latency matters more than context length.",
        keywords=["Claude", "Latency"],
        companies=["Anthropic"],
        technologies=["LLM"]
    )

    print("\n========== PERSONA ==========")
    print(engine.get_persona())

    print("\n========== SUMMARY ==========")
    print(engine.summary())


if __name__ == "__main__":
    main()