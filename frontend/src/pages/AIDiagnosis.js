import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  Brain,
  Play,
  Clock,
  ShieldCheck,
  Lightbulb,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Copy,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import ConfidenceMeter from "@/components/ConfidenceMeter";
import EmptyState from "@/components/EmptyState";
import { getIncidents, diagnoseIncident } from "@/lib/api";

export default function AIDiagnosis() {
  const [incidents, setIncidents] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [diagnosing, setDiagnosing] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchIncidents = useCallback(async () => {
    try {
      const res = await getIncidents();
      setIncidents(res.data);
    } catch (err) {
      console.error("Fetch incidents error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 10000);
    return () => clearInterval(interval);
  }, [fetchIncidents]);

  // Auto-select first undiagnosed incident
  useEffect(() => {
    if (!selectedId && incidents.length > 0) {
      const undiagnosed = incidents.find((i) => i.status === "open");
      if (undiagnosed) setSelectedId(undiagnosed.id);
      else setSelectedId(incidents[0].id);
    }
  }, [incidents, selectedId]);

  const handleDiagnose = async () => {
    if (!selectedId) return;
    setDiagnosing(true);
    setResult(null);
    try {
      const res = await diagnoseIncident(selectedId);
      setResult(res.data);
      toast.success("Diagnosis complete", {
        description: `Confidence: ${res.data.confidence}%`,
      });
      fetchIncidents();
    } catch (err) {
      toast.error("Diagnosis failed", { description: err.message });
    } finally {
      setDiagnosing(false);
    }
  };

  const selectedIncident = incidents.find((i) => i.id === selectedId);

  const copyFixes = () => {
    if (result?.diagnosis?.recommended_fixes) {
      navigator.clipboard.writeText(
        result.diagnosis.recommended_fixes.join("\n")
      );
      toast.success("Fixes copied to clipboard");
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="font-heading text-2xl sm:text-3xl font-semibold tracking-tight" data-testid="ai-diagnosis-title">
          AI Diagnosis
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          GPT-4o powered root cause analysis for infrastructure incidents
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Incident Selection */}
        <Card className="bg-card/60 backdrop-blur border-border/70">
          <CardHeader>
            <CardTitle className="font-heading text-lg">Select Incident</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {incidents.length === 0 ? (
              <EmptyState
                icon={Brain}
                title="No incidents to diagnose"
                description="Trigger a failure scenario first from the Dashboard."
              />
            ) : (
              <>
                <Select value={selectedId} onValueChange={setSelectedId}>
                  <SelectTrigger data-testid="diagnosis-incident-select" className="bg-secondary/50">
                    <SelectValue placeholder="Select an incident" />
                  </SelectTrigger>
                  <SelectContent>
                    {incidents.map((inc) => (
                      <SelectItem key={inc.id} value={inc.id}>
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              inc.status === "resolved"
                                ? "bg-emerald-400"
                                : inc.status === "diagnosed"
                                ? "bg-cyan-400"
                                : "bg-amber-400"
                            }`}
                          />
                          <span className="font-mono text-sm">{inc.anomaly_type}</span>
                          <span className="text-xs text-muted-foreground">
                            [{inc.status}]
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {/* Incident Info */}
                {selectedIncident && (
                  <div className="space-y-3 p-3 rounded-lg bg-secondary/30 border border-border/50">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Type</span>
                      <span className="text-sm font-mono">{selectedIncident.anomaly_type}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Service</span>
                      <span className="text-sm">{selectedIncident.service}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Status</span>
                      <Badge
                        variant="outline"
                        className={`capitalize text-xs ${
                          selectedIncident.status === "resolved"
                            ? "border-emerald-500/40 text-emerald-400"
                            : selectedIncident.status === "diagnosed"
                            ? "border-cyan-500/40 text-cyan-400"
                            : "border-amber-500/40 text-amber-400"
                        }`}
                      >
                        {selectedIncident.status}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Time</span>
                      <span className="text-xs">
                        {new Date(selectedIncident.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}

                <Button
                  onClick={handleDiagnose}
                  disabled={!selectedId || diagnosing}
                  data-testid="ai-diagnosis-run-button"
                  className="w-full bg-primary text-primary-foreground hover:brightness-110"
                >
                  {diagnosing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing with GPT-4o...
                    </>
                  ) : (
                    <>
                      <Brain className="w-4 h-4 mr-2" />
                      Run AI Diagnosis
                    </>
                  )}
                </Button>
              </>
            )}
          </CardContent>
        </Card>

        {/* Right: Diagnosis Results */}
        <Card className="bg-card/60 backdrop-blur border-border/70">
          <CardHeader>
            <CardTitle className="font-heading text-lg flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-primary" />
              Diagnosis Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            {diagnosing ? (
              <div className="space-y-4 py-8">
                <div className="flex flex-col items-center gap-3">
                  <Loader2 className="w-10 h-10 text-primary animate-spin" />
                  <p className="text-sm text-muted-foreground">Running AI analysis...</p>
                  <p className="text-xs text-muted-foreground">GPT-4o is analyzing log patterns</p>
                </div>
              </div>
            ) : result?.diagnosis ? (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-5"
              >
                {/* Confidence */}
                <ConfidenceMeter value={result.confidence || result.diagnosis.confidence || 0} />

                {/* Root Cause */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    <span className="text-sm font-medium">Root Cause</span>
                  </div>
                  <p className="text-sm text-foreground/80 bg-secondary/30 rounded-lg p-3 border border-border/50">
                    {result.diagnosis.root_cause}
                  </p>
                </div>

                {/* Severity + MTTR */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-secondary/30 border border-border/50">
                    <span className="text-xs text-muted-foreground">Severity</span>
                    <Badge
                      variant="outline"
                      className={`mt-1 capitalize ${
                        result.diagnosis.severity === "critical"
                          ? "border-red-500/40 text-red-400"
                          : result.diagnosis.severity === "high"
                          ? "border-amber-500/40 text-amber-400"
                          : "border-cyan-500/40 text-cyan-400"
                      }`}
                    >
                      {result.diagnosis.severity}
                    </Badge>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/30 border border-border/50">
                    <span className="text-xs text-muted-foreground">Est. MTTR</span>
                    <p data-testid="diagnosis-mttr" className="text-sm font-medium mt-1 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {result.diagnosis.estimated_mttr || result.estimated_mttr}
                    </p>
                  </div>
                </div>

                {/* Recommended Fixes */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Lightbulb className="w-4 h-4 text-amber-400" />
                      <span className="text-sm font-medium">Recommended Fixes</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={copyFixes}
                      className="h-7 text-xs"
                    >
                      <Copy className="w-3 h-3 mr-1" />
                      Copy
                    </Button>
                  </div>
                  <ol className="space-y-2">
                    {(result.diagnosis.recommended_fixes || []).map((fix, idx) => (
                      <li
                        key={idx}
                        className="flex items-start gap-2 text-sm text-foreground/80 bg-secondary/20 rounded-lg px-3 py-2 border border-border/40"
                      >
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                        <span>{fix}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              </motion.div>
            ) : (
              <EmptyState
                icon={Brain}
                title="No diagnosis yet"
                description="Select an incident and click 'Run AI Diagnosis' to analyze."
              />
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
