/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: "#05070D",                    // page background (near-black)
        panel: "rgba(16,20,34,0.55)",      // glass card fill
        panelHi: "rgba(22,27,46,0.72)",    // glass card fill, hovered
        panelEdge: "rgba(146,160,255,0.13)",   // borders/dividers
        panelEdgeHi: "rgba(146,160,255,0.28)", // borders, hovered/focused
        violet: "#7B78FF",     // primary accent
        cyan: "#33D6FF",       // primary accent, secondary
        amber: "#FFB347",      // figure color / warnings
        up: "#3EE6A8",         // positive delta
        down: "#FF7A93",       // negative delta
        mute: "#8B94B5",       // secondary text
        faint: "#5A6284"       // tertiary text
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"]
      },
      backgroundImage: {
        grad: "linear-gradient(120deg, #7B78FF 0%, #33D6FF 100%)"
      }
    }
  },
  plugins: []
};
