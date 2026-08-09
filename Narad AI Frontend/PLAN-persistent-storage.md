# Plan: Replace Database With Persistent File Storage

## Current State Analysis

### Backend (`Narad_AI_pipeline/`)
- **Already uses `JsonStore`** (`app/storage.py`) for atomic JSON persistence
- **Publisher** (`app/publishing/publisher.py`) persists posts + memory to `data/posts.json` and `data/memory.json`
- **PersonaEngine** (`app/agent/engine.py`) persists persona to file (optional)
- **CycleManager** (`app/cycle/manager.py`) — **in-memory only**, state lost on restart
- **Publication candidates** — **in-memory only**, lost on restart
- **Empty database directory** (`app/database/`) — `models.py` and `session.py` are empty files

### Frontend (`narad-ai/`)
- **All mock data** in `src/lib/mock-data.ts` (410 lines)
- **API layer** (`src/lib/api.ts`) has `USE_MOCK = true`, talks to `localhost:8000`
- **No real backend connection** currently active

### Data That Must Persist Across Restarts
1. **Posts** — already persisted via `JsonStore` ✅
2. **Memory** — already persisted via `JsonStore` ✅
3. **Persona** — persisted if `AUTONOMOUSAI_PERSONA_FILE` env var set ✅
4. **Cycle state** — NOT persisted ❌
5. **Publication candidates** — NOT persisted ❌
6. **Story clusters** — NOT persisted ❌

---

## Implementation Plan

### Step 1: Persist CycleManager State (Backend)

**File: `app/cycle/manager.py`**

Add `JsonStore` persistence for:
- `candidates` dict
- `story_clusters` dict
- `history` list
- `next_cycle_id`
- `posting_deadline`

Changes:
- Import `JsonStore` from `app.storage`
- Add `__init__` parameter `data_dir` (default: `Path(__file__).parents[2] / "data"`)
- Create `JsonStore` for `cycle_state.json`
- On `complete_cycle()`: write state to disk
- On `__init__`: load state from disk if exists
- On `start_cycle()`: load previous state if fresh start

Data directory: `Narad_AI_pipeline/data/cycle_state.json`

**State to persist:**
```json
{
  "next_cycle_id": 5,
  "posting_deadline": "2026-08-09T12:00:00Z",
  "candidates": { ... },
  "story_clusters": { ... },
  "history": [ ... ]
}
```

### Step 2: Clean Up Empty Database Directory (Backend)

**Delete:**
- `app/database/__init__.py`
- `app/database/models.py`
- `app/database/session.py`
- `app/database/` directory

**Reason:** These files are empty and unused. The project uses `JsonStore`, not SQLAlchemy/ORM.

### Step 3: Connect Frontend to Backend API

**File: `src/lib/api.ts`**

Change `USE_MOCK = false` so the frontend calls the real backend at `localhost:8000`.

**File: `src/lib/mock-data.ts`**

Keep as fallback but add a note that it's only used when backend is unavailable.

### Step 4: Add CORS for Next.js Dev Server (Backend)

**File: `app/main.py`**

Current CORS only allows `localhost:5173`. Add `localhost:3000` for Next.js:

```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Step 5: Add Missing API Endpoints (Backend)

**File: `app/api/routes.py`**

The frontend expects these endpoints that may be missing:

- `GET /api/agent/feed` — ✅ exists
- `GET /api/agent/memory` — ✅ exists
- `GET /api/agent/status` — ✅ exists
- `GET /api/agent/candidates` — ✅ exists
- `GET /api/agent/cycles` — ✅ exists

Check if any endpoints return data in the format the frontend expects. The frontend types expect:
- `Post.id`, `Post.createdAt`, `Post.title`, `Post.text`, `Post.rationale`, `Post.sources`, `Post.tags`, `Post.score`
- Backend returns: `id`, `createdAt`, `text`, `rationale`, `sources` (no `title`, `tags`, `score`)

**Fix: Enrich the `/feed` endpoint response** to include `title`, `tags`, `score` fields.

### Step 6: Add Persistence Test

Create a simple test script that:
1. Starts the backend
2. Runs a cycle
3. Restarts the backend
4. Verifies data survives

---

## Files to Modify

| File | Change |
|------|--------|
| `app/cycle/manager.py` | Add `JsonStore` persistence for cycle state, candidates, clusters |
| `app/database/` (3 files) | Delete empty directory |
| `app/main.py` | Add `localhost:3000` to CORS |
| `app/api/routes.py` | Enrich `/feed` response with `title`, `tags`, `score` |
| `src/lib/api.ts` | Set `USE_MOCK = false` |

## Files to Create

| File | Purpose |
|------|---------|
| `data/` directory | Auto-created by `JsonStore` |
| `data/cycle_state.json` | Persisted cycle state |
| `data/posts.json` | Already exists (publisher) |
| `data/memory.json` | Already exists (publisher) |

## No Changes To

- Frontend components
- Frontend types
- Frontend routing
- `mock-data.ts` (keep as fallback)
- Pipeline logic
- Evaluation/ranking logic
- Verification logic

---

## Verification

1. Start backend: `cd Narad_AI_pipeline && python -m app.main`
2. Run a cycle via API: `POST /api/agent/run-cycle`
3. Check `data/cycle_state.json` exists and has state
4. Restart backend
5. Check state is restored: `GET /api/agent/status`
6. Start frontend: `cd narad-ai && npm run dev`
7. Frontend should show real data from backend
8. Feed page should show posts with title, tags, score
