import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";

export interface GraphNode {
  id: string;
  account_type: string;
  kyc_risk: string;
  risk_level: string;
  dormant_days?: number;
  degree_in?: number;
  degree_out?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  amount: number;
  channel: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
  summary: {
    total_nodes: number;
    total_edges: number;
    flagged_nodes: number;
  };
}

export function useGraphData(subgraphAccount?: string) {
  const [data, setData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGraph = useCallback(async () => {
    try {
      setLoading(true);
      const url = subgraphAccount ? `/graph/${subgraphAccount}?depth=3` : "/graph?limit=800";
      const res = await api.get<GraphData>(url);
      setData(res.data);
      setError(null);
    } catch (e: any) {
      setError(e.message ?? "Failed to load graph");
    } finally {
      setLoading(false);
    }
  }, [subgraphAccount]);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  return { data, loading, error, refetch: fetchGraph };
}
