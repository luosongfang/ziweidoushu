/** Knowledge Core analyze API types — POST /api/v1/knowledge/analyze */

export interface KnowledgeAnalyzeRequest {
  chart_id?: string | null;
  question: string;
  user_context?: Record<string, unknown> | null;
  chart_data?: Record<string, unknown> | null;
  engine_version?: string;
  persist_memory?: boolean;
  persist_growth_memory?: boolean;
  user_id?: string | null;
}

export interface KnowledgeSourceItem {
  book?: string;
  page?: number | string;
  chapter?: string;
  type?: string;
  name?: string;
  category?: string;
  [key: string]: unknown;
}

export interface KnowledgeAnalyzeResponse {
  success: boolean;
  question_type?: string | null;
  engine_version?: string;
  traditional_analysis?: unknown;
  theory_used?: string[];
  sources?: KnowledgeSourceItem[];
  evidence?: Array<Record<string, unknown>>;
  advisor_analysis?: Record<string, unknown> | null;
  reasoning?: Array<Record<string, unknown>>;
  suggestions?: string[];
  safety_notice?: unknown;
  reflection_questions?: string[];
  decision_analysis?: Record<string, unknown> | null;
  knowledge_trace?: Record<string, unknown> | null;
  life_advisor?: Record<string, unknown> | null;
  error?: string | null;
  [key: string]: unknown;
}
