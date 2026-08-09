from datetime import datetime, timezone

from app.agent.models import Topic, EnrichmentStatus
from app.clustering.models import StoryCluster
from app.pipeline import EditorialPipeline


def make_topic(i, source):
    return Topic(
        id=i, url=f"https://{source.lower().replace(' ', '')}.example/{i}",
        title="OpenAI launches a new AI speaker",
        summary="OpenAI launches a new AI speaker with a reported new design.",
        content="OpenAI launches a new AI speaker. The report includes specific details and attribution.",
        source=source, published_at=datetime.now(timezone.utc)
    )


def test_multi_source_evidence_enrichment_targets_unenriched_sources(monkeypatch):
    class FakeFetcher:
        def __init__(self): self.calls=[]
        def enrich(self, topic, force=False):
            self.calls.append(topic.id)
            topic.enrichment_status = EnrichmentStatus.SUCCESS
            return None

    class DummyPersona: pass

    pipeline = EditorialPipeline(DummyPersona())
    fake = FakeFetcher()
    pipeline.fetcher = fake

    a = make_topic("a", "Ars Technica")
    b = make_topic("b", "TechCrunch")
    c = make_topic("c", "The Verge")
    cluster = StoryCluster("cluster-test")
    cluster.add_topic(a); cluster.add_topic(b); cluster.add_topic(c)

    pipeline._enrich_multi_source_evidence([cluster])

    assert set(fake.calls) == {"a", "b", "c"}


def test_multi_source_evidence_skips_successful_enrichment(monkeypatch):
    class FakeFetcher:
        def __init__(self): self.calls=[]
        def enrich(self, topic, force=False): self.calls.append(topic.id)

    pipeline = EditorialPipeline(type("P", (), {})())
    fake = FakeFetcher(); pipeline.fetcher = fake
    a = make_topic("a", "Ars Technica")
    b = make_topic("b", "TechCrunch")
    a.enrichment_status = EnrichmentStatus.SUCCESS
    cluster = StoryCluster("cluster-test")
    cluster.add_topic(a); cluster.add_topic(b)
    pipeline._enrich_multi_source_evidence([cluster])
    assert fake.calls == ["b"]
