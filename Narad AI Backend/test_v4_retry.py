from datetime import datetime, timezone, timedelta
from app.agent.models import Topic, EnrichmentStatus
from app.enrichment.article_fetcher import ArticleFetcher

class FakeFetcher(ArticleFetcher):
    def __init__(self):
        super().__init__(timeout=1)
        self.calls = 0
    def _request(self, *args, **kwargs):
        pass

def main():
    topic = Topic(id="retry-1", url="https://example.com", title="Test", summary="Test", content="RSS summary", source="Example")
    fetcher = ArticleFetcher(timeout=1)
    topic.enrichment_status = EnrichmentStatus.FAILED
    topic.enrichment_attempts = 1
    topic.next_enrichment_retry = datetime.now() + timedelta(minutes=30)
    result = fetcher.enrich(topic)
    assert result.extractor == "backoff"
    assert fetcher.processed_count == 0
    print("PASS: Failed enrichment respects retry backoff.")

if __name__ == "__main__":
    main()
