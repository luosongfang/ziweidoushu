import axios from "axios";
import { getAuthHeaders } from "@/lib/auth/authService";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ReportSection {
  identity?: {
    chart_summary?: string;
    traditional_basis?: string;
    modern_interpretation?: string;
  };
  personality?: {
    strengths?: string[];
    challenges?: string[];
    growth_direction?: string[];
  };
  career?: {
    traditional_view?: string;
    advantages?: string[];
    development_advice?: string[];
  };
  wealth?: {
    resource_pattern?: string;
    risk_awareness?: string;
    growth_advice?: string;
  };
  relationship?: {
    interaction_style?: string;
    growth_advice?: string;
  };
  life_cycle?: {
    current_stage?: string;
    focus?: string;
    advice?: string;
  };
  advisor_message?: string;
}

export interface ReportDetail {
  report_id?: string;
  id?: string;
  summary: string;
  report_sections: ReportSection;
  knowledge_trace?: Record<string, unknown>;
  safety_notice?: string;
  sources?: Array<Record<string, unknown>>;
}

async function authedClient(timeout = 180_000) {
  const headers = await getAuthHeaders();
  return axios.create({
    baseURL: API_BASE,
    headers: { "Content-Type": "application/json", ...headers },
    timeout,
  });
}

export async function createReport(
  chartId: string,
  reportType = "life_profile",
): Promise<ReportDetail | null> {
  try {
    const client = await authedClient();
    const response = await client.post<ReportDetail>("/api/v1/report/create", {
      chart_id: chartId,
      report_type: reportType,
    });
    return response.data;
  } catch {
    return null;
  }
}

export async function getReport(reportId: string): Promise<ReportDetail | null> {
  try {
    const client = await authedClient(30000);
    const response = await client.get<ReportDetail>(`/api/v1/report/${reportId}`);
    return response.data;
  } catch {
    return null;
  }
}

export async function listReports(): Promise<
  Array<{ id: string; summary: string; report_type: string; created_at: string }>
> {
  try {
    const client = await authedClient(30000);
    const response = await client.get("/api/v1/report/list");
    return response.data;
  } catch {
    return [];
  }
}

export async function submitReportFeedback(
  reportId: string,
  helpful: boolean,
  comment = "",
): Promise<boolean> {
  try {
    const client = await authedClient(30000);
    await client.post("/api/v1/report/feedback", {
      report_id: reportId,
      helpful,
      comment,
    });
    return true;
  } catch {
    return false;
  }
}

export async function getGrowthProfile(): Promise<{
  history: Array<Record<string, unknown>>;
  focus_topics: string[];
  goals: Array<Record<string, unknown>>;
  advisor_suggestions: string[];
  continuity_message: string;
} | null> {
  try {
    const client = await authedClient(30000);
    const response = await client.get("/api/v1/growth/profile");
    return response.data;
  } catch {
    return null;
  }
}

export async function getKnowledgeHealth(): Promise<Record<string, unknown> | null> {
  try {
    const client = await authedClient(15000);
    const response = await client.get("/api/v1/system/knowledge-health");
    return response.data;
  } catch {
    return null;
  }
}
