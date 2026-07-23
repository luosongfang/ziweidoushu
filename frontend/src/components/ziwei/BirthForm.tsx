"use client";

import { useRef, useState } from "react";
import { MapPin, User, Calendar, Clock } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import AnalysisLoading from "@/components/AnalysisLoading";
import { createChart, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { BirthFormData, ChartCreateResponse } from "@/types/ziwei";
import { cn } from "@/lib/utils";

interface BirthFormProps {
  onSuccess: (data: ChartCreateResponse) => void;
}

const DEFAULT_VALUES: BirthFormData = {
  name: "",
  gender: "male",
  calendarType: "solar",
  date: "1990-05-20",
  time: "14:30",
  location: "北京",
};

export default function BirthForm({ onSuccess }: BirthFormProps) {
  const { user, isAuthenticated } = useAuth();
  const [form, setForm] = useState<BirthFormData>(DEFAULT_VALUES);
  const [loading, setLoading] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [pendingData, setPendingData] = useState<ChartCreateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const completedRef = useRef(false);

  const update = <K extends keyof BirthFormData>(key: K, value: BirthFormData[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.calendarType === "lunar") {
      setError("农历输入即将上线，请暂时使用公历日期");
      return;
    }

    setLoading(true);
    setShowOverlay(true);
    setError(null);
    setPendingData(null);

    try {
      const data = await createChart({
        name: form.name.trim() || "访客",
        gender: form.gender,
        solar_date: form.date,
        time: form.time,
        location: form.location || undefined,
        persist: true,
        user_id: isAuthenticated ? user?.id : undefined,
      });
      setPendingData(data);
    } catch (err) {
      setShowOverlay(false);
      setError(err instanceof ApiError ? err.message : "排盘失败，请稍后重试");
      setLoading(false);
    }
  };

  const handleLoadingComplete = () => {
    if (completedRef.current || !pendingData) return;
    completedRef.current = true;
    onSuccess(pendingData);
    setLoading(false);
    setShowOverlay(false);
  };

  return (
    <>
      {showOverlay && (
        <AnalysisLoading ready={!!pendingData} onComplete={handleLoadingComplete} />
      )}

      <Card className="mx-auto max-w-lg border-paper/10 bg-ink-soft/80">
        <CardHeader>
          <CardTitle className="text-gold-light">出生信息</CardTitle>
          <CardDescription className="text-paper/45">
            出生信息仅用于生成个人分析，不会用于其他用途。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="flex rounded-xl border border-white/10 p-1">
              {(["solar", "lunar"] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => update("calendarType", type)}
                  className={cn(
                    "flex-1 rounded-lg py-2 text-sm transition-all",
                    form.calendarType === type
                      ? "bg-gold/20 text-gold-light"
                      : "text-paper/40 hover:text-paper/70",
                  )}
                >
                  {type === "solar" ? "公历" : "农历"}
                </button>
              ))}
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">
                <User className="mr-1 inline h-3.5 w-3.5" />
                姓名
              </Label>
              <Input
                id="name"
                placeholder="请输入姓名"
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>性别</Label>
              <div className="flex gap-3">
                {(["male", "female"] as const).map((g) => (
                  <button
                    key={g}
                    type="button"
                    onClick={() => update("gender", g)}
                    className={cn(
                      "flex-1 rounded-xl border py-2.5 text-sm transition-all",
                      form.gender === g
                        ? "border-gold/40 bg-gold/10 text-gold-light"
                        : "border-white/10 text-white/50 hover:border-white/20",
                    )}
                  >
                    {g === "male" ? "男" : "女"}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="date">
                  <Calendar className="mr-1 inline h-3.5 w-3.5" />
                  出生日期
                </Label>
                <Input
                  id="date"
                  type="date"
                  value={form.date}
                  onChange={(e) => update("date", e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="time">
                  <Clock className="mr-1 inline h-3.5 w-3.5" />
                  出生时间
                </Label>
                <Input
                  id="time"
                  type="time"
                  value={form.time}
                  onChange={(e) => update("time", e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">
                <MapPin className="mr-1 inline h-3.5 w-3.5" />
                出生地点
              </Label>
              <Input
                id="location"
                placeholder="如：北京、上海、深圳"
                value={form.location}
                onChange={(e) => update("location", e.target.value)}
              />
            </div>

            {error && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {error}
              </div>
            )}

            <Button type="submit" variant="gold" size="lg" className="w-full" disabled={loading}>
              生成我的星盘
            </Button>
          </form>
        </CardContent>
      </Card>
    </>
  );
}
