from datetime import datetime, timezone
from app.agent.models import Topic
from app.clustering.clusterer import StoryClusterer

def t(i, title, source):
    return Topic(id=i, url=f"https://example.com/{i}", title=title, summary=title, content=title, source=source, published_at=datetime.now(timezone.utc))

def main():
    c = StoryClusterer()
    a = t("a", "OpenAI launches a new AI speaker", "Ars Technica")
    b = t("b", "OpenAI launches new AI speaker device", "Ars Technica")
    cl = c.add_topic(a); cl = c.add_topic(b)
    assert cl.source_count == 1
    assert cl.corroboration_score() == 0.0

    c2 = StoryClusterer()
    a = t("a", "OpenAI launches a new AI speaker", "Ars Technica")
    b = t("b", "OpenAI launches new AI speaker device", "TechCrunch")
    cl = c2.add_topic(a); cl = c2.add_topic(b)
    assert cl.source_count == 2
    assert cl.corroboration_score() == 0.65
    print("PASS: Source aliases/identity distinguish duplicate and independent reporting.")

if __name__ == "__main__": main()
