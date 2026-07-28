import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { Bot, FileText, Send, Sparkles } from "lucide-react";
import api from "../services/api";
import type { Citation } from "../types";

const SUGGESTIONS = [
  "Why did profit decline?", "Compare FY2024-25 vs FY2025-26",
  "What are the major financial risks?", "Generate a board meeting summary",
];

interface Msg {
  id: number;
  role: "user" | "assistant";
  content: string;
  typed?: string;
  citations?: Citation[];
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function AskBox({ input, setInput, onSend, busy, autoFocus }: {
  input: string; setInput: (v: string) => void; onSend: () => void; busy: boolean; autoFocus?: boolean;
}) {
  return (
    <div className="grad-border">
      <div className="flex items-end gap-2 rounded-[17px] px-4 py-3.5" style={{ background: "rgba(11,14,26,.92)", backdropFilter: "blur(20px)" }}>
        <textarea
          rows={1}
          autoFocus={autoFocus}
          value={input}
          placeholder="Ask anything about your financial reports…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onSend(); } }}
          aria-label="Ask the AI about your financial reports"
          className="flex-1 bg-transparent border-0 outline-none resize-none text-[15px] leading-relaxed max-h-36 min-h-[24px] placeholder:text-faint"
        />
        <button onClick={onSend} disabled={!input.trim() || busy} aria-label="Send"
          className="w-9 h-9 rounded-[11px] bg-grad text-ink grid place-items-center shrink-0 disabled:opacity-35 transition-opacity hover:brightness-110">
          <Send size={15} />
        </button>
      </div>
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const sessionRef = useRef<string | null>(null);
  const idRef = useRef(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  const patch = (id: number, patch: Partial<Msg>) =>
    setMessages((ms) => ms.map((m) => (m.id === id ? { ...m, ...patch } : m)));

  const scrollDown = () =>
    requestAnimationFrame(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }));

  const send = async (raw: string) => {
    const text = raw.trim();
    if (!text || busy) return;
    setInput("");
    setBusy(true);
    const uid = ++idRef.current;
    setMessages((ms) => [...ms, { id: uid, role: "user", content: text }]);
    scrollDown();

    try {
      const { data } = await api.post("/chat", { session_id: sessionRef.current, message: text });
      sessionRef.current = data.session_id;
      const aid = ++idRef.current;
      setMessages((ms) => [...ms, { id: aid, role: "assistant", content: data.answer, typed: "", citations: data.citations }]);
      scrollDown();
      // reveal the real answer progressively — genuine content, animated pacing only
      const full: string = data.answer;
      for (let i = 0; i < full.length; i += 4) {
        patch(aid, { typed: full.slice(0, i + 4) });
        if (i % 60 === 0) scrollDown();
        await sleep(10);
      }
      patch(aid, { typed: full });
    } catch {
      const aid = ++idRef.current;
      setMessages((ms) => [...ms, {
        id: aid, role: "assistant",
        content: "Couldn't reach the AI service. Check that the backend and LLM provider (Ollama or Azure OpenAI) are running, then try again.",
        typed: "Couldn't reach the AI service. Check that the backend and LLM provider (Ollama or Azure OpenAI) are running, then try again.",
      }]);
    } finally {
      setBusy(false);
      scrollDown();
    }
  };

  const location = useLocation();
  const autoSentRef = useRef(false);
  useEffect(() => {
    const prompt = (location.state as { initialPrompt?: string } | null)?.initialPrompt;
    if (prompt && !autoSentRef.current) {
      autoSentRef.current = true;
      send(prompt);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  const inChat = messages.length > 0;

  if (!inChat) {
    return (
      <div className="max-w-3xl mx-auto px-2 py-10 animate-rise">
        <span className="eyebrow"><Sparkles size={12} /> Grounded in your uploaded reports</span>
        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight leading-tight mt-4 mb-2">
          Don't read the report.<br /><span className="grad-text">Interrogate it.</span>
        </h1>
        <p className="text-mute text-[15px] max-w-md mb-7">
          Ask a question about your financial documents — every answer cites the source file and page.
        </p>
        <AskBox input={input} setInput={setInput} onSend={() => send(input)} busy={busy} autoFocus />
        <div className="flex flex-wrap gap-2 mt-4">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => send(s)}
              className="inline-flex items-center gap-1.5 text-[12.5px] text-mute border border-panelEdge rounded-full px-3.5 py-1.5
                hover:text-slate-200 hover:border-panelEdgeHi transition-colors">
              <Sparkles size={11} className="text-cyan" />{s}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)] max-w-3xl mx-auto w-full">
      <div className="flex-1 overflow-y-auto py-6 space-y-6">
        {messages.map((m) =>
          m.role === "user" ? (
            <div key={m.id} className="max-w-[78%] ml-auto rounded-2xl rounded-br-md px-4 py-2.5 text-sm animate-rise"
              style={{ background: "linear-gradient(120deg, rgba(123,120,255,.2), rgba(51,214,255,.12))", border: "1px solid rgba(123,120,255,.3)" }}>
              {m.content}
            </div>
          ) : (
            <div key={m.id} className="animate-rise">
              <div className="flex items-center gap-2 mb-2.5">
                <div className="w-6 h-6 rounded-lg bg-grad grid place-items-center shadow-[0_0_16px_rgba(93,140,255,.4)]">
                  <Bot size={13} className="text-ink" />
                </div>
                <span className="text-[13px] font-semibold">FinSight</span>
                <span className="text-[11px] text-faint">· grounded in your reports</span>
              </div>
              <div className="panel px-5 py-4 space-y-3">
                <p className="text-sm leading-relaxed whitespace-pre-wrap text-slate-200">
                  {m.typed ?? m.content}
                  {m.typed !== undefined && m.typed.length < m.content.length && <span className="caret" />}
                </p>
                {m.citations && m.citations.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1 border-t border-panelEdge">
                    {m.citations.map((c, j) => (
                      <span key={j} className="flex items-center gap-1 text-[10px] font-mono text-mute border border-panelEdge rounded px-1.5 py-0.5 mt-2">
                        <FileText size={10} />{c.filename} · p{c.page_number}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        )}
        {busy && (
          <div className="flex items-center gap-2 text-xs font-mono text-cyan">
            <span className="pulse-dot" /> analyzing your documents…
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="pb-4 pt-1">
        <AskBox input={input} setInput={setInput} onSend={() => send(input)} busy={busy} />
      </div>
    </div>
  );
}
