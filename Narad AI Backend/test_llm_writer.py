from types import SimpleNamespace

from app.agent.engine import PersonaEngine
from app.agent.llm_writer import LLMWriter


def main():
    print("========================================")
    print("        GEMINI LLM WRITER TEST")
    print("========================================")

    # Load the existing persona system
    persona_engine = PersonaEngine()
    persona = persona_engine.ensure_default_persona()

    print(f"Persona: {persona.name}")
    print(f"Tone: {persona.tone}")
    print(f"Writing style: {persona.writing_style}")

    # Create a small test topic.
    # We use SimpleNamespace so this test does not modify your
    # existing Topic model or database/persistence.
    topic = SimpleNamespace(
        id="test-topic-001",
        url="https://example.com/test",
        title="OpenAI announces a new AI research initiative",
        summary=(
            "OpenAI has announced a new research initiative focused "
            "on improving the reliability and usefulness of artificial intelligence."
        ),
        content=(
            "OpenAI announced a new research initiative focused on "
            "AI reliability and usefulness. The initiative is intended "
            "to explore methods for making AI systems more dependable "
            "and useful in practical applications."
        ),
        source="Test Source",
        author="Test Author",
    )

    print()
    print("Sending test story to Gemini...")
    print("----------------------------------------")

    writer = LLMWriter()

    article = writer.generate_article(
        topic=topic,
        persona=persona,
    )

    print()
    print("GENERATED ARTICLE")
    print("========================================")
    print(article)
    print("========================================")
    print()
    print("LLM WRITER TEST PASSED")


if __name__ == "__main__":
    main()