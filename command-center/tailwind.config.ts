import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "rgb(var(--cc-bg) / <alpha-value>)",
        surface: "rgb(var(--cc-surface) / <alpha-value>)",
        text: "rgb(var(--cc-text) / <alpha-value>)",
        muted: "rgb(var(--cc-muted) / <alpha-value>)",
        accent: "rgb(var(--cc-accent) / <alpha-value>)",
        accentstrong: "rgb(var(--cc-accent-strong) / <alpha-value>)",
        border: "rgb(var(--cc-border) / <alpha-value>)",
        danger: "rgb(var(--cc-danger) / <alpha-value>)"
      },
      boxShadow: {
        panel: "0 12px 28px rgba(0, 0, 0, 0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
