import { Progress } from "@/components/ui/progress";

export default function ConfidenceMeter({ value, label = "Confidence" }) {
  const getColor = (v) => {
    if (v >= 80) return "bg-emerald-500";
    if (v >= 60) return "bg-amber-500";
    return "bg-red-500";
  };

  return (
    <div data-testid="diagnosis-confidence-meter" className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-sm font-medium tabular-nums text-foreground">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-secondary overflow-hidden">
        <div
          className={`h-full rounded-full ${getColor(value)} transition-all duration-500 ease-out`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
