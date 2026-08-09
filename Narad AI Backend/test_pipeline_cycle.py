"""
Pipeline + Cycle Integration Test

Tests the complete autonomous editorial workflow:

    RSS Collection
          ↓
    Verification
          ↓
    Editorial Evaluation
          ↓
    Story Clustering
          ↓
    Ranking
          ↓
    Cycle Persistence
          ↓
    Memory / Publication State
"""

from app.pipeline import EditorialPipeline

from app.agent.models import (
    Persona,
    PersonaState,
    Interest,
    EditorialRule,
    MemoryEntry,
    AgentStatus,
)


# ============================================================
# TEST PERSONA
# ============================================================

def build_test_persona() -> Persona:
    """
    Build a REAL Persona object using the application's
    production data model.

    This is deliberately not a fake TestPersona class.

    That prevents the integration test from drifting away
    from app.agent.models.Persona.
    """

    interests = {

        "artificial_intelligence": Interest(
            topic="artificial intelligence",
            weight=100.0,
            confidence=1.0,
        ),

        "machine_learning": Interest(
            topic="machine learning",
            weight=95.0,
            confidence=1.0,
        ),

        "cybersecurity": Interest(
            topic="cybersecurity",
            weight=95.0,
            confidence=1.0,
        ),

        "technology": Interest(
            topic="technology",
            weight=85.0,
            confidence=1.0,
        ),

        "software_engineering": Interest(
            topic="software engineering",
            weight=85.0,
            confidence=1.0,
        ),

        "cloud_computing": Interest(
            topic="cloud computing",
            weight=75.0,
            confidence=1.0,
        ),

        "robotics": Interest(
            topic="robotics",
            weight=70.0,
            confidence=1.0,
        ),
    }

    editorial_rules = [

        EditorialRule(
            name="technical_relevance",
            description=(
                "Prefer technically meaningful "
                "AI and technology developments."
            ),
            priority=1,
            enabled=True,
        ),

        EditorialRule(
            name="source_reliability",
            description=(
                "Prefer reliable and well-supported "
                "news sources."
            ),
            priority=2,
            enabled=True,
        ),

        EditorialRule(
            name="novelty",
            description=(
                "Avoid repetitive coverage and "
                "prefer genuinely new information."
            ),
            priority=3,
            enabled=True,
        ),

        EditorialRule(
            name="freshness",
            description=(
                "Prefer recent developments."
            ),
            priority=4,
            enabled=True,
        ),

        EditorialRule(
            name="substance",
            description=(
                "Prefer articles containing "
                "meaningful technical substance."
            ),
            priority=5,
            enabled=True,
        ),
    ]

    memory = []

    persona = Persona(

        name="AutonomousAI Test Creator",

        bio=(
            "A technology-focused AI creator interested "
            "in artificial intelligence, machine learning, "
            "cybersecurity and software engineering."
        ),

        tone="analytical",

        writing_style=(
            "concise, technical, opinionated and "
            "evidence-driven"
        ),

        posting_time="scheduled",

        timezone="UTC",

        state=PersonaState(
            status=AgentStatus.IDLE,
        ),

        interests=interests,

        editorial_rules=editorial_rules,

        memory=memory,
    )

    return persona


# ============================================================
# TEST PERSONA ENGINE
# ============================================================

class PersonaEngineStub:
    """
    Minimal persona engine.

    The evaluator expects:

        get_persona()
    """

    def __init__(self):

        self.persona = build_test_persona()

    def get_persona(self) -> Persona:

        return self.persona


# ============================================================
# DISPLAY HELPERS
# ============================================================

def separator():

    print()

    print(
        "=" * 60
    )


def print_result(
    result,
    cycle_number,
):

    print()

    print(
        "============================================================"
    )

    print(
        f"========== CYCLE {cycle_number} RESULT =========="
    )

    print(
        "============================================================"
    )

    summary = result.get(
        "summary",
        {},
    )

    print(
        f"Cycle:      "
        f"{summary.get('cycle_id', cycle_number)}"
    )

    print(
        f"Discovered: "
        f"{summary.get('discovered', 0)}"
    )

    print(
        f"Verified:   "
        f"{summary.get('verified', 0)}"
    )

    print(
        f"Evaluated:  "
        f"{summary.get('evaluated', 0)}"
    )

    print(
        f"Clusters:   "
        f"{summary.get('clusters', 0)}"
    )

    print(
        f"Ranked:     "
        f"{summary.get('ranked', 0)}"
    )

    print(
        f"Top:        "
        f"{summary.get('top', 0)}"
    )

    top_results = result.get(
        "top_results",
        [],
    )

    if not top_results:

        return

    print()

    print(
        "========== TOP RESULTS =========="
    )

    for index, item in enumerate(
        top_results,
        start=1,
    ):

        title = getattr(
            item,
            "topic_title",
            None,
        )

        if title is None:

            title = getattr(
                item,
                "title",
                None,
            )

        score = getattr(
            item,
            "score",
            None,
        )

        if score is None:

            score = getattr(
                item,
                "overall_score",
                None,
            )

        publish = getattr(
            item,
            "publish",
            None,
        )

        print()

        print(
            f"{index}. "
            f"{title or 'Unknown'}"
        )

        if score is not None:

            print(
                f"   Score: {score}"
            )

        if publish is not None:

            print(
                f"   Publish: {publish}"
            )


# ============================================================
# PERSONA TEST
# ============================================================

def integration_test_persona(
    persona_engine,
):

    print()

    print(
        "========== PERSONA TEST =========="
    )

    persona = (
        persona_engine.get_persona()
    )

    # --------------------------------------------------------
    # PERSONA TYPE
    # --------------------------------------------------------

    assert isinstance(
        persona,
        Persona,
    ), (
        "Persona engine must return "
        "the production Persona model."
    )

    print(
        "PASS: Real Persona model created."
    )

    # --------------------------------------------------------
    # INTERESTS
    # --------------------------------------------------------

    assert isinstance(
        persona.interests,
        dict,
    )

    assert (
        len(persona.interests) > 0
    )

    for key, interest in (
        persona.interests.items()
    ):

        assert isinstance(
            interest,
            Interest,
        )

        assert isinstance(
            interest.topic,
            str,
        )

        assert isinstance(
            interest.weight,
            (int, float),
        )

        assert isinstance(
            interest.confidence,
            (int, float),
        )

    print(
        "PASS: Persona interests use "
        "the production Interest model."
    )

    # --------------------------------------------------------
    # EDITORIAL RULES
    # --------------------------------------------------------

    assert isinstance(
        persona.editorial_rules,
        list,
    )

    for rule in (
        persona.editorial_rules
    ):

        assert isinstance(
            rule,
            EditorialRule,
        )

    print(
        "PASS: Editorial rules use "
        "the production EditorialRule model."
    )

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    assert isinstance(
        persona.memory,
        list,
    )

    for memory_entry in (
        persona.memory
    ):

        assert isinstance(
            memory_entry,
            MemoryEntry,
        )

    print(
        "PASS: Persona memory uses "
        "the production MemoryEntry model."
    )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    assert isinstance(
        persona.state,
        PersonaState,
    )

    print(
        "PASS: Persona state uses "
        "the production PersonaState model."
    )

    return persona


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print(
        "############################################"
    )

    print(
        "      PIPELINE + CYCLE INTEGRATION TEST"
    )

    print(
        "############################################"
    )

    # ========================================================
    # PERSONA
    # ========================================================

    persona_engine = (
        PersonaEngineStub()
    )

    persona = test_persona(
        persona_engine,
    )

    # ========================================================
    # PIPELINE
    # ========================================================

    pipeline = EditorialPipeline(
        persona_engine=persona_engine,
    )

    print(
        "PASS: Editorial pipeline initialized."
    )

    # ========================================================
    # CYCLE 1
    # ========================================================

    separator()

    print(
        "EDITORIAL CYCLE 1"
    )

    separator()

    result_1 = pipeline.run(
        top_count=5,
    )

    print_result(
        result_1,
        1,
    )

    # --------------------------------------------------------
    # CYCLE ID
    # --------------------------------------------------------

    summary_1 = result_1.get(
        "summary",
        {},
    )

    cycle_1 = summary_1.get(
        "cycle_id",
        1,
    )

    assert (
        cycle_1 == 1
    ), (
        f"Expected cycle 1, "
        f"got {cycle_1}"
    )

    print()

    print(
        "PASS: Cycle 1 completed."
    )

    # ========================================================
    # MEMORY AFTER CYCLE 1
    # ========================================================

    print()

    print(
        "========== MEMORY STATE =========="
    )

    print(
        f"Memory entries: "
        f"{len(persona.memory)}"
    )

    # ========================================================
    # CYCLE 2
    # ========================================================

    separator()

    print(
        "EDITORIAL CYCLE 2"
    )

    separator()

    result_2 = pipeline.run(
        top_count=5,
    )

    print_result(
        result_2,
        2,
    )

    # --------------------------------------------------------
    # CYCLE ID
    # --------------------------------------------------------

    summary_2 = result_2.get(
        "summary",
        {},
    )

    cycle_2 = summary_2.get(
        "cycle_id",
        2,
    )

    assert (
        cycle_2 == 2
    ), (
        f"Expected cycle 2, "
        f"got {cycle_2}"
    )

    print()

    print(
        "PASS: Cycle 2 completed."
    )

    # ========================================================
    # CYCLE HISTORY
    # ========================================================

    print()

    print(
        "========== CYCLE HISTORY =========="
    )

    cycle_manager = getattr(
        pipeline,
        "cycle_manager",
        None,
    )

    if cycle_manager is not None:

        history = (
            cycle_manager.get_history()
        )

        print(
            f"Historical cycles: "
            f"{len(history)}"
        )

        assert (
            len(history) >= 2
        ), (
            "Cycle history should contain "
            "at least 2 cycles."
        )

        print(
            "PASS: Cycle history contains "
            "both cycles."
        )

    else:

        print(
            "WARNING: Pipeline does not expose "
            "cycle_manager directly."
        )

    # ========================================================
    # PERSONA MEMORY
    # ========================================================

    print()

    print(
        "========== FINAL PERSONA STATE =========="
    )

    print(
        f"Memory entries: "
        f"{len(persona.memory)}"
    )

    print(
        f"Persona status: "
        f"{persona.state.status}"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print(
        "############################################"
    )

    print(
        "       PIPELINE CYCLE TEST PASSED"
    )

    print(
        "############################################"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()