from app.publishing.policy import PublicationPolicy
from app.agent.models import EvaluationResult

def ev(score, rel, editorial=80):
    return EvaluationResult("t", "Test", 90, 80, rel, 95, 100, editorial, score, False, "test")

def main():
    p=PublicationPolicy()
    assert p.decide(ev(74,76),2,False,.65).ready
    assert p.decide(ev(72,76),1,True,0).path == "primary_source" or p.decide(ev(72,76),1,True,0).ready
    assert p.decide(ev(80,85),1,False,0,best_source_score=95).path == "trusted_single_source"
    d=p.decide(ev(60,60),1,False,0)
    assert not d.ready and d.blockers
    print("PASS: Final publication paths and safety blockers work.")

if __name__ == "__main__": main()
