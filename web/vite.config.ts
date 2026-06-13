import { defineConfig } from "vite";

// Static SPA — relative base so it works under any Cloudflare Pages path.
export default defineConfig({
  base: "./",
  build: {
    target: "es2022",
    outDir: "dist",
  },
});
