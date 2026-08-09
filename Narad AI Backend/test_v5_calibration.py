from datetime import datetime, timezone
from app.agent.engine import PersonaEngine
from app.agent.evaluator import EditorialEvaluator
from app.agent.models import Topic
from app.verification.verifier import VerificationEngine
from app.publishing.policy import PublicationPolicy

def make(source):
    return Topic(
        id=source, url=f"https://example.com/{source}",
        title="OpenAI releases a new AI model with benchmark results",
        summary="OpenAI announces a new AI model with benchmark results and API access.",
        content=("OpenAI announced a new AI model and published benchmark results. "
                 "Developers can access it through the API. The model improves "
                 "inference speed by 30 percent and includes technical documentation."),
        source=source, category="AI", tags=["LLM", "AI"],
        published_at=datetime.now(timezone.utc),
    )

def main():
    v=VerificationEngine(); engine=PersonaEngine(); engine.create_default_persona(); ev=EditorialEvaluator(engine); policy=PublicationPolicy()
    official=make("OpenAI"); vr=v.verify(official); er=ev.evaluate(official)
    assert vr.reliability_score >= 60
    primary=policy.decide(er, 1, has_primary_source=True)
    assert primary.ready, (vr.reliability_score, er.overall_score, primary)

    a=make("Reuters"); b=make("TechCrunch")
    va=v.verify(a); vb=v.verify(b)
    ea=ev.evaluate(a)
    # Simulate the story-level corroboration boost applied by the pipeline.
    ea.reliability_score = min(100.0, ea.reliability_score + 9.75)
    ea.overall_score = round(
        ea.interest_score * 0.25 + ea.technical_score * 0.20 +
        ea.reliability_score * 0.25 + ea.freshness_score * 0.15 +
        ea.memory_score * 0.10 + ea.editorial_score * 0.05, 2
    )
    decision=policy.decide(ea, 2, has_primary_source=False, corroboration=0.65)
    assert decision.ready, (ea.overall_score, ea.reliability_score, decision)
    print("PASS: V5 calibration supports strong primary-source stories and corroborated reporting.")

if __name__ == "__main__": main()
