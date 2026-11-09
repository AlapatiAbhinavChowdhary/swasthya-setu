import { defineConfig, type HttpProxy } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import type { IncomingMessage } from "http";

const createApiProxy = () => ({
  target: "http://127.0.0.1:8000",
  changeOrigin: true,
  bypass: (req: IncomingMessage) => {
    const accept = req.headers?.accept || "";
    if (accept.includes("text/html")) {
      return "/index.html";
    }
  },
});

export default defineConfig({
  plugins: [react(), tailwindcss()],
  appType: "spa",
  server: {
    port: 5173,
    proxy: {
      "/chat": createApiProxy(),
      "/health": createApiProxy(),
      "/coverage": createApiProxy(),
      "/diseases": createApiProxy(),
      "/vaccination": createApiProxy(),
      "/alerts": createApiProxy(),
      "/facilities": createApiProxy(),
      "/languages": createApiProxy(),
      "/feedback": createApiProxy(),
      "/sources": createApiProxy(),
      "/admin/feedback": createApiProxy(),
    },
  },
  preview: {
    port: 4173,
    host: "127.0.0.1",
    proxy: {
      "/chat": createApiProxy(),
      "/health": createApiProxy(),
      "/coverage": createApiProxy(),
      "/diseases": createApiProxy(),
      "/vaccination": createApiProxy(),
      "/alerts": createApiProxy(),
      "/facilities": createApiProxy(),
      "/languages": createApiProxy(),
      "/feedback": createApiProxy(),
      "/sources": createApiProxy(),
      "/admin/feedback": createApiProxy(),
    },
  },
});
