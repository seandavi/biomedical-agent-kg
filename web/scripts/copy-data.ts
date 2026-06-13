/**
 * Mirror the pipeline's generated artifacts into the SPA's static assets.
 *
 * The graph is self-sufficient (graph.json); per-node markdown profiles under
 * agents/<slug>.md are progressive enhancement and may not exist yet. We copy
 * whatever is present, non-fatally. Run via predev/prebuild so dev + build
 * always serve the latest generator output without committing it here.
 *
 * The pipeline (agentkg package) and this SPA live in separate worktrees, so we
 * don't assume web/ sits at the repo root: we walk up from web/ to find the
 * directory that actually contains graph.json. Override with KG_GRAPH_JSON
 * (absolute path to graph.json) when the artifacts live somewhere else entirely.
 */
import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const webDir = resolve(here, "..");
const dataDir = join(webDir, "public", "data");

// Node-profile dirs the pipeline may emit (SPEC §3.1). `agents/` is the one in
// use today; the per-type singulars cover the spec's future generalization.
const PROFILE_DIRS = [
  "agents",
  "agent",
  "paper",
  "repo",
  "benchmark",
  "org",
  "domain",
  "toolenv",
  "database",
];

/**
 * Walk up from `start` looking for graph.json, returning the directory that
 * directly contains it. The pipeline emits to a `data/` subdir, so at each
 * ancestor we check both `<dir>/graph.json` and `<dir>/data/graph.json`.
 */
function findArtifactsRoot(start: string): string | null {
  let dir = start;
  for (let i = 0; i < 8; i++) {
    if (existsSync(join(dir, "graph.json"))) return dir;
    if (existsSync(join(dir, "data", "graph.json"))) return join(dir, "data");
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

const override = process.env.KG_GRAPH_JSON;
const graphPath = override ? resolve(override) : null;
const artifactsRoot = graphPath ? dirname(graphPath) : findArtifactsRoot(webDir);

rmSync(dataDir, { recursive: true, force: true });
mkdirSync(dataDir, { recursive: true });

const graph = graphPath ?? (artifactsRoot ? join(artifactsRoot, "graph.json") : null);
if (!graph || !existsSync(graph)) {
  console.warn(
    "[copy-data] WARNING: graph.json not found (looked upward from web/, " +
      "or set KG_GRAPH_JSON). Run `uv run agentkg run` first. SPA will be empty.",
  );
} else {
  cpSync(graph, join(dataDir, "graph.json"));
  console.log(`[copy-data] ${graph} -> public/data/graph.json`);
}

let profileCount = 0;
if (artifactsRoot) {
  for (const type of PROFILE_DIRS) {
    const src = join(artifactsRoot, type);
    if (existsSync(src)) {
      cpSync(src, join(dataDir, type), { recursive: true });
      profileCount++;
      console.log(`[copy-data] ${type}/ -> public/data/${type}/`);
    }
  }
}

// Emit a manifest of available profiles so the SPA can show prose without the
// pipeline having to set detail_ref on each node, and without speculative 404s.
function listMarkdown(dir: string): string[] {
  if (!existsSync(dir)) return [];
  const out: string[] = [];
  for (const ent of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, ent.name);
    if (ent.isDirectory()) out.push(...listMarkdown(full));
    // Forward-slash paths so the manifest matches the SPA's lookups on any OS.
    else if (ent.name.endsWith(".md")) out.push(relative(dataDir, full).replaceAll("\\", "/"));
  }
  return out;
}
const manifest = PROFILE_DIRS.flatMap((t) => listMarkdown(join(dataDir, t))).sort();
writeFileSync(join(dataDir, "profiles.json"), JSON.stringify(manifest));

if (profileCount === 0) {
  console.log("[copy-data] no profile dirs yet (graph is self-sufficient).");
} else {
  console.log(`[copy-data] ${manifest.length} profile(s) -> public/data/profiles.json`);
}
