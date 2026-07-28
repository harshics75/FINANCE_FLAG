import { useEffect, useRef, useState } from "react";

/** Reveals real, already-fetched text progressively, like a live AI response —
 * animated pacing only, never fabricates content. Skips re-animating if the
 * text hasn't actually changed (e.g. on a routine background refetch). */
export default function TypingReveal({ text, speed = 12, className }: {
  text: string; speed?: number; className?: string;
}) {
  const [typed, setTyped] = useState(text);
  const prevText = useRef(text);

  useEffect(() => {
    if (text === prevText.current) return;
    prevText.current = text;
    let i = 0;
    setTyped("");
    const interval = setInterval(() => {
      i += 4;
      setTyped(text.slice(0, i));
      if (i >= text.length) clearInterval(interval);
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <p className={className ?? "text-sm leading-relaxed whitespace-pre-line"}>
      {typed}{typed.length < text.length && <span className="caret" />}
    </p>
  );
}
