import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { akashicPlugin } from "./vite-plugin-akashic";

const kbRoot = process.env.AKASHIC_KB_ROOT ?? process.cwd();
const distDir = process.env.AKASHIC_DIST_DIR ?? "dist";
const base = process.env.AKASHIC_BASE ?? "./";
const port = Number(process.env.AKASHIC_PORT ?? 6969);

export default defineConfig({
  plugins: [react(), akashicPlugin(kbRoot)],
  base,
  build: {
    outDir: distDir,
    emptyOutDir: true,
  },
  server: {
    host: "127.0.0.1",
    port,
  },
  worker: {
    format: "es",
  },
  optimizeDeps: {
    include: ["monaco-editor"],
  },
});
