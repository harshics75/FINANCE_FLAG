import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Activity, Banknote, ClipboardList, Compass, FileSearch, FileText, Globe, LayoutDashboard, LineChart, LogOut,
  MessageSquareText, Moon, Network, PanelLeftClose, PanelLeftOpen, ShieldAlert, Sparkles, Sun,
  TrendingUp, UploadCloud, Wallet,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "../contexts/ThemeContext";

const NAV = [
  { to: "/", label: "Executive Overview", icon: LayoutDashboard },
  { to: "/performance", label: "Financial Performance", icon: LineChart },
  { to: "/cash-flow", label: "Cash Flow", icon: Banknote },
  { to: "/working-capital", label: "Working Capital", icon: Wallet },
  { to: "/insights", label: "AI Insights", icon: Sparkles },
  { to: "/agents", label: "Agent Network", icon: Network },
  { to: "/forecast", label: "Forecast Timeline", icon: TrendingUp },
  { to: "/operational", label: "Operational Highlights", icon: ClipboardList },
  { to: "/market", label: "Market Intel — Operations", icon: Globe },
  { to: "/market/strategy", label: "Market Intel — Strategy", icon: Compass },
  { to: "/documents", label: "Document Explorer", icon: FileSearch },
  { to: "/audit", label: "Audit Findings", icon: ShieldAlert },
  { to: "/board-report", label: "Board Report", icon: FileText },
  { to: "/chat", label: "Chat with Reports", icon: MessageSquareText },
  { to: "/upload", label: "Upload", icon: UploadCloud },
];

export default function AppShell() {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen flex">
      <aside className={`shrink-0 border-r border-panelEdge bg-panel flex flex-col transition-[width] duration-300
        ${collapsed ? "w-16" : "w-64"}`} style={{ backdropFilter: "blur(24px)" }}>
        <div className="px-4 py-5 flex items-center gap-2.5 border-b border-panelEdge">
          <div className="w-8 h-8 rounded-[10px] bg-grad grid place-items-center shrink-0 shadow-[0_0_20px_rgba(93,140,255,.4)]">
            <Activity className="text-ink" size={16} />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <div className="font-semibold tracking-tight leading-tight">FinSight</div>
              <div className="text-[10px] font-mono text-faint uppercase tracking-widest">AI workspace</div>
            </div>
          )}
          <button onClick={() => setCollapsed((c) => !c)} aria-label="Toggle sidebar"
            className="ml-auto p-1.5 rounded-lg text-mute hover:text-slate-200 hover:bg-white/5 transition-colors shrink-0">
            {collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
          </button>
        </div>

        <nav className="flex-1 py-3 space-y-0.5 overflow-y-auto">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === "/" || to === "/market"} title={collapsed ? label : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3 mx-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "text-cyan bg-cyan/10 border border-cyan/20"
                    : "text-mute hover:text-slate-200 hover:bg-white/5 border border-transparent"}`}>
              <Icon size={15} className="shrink-0" /> {!collapsed && label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-panelEdge text-xs space-y-2">
          {!collapsed && (
            <>
              <div className="text-mute truncate">{user?.email}</div>
              <div className="font-mono uppercase text-[10px] text-cyan">{user?.role.replace("_", " ")}</div>
            </>
          )}
          <div className={`flex gap-2 pt-1 ${collapsed ? "flex-col items-center" : ""}`}>
            <button onClick={toggle} aria-label="Toggle dark mode"
              className="p-1.5 rounded-lg border border-panelEdge hover:border-cyan/50 hover:text-cyan transition-colors">
              {dark ? <Sun size={13} /> : <Moon size={13} />}
            </button>
            <button onClick={() => { logout(); navigate("/login"); }} aria-label="Sign out"
              className="p-1.5 rounded-lg border border-panelEdge hover:border-down/50 hover:text-down transition-colors">
              <LogOut size={13} />
            </button>
          </div>
        </div>
      </aside>
      <main className="flex-1 p-6 overflow-x-hidden">
        <Outlet />
      </main>
    </div>
  );
}
