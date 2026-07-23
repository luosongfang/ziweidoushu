import axios from "axios";
import { getAuthHeaders } from "@/lib/auth/authService";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface GrowthContext {
  continuity_message: string;
  growth_goals: string[];
  focus_topics: string[];
  important_topics?: string[];
  recent_questions: string[];
  summary?: string;
  career_focus?: string | null;
  growth_notes?: string | null;
}

export interface HistoryRecord {
  id: string;
  question: string;
  analysis_type?: string | null;
  topic: string;
  summary?: string;
  suggestions: string[];
  created_at: string;
}

async function authedClient() {
  const headers = await getAuthHeaders();
  return axios.create({
    baseURL: API_BASE,
    headers: { "Content-Type": "application/json", ...headers },
    timeout: 30000,
  });
}

/** 导师页 — 加载 advisor_continuity_context */
export async function getGrowthContext(): Promise<GrowthContext | null> {
  try {
    const client = await authedClient();
    const response = await client.get<GrowthContext>("/api/v1/memory/context");
    return response.data;
  } catch {
    try {
      const client = await authedClient();
      const fallback = await client.get<GrowthContext>("/api/user/growth-context");
      return fallback.data;
    } catch {
      return null;
    }
  }
}

export async function getAnalysisHistory(): Promise<HistoryRecord[]> {
  try {
    const client = await authedClient();
    const response = await client.get<HistoryRecord[]>("/api/user/history");
    return response.data.map((r) => ({
      ...r,
      topic: r.topic || r.analysis_type || "分析",
      suggestions: r.summary ? [r.summary] : r.suggestions || [],
    }));
  } catch {
    return [];
  }
}
