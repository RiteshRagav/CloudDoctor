import { useState, useEffect, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import { FileSearch, Pause, Play, RefreshCw, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import SeverityChip from "@/components/SeverityChip";
import LogLine from "@/components/LogLine";
import EmptyState from "@/components/EmptyState";
import { getLogs, getLogStats } from "@/lib/api";

const SEVERITY_LEVELS = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG"];

export default function LogAnalyzer() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [activeLevels, setActiveLevels] = useState(new Set(SEVERITY_LEVELS));
  const [streaming, setStreaming] = useState(true);
  const [loading, setLoading] = useState(true);
  const scrollRef = useRef(null);

  const fetchLogs = useCallback(async () => {
    try {
      const levels = Array.from(activeLevels).join(",");
      const [logsRes, statsRes] = await Promise.all([
        getLogs({ levels, limit: 200 }),
        getLogStats(),
      ]);
      setLogs(logsRes.data.logs || []);
      setStats(statsRes.data.stats || {});
    } catch (err) {
      console.error("Log fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, [activeLevels]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    if (!streaming) return;
    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, [streaming, fetchLogs]);

  const toggleLevel = (level) => {
    setActiveLevels((prev) => {
      const next = new Set(prev);
      if (next.has(level)) {
        next.delete(level);
      } else {
        next.add(level);
      }
      return next;
    });
  };

  const totalLogs = Object.values(stats).reduce((a, b) => a + b, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="font-heading text-2xl sm:text-3xl font-semibold tracking-tight" data-testid="log-analyzer-title">
          Log Analyzer
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Real-time log monitoring and analysis &middot;{" "}
          <span className="tabular-nums">{totalLogs}</span> total logs
        </p>
      </div>

      {/* Log Stream Panel */}
      <Card
        className="bg-card/50 backdrop-blur border-border/70 overflow-hidden"
        data-testid="log-stream-panel"
      >
        {/* Toolbar */}
        <div className="sticky top-0 z-10 flex flex-wrap items-center gap-2 border-b border-border/60 bg-card/90 backdrop-blur px-4 py-3">
          {/* Severity Filters */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {SEVERITY_LEVELS.map((level) => (
              <SeverityChip
                key={level}
                level={level}
                count={stats[level] || 0}
                active={activeLevels.has(level)}
                onClick={() => toggleLevel(level)}
              />
            ))}
          </div>

          <div className="flex-1" />

          {/* Controls */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              {streaming && (
                <span className="flex items-center gap-1.5 text-xs text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-dot" />
                  Live
                </span>
              )}
              <Switch
                checked={streaming}
                onCheckedChange={setStreaming}
                data-testid="log-stream-pause-button"
              />
              <span className="text-xs text-muted-foreground">
                {streaming ? "Streaming" : "Paused"}
              </span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={fetchLogs}
              className="h-8 w-8"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>

        {/* Log Lines */}
        <CardContent className="p-0">
          <ScrollArea className="h-[65vh]" ref={scrollRef}>
            <div className="divide-y divide-border/30">
              {loading ? (
                <div className="p-8 text-center text-muted-foreground">Loading logs...</div>
              ) : logs.length === 0 ? (
                <EmptyState
                  icon={FileSearch}
                  title="No logs found"
                  description="Trigger a failure scenario to generate logs, or adjust your severity filters."
                />
              ) : (
                logs.map((log, idx) => <LogLine key={log.id || idx} log={log} />)
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}
