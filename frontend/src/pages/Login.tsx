import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Activity } from "lucide-react";
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
    <div className="min-h-screen grid place-items-center">
      <div className="panel w-full max-w-sm p-8 space-y-5">
        <div className="flex items-center gap-2">
          <Activity className="text-amber" size={22} />
          <h1 className="text-lg font-semibold tracking-tight">FinIntel</h1>
        </div>
        <p className="text-sm text-mute">AI Financial Intelligence & Executive Dashboard</p>
        <div className="space-y-3">
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Email"
            className="w-full rounded bg-ink border border-panelEdge px-3 py-2 text-sm focus:border-amber outline-none" />
          <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password"
            onKeyDown={(e) => e.key === "Enter" && submit()}
            className="w-full rounded bg-ink border border-panelEdge px-3 py-2 text-sm focus:border-amber outline-none" />
          {error && <p className="text-down text-xs">{error}</p>}
          <button onClick={submit} disabled={busy}
            className="w-full rounded bg-amber text-ink font-semibold py-2 text-sm hover:brightness-110 disabled:opacity-60">
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}
