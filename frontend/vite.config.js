import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During `npm run dev`, /api requests proxy to the Flask server on :5001
// so the browser only ever talks to one origin (no CORS headaches).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    host: true,
    proxy: {
      "/api": "http://localhost:5001",
    },
  },
  build: {
    outDir: "dist",
  },
});
