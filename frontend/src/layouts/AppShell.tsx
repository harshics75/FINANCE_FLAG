import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Activity, Banknote, FileSearch, LayoutDashboard, LineChart, LogOut,
  MessageSquareText, Moon, ShieldAlert, Sparkles, Sun, UploadCloud, Wallet,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "../contexts/ThemeContext";

const NAV = [
  { to: "/", label: "Executive Overview", icon: LayoutDashboard },
  { to: "/performance", label: "Financial Performance", icon: LineChart },
  { to: "/cash-flow", label: "Cash Flow", icon: Banknote },
  { to: "/working-capital", label: "Working Capital", icon: Wallet },
  { to: "/insights", label: "AI Insights", icon: Sparkles },
  { to: "/documents", label: "Document Explorer", icon: FileSearch },
  { to: "/audit", label: "Audit Findings", icon: ShieldAlert },
  { to: "/chat", label: "Chat with Reports", icon: MessageSquareText },
  { to: "/upload", label: "Upload", icon: UploadCloud },
];

export default function AppShell() {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 border-r border-panelEdge bg-panel/60 flex flex-col">
        <div className="px-4 py-5 flex items-center gap-2 border-b border-panelEdge">
          <Activity className="text-amber" size={20} />
          <span className="font-semibold tracking-tight">FinIntel</span>
          <span className="ml-auto text-[10px] font-mono text-mute">v1.0</span>
        </div>
        <nav className="flex-1 py-3 space-y-0.5">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2 text-sm transition-colors ${
                  isActive ? "text-amber bg-amber/5 border-r-2 border-amber" : "text-mute hover:text-slate-200"}`}>
              <Icon size={15} /> {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-panelEdge text-xs space-y-2">
          <div className="text-mute">{user?.email}</div>
          <div className="font-mono uppercase text-[10px] text-amber">{user?.role.replace("_", " ")}</div>
          <div className="flex gap-2 pt-1">
            <button onClick={toggle} aria-label="Toggle dark mode"
              className="p-1.5 rounded border border-panelEdge hover:border-amber">
              {dark ? <Sun size={13} /> : <Moon size={13} />}
            </button>
            <button onClick={() => { logout(); navigate("/login"); }} aria-label="Sign out"
              className="p-1.5 rounded border border-panelEdge hover:border-down">
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
