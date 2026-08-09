// ── Agent ────────────────────────────────────────────────────────────────────

export interface Agent {
  agentId: string;
  name: string;
  domain: string;
  bio: string;
  editorialStyle: string;
  status: AgentStatus;
  createdAt: string;
}

export type AgentStatus =
  | "scanning"
  | "judging"
  | "checking_memory"
  | "writing"
  | "publishing"
  | "sleeping";

// ── Agent Status ─────────────────────────────────────────────────────────────

export interface AgentStatusResponse {
  agentId: string;
  running: boolean;
  lastError: string | null;
  memoryEntries: number;
  posts: number;
  cycle: {
    current_cycle: number;
    historical_cycles: number;
    persistent_clusters: number;
    posting_deadline: string;
    published: boolean;
    active_candidates: number;
    candidates: number;
  };
}

// ── Posts / Feed ─────────────────────────────────────────────────────────────

export interface Post {
  id: string;
  createdAt: string;
  text: string;
  rationale: string;
  sources: string | string[];
  title?: string;
  tags?: string[];
  score?: number;
}

export interface FeedResponse {
  agentId?: string;
  posts: Post[];
}

// ── Candidates ───────────────────────────────────────────────────────────────

export interface Candidate {
  clusterId: string;
  title: string;
  status: string;
  score: number | null;
  reliability: number;
  sources: number;
  corroboration: number;
  path: string;
  blockers: string[];
}

export interface CandidatesResponse {
  agentId: string;
  candidates: Candidate[];
}

// ── Cycles ───────────────────────────────────────────────────────────────────

export interface Cycle {
  cycle_id: number;
  started_at: string;
  last_cycle_at: string | null;
  discovered_topics: unknown[];
  [key: string]: unknown;
}

export interface CyclesResponse {
  agentId: string;
  cycles: Cycle[];
}

// ── Memory ───────────────────────────────────────────────────────────────────

export interface MemoryEntry {
  topic: string;
  opinion: string;
  keywords: string[];
  companies: string[];
  technologies: string[];
  memoryId?: string;
  summary?: string;
  source?: string;
  similarity?: number;
  decision?: string;
  isDuplicate?: boolean;
  postId?: string | null;
  similarPostTitle?: string | null;
  lastCoveredAt?: string;
  createdAt?: string;
}

export interface MemoryResponse {
  agentId: string;
  memory: MemoryEntry[];
}

// ── News Sources ─────────────────────────────────────────────────────────────

export interface NewsSource {
  name: string;
  url: string;
}

export interface NewsSourcesResponse {
  sources: NewsSource[];
}

// ── News Latest ──────────────────────────────────────────────────────────────

export interface NewsTopic {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  author: string;
  category: string;
  tags: string[];
  publishedAt: string;
  discoveredAt: string;
  enrichment: {
    status: string;
    attempts: number;
    contentLength: number;
    enrichedContentLength: number;
    error: string | null;
  };
}

export interface NewsLatestResponse {
  count: number;
  topics: NewsTopic[];
}

// ── Onboarding ───────────────────────────────────────────────────────────────

export interface OnboardingData {
  name: string;
  domain: string;
  bio: string;
  topics: string[];
  frequency: string;
  tone: string;
}
