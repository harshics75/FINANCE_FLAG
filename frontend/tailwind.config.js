/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: "#0B1220",        // page background (terminal navy-black)
        panel: "#111A2E",      // card background
        panelEdge: "#1E2A44",  // borders/dividers
        amber: "#FFB020",      // signature figure color (terminal amber)
        up: "#2DD4BF",         // positive delta
        down: "#F87171",       // negative delta
        mute: "#8CA0C6"        // secondary text
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"]
      }
    }
  },
  plugins: []
};
