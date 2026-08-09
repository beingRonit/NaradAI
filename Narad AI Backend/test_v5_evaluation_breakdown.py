from datetime import datetime, timezone
from app.agent.engine import PersonaEngine
from app.agent.evaluator import EditorialEvaluator
from app.agent.models import Topic

def main():
    engine = PersonaEngine(); engine.create_default_persona()
    topic = Topic(id="t", url="https://openai.com/x", title="OpenAI releases a new AI model", summary="OpenAI releases a new AI model with benchmark results", content="OpenAI releases a new AI model with benchmark results and API access.", source="OpenAI", published_at=datetime.now(timezone.utc), category="AI", tags=["LLM"])
    r = EditorialEvaluator(engine).evaluate(topic)
    assert set(r.score_breakdown) >= {"interest","technical","reliability","freshness","memory","editorial","overall"}
    assert r.score_breakdown["overall"] == r.overall_score
    print("PASS: Evaluation exposes a complete editorial score breakdown.")

if __name__ == "__main__": main()
