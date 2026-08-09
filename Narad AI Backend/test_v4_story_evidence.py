from datetime import datetime, timezone
from app.agent.models import Topic
from app.clustering.clusterer import StoryClusterer

def t(i, title, source):
    return Topic(id=i, url=f"https://example.com/{i}", title=title, summary=title, content=title, source=source, published_at=datetime.now(timezone.utc))

def main():
    c = StoryClusterer()
    a = t("a", "OpenAI launches a new AI speaker", "Source A")
    b = t("b", "OpenAI launches new AI speaker device", "Source B")
    cluster = c.add_topic(a)
    cluster = c.add_topic(b)
    assert cluster.article_count == 2
    assert cluster.source_count == 2
    assert cluster.corroboration_score() == 0.65
    print("PASS: Same-event articles accumulate distinct-source evidence.")

if __name__ == "__main__":
    main()
