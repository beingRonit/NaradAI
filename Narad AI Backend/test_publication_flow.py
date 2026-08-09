from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile

from app.agent.engine import PersonaEngine
from app.agent.models import Topic
from app.pipeline import EditorialPipeline
from app.publishing.publisher import Publisher


class FakeCollector:
    def __init__(self, topic): self.topic = topic
    def collect(self): return [self.topic]


def main():
    now = datetime.now(timezone.utc)
    topic = Topic(
        id="publication-test-001",
        url="https://www.reuters.com/technology/example",
        title="OpenAI announces a new model architecture for developers",
        summary="OpenAI announced a new model architecture that improves inference efficiency and developer tooling.",
        content=("According to OpenAI, the company announced a new model architecture for developers. The system improves inference efficiency by 30 percent and includes an official developer API. Researchers said the release will be available through the developer platform. https://openai.com/research/example. " * 10),
        source="Reuters",
        category="Technology",
        tags=["AI", "LLM", "developer", "architecture"],
        published_at=now,
        discovered_at=now,
    )

    engine = PersonaEngine()
    engine.create_default_persona()

    with tempfile.TemporaryDirectory() as tmp:
        publisher = Publisher(agent_id="test-agent", data_dir=tmp)
        pipeline = EditorialPipeline(engine, publisher=publisher, auto_publish=True, posting_deadline=now - timedelta(seconds=1))
        pipeline.collector = FakeCollector(topic)
        result = pipeline.run(top_count=5, enrich=False)

        assert result["summary"]["discovered"] == 1
        assert result["summary"]["verified"] == 1
        assert len(result["evaluation_results"]) == 1
        assert result["published_post"] is not None, result["evaluation_results"][0]
        assert len(engine.get_persona().memory) == 1
        assert len(publisher.list_posts()) == 1

        # Idempotency: second cycle must not create a second post.
        result2 = pipeline.run(top_count=5, enrich=False)
        assert len(publisher.list_posts()) == 1

    print("PASS: Publication flow")
    print("PASS: Memory write")
    print("PASS: Persistent feed write")
    print("PASS: Publication idempotency")


if __name__ == "__main__":
    main()
