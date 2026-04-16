const SEVERITY_STYLES = {
  FATAL: "severity-fatal",
  ERROR: "severity-error",
  WARN: "severity-warn",
  INFO: "severity-info",
  DEBUG: "severity-debug",
};

export default function SeverityChip({ level, count, active, onClick, testId }) {
  const colorClass = SEVERITY_STYLES[level] || SEVERITY_STYLES.DEBUG;

  return (
    <button
      data-testid={testId || `log-severity-filter-${level.toLowerCase()}`}
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors duration-150 ${
        active
          ? colorClass
          : "bg-transparent text-muted-foreground border-border/40 hover:text-foreground hover:border-border"
      }`}
    >
      {level}
      {count !== undefined && (
        <span className="text-[10px] opacity-70 tabular-nums">{count}</span>
      )}
    </button>
  );
}
