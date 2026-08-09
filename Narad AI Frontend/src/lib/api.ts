/**
 * API Abstraction Layer
 *
 * All backend communication goes through this module.
 * Next.js rewrites /api/agent/* to the backend in development.
 */

import type {
  AgentStatusResponse,
  CandidatesResponse,
  CyclesResponse,
  FeedResponse,
  MemoryResponse,
  NewsLatestResponse,
  NewsSourcesResponse,
  OnboardingData,
} from "./types";

// ── Configuration ────────────────────────────────────────────────────────────

// In development, Next.js rewrites /api/agent/* to the backend (avoids CORS).
const API_BASE = "";

// ── Agent ────────────────────────────────────────────────────────────────────

export async function initializeAgent(
  data: OnboardingData
): Promise<{ agentId: string }> {
  const res = await fetch(`${API_BASE}/api/agent/init`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      persona: {
        name: data.name,
        domain: data.domain,
        bio: data.bio,
        editorialStyle: data.tone,
      },
      topics: data.topics,
      frequency: data.frequency,
    }),
  });

  if (!res.ok) throw new Error("Failed to initialize agent");
  return res.json();
}

// ── Status ───────────────────────────────────────────────────────────────────

export async function getStatus(agentId: string): Promise<AgentStatusResponse> {
  const res = await fetch(`${API_BASE}/api/agent/status?agentId=${agentId}`);
  if (!res.ok) throw new Error("Failed to fetch status");
  return res.json();
}

// ── Feed ─────────────────────────────────────────────────────────────────────

export async function getFeed(agentId?: string): Promise<FeedResponse> {
  const params = agentId ? `?agentId=${agentId}` : "";
  const res = await fetch(`${API_BASE}/api/agent/feed${params}`);
  if (!res.ok) throw new Error("Failed to fetch feed");
  return res.json();
}

// ── Candidates ───────────────────────────────────────────────────────────────

export async function getCandidates(
  agentId: string,
  activeOnly = true
): Promise<CandidatesResponse> {
  const res = await fetch(
    `${API_BASE}/api/agent/candidates?agentId=${agentId}&activeOnly=${activeOnly}`
  );
  if (!res.ok) throw new Error("Failed to fetch candidates");
  return res.json();
}

// ── Cycles ───────────────────────────────────────────────────────────────────

export async function getCycles(agentId: string): Promise<CyclesResponse> {
  const res = await fetch(`${API_BASE}/api/agent/cycles?agentId=${agentId}`);
  if (!res.ok) throw new Error("Failed to fetch cycles");
  return res.json();
}

// ── Memory ───────────────────────────────────────────────────────────────────

export async function getMemory(agentId: string): Promise<MemoryResponse> {
  const res = await fetch(`${API_BASE}/api/agent/memory?agentId=${agentId}`);
  if (!res.ok) throw new Error("Failed to fetch memory");
  return res.json();
}

// ── News Sources ─────────────────────────────────────────────────────────────

export async function getNewsSources(): Promise<NewsSourcesResponse> {
  const res = await fetch(`${API_BASE}/api/agent/news/sources`);
  if (!res.ok) throw new Error("Failed to fetch news sources");
  return res.json();
}

// ── News Latest ──────────────────────────────────────────────────────────────

export async function getNewsLatest(limit = 10): Promise<NewsLatestResponse> {
  const res = await fetch(`${API_BASE}/api/agent/news/latest?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch latest news");
  return res.json();
}

export async function refreshNews(limit = 10): Promise<NewsLatestResponse> {
  const res = await fetch(
    `${API_BASE}/api/agent/news/refresh?limit=${limit}`,
    { method: "POST" }
  );
  if (!res.ok) throw new Error("Failed to refresh news");
  return res.json();
}
