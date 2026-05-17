import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { api } from "../api/client";
import { useAlertWebSocket } from "../hooks/useWebSocket";

interface DriftEvent {
  account_id: string;
  score_before: number;
  score_after: number;
  timestamp: string;
}

interface ChartPoint {
  time: string;
  score: number;
  isDrift: boolean;
  account_id: string;
}

function toPoint(e: DriftEvent): ChartPoint {
  return {
    time: new Date(e.timestamp).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    score: Math.round(e.score_after * 100),
    isDrift: Math.abs(e.score_after - e.score_before) > 0.15,
    account_id: e.account_id,
  };
}

const CustomDot = (props: any) => {
  const { cx, cy, payload } = props;
  if (!payload?.isDrift) return null;
  return (
    <circle
      cx={cx}
      cy={cy}
      r={5}
      fill="#e74c3c"
      stroke="#e74c3c"
      strokeWidth={2}
      style={{ filter: "drop-shadow(0 0 6px #e74c3c)" }}
    />
  );
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as ChartPoint;
  return (
    <div
      style={{
        background: "#0e1117",
        border: "1px solid #2a1e0e",
        borderRadius: 6,
        padding: "6px 10px",
        fontSize: 11,
      }}
    >
      <div style={{ color: "#6b7280" }}>{d.time}</div>
      <div style={{ color: "#d1d5db", fontFamily: "monospace" }}>{d.account_id}</div>
      <div style={{ color: d.isDrift ? "#e74c3c" : "#f97316", fontWeight: 700 }}>
        Score: {d.score}%{d.isDrift ? " ⚠ DRIFT" : ""}
      </div>
    </div>
  );
};

export default function DriftTimeline() {
  const [points, setPoints] = useState<ChartPoint[]>([]);
  const [injecting, setInjecting] = useState(false);
  const [lastInjected, setLastInjected] = useState<string | null>(null);
  const { driftEvents } = useAlertWebSocket();

  useEffect(() => {
    api
      .get<DriftEvent[]>("/alerts/drift-events")
      .then((r) => {
        const initial = (r.data ?? []).slice(-30).map(toPoint);
        setPoints(initial);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (driftEvents.length === 0) return;
    const latest = driftEvents[0];
    if (!latest.account_id) return;
    const p: ChartPoint = {
      time: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      score: Math.round((latest.score ?? 0.5) * 100),
      isDrift: (latest.score ?? 0) > 0.7,
      account_id: latest.account_id,
    };
    setPoints((prev) => [...prev.slice(-49), p]);
  }, [driftEvents]);

  const injectPattern = async () => {
    setInjecting(true);
    try {
      await fetch("/demo/inject-pattern", { method: "POST" });
      setLastInjected(new Date().toLocaleTimeString("en-IN"));
    } finally {
      setInjecting(false);
    }
  };

  const driftCount = points.filter((p) => p.isDrift).length;

  return (
    <div
      style={{
        background: "#0e1117",
        border: "1px solid #1c1f2a",
        borderRadius: 10,
        padding: "12px 14px",
        display: "flex",
        flexDirection: "column",
        gap: 10,
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 14 }}>📡</span>
          <span style={{ fontWeight: 700, fontSize: 13, letterSpacing: 0.3 }}>Live Concept Drift</span>
          {driftCount > 0 && (
            <span
              style={{
                fontSize: 10,
                background: "#2d0f0f",
                color: "#e74c3c",
                border: "1px solid #7f1d1d",
                borderRadius: 10,
                padding: "1px 7px",
                fontWeight: 700,
              }}
            >
              {driftCount} drift{driftCount !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {lastInjected && (
            <span style={{ fontSize: 10, color: "#4b5563" }}>injected {lastInjected}</span>
          )}
          <button
            onClick={injectPattern}
            disabled={injecting}
            style={{
              padding: "4px 12px",
              background: injecting ? "#1c1f2a" : "#2d1f00",
              border: `1px solid ${injecting ? "#2a1e0e" : "#a05c00"}`,
              borderRadius: 6,
              color: injecting ? "#555" : "#f59e0b",
              cursor: injecting ? "not-allowed" : "pointer",
              fontSize: 11,
              fontWeight: 600,
              transition: "all 0.2s",
              whiteSpace: "nowrap",
            }}
          >
            {injecting ? (
              <span style={{ animation: "spin 1s linear infinite", display: "inline-block" }}>⟳</span>
            ) : (
              "⚡ Inject Pattern"
            )}
          </button>
        </div>
      </div>

      {/* Chart */}
      <div style={{ height: 120 }}>
        {points.length === 0 ? (
          <div
            style={{
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#374151",
              fontSize: 12,
            }}
          >
            Waiting for River ADWIN events…
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={points} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
              <defs>
                <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="time"
                tick={{ fontSize: 9, fill: "#374151" }}
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 9, fill: "#374151" }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={70} stroke="#e74c3c" strokeDasharray="3 3" strokeOpacity={0.4} />
              <Area
                type="monotone"
                dataKey="score"
                stroke="#f97316"
                strokeWidth={1.5}
                fill="url(#scoreGrad)"
                dot={<CustomDot />}
                activeDot={{ r: 4, fill: "#f97316" }}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Legend */}
      <div style={{ display: "flex", gap: 14, fontSize: 10, color: "#374151" }}>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span
            style={{
              width: 8,
              height: 2,
              background: "#f97316",
              display: "inline-block",
              borderRadius: 2,
            }}
          />
          River HST score
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span
            style={{
              width: 8,
              height: 2,
              background: "#e74c3c",
              display: "inline-block",
              borderRadius: 2,
              opacity: 0.5,
            }}
          />
          ADWIN threshold (70%)
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span
            style={{
              width: 8,
              height: 8,
              background: "#e74c3c",
              display: "inline-block",
              borderRadius: "50%",
            }}
          />
          Drift detected
        </span>
      </div>
    </div>
  );
}
