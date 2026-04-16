import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const STATUS_COLORS = {
  connected: "bg-emerald-400",
  healthy: "bg-emerald-400",
  ok: "bg-emerald-400",
  warning: "bg-amber-400",
  not_configured: "bg-amber-400",
  error: "bg-red-400",
  unhealthy: "bg-red-400",
  unknown: "bg-slate-400",
};

const STATUS_LABELS = {
  connected: "Connected",
  healthy: "Healthy",
  ok: "OK",
  warning: "Warning",
  not_configured: "Local Mode",
  error: "Error",
  unhealthy: "Unhealthy",
  unknown: "Unknown",
};

export default function StatusPill({ name, status, message, testId }) {
  const dotColor = STATUS_COLORS[status] || STATUS_COLORS.unknown;
  const label = STATUS_LABELS[status] || status;

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            data-testid={testId}
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg border border-border/60 bg-card/40 backdrop-blur hover:border-border hover:bg-card/60 transition-colors duration-150 cursor-default"
          >
            <span className={`h-2 w-2 rounded-full ${dotColor} flex-shrink-0`} />
            <span className="text-xs font-medium text-foreground/90 flex-1 truncate">{name}</span>
            <span
              data-testid={`${testId}-status`}
              className="text-[10px] text-muted-foreground uppercase tracking-wide"
            >
              {label}
            </span>
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="text-xs max-w-[250px]">
          <p>{message}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
