# AutonomousAI Backend V5

V5 is the calibrated story-centric autonomous editorial backend.

## Pipeline

```text
RSS collection
    ↓
Persistent Topic registry
    ↓
Enrichment + retry backoff/cache
    ↓
Event similarity / provisional clustering
    ↓
Stage-1 verification
    ↓
Story evidence aggregation
    ↓
Cross-cycle story re-verification
    ↓
Editorial evaluation + score breakdown
    ↓
V5 publication policy
    ↓
Ranking
    ↓
Publisher
    ↓
Persistent feed + persona memory
```

## V5 changes

- Canonical source identity prevents duplicate reporting from being counted as independent corroboration.
- Independent-source corroboration uses diminishing returns.
- Official technology/company sources have a controlled primary-source publication path.
- Two or more independent sources can qualify a strong story without requiring a primary source.
- Final-hour publication policy remains evidence-aware; at the posting deadline, the highest-ranked eligible verified story can be selected as a fallback when no story passed the normal publication policy.
- Editorial evaluation exposes interest, technical, reliability, freshness, memory, editorial and overall scores.
- Every publication decision exposes blockers and the selected policy path.
- Enrichment success is cached; failed enrichment follows retry backoff instead of being retried every cycle.
- Active stories are re-verified and re-evaluated every cycle.
- Published clusters cannot be revived or republished.
- Persona default interests/rules are installed case-insensitively to avoid duplicate defaults.

## Development run (Windows CMD / PowerShell)

Run these commands from the folder that contains `app\main.py` and `requirements.txt`:

```cmd
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

For a 60-second development cycle in CMD:

```cmd
set AUTONOMOUSAI_CYCLE_SECONDS=60
python -m uvicorn app.main:app --reload
```

For PowerShell:

```powershell
$env:AUTONOMOUSAI_CYCLE_SECONDS="60"
python -m uvicorn app.main:app --reload
```

The default scheduler cadence is 30 minutes. The live-news endpoints do not start the agent.

Then initialize the agent:

```cmd
curl -X POST http://127.0.0.1:8000/api/agent/init -H "Content-Type: application/json" -d "{}"
```

Production/default scheduler cadence remains 30 minutes unless configured otherwise.

## Tests

Important V5 tests:

```cmd
python test_v5_source_identity.py
python test_v5_publication_policy.py
python test_v5_evaluation_breakdown.py
python test_v5_calibration.py
python test_v4_retry.py
python test_v4_story_evidence.py
python test_candidate_lifecycle.py
python test_publication_flow.py
python test_cycle.py
python test_clusterer.py
```

The RSS-dependent tests may return zero articles when the machine cannot reach external feeds. That is an environment/network condition, not an assertion that the pipeline logic failed.


## Final backend validation

Start with `uvicorn app.main:app --reload`. Initialize with `POST /api/agent/init`.
Useful endpoints: `/api/agent/status`, `/api/agent/feed`, `/api/agent/candidates`,
`/api/agent/cycles`, `/api/agent/memory`, `/api/agent/run-cycle`, `/api/agent/stop`.

The final publication policy has three evidence paths: `corroborated`, `primary_source`,
and `trusted_single_source`. At the posting deadline, if no story is policy-ready, the pipeline selects the highest-ranked story that still satisfies one of those evidence/editorial eligibility paths. A deadline never overrides verification.
