import type { HistoryRecord } from "@/services/growthService";

const STORAGE_PREFIX = "ziwei-analysis-history";

export function saveLocalAnalysisHistory(
  userId: string | null,
  entry: Omit<HistoryRecord, "id" | "created_at" | "suggestions"> & {
    id?: string;
    suggestions?: string[];
    question_type?: string | null;
  },
) {
  if (typeof window === "undefined") return;
  const key = `${STORAGE_PREFIX}-${userId || "guest"}`;
  const record: HistoryRecord = {
    id: entry.id || crypto.randomUUID(),
    question: entry.question,
    analysis_type: entry.analysis_type ?? entry.question_type,
    topic: entry.topic,
    summary: entry.summary,
    suggestions: entry.suggestions ?? [],
    created_at: new Date().toISOString(),
  };
  try {
    const existing = loadLocalAnalysisHistory(userId);
    const next = [record, ...existing].slice(0, 50);
    localStorage.setItem(key, JSON.stringify(next));
  } catch {
    /* ignore */
  }
}

export function loadLocalAnalysisHistory(userId?: string | null): HistoryRecord[] {
  if (typeof window === "undefined") return [];
  const key = `${STORAGE_PREFIX}-${userId || "guest"}`;
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as HistoryRecord[]) : [];
  } catch {
    return [];
  }
}
