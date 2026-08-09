"""Publication and feed persistence.

The hackathon does not require a real social-network API. The publisher
therefore creates durable feed posts locally. Replacing this adapter with a
real platform publisher later does not change the editorial pipeline.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional
from uuid import uuid4

from app.agent.models import EvaluationResult, MemoryEntry, Topic, TopicStatus
from app.agent.llm_writer import LLMWriter
from app.storage import JsonStore


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass
class PublishedPost:
    id: str
    agent_id: str
    created_at: str
    text: str
    rationale: str
    sources: list[str]
    topic_id: str
    cluster_id: Optional[str] = None


class Publisher:
    def __init__(self, agent_id: str = "default-agent", data_dir: str | Path | None = None):
        root = Path(data_dir) if data_dir else DATA_DIR
        root.mkdir(parents=True, exist_ok=True)
        self.agent_id = agent_id
        self.store = JsonStore(root / "posts.json")
        self.memory_store = JsonStore(root / "memory.json")

        self.llm_writer = None

        try:
            self.llm_writer = LLMWriter()
        except Exception as exc:
            print(f"LLM writer unavailable: {exc}")

    def list_posts(self, limit: int = 50) -> list[PublishedPost]:
        rows = self.store.read([])
        rows = rows if isinstance(rows, list) else []
        rows.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return [PublishedPost(**row) for row in rows[: max(0, limit)]]

    def publish(
        self,
        topic: Topic,
        evaluation: EvaluationResult,
        cluster_id: str | None = None,
        sources: Iterable[str] | None = None,
        persona=None,
    ) -> PublishedPost:
        posts = self.store.read([])
        posts = posts if isinstance(posts, list) else []

        # Idempotency: the same topic is never published twice.
        for row in posts:
            if row.get("topic_id") == topic.id:
                return PublishedPost(**row)

        if self.llm_writer is not None and persona is not None:
            try:
                text = self.llm_writer.generate_article(
                    topic=topic,
                    persona=persona,
                )
                print(f"LLM article generated for: {topic.title}")
            except Exception as exc:
                print(f"LLM generation failed, using fallback: {exc}")
                text = self._compose_text(topic)
        else:
            text = self._compose_text(topic)
        rationale = evaluation.reason
        source_list = sorted(set(sources or [topic.url]))
        now = datetime.now(timezone.utc).isoformat()

        post = PublishedPost(
            id=f"post-{uuid4().hex[:12]}",
            agent_id=self.agent_id,
            created_at=now,
            text=text,
            rationale=rationale,
            sources=source_list,
            topic_id=topic.id,
            cluster_id=cluster_id,
        )

        posts.append(asdict(post))
        self.store.write(posts)
        topic.status = TopicStatus.PUBLISHED
        return post

    def remember_publication(self, persona, topic: Topic, opinion: str, technologies: list[str] | None = None):
        # Deduplicate by normalized topic/title.
        existing = self.memory_store.read([])
        existing = existing if isinstance(existing, list) else []
        key = self._norm(topic.title)
        if any(self._norm(x.get("topic", "")) == key for x in existing):
            return

        entry = MemoryEntry(
            topic=topic.title,
            opinion=opinion,
            keywords=self._keywords(topic.title + " " + topic.summary),
            companies=self._companies(topic.title + " " + topic.summary),
            technologies=technologies or [],
        )
        existing.append(asdict(entry))
        self.memory_store.write(existing)
        persona.memory.append(entry)

    def load_memory(self, persona) -> None:
        rows = self.memory_store.read([])
        if not isinstance(rows, list):
            return
        persona.memory.clear()
        for row in rows:
            try:
                persona.memory.append(MemoryEntry(**row))
            except TypeError:
                continue

    @staticmethod
    def _compose_text(topic: Topic) -> str:
        summary = (topic.summary or topic.content or "").strip()
        if len(summary) > 500:
            summary = summary[:497].rsplit(" ", 1)[0] + "..."
        if summary:
            return f"{topic.title}\n\n{summary}"
        return topic.title

    @staticmethod
    def _norm(value: str) -> str:
        return " ".join(value.lower().split())

    @staticmethod
    def _keywords(text: str) -> list[str]:
        import re
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{3,}", text.lower())
        stop = {"this", "that", "with", "from", "into", "about", "after", "have", "will", "says"}
        return sorted(set(w for w in words if w not in stop))[:20]

    @staticmethod
    def _companies(text: str) -> list[str]:
        names = ["OpenAI", "Google", "Microsoft", "Anthropic", "Meta", "Apple", "Amazon", "NVIDIA", "Cloudflare", "Suno"]
        lower = text.lower()
        return [n for n in names if n.lower() in lower]