import axios from "axios";
import { getAuthHeaders } from "@/lib/auth/authService";
import type { PlanId } from "@/context/MembershipContext";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface MembershipStatus {
  plan_id: PlanId;
  plan_label?: string;
  points: number;
  analysis_used: number;
  analysis_quota: number;
  advisor_enabled: boolean;
}

export interface PointsConsumeResult {
  success: boolean;
  balance: number;
  message?: string;
}

async function authedClient() {
  const headers = await getAuthHeaders();
  return axios.create({
    baseURL: API_BASE,
    headers: { "Content-Type": "application/json", ...headers },
    timeout: 30000,
  });
}

export async function setMembershipPreview(planId: PlanId): Promise<MembershipStatus | null> {
  try {
    const client = await authedClient();
    const response = await client.post<MembershipStatus>("/api/user/membership/preview", {
      plan_id: planId,
    });
    return response.data;
  } catch {
    return null;
  }
}

export async function getMembership(): Promise<MembershipStatus | null> {
  try {
    const client = await authedClient();
    const response = await client.get<MembershipStatus>("/api/user/membership");
    return response.data;
  } catch {
    return null;
  }
}

export async function getPoints(): Promise<number> {
  const status = await getMembership();
  return status?.points ?? 0;
}

export async function consumePoints(amount = 2, reason = "advisor_chat"): Promise<PointsConsumeResult> {
  try {
    const client = await authedClient();
    const response = await client.post<PointsConsumeResult>("/api/user/points/consume", {
      amount,
      reason,
    });
    return response.data;
  } catch {
    return { success: false, balance: 0, message: "积分扣减失败" };
  }
}
