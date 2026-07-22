"use client";

import { useState } from "react";
import { Loader2, MapPin, User, Calendar, Clock } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createChart, ApiError } from "@/lib/api";
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
  const [form, setForm] = useState<BirthFormData>(DEFAULT_VALUES);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = <K extends keyof BirthFormData>(key: K, value: BirthFormData[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("请输入姓名");
      return;
    }
    if (form.calendarType === "lunar") {
      setError("农历输入即将上线，请暂时使用公历日期");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await createChart({
        name: form.name.trim(),
        gender: form.gender,
        solar_date: form.date,
        time: form.time,
        location: form.location || undefined,
      });
      onSuccess(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "排盘失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mx-auto max-w-lg border-purple-glow/20">
      <CardHeader>
        <CardTitle className="text-gradient-gold">出生信息</CardTitle>
        <CardDescription>填写资料后，将调用 Phase 2 排盘引擎实时计算命盘</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* 历法切换 */}
          <div className="flex rounded-xl border border-white/10 p-1">
            {(["solar", "lunar"] as const).map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => update("calendarType", type)}
                className={cn(
                  "flex-1 rounded-lg py-2 text-sm transition-all",
                  form.calendarType === type
                    ? "bg-purple-glow/30 text-white"
                    : "text-white/40 hover:text-white/70",
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
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                正在排盘…
              </>
            ) : (
              "生成紫微命盘"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
