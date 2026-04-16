import { Badge } from "@/components/ui/badge";

const LEVEL_CLASSES = {
  FATAL: "severity-fatal border",
  ERROR: "severity-error border",
  WARN: "severity-warn border",
  INFO: "severity-info border",
  DEBUG: "severity-debug border",
};

export default function LogLine({ log }) {
  const levelClass = LEVEL_CLASSES[log.level] || LEVEL_CLASSES.DEBUG;
  const timestamp = log.timestamp
    ? new Date(log.timestamp).toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "--:--:--";

  return (
    <div className="log-line grid grid-cols-[auto_auto_1fr] gap-3 px-3 py-2 rounded transition-colors duration-150">
      <span className="font-mono text-xs text-muted-foreground tabular-nums whitespace-nowrap">
        {timestamp}
      </span>
      <Badge variant="outline" className={`${levelClass} text-[10px] px-2 py-0 h-5 font-mono font-medium`}>
        {log.level}
      </Badge>
      <span className="font-mono text-sm text-foreground/90 break-words">
        <span className="text-muted-foreground">[{log.service}]</span>{" "}
        {log.message}
      </span>
    </div>
  );
}
