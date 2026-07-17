import { useRef, useState } from "react";
import { SendHorizonal } from "lucide-react";
import api from "../services/api";
import type { ChatMessage } from "../types";

const SUGGESTIONS = [
  "Why did profit decline?", "Compare FY2024-25 vs FY2025-26",
  "What are the major financial risks?", "Generate a board meeting summary",
];

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const sessionRef = useRef<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const send = async (text: string) => {
    if (!text.trim() || busy) return;
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput(""); setBusy(true);
    try {
      const { data } = await api.post("/chat", { session_id: sessionRef.current, message: text });
      sessionRef.current = data.session_id;
      setMessages((m) => [...m, { role: "assistant", content: data.answer, citations: data.citations }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "The analysis service is unavailable. Check that Azure OpenAI credentials are configured, then try again." }]);
    } finally {
      setBusy(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <h1 className="text-xl font-semibold tracking-tight mb-3">Chat with Financial Reports</h1>
      <div className="panel flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-sm text-mute space-y-3">
            <p>Ask anything about the uploaded reports. Answers are grounded in your documents with citations.</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => send(s)}
                  className="border border-panelEdge rounded-full px-3 py-1 text-xs hover:border-amber">{s}</button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`max-w-2xl ${m.role === "user" ? "ml-auto" : ""}`}>
            <div className={`rounded-lg px-4 py-2.5 text-sm whitespace-pre-wrap ${
              m.role === "user" ? "bg-amber/10 border border-amber/30" : "bg-ink border border-panelEdge"}`}>
              {m.content}
            </div>
            {m.citations && m.citations.length > 0 && (
              <div className="mt-1 flex flex-wrap gap-1.5">
                {m.citations.map((c, j) => (
                  <span key={j} className="text-[10px] font-mono text-mute border border-panelEdge rounded px-1.5 py-0.5">
                    {c.filename} · p{c.page_number}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="text-xs font-mono text-amber animate-pulse">analyzing…</div>}
        <div ref={bottomRef} />
      </div>
      <div className="mt-3 flex gap-2">
        <input value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send(input)}
          placeholder="Ask a question about your financials…"
          className="flex-1 rounded bg-panel border border-panelEdge px-4 py-2.5 text-sm focus:border-amber outline-none" />
        <button onClick={() => send(input)} disabled={busy} aria-label="Send"
          className="rounded bg-amber text-ink px-4 hover:brightness-110 disabled:opacity-60">
          <SendHorizonal size={16} />
        </button>
      </div>
    </div>
  );
}
