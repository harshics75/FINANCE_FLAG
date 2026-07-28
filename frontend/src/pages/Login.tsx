import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Activity, ArrowRight } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true); setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError("Incorrect email or password.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center px-4">
      <div className="w-full max-w-sm animate-rise">
        <div className="flex items-center gap-2.5 mb-8 justify-center">
          <div className="w-9 h-9 rounded-[11px] bg-grad grid place-items-center shadow-[0_0_24px_rgba(93,140,255,.45)]">
            <Activity className="text-ink" size={18} />
          </div>
          <span className="text-lg font-semibold tracking-tight">FinSight</span>
        </div>

        <div className="grad-border">
          <div className="rounded-[17px] p-8 space-y-5" style={{ background: "rgba(11,14,26,.92)", backdropFilter: "blur(20px)" }}>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">Welcome back</h1>
              <p className="text-sm text-mute mt-1">AI Financial Intelligence &amp; Executive Dashboard</p>
            </div>
            <div className="space-y-3">
              <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Email"
                className="w-full rounded-lg bg-ink border border-panelEdge px-3 py-2.5 text-sm focus:border-cyan/60 outline-none transition-colors" />
              <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password"
                onKeyDown={(e) => e.key === "Enter" && submit()}
                className="w-full rounded-lg bg-ink border border-panelEdge px-3 py-2.5 text-sm focus:border-cyan/60 outline-none transition-colors" />
              {error && <p className="text-down text-xs">{error}</p>}
              <button onClick={submit} disabled={busy}
                className="w-full flex items-center justify-center gap-2 rounded-lg bg-grad text-ink font-semibold py-2.5 text-sm
                  hover:brightness-110 disabled:opacity-50 transition-all">
                {busy ? "Signing in…" : <>Sign in <ArrowRight size={15} /></>}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
