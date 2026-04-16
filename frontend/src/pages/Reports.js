import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  FileBarChart,
  Eye,
  CheckCircle2,
  Brain,
  Clock,
  X,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import ConfidenceMeter from "@/components/ConfidenceMeter";
import EmptyState from "@/components/EmptyState";
import { getIncidents, resolveIncident, diagnoseIncident } from "@/lib/api";

const STATUS_STYLES = {
  open: "border-amber-500/40 text-amber-400",
  diagnosed: "border-cyan-500/40 text-cyan-400",
  resolved: "border-emerald-500/40 text-emerald-400",
};

export default function Reports() {
  const [incidents, setIncidents] = useState([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [diagnosing, setDiagnosing] = useState(false);

  const fetchIncidents = useCallback(async () => {
    try {
      const status = statusFilter === "all" ? undefined : statusFilter;
      const res = await getIncidents(status);
      setIncidents(res.data);
    } catch (err) {
      console.error("Fetch incidents error:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 10000);
    return () => clearInterval(interval);
  }, [fetchIncidents]);

  const handleResolve = async (id) => {
    setResolving(true);
    try {
      const res = await resolveIncident(id);
      setSelectedIncident(res.data);
      toast.success("Incident resolved");
      fetchIncidents();
    } catch (err) {
      toast.error("Failed to resolve", { description: err.message });
    } finally {
      setResolving(false);
    }
  };

  const handleDiagnose = async (id) => {
    setDiagnosing(true);
    try {
      const res = await diagnoseIncident(id);
      setSelectedIncident(res.data);
      toast.success("Diagnosis complete");
      fetchIncidents();
    } catch (err) {
      toast.error("Diagnosis failed", { description: err.message });
    } finally {
      setDiagnosing(false);
    }
  };

  const openDetails = (incident) => {
    setSelectedIncident(incident);
    setSheetOpen(true);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl sm:text-3xl font-semibold tracking-tight" data-testid="reports-title">
            Incident Reports
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            View and manage all infrastructure incidents
          </p>
        </div>
        <Select
          value={statusFilter}
          onValueChange={setStatusFilter}
        >
          <SelectTrigger data-testid="reports-status-filter-select" className="w-[180px] bg-secondary/50">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="diagnosed">Diagnosed</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <Card className="bg-card/60 backdrop-blur border-border/70">
        <CardContent className="p-0">
          {loading ? (
            <div className="p-6 space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-12" />
              ))}
            </div>
          ) : incidents.length === 0 ? (
            <EmptyState
              icon={FileBarChart}
              title="No incidents found"
              description={statusFilter === "all" ? "Trigger a scenario to create incidents." : `No ${statusFilter} incidents.`}
            />
          ) : (
            <Table data-testid="incident-reports-table">
              <TableHeader>
                <TableRow className="border-border/60 hover:bg-transparent">
                  <TableHead className="text-xs font-medium uppercase tracking-wide">Type</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wide">Service</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wide">Status</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wide">Severity</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wide">Confidence</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wide">Time</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wide text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidents.map((inc) => (
                  <TableRow
                    key={inc.id}
                    className="border-border/40 hover:bg-secondary/30 cursor-pointer transition-colors duration-150"
                    data-testid={`incident-row-${inc.id}`}
                    onClick={() => openDetails(inc)}
                  >
                    <TableCell className="font-mono text-sm font-medium">{inc.anomaly_type}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{inc.service}</TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={`capitalize text-xs ${STATUS_STYLES[inc.status] || ""}`}
                        data-testid={`incident-status-${inc.id}`}
                      >
                        {inc.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={`capitalize text-xs ${
                          inc.severity_label === "critical"
                            ? "border-red-500/40 text-red-400"
                            : inc.severity_label === "high"
                            ? "border-amber-500/40 text-amber-400"
                            : "border-cyan-500/40 text-cyan-400"
                        }`}
                      >
                        {inc.severity_label}
                      </Badge>
                    </TableCell>
                    <TableCell className="tabular-nums text-sm">
                      {inc.confidence > 0 ? `${inc.confidence}%` : "-"}
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(inc.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          openDetails(inc);
                        }}
                        className="h-7 text-xs"
                      >
                        <Eye className="w-3 h-3 mr-1" />
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Detail Sheet */}
      <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
        <SheetContent className="w-[420px] sm:w-[520px] bg-card border-border overflow-y-auto">
          <SheetHeader>
            <SheetTitle className="font-heading text-lg">Incident Details</SheetTitle>
          </SheetHeader>

          {selectedIncident && (
            <div className="mt-6 space-y-5">
              {/* Basic Info */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">Type</span>
                  <span className="font-mono text-sm font-medium">{selectedIncident.anomaly_type}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">Service</span>
                  <span className="text-sm">{selectedIncident.service}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">Status</span>
                  <Badge
                    variant="outline"
                    className={`capitalize ${STATUS_STYLES[selectedIncident.status] || ""}`}
                  >
                    {selectedIncident.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">Created</span>
                  <span className="text-xs">{new Date(selectedIncident.timestamp).toLocaleString()}</span>
                </div>
                {selectedIncident.resolved_at && (
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground uppercase tracking-wide">Resolved</span>
                    <span className="text-xs">{new Date(selectedIncident.resolved_at).toLocaleString()}</span>
                  </div>
                )}
              </div>

              <Separator className="opacity-50" />

              {/* Log Stats */}
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center p-3 rounded-lg bg-secondary/30 border border-border/50">
                  <p className="text-lg font-semibold tabular-nums">{selectedIncident.log_count}</p>
                  <p className="text-xs text-muted-foreground">Logs</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-secondary/30 border border-border/50">
                  <p className="text-lg font-semibold tabular-nums text-red-400">{selectedIncident.error_count}</p>
                  <p className="text-xs text-muted-foreground">Errors</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-secondary/30 border border-border/50">
                  <p className="text-lg font-semibold tabular-nums text-red-400">{selectedIncident.fatal_count}</p>
                  <p className="text-xs text-muted-foreground">Fatal</p>
                </div>
              </div>

              {/* Diagnosis */}
              {selectedIncident.diagnosis && (
                <>
                  <Separator className="opacity-50" />
                  <div className="space-y-4">
                    <h4 className="text-sm font-medium flex items-center gap-2">
                      <Brain className="w-4 h-4 text-primary" />
                      AI Diagnosis
                    </h4>
                    <ConfidenceMeter value={selectedIncident.confidence || 0} />
                    <div className="space-y-2">
                      <span className="text-xs text-muted-foreground">Root Cause</span>
                      <p className="text-sm bg-secondary/30 rounded-lg p-3 border border-border/50">
                        {selectedIncident.diagnosis.root_cause}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                      <span className="text-sm">MTTR: {selectedIncident.diagnosis.estimated_mttr || selectedIncident.estimated_mttr}</span>
                    </div>
                    {selectedIncident.diagnosis.recommended_fixes?.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-xs text-muted-foreground">Recommended Fixes</span>
                        <ol className="space-y-1.5">
                          {selectedIncident.diagnosis.recommended_fixes.map((fix, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm bg-secondary/20 rounded px-3 py-2 border border-border/40">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0" />
                              <span>{fix}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                </>
              )}

              <Separator className="opacity-50" />

              {/* Actions */}
              <div className="flex gap-3">
                {selectedIncident.status === "open" && (
                  <Button
                    onClick={() => handleDiagnose(selectedIncident.id)}
                    disabled={diagnosing}
                    className="flex-1 bg-primary text-primary-foreground"
                  >
                    <Brain className="w-4 h-4 mr-2" />
                    {diagnosing ? "Diagnosing..." : "Run Diagnosis"}
                  </Button>
                )}
                {selectedIncident.status !== "resolved" && (
                  <Button
                    variant="outline"
                    onClick={() => handleResolve(selectedIncident.id)}
                    disabled={resolving}
                    className="flex-1 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10"
                  >
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    {resolving ? "Resolving..." : "Resolve"}
                  </Button>
                )}
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </motion.div>
  );
}
