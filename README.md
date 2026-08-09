<div align="center">

# Narad AI

### An autonomous AI editorial persona that discovers, verifies, scores, and publishes tech news — with zero human prompts after launch.

*Built for a 44-hour hackathon window. No fake autonomy, no prewritten posts, no manual "generate" button.*

</div>

---

## 🧭 What This Is

Narad AI is a two-part system:

- **`Narad_AI_pipeline/`** — the backend. A story-centric autonomous editorial engine (FastAPI + Python) that collects live news, verifies it, clusters related coverage, scores it against a persona's interests, and decides what's worth publishing — on its own, on a recurring cycle.
- **`narad-ai/`** — the frontend. A Next.js dashboard (dark, purple-accented, "premium AI creator" aesthetic) that shows the whole editorial process happening in real time: what's being discovered, what's getting rejected and why, what the agent remembers, and what it has published.

Once initialized, the agent needs nothing further from a human. It scans, judges, remembers, and publishes on its own schedule.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────┐
                    │   narad-ai (Frontend)    │
                    │  Next.js · Tailwind      │
                    │  Dashboard · Feed        │
                    │  Memory · Sources        │
                    └────────────┬─────────────┘
                                 │  HTTP (polling)
                                 ▼
                    ┌─────────────────────────┐
                    │ Narad_AI_pipeline (API)  │
                    │      FastAPI backend     │
                    └────────────┬─────────────┘
                                 │
   RSS Collection → Topic Registry → Enrichment (retry + cache)
        → Event Similarity / Clustering → Stage-1 Verification
        → Story Evidence Aggregation → Cross-Cycle Re-Verification
        → Editorial Evaluation (score breakdown) → Publication Policy
        → Ranking → Publisher → Persistent Feed + Persona Memory
```

The pipeline doesn't score a topic once and forget it. Active stories are **re-verified and re-evaluated every cycle** — confidence builds (or drops) as more evidence arrives, which is what lets a borderline topic get promoted later instead of being judged once and discarded.

---

## ✨ Core Capabilities

| Capability | How it works |
|---|---|
| **Live topic discovery** | RSS-based `NewsCollector` pulls from real tech/AI sources on every cycle |
| **Editorial judgment** | `EditorialEvaluator` scores each topic on interest, technical depth, reliability, freshness, memory overlap, and editorial fit — every rejection has a stated reason and a policy path |
| **Consistent persona voice** | `PersonaEngine` maintains one identity, tone, and interest set across every generated post |
| **Memory** | Published topics and persona learnings persist to disk (`data/memory.json`), so the agent never re-covers the same story from scratch |
| **Autonomous publishing loop** | `AutonomousScheduler` runs the full pipeline on an interval (default 30 min, configurable) — no manual trigger required after init |
| **Transparent rationale** | Every published post ships with *why it was selected, why now,* and its source URLs |
| **Candidate lifecycle** | Topics aren't binary accept/reject — they move through `ACTIVE → READY → PUBLISHED / EXPIRED / DROPPED`, so "still building confidence" is a visible state, not a black box |

---

## 📁 Project Structure

<details>
<summary><strong>Narad_AI_pipeline/</strong> (backend) — click to expand</summary>

```
Narad_AI_pipeline/
├── app/
│   ├── agent/
│   │   ├── engine.py         # PersonaEngine — identity, tone, interests
│   │   ├── evaluator.py       # EditorialEvaluator — scoring logic
│   │   ├── editorial.py       # Editorial rules / voice
│   │   ├── interests.py       # Persona interest matching
│   │   ├── learning.py        # Feedback / learning hooks
│   │   ├── memory.py          # Memory read/write
│   │   ├── models.py          # Core data models (Topic, Persona, etc.)
│   │   └── prompts.py         # LLM prompt templates
│   ├── api/
│   │   └── routes.py          # All /api/agent/* endpoints
│   ├── clustering/
│   │   ├── clusterer.py       # Story clustering
│   │   └── event_similarity.py
│   ├── cycle/
│   │   └── manager.py         # CycleManager — orchestrates each run
│   ├── discovery/
│   │   └── collector.py       # NewsCollector — RSS ingestion
│   ├── enrichment/
│   │   └── article_fetcher.py # Full-article fetch + retry/backoff
│   ├── publishing/
│   │   ├── policy.py          # Publication decision policy
│   │   └── publisher.py       # Writes posts + memory to disk
│   ├── ranking/
│   │   └── ranker.py          # TopicRanker
│   ├── scheduler/
│   │   └── scheduler.py       # AutonomousScheduler — the 30-min loop
│   ├── storage.py             # JsonStore — atomic JSON persistence
│   ├── pipeline.py            # EditorialPipeline — full cycle orchestration
│   └── main.py                # FastAPI app entrypoint
├── data/                       # Persisted posts.json, memory.json (created at runtime)
├── test_*.py                   # 20+ test files covering every stage
├── requirements.txt
├── run_windows.cmd
└── install_requirements.cmd
```

</details>

<details>
<summary><strong>narad-ai/</strong> (frontend) — click to expand</summary>

```
narad-ai/
├── src/
│   ├── app/
│   │   ├── page.tsx            # Entry — routes to onboarding or dashboard
│   │   ├── onboarding/          # 4-step persona setup wizard
│   │   ├── dashboard/           # Live agent console, timeline, summary
│   │   ├── feed/                # Published posts feed
│   │   ├── memory/              # Memory table + feed-matching
│   │   ├── intelligence/        # Editorial funnel, decisions, source stats
│   │   └── sources/              # Active sources + source events
│   ├── components/
│   │   ├── dashboard/            # LiveAgentConsole, AgentTimeline, DecisionTree, AIBrain
│   │   ├── feed/                 # FeedCard, FeedFilters
│   │   ├── intelligence/         # DiscoveryTrend, EditorialDecisions, IntelligenceStats
│   │   ├── memory/                # MemoryTable, MemoryMatch, MemoryStats
│   │   ├── onboarding/            # OnboardingWizard + 4 step components
│   │   ├── sources/                # ActiveSources, SourceEvents, SourceStats
│   │   ├── layout/                 # AppShell, Sidebar, SystemStatus
│   │   └── ui/                      # shadcn primitives + custom visual effects
│   └── lib/
│       ├── api.ts               # Backend API client
│       └── types.ts             # Shared TypeScript contract
├── public/
│   ├── Logo.png
│   └── Favicon.png
└── package.json
```

</details>

---

## 🔌 API Contract

All endpoints live under `/api/agent`. Base URL defaults to `http://localhost:8000`.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/init?agentId=` | Initialize the agent and start the autonomous loop (call once) |
| `POST` | `/stop?agentId=` | Stop the running scheduler |
| `POST` | `/run-cycle?agentId=&topCount=` | Manually trigger one cycle (for demos/debugging) |
| `GET` | `/status?agentId=` | Current agent state, running flag, last error, cycle summary |
| `GET` | `/feed?agentId=&limit=` | Published posts, reverse chronological |
| `GET` | `/candidates?agentId=&activeOnly=` | Live scoring/lifecycle state of in-flight topics |
| `GET` | `/cycles?agentId=` | History of completed cycles |
| `GET` | `/memory?agentId=` | Persona memory — covered topics, opinions, keywords |
| `GET` | `/news/sources` | Configured RSS sources |
| `GET` | `/news/latest` | Most recently discovered raw topics |
| `GET` | `/news/refresh` | Force a fresh discovery pass |

**Publication paths:** every accepted post reaches the feed via one of three evidence paths — `corroborated`, `primary_source`, or `trusted_single_source`. A posting deadline never overrides verification; a story that isn't ready doesn't get force-published just because time is running out.

---

## 🚀 Getting Started

### Backend

```bash
cd Narad_AI_pipeline
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Then initialize the agent once:

```bash
curl -X POST "http://127.0.0.1:8000/api/agent/init?agentId=default-agent"
```

Optional: shorten the cycle interval for faster demos (default is 30 minutes):

```bash
# CMD
set AUTONOMOUSAI_CYCLE_SECONDS=60
# PowerShell
$env:AUTONOMOUSAI_CYCLE_SECONDS="60"
```

### Frontend

```bash
cd narad-ai
npm install
npm run dev
```

Open **http://localhost:3000**.

> ⚠️ **CORS note:** the backend's default CORS allowlist includes `localhost:5173` (Vite's default port). If you're running the Next.js frontend on `localhost:3000`, make sure `app/main.py`'s `CORSMiddleware` origins include it, or requests from the dashboard will be silently blocked by the browser.

---

## 🧪 Running Tests

The pipeline ships with 20+ targeted test files covering each stage of the cycle:

```bash
cd Narad_AI_pipeline
python test_v5_source_identity.py
python test_v5_publication_policy.py
python test_v5_evaluation_breakdown.py
python test_v5_calibration.py
python test_candidate_lifecycle.py
python test_publication_flow.py
python test_cycle.py
python test_clusterer.py
```

RSS-dependent tests may return zero articles in a network-restricted environment — that's an environment condition, not a pipeline failure.

---

## 🛠️ Tech Stack

**Backend:** FastAPI · Uvicorn · feedparser · BeautifulSoup4 · Trafilatura · python-dotenv

**Frontend:** Next.js 16 · React 19 · Tailwind CSS 4 · shadcn/ui · Framer Motion · Recharts · Three.js / React Three Fiber (visual effects) · TypeScript

---

## 🗺️ Roadmap / Known Gaps

- Persona customization from the onboarding wizard (name, bio, domain, focus topics) is **not yet wired into the backend** — `/init` currently always creates a default persona regardless of what the frontend sends. Onboarding UI exists and is functional; the backend contract for accepting custom persona data is the next step.
- `CycleManager` state (candidates, clusters, cycle history) is currently in-memory only — a restart clears it. Persisting this to `JsonStore` alongside posts/memory is planned.
- Feed enrichment (`title`, `tags`, `score` on published posts) is being extended so the frontend's feed cards don't have to infer missing fields.

---

## 📜 Hackathon Compliance Notes

- No fake autonomy — the scheduler genuinely runs unattended; nothing is prewritten.
- Every published post carries a rationale and its sources, per the evaluator's contract.
- Rejected topics are tracked with a reason and a policy path, not silently dropped.
- Persona voice is enforced by a single `PersonaEngine` instance shared across the whole pipeline.

---

<div align="center">

**~Developed by Nadaan Parindey**

</div>
