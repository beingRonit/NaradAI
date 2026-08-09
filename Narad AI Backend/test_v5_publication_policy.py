from app.publishing.policy import PublicationPolicy
from app.agent.models import EvaluationResult

def e(score, rel, editorial=80):
    return EvaluationResult("t", "Test story", 90, 80, rel, 95, 100, editorial, score, False, "test")

def main():
    p = PublicationPolicy()
    d = p.decide(e(76, 76), 2, False, .65)
    assert d.ready and d.path == "corroborated"
    d = p.decide(e(75, 86), 1, True, 0.0)
    assert d.ready and d.path == "primary_source"
    d = p.decide(e(68, 68), 1, False, 0.0)
    assert not d.ready and d.blockers
    print("PASS: V5 publication policy supports corroborated and high-confidence primary-source paths.")

if __name__ == "__main__": main()
