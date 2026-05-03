import { useEffect, useRef, useState } from "react";

export function useAlertWebSocket(url: string = "/ws/alerts") {
  const [alerts, setAlerts] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  useEffect(() => {
    const wsUrl = url.startsWith("ws") ? url : `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}${url}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onmessage = (evt) => {
      try {
        const alert = JSON.parse(evt.data);
        setAlerts((prev) => [alert, ...prev].slice(0, 50));
      } catch {}
    };
    return () => ws.close();
  }, [url]);
  return alerts;
}
