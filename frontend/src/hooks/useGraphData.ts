import { useEffect, useState } from "react";

export function useGraphData() {
  const [data, setData] = useState<{ summary?: any; nodes?: any[]; links?: any[] }>();
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    // TODO(frontend): fetch("/api/graph") and set state
    setLoading(false);
    setData({ summary: { status: "scaffold — wire /api/graph endpoint" } });
  }, []);
  return { data, loading };
}
