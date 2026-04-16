import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  AlertTriangle,
  Zap,
  TrendingUp,
  Clock,
  Activity,
  ShieldAlert,
  CircleStop,
  Server,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import EmptyState from "@/components/EmptyState";
import {
  triggerIncident,
  getIncidents,
  getLogStats,
  getSimulatorState,
  stopSimulator,
  getScenarios,
} from "@/lib/api";

const SCENARIO_ICONS = {
  "db-crash": Server,
  "memory-leak": TrendingUp,
  "high-latency": Clock,
  crash: AlertTriangle,
};

export default function Dashboard() {
  const [scenarios, setScenarios] = useState({});
  const [selectedScenario, setSelectedScenario] = useState("");
  const [simState, setSimState] = useState(null);
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [logStats, setLogStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [scenariosRes, simRes, incidentsRes, statsRes] = await Promise.all([
        getScenarios(),
        getSimulatorState(),
        getIncidents(),
        getLogStats(),
      ]);
      setScenarios(scenariosRes.data);
      setSimState(simRes.data);
      setRecentIncidents(incidentsRes.data.slice(0, 5));
      setLogStats(statsRes.data);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleTrigger = async () => {
    if (!selectedScenario) return;
    setTriggering(true);
    try {
      await triggerIncident(selectedScenario);
      toast.success(`Incident triggered: ${selectedScenario}`, {
        description: "Failure scenario is now active. Logs are being generated.",
      });
      setDialogOpen(false);
      fetchData();
    } catch (err) {
      toast.error("Failed to trigger incident", { description: err.message });
    } finally {
      setTriggering(false);
    }
  };

  const handleStop = async () => {
    setStopping(true);
    try {
      await stopSimulator();
      toast.success("System reset to healthy", {
        description: "All failure scenarios have been stopped.",
      });
      fetchData();
    } catch (err) {
      toast.error("Failed to stop scenario", { description: err.message });
    } finally {
      setStopping(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl sm:text-3xl font-semibold tracking-tight" data-testid="dashboard-title">
            Dashboard
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Monitor your cloud infrastructure in real-time
          </p>
        </div>
        <div className="flex items-center gap-3">
          {simState && !simState.is_healthy && (
            <Button
              variant="outline"
              onClick={handleStop}
              disabled={stopping}
              data-testid="stop-scenario-button"
              className="border-red-500/30 text-red-400 hover:bg-red-500/10"
            >
              <CircleStop className="w-4 h-4 mr-2" />
              {stopping ? "Stopping..." : "Stop Scenario"}
            </Button>
          )}
          <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) setSelectedScenario(""); }}>
            <DialogTrigger asChild>
              <Button data-testid="trigger-incident-open-button" className="bg-primary text-primary-foreground hover:brightness-110">
                <Zap className="w-4 h-4 mr-2" />
                Trigger Incident
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-border">
              <DialogHeader>
                <DialogTitle className="font-heading">Trigger Failure Scenario</DialogTitle>
                <DialogDescription>
                  Select a failure scenario to simulate an infrastructure issue.
                </DialogDescription>
              </DialogHeader>
              <Alert className="border-amber-500/30 bg-amber-500/10">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                <AlertDescription className="text-amber-200/80 text-sm">
                  This will simulate a failure and generate error logs. Use for testing only.
                </AlertDescription>
              </Alert>
              <Select
                value={selectedScenario}
                onValueChange={setSelectedScenario}
              >
                <SelectTrigger data-testid="trigger-incident-scenario-select" className="bg-secondary/50">
                  <SelectValue placeholder="Select a scenario" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(scenarios).map(([key, val]) => (
                    <SelectItem key={key} value={key}>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{key}</span>
                        <span className="text-xs text-muted-foreground">
                          — {val.description}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleTrigger}
                  disabled={!selectedScenario || triggering}
                  data-testid="trigger-incident-confirm-button"
                  className="bg-primary text-primary-foreground"
                >
                  {triggering ? "Triggering..." : "Trigger Incident"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Active Incident Banner */}
      {simState && !simState.is_healthy && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-red-500/30 bg-red-500/10 p-4"
        >
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-red-400 animate-pulse-dot" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-300">
                Active Incident: <span className="font-mono">{simState.current_scenario}</span>
              </p>
              <p className="text-xs text-red-400/70 mt-0.5">
                {simState.description} &middot; Since{" "}
                {simState.active_since
                  ? new Date(simState.active_since).toLocaleTimeString()
                  : "now"}
              </p>
            </div>
            <Badge variant="outline" className="border-red-500/40 text-red-300">
              ACTIVE
            </Badge>
          </div>
        </motion.div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <Card className="bg-card/60 backdrop-blur border-border/70">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              Error Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-heading text-3xl font-semibold tabular-nums text-red-400">
              {logStats?.stats?.ERROR || 0}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {logStats?.stats?.FATAL || 0} fatal
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/60 backdrop-blur border-border/70">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Warnings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-heading text-3xl font-semibold tabular-nums text-amber-400">
              {logStats?.stats?.WARN || 0}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/60 backdrop-blur border-border/70">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" />
              Total Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-heading text-3xl font-semibold tabular-nums">
              {logStats?.total || 0}
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card/60 backdrop-blur border-border/70">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Server className="w-4 h-4" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  simState?.is_healthy ? "bg-emerald-400" : "bg-red-400 animate-pulse-dot"
                }`}
              />
              <p className="font-heading text-lg font-semibold">
                {simState?.is_healthy ? "Healthy" : "Incident Active"}
              </p>
            </div>
            {simState?.current_scenario && (
              <p className="text-xs text-muted-foreground mt-1 font-mono">
                {simState.current_scenario}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Incidents */}
      <Card className="bg-card/60 backdrop-blur border-border/70">
        <CardHeader>
          <CardTitle className="font-heading text-lg flex items-center gap-2">
            Recent Incidents
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recentIncidents.length === 0 ? (
            <EmptyState
              icon={Activity}
              title="No incidents yet"
              description="Trigger a failure scenario to see incidents here."
            />
          ) : (
            <div className="space-y-3">
              {recentIncidents.map((incident) => (
                <div
                  key={incident.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border/60 hover:bg-secondary/30 transition-colors duration-150"
                  data-testid={`incident-row-${incident.id}`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        incident.status === "resolved"
                          ? "bg-emerald-400"
                          : incident.status === "diagnosed"
                          ? "bg-cyan-400"
                          : "bg-amber-400"
                      }`}
                    />
                    <div>
                      <p className="text-sm font-medium font-mono">
                        {incident.anomaly_type}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {incident.service} &middot;{" "}
                        {new Date(incident.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant="outline"
                    className={`capitalize text-xs ${
                      incident.status === "resolved"
                        ? "border-emerald-500/40 text-emerald-400"
                        : incident.status === "diagnosed"
                        ? "border-cyan-500/40 text-cyan-400"
                        : "border-amber-500/40 text-amber-400"
                    }`}
                    data-testid={`incident-status-${incident.id}`}
                  >
                    {incident.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
