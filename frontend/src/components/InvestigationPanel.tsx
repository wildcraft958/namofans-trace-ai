import { useState } from "react";
import { api } from "../api/client";

interface InvestigateResult {
  summary: string;
  result_nodes: string[];
  result_edges: { source: string; target: string; amount: number; channel: string }[];
  latency_ms: number;
  handler: string;
}

const SUGGESTED_QUERIES = [
  "Show circular flows above ₹5L",
  "Find dormant accounts with recent activity",
  "Show fund trail for high KYC risk transfers above ₹10L",
  "Top 10 accounts by network centrality",
  "Find velocity spikes in last 7 days",
  "Mule accounts with high fan-in fan-out",
];

interface Props {
  onSubgraphFocus?: (accountIds: string[]) => void;
}

export default function InvestigationPanel({ onSubgraphFocus }: Props) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<InvestigateResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await api.post<InvestigateResult>("/investigate", { query: q });
      setResult(r.data);
      if (r.data.result_nodes?.length > 0) {
        onSubgraphFocus?.(r.data.result_nodes);
      }
    } catch {
      setError("Investigation failed — check backend connection");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        background: "#0e1117",
        border: "1px solid #1c1f2a",
        borderRadius: 10,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        height: "100%",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "10px 14px",
          borderBottom: "1px solid #1c1f2a",
          display: "flex",
          alignItems: "center",
          gap: 8,
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: 15 }}>🔍</span>
        <span style={{ fontWeight: 700, fontSize: 13, letterSpacing: 0.3 }}>NL Investigation Copilot</span>
        <span
          style={{
            marginLeft: "auto",
            fontSize: 10,
            background: "#1a2a1a",
            color: "#4ade80",
            border: "1px solid #2d4a2d",
            borderRadius: 10,
            padding: "2px 8px",
          }}
        >
          Gemini-powered
        </span>
      </div>

      <div
        style={{
          flex: 1,
          overflow: "auto",
          padding: "12px 14px",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        {/* Input */}
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run(query)}
            placeholder='e.g. "Show circular flows above ₹5L"'
            style={{
              flex: 1,
              background: "#151922",
              border: "1px solid #2d3250",
              borderRadius: 8,
              padding: "8px 12px",
              color: "#d1d5db",
              fontSize: 12,
              outline: "none",
              fontFamily: "inherit",
            }}
          />
          <button
            onClick={() => run(query)}
            disabled={loading || !query.trim()}
            style={{
              padding: "8px 14px",
              background: loading ? "#1c1f2a" : "#1a3060",
              border: "1px solid #2a4a8c",
              borderRadius: 8,
              color: loading ? "#555" : "#7aa2ff",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: 12,
              fontWeight: 600,
              whiteSpace: "nowrap",
              transition: "all 0.2s",
            }}
          >
            {loading ? (
              <span style={{ animation: "spin 1s linear infinite", display: "inline-block" }}>⟳</span>
            ) : (
              "Run →"
            )}
          </button>
        </div>

        {/* Suggested queries */}
        {!result && !loading && (
          <div>
            <div
              style={{
                fontSize: 10,
                color: "#374151",
                marginBottom: 6,
                textTransform: "uppercase",
                letterSpacing: 0.8,
              }}
            >
              Suggested queries
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
              {SUGGESTED_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => {
                    setQuery(q);
                    run(q);
                  }}
                  style={{
                    fontSize: 10,
                    padding: "3px 9px",
                    background: "#11141d",
                    border: "1px solid #2d3250",
                    borderRadius: 20,
                    color: "#93c5fd",
                    cursor: "pointer",
                    transition: "all 0.15s",
                    fontFamily: "inherit",
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            style={{
              padding: "10px 12px",
              background: "#2d0f0f",
              border: "1px solid #7f1d1d",
              borderRadius: 8,
              color: "#fca5a5",
              fontSize: 12,
            }}
          >
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div
              style={{
                padding: "10px 12px",
                background: "#0d1420",
                border: "1px solid #1a2540",
                borderRadius: 8,
              }}
            >
              <div
                style={{
                  fontSize: 10,
                  color: "#374151",
                  marginBottom: 4,
                  textTransform: "uppercase",
                  letterSpacing: 0.8,
                }}
              >
                Analysis
              </div>
              <p style={{ margin: 0, fontSize: 12, color: "#d1d5db", lineHeight: 1.6 }}>
                {result.summary}
              </p>
            </div>

            <div style={{ display: "flex", gap: 8 }}>
              {[
                { label: "Accounts", value: result.result_nodes?.length ?? 0, color: "#7aa2ff" },
                { label: "Txns", value: result.result_edges?.length ?? 0, color: "#a78bfa" },
                { label: "Latency", value: `${result.latency_ms}ms`, color: "#4ade80" },
              ].map((s) => (
                <div
                  key={s.label}
                  style={{
                    flex: 1,
                    background: "#151922",
                    borderRadius: 8,
                    padding: "6px 8px",
                    textAlign: "center",
                    border: "1px solid #1c1f2a",
                  }}
                >
                  <div style={{ fontSize: 16, fontWeight: 700, color: s.color }}>{s.value}</div>
                  <div
                    style={{
                      fontSize: 9,
                      color: "#4b5563",
                      textTransform: "uppercase",
                      letterSpacing: 0.5,
                    }}
                  >
                    {s.label}
                  </div>
                </div>
              ))}
            </div>

            {result.result_nodes?.length > 0 && (
              <div>
                <div
                  style={{
                    fontSize: 10,
                    color: "#374151",
                    marginBottom: 5,
                    textTransform: "uppercase",
                    letterSpacing: 0.8,
                  }}
                >
                  Matched accounts{" "}
                  {result.result_nodes.length > 6 ? `(top 6 of ${result.result_nodes.length})` : ""}
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {result.result_nodes.slice(0, 6).map((id) => (
                    <span
                      key={id}
                      style={{
                        fontSize: 10,
                        padding: "2px 7px",
                        background: "#1c2030",
                        border: "1px solid #2d3250",
                        borderRadius: 5,
                        color: "#93c5fd",
                        fontFamily: "monospace",
                      }}
                    >
                      {id}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.result_edges?.length > 0 && (
              <div>
                <div
                  style={{
                    fontSize: 10,
                    color: "#374151",
                    marginBottom: 5,
                    textTransform: "uppercase",
                    letterSpacing: 0.8,
                  }}
                >
                  Key transactions
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                  {result.result_edges.slice(0, 4).map((e, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "4px 8px",
                        background: "#151922",
                        borderRadius: 5,
                        fontSize: 10,
                      }}
                    >
                      <span style={{ color: "#9ca3af", fontFamily: "monospace" }}>
                        {e.source} → {e.target}
                      </span>
                      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        <span style={{ color: "#6b7280" }}>{e.channel}</span>
                        <span style={{ color: "#7aa2ff", fontWeight: 600 }}>
                          ₹{Number(e.amount).toLocaleString("en-IN")}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => {
                setResult(null);
                setQuery("");
              }}
              style={{
                alignSelf: "flex-start",
                padding: "4px 10px",
                background: "#1c1f2a",
                border: "1px solid #2d3250",
                borderRadius: 5,
                color: "#6b7280",
                cursor: "pointer",
                fontSize: 10,
                fontFamily: "inherit",
              }}
            >
              ← New query
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
