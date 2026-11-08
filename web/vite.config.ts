import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/chat": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
      "/coverage": "http://127.0.0.1:8000",
      "/diseases": "http://127.0.0.1:8000",
      "/vaccination": "http://127.0.0.1:8000",
      "/alerts": "http://127.0.0.1:8000",
      "/facilities": "http://127.0.0.1:8000",
      "/languages": "http://127.0.0.1:8000",
      "/feedback": "http://127.0.0.1:8000",
      "/sources": "http://127.0.0.1:8000",
      "/admin": "http://127.0.0.1:8000",
    },
  },
});
