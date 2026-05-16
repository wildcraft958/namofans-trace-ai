import { useState } from "react";

export default function STRDownload({ alertId }: { alertId: string }) {
  const [loading, setLoading] = useState(false);

  const download = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/reports/str/${alertId}`, { method: "POST" });
      if (!res.ok) throw new Error("PDF generation failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `STR_${alertId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={download}
      disabled={loading}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        padding: "6px 12px",
        background: loading ? "#1c1f2a" : "#1a3a5c",
        color: loading ? "#555" : "#7aa2ff",
        border: "1px solid #2a4a7c",
        borderRadius: 6,
        cursor: loading ? "not-allowed" : "pointer",
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: 0.3,
        whiteSpace: "nowrap",
        transition: "all 0.2s",
      }}
    >
      {loading ? (
        <>
          <span style={{ animation: "spin 1s linear infinite", display: "inline-block" }}>⟳</span>
          Generating PDF…
        </>
      ) : (
        <>📄 Download STR PDF</>
      )}
    </button>
  );
}
