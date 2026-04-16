import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FileSearch,
  Brain,
  FileBarChart,
  Menu,
  X,
  Activity,
  Stethoscope,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import StatusPill from "@/components/StatusPill";
import { useHealthStatus } from "@/hooks/useHealthStatus";

const NAV_ITEMS = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard, testId: "sidebar-nav-dashboard-link" },
  { path: "/logs", label: "Log Analyzer", icon: FileSearch, testId: "sidebar-nav-log-analyzer-link" },
  { path: "/diagnosis", label: "AI Diagnosis", icon: Brain, testId: "sidebar-nav-ai-diagnosis-link" },
  { path: "/reports", label: "Reports", icon: FileBarChart, testId: "sidebar-nav-reports-link" },
];

function SidebarContent() {
  const { health, loading } = useHealthStatus();

  return (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div className="px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary/15 flex items-center justify-center">
            <Stethoscope className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="font-heading text-lg font-semibold text-foreground tracking-tight">CloudDoctor</h1>
            <p className="text-xs text-muted-foreground">AI Cloud Diagnostics</p>
          </div>
        </div>
      </div>

      <Separator className="opacity-50" />

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            data-testid={item.testId}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                isActive
                  ? "bg-primary/10 text-primary border border-primary/20"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              }`
            }
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <Separator className="opacity-50" />

      {/* Health Status Pills */}
      <div className="px-4 py-4 space-y-2">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide px-1 mb-3">System Health</p>
        <StatusPill
          name="BetterStack"
          status={health?.betterstack?.status || "unknown"}
          message={health?.betterstack?.message || "Checking..."}
          testId="health-pill-betterstack"
        />
        <StatusPill
          name="MongoDB"
          status={health?.mongodb?.status || "unknown"}
          message={health?.mongodb?.message || "Checking..."}
          testId="health-pill-mongodb"
        />
        <StatusPill
          name="Groq LLM"
          status={health?.llm?.status || "unknown"}
          message={health?.llm?.message || "Checking..."}
          testId="health-pill-llm"
        />
        <StatusPill
          name="Sample App"
          status={health?.sample_app?.status || "unknown"}
          message={health?.sample_app?.message || "Checking..."}
          testId="health-pill-sample-app"
        />
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-border/50">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Activity className="w-3 h-3" />
          <span>v1.0 &middot; {loading ? "Checking..." : "System Active"}</span>
        </div>
      </div>
    </div>
  );
}

export default function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-background min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:w-[280px] bg-card/80 backdrop-blur border-r border-border/70 z-20">
        <SidebarContent />
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-border/70 bg-card/80 backdrop-blur sticky top-0 z-30">
        <div className="flex items-center gap-2">
          <Stethoscope className="w-5 h-5 text-primary" />
          <span className="font-heading font-semibold">CloudDoctor</span>
        </div>
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" data-testid="mobile-menu-button">
              <Menu className="w-5 h-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[280px] p-0 bg-card">
            <SidebarContent />
          </SheetContent>
        </Sheet>
      </div>

      {/* Main Content */}
      <main className="lg:pl-[280px] relative z-10">
        <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
