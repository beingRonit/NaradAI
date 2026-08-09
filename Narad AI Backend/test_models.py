from app.agent.models import (
    Interest,
    EditorialRule,
    MemoryEntry,
    Persona,
)


def main():

    # ------------------------------------
    # Interests
    # ------------------------------------

    interests = {

        "LLMs": Interest(
            topic="LLMs",
            weight=95,
            confidence=0.90,
            interactions=10
        ),

        "Open Source": Interest(
            topic="Open Source",
            weight=90
        )
    }

    # ------------------------------------
    # Editorial Rules
    # ------------------------------------

    rules = [

        EditorialRule(
            name="Avoid Hype",
            description="Never exaggerate AI news.",
            priority=10
        ),

        EditorialRule(
            name="Verify Sources",
            description="Always verify information using multiple trusted sources.",
            priority=9
        )
    ]

    # ------------------------------------
    # Memory
    # ------------------------------------

    memory = [

        MemoryEntry(
            topic="Claude 5",
            opinion="Inference latency matters more than context length.",
            keywords=["Claude", "Latency"],
            companies=["Anthropic"],
            technologies=["LLM"]
        )
    ]

    # ------------------------------------
    # Persona
    # ------------------------------------

    persona = Persona(

        name="Ada Vector",

        bio="Senior AI Research Engineer",

        tone="Analytical",

        writing_style="Evidence Driven",

        posting_time="09:00",

        timezone="Asia/Kolkata",

        interests=interests,

        editorial_rules=rules,

        memory=memory
    )

    # ------------------------------------
    # Print
    # ------------------------------------

    print("\n========== PERSONA ==========")
    print(persona)

    print("\n========== PERSONA STATE ==========")
    print(persona.state)

    print("\n========== INTERESTS ==========")

    for topic, interest in persona.interests.items():
        print(topic, "->", interest)

    print("\n========== RULES ==========")

    for rule in persona.editorial_rules:
        print(rule)

    print("\n========== MEMORY ==========")

    for item in persona.memory:
        print(item)


if __name__ == "__main__":
    main()