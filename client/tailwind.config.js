/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0D0D0D",
        surface: "#1A1A1A",
        panel: "#111111",
        accent: "#FF6B2B",
        accentAlt: "#138808",
        textMain: "#E8E8E8",
        muted: "#888888",
        error: "#FF4444",
        warning: "#FFB800",
        success: "#00C853",
      },
      fontFamily: {
        ui: ["JetBrains Mono", "monospace"],
        editor: ["Fira Code", "monospace"],
      },
      boxShadow: {
        pane: "0 8px 30px rgba(0, 0, 0, 0.35)",
      },
      keyframes: {
        pulseAccent: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(255, 107, 43, 0.45)" },
          "70%": { boxShadow: "0 0 0 12px rgba(255, 107, 43, 0)" },
        },
      },
      animation: {
        pulseAccent: "pulseAccent 1.6s infinite",
      },
    },
  },
  plugins: [],
};
