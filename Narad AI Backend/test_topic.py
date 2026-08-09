from app.agent.models import Topic, TopicStatus


def main():

    topic = Topic(
        id="topic-001",

        url="https://example.com/gpt-6",

        title="OpenAI announces a new generation of AI models",

        summary=(
            "OpenAI has announced a new generation "
            "of artificial intelligence models."
        ),

        content=(
            "This is placeholder article content "
            "for our development test."
        ),

        source="Example News",

        author="Test Author",

        category="Artificial Intelligence",

        language="en",

        tags=[
            "AI",
            "LLM",
            "OpenAI"
        ]
    )

    print("\n========== TOPIC ==========")
    print(topic)

    print("\n========== TOPIC STATUS ==========")
    print(topic.status)

    print("\n========== TOPIC DETAILS ==========")
    print("ID:", topic.id)
    print("Title:", topic.title)
    print("Source:", topic.source)
    print("Category:", topic.category)
    print("Tags:", topic.tags)

    print("\n========== SCORES ==========")
    print("Reliability:", topic.reliability_score)
    print("Evaluation:", topic.evaluation_score)


if __name__ == "__main__":
    main()