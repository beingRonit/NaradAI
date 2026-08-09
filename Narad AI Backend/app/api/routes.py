"""FastAPI endpoints required by the hackathon contract."""
from __future__ import annotations

import os
from datetime import datetime, timezone , timedelta

from fastapi import APIRouter, HTTPException, Query

from app.agent.engine import PersonaEngine
from app.discovery.collector import NewsCollector
from app.pipeline import EditorialPipeline
from app.publishing.publisher import Publisher
from app.scheduler.scheduler import AutonomousScheduler

router = APIRouter(prefix="/api/agent", tags=["agent"])

_engine: PersonaEngine | None = None
_pipeline: EditorialPipeline | None = None
_publisher: Publisher | None = None
_scheduler: AutonomousScheduler | None = None
_agent_id: str = "default-agent"
_news_collector = NewsCollector()


def _topic_payload(topic):
    return {
        "id": topic.id,
        "title": topic.title,
        "summary": topic.summary,
        "url": topic.url,
        "source": topic.source,
        "author": topic.author,
        "category": topic.category,
        "tags": topic.tags,
        "publishedAt": topic.published_at,
        "discoveredAt": topic.discovered_at,
        "enrichment": {
            "status": topic.enrichment_status,
            "attempts": topic.enrichment_attempts,
            "contentLength": len(topic.content or ""),
            "enrichedContentLength": topic.enriched_content_length,
            "error": topic.enrichment_error,
        },
    }


def get_runtime():
    return _engine, _pipeline, _publisher, _scheduler


def initialize_agent(agent_id: str = "default-agent"):
    global _engine, _pipeline, _publisher, _scheduler, _agent_id
    if _scheduler and _scheduler.running:
        return _engine, _pipeline, _publisher, _scheduler

    _agent_id = agent_id
    _engine = PersonaEngine(persistence_path=os.getenv("AUTONOMOUSAI_PERSONA_FILE"))
    _engine.ensure_default_persona()
    _publisher = Publisher(agent_id=agent_id)
    _publisher.load_memory(_engine.get_persona())

    interval = int(os.getenv("AUTONOMOUSAI_CYCLE_SECONDS", "1800"))
    enrich = os.getenv("AUTONOMOUSAI_ENRICH", "true").lower() not in {"0", "false", "no"}
    _pipeline = EditorialPipeline(
        persona_engine=_engine,
        publisher=_publisher,
        auto_publish=True,
       
    )
    _scheduler = AutonomousScheduler(_pipeline, interval_seconds=interval, enrich=enrich)
    _scheduler.start(run_immediately=True)
    return _engine, _pipeline, _publisher, _scheduler


@router.get("/news/sources")
def news_sources():
    """Return the live RSS sources configured for discovery."""
    return {
        "sources": [
            {"name": name, "url": url}
            for name, url in _news_collector.RSS_FEEDS.items()
        ]
    }


@router.get("/news/latest")
def latest_news(limit: int = Query(20, ge=1, le=50)):
    """Fetch the current live AI/technology RSS feed without starting the agent."""
    topics = _news_collector.collect()
    topics = topics[:limit]
    return {
        "count": len(topics),
        "topics": [_topic_payload(topic) for topic in topics],
        "collector": _news_collector.get_status(),
    }


@router.post("/news/refresh")
def refresh_news(limit: int = Query(20, ge=1, le=50)):
    """Force a fresh live RSS collection for diagnostics/frontend use."""
    topics = _news_collector.collect()
    return {
        "count": min(len(topics), limit),
        "topics": [_topic_payload(topic) for topic in topics[:limit]],
        "collector": _news_collector.get_status(),
    }


@router.post("/init")
def init_agent(agentId: str = Query("default-agent")):
    engine, pipeline, publisher, scheduler = initialize_agent(agentId)
    return {
        "agentId": agentId,
        "status": "running" if scheduler.running else "ready",
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "nextCycleSeconds": scheduler.interval_seconds,
        "memoryEntries": len(engine.get_persona().memory),
    }


@router.post("/stop")
def stop_agent(agentId: str = Query("default-agent")):
    global _scheduler
    if _scheduler is None or agentId != _agent_id:
        raise HTTPException(status_code=404, detail="Agent is not running")
    _scheduler.stop()
    return {"agentId": agentId, "status": "stopped"}

@router.post("/run-cycle")
def run_cycle(agentId: str = Query("default-agent"), topCount: int = Query(5, ge=1, le=50)):
    if _pipeline is None or agentId != _agent_id:
        raise HTTPException(status_code=409, detail="Agent must be initialized before running a manual cycle")
    try:
        result = _pipeline.run(top_count=topCount, enrich=True)
        published = result.get("published_post")
        return {
            "agentId": agentId,
            "cycle": result.get("cycle_id"),
            "summary": result.get("summary"),
            "published": ({
                "id": published.id,
                "createdAt": published.created_at,
                "topicId": published.topic_id,
                "clusterId": published.cluster_id,
                "text": published.text,
                "rationale": published.rationale,
                "sources": published.sources,
            } if published is not None else None),
            "discovery": _pipeline.collector.get_status(),
            "enrichment": _pipeline.fetcher.get_status(),
            "topResults": [
                {"topicId": r.topic_id, "title": r.topic_title, "score": r.overall_score, "publish": r.publish, "reason": r.reason}
                for r in result.get("top_results", [])
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/candidates")
def candidates(agentId: str = Query("default-agent"), activeOnly: bool = True):
    if _pipeline is None or agentId != _agent_id:
        initialize_agent(agentId)
    rows = _pipeline.get_candidates(active_only=activeOnly)
    return {"agentId": agentId, "candidates": [
        {
            "clusterId": c.cluster_id, "title": c.title, "status": c.status,
            "score": c.score, "reliability": c.reliability_score,
            "sources": c.independent_source_count, "corroboration": c.corroboration_score,
            "path": c.publication_path, "blockers": c.blocking_reasons,
        } for c in rows
    ]}

@router.get("/cycles")
def cycles(agentId: str = Query("default-agent")):
    if _pipeline is None or agentId != _agent_id:
        initialize_agent(agentId)
    history = _pipeline.cycle_manager.get_history()
    return {"agentId": agentId, "cycles": history}

@router.get("/memory")
def memory(agentId: str = Query("default-agent")):
    if _engine is None or agentId != _agent_id:
        initialize_agent(agentId)
    return {"agentId": agentId, "memory": [
        {"topic": m.topic, "opinion": m.opinion, "keywords": m.keywords, "companies": m.companies, "technologies": m.technologies}
        for m in _engine.get_persona().memory
    ]}

@router.get("/feed")
def feed(agentId: str = Query("default-agent"), limit: int = Query(50, ge=1, le=200)):
    if _publisher is None or agentId != _agent_id:
        initialize_agent(agentId)
    posts = _publisher.list_posts(limit=limit)
    return {
        "agentId": agentId,
        "posts": [
            {
                "id": p.id,
                "createdAt": p.created_at,
                "text": p.text,
                "rationale": p.rationale,
                "sources": p.sources,
            }
            for p in posts
        ],
    }


@router.get("/status")
def status(agentId: str = Query("default-agent")):
    if _pipeline is None or agentId != _agent_id:
        initialize_agent(agentId)
    engine, pipeline, publisher, scheduler = get_runtime()
    persona = engine.get_persona()
    return {
        "agentId": agentId,
        "running": scheduler.running,
        "lastError": scheduler.last_error,
        "cycle": pipeline.summary(),
        "memoryEntries": len(persona.memory),
        "posts": len(publisher.list_posts(limit=100000)),
    }
