import { useCallback, useEffect, useRef, useState } from "react";

export interface WsAlert {
  type: "alert" | "drift_event";
  alert_id?: string;
  account_id?: string;
  risk_level?: string;
  composite_score?: number;
  score?: number;
}

export interface WsDriftEvent {
  type: "drift_event";
  account_id: string;
  score: number;
  timestamp?: string;
}

export function useAlertWebSocket(path: string = "/ws/alerts") {
  const [wsAlerts, setWsAlerts] = useState<WsAlert[]>([]);
  const [driftEvents, setDriftEvents] = useState<WsDriftEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryCountRef = useRef(0);

  const connect = useCallback(() => {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const url = `${proto}://${location.host}${path}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      retryCountRef.current = 0;
    };

    ws.onmessage = (evt) => {
      try {
        const payload = JSON.parse(evt.data) as { events: WsAlert[] };
        const events = payload.events ?? [];
        for (const ev of events) {
          if (ev.type === "drift_event") {
            setDriftEvents((prev) => [
              { ...ev, timestamp: new Date().toISOString() } as WsDriftEvent,
              ...prev,
            ].slice(0, 100));
          } else {
            setWsAlerts((prev) => [ev, ...prev].slice(0, 50));
          }
        }
      } catch {
        // ignore malformed frames
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
      const delay = Math.min(1000 * 2 ** retryCountRef.current, 30_000);
      retryCountRef.current += 1;
      retryRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [path]);

  useEffect(() => {
    connect();
    return () => {
      retryRef.current && clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { wsAlerts, driftEvents, connected };
}
