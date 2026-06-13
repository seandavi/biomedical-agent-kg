import { marked } from "marked";
import { EDGE_COLOR, EDGE_LABEL, TYPE_COLOR, TYPE_LABEL } from "./theme";
import type { EdgeRel, GraphNode } from "./types";
import { nodeLabel } from "./types";

/** One traversable connection from the selected node. */
export interface Connection {
  rel: EdgeRel;
  dir: "out" | "in";
  node: GraphNode;
}

const DATA_BASE = `${import.meta.env.BASE_URL}data/`;

/** Cache fetched profiles by node id (also remembers misses to avoid re-fetch). */
const profileCache = new Map<string, string | null>();

/**
 * Set of available profile paths (e.g. "agents/txagent.md"), written by
 * copy-data. Lets us show prose without the pipeline setting detail_ref, and
 * without speculative 404s. Loaded once, lazily.
 */
let manifest: Set<string> | null = null;
let manifestLoad: Promise<Set<string>> | null = null;
function loadManifest(): Promise<Set<string>> {
  if (manifest) return Promise.resolve(manifest);
  if (!manifestLoad) {
    manifestLoad = fetch(`${DATA_BASE}profiles.json`)
      .then((r) => (r.ok ? (r.json() as Promise<string[]>) : []))
      .then((paths) => (manifest = new Set(paths)))
      .catch(() => {
        // Transient failure: don't cache the miss — let a later selection retry.
        manifestLoad = null;
        return new Set<string>();
      });
  }
  return manifestLoad;
}

/**
 * Turn [[type:slug]] / [[type:slug|display]] into intercepted anchors, then
 * render markdown. Display text prefers an explicit label, else the resolved
 * node's name, else the bare slug — never the internal "type:slug" id.
 * Unresolvable targets are left as plain text (SPEC §3.2).
 */
function renderMarkdown(md: string, resolveLabel: (id: string) => string | null): string {
  const withLinks = md.replace(
    /\[\[([a-z_]+:[^\]|]+?)(?:\|([^\]]+))?\]\]/g,
    (_m, rawTarget: string, display?: string) => {
      const target = rawTarget.trim();
      const slug = target.slice(target.indexOf(":") + 1);
      const label = resolveLabel(target);
      const text = (display?.trim() || label || slug).trim();
      if (label !== null) {
        // Emit an HTML anchor (marked passes inline HTML through) rather than
        // markdown link syntax, so a label containing []() can't break it.
        return `<a href="#nav:${encodeURIComponent(target)}">${escapeHtml(text)}</a>`;
      }
      return escapeHtml(text); // dangling link -> plain text (the slug, not the raw id)
    },
  );
  return marked.parse(withLinks, { async: false }) as string;
}

function profilePath(n: GraphNode, available: Set<string>): string | null {
  // detail_ref wins when the pipeline sets it (SPEC §3.1).
  if (typeof n.detail_ref === "string" && n.detail_ref) {
    return n.detail_ref.replace(/^\.?\//, "");
  }
  // Otherwise consult the manifest: derive <slug> from the "type:slug" id and
  // match a known profile file. No guessing against the network → no 404s.
  const colon = n.id.indexOf(":");
  if (colon < 0) return null;
  const slug = n.id.slice(colon + 1);
  if (/[/\\]/.test(slug)) return null;
  // try plural-type dir first (agents/), then singular (agent/)
  for (const cand of [`${n.type}s/${slug}.md`, `${n.type}/${slug}.md`]) {
    if (available.has(cand)) return cand;
  }
  return null;
}

async function fetchProfile(n: GraphNode): Promise<string | null> {
  if (profileCache.has(n.id)) return profileCache.get(n.id)!;
  const available = await loadManifest();
  const path = profilePath(n, available);
  if (!path) {
    profileCache.set(n.id, null);
    return null;
  }
  try {
    const res = await fetch(DATA_BASE + path);
    const body = res.ok ? await res.text() : null;
    profileCache.set(n.id, body);
    return body;
  } catch {
    profileCache.set(n.id, null);
    return null;
  }
}

function chip(label: string, value: string): string {
  return `<span class="meta-chip" title="${label}">${escapeHtml(value)}</span>`;
}

function escapeHtml(s: string): string {
  return s.replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!,
  );
}

/** Structured summary shown above the prose (or alone, when no profile exists). */
function structuredHeader(n: GraphNode): string {
  const color = TYPE_COLOR[n.type] ?? "#666";
  const rows: string[] = [];

  if (n.one_liner) rows.push(`<p class="one-liner">${escapeHtml(n.one_liner)}</p>`);

  const facets: string[] = [];
  if (n.venue) facets.push(chip("venue", n.venue));
  if (typeof n.stars === "number") facets.push(chip("stars", `★ ${n.stars}`));
  if (n.language) facets.push(chip("language", n.language));
  if (n.license) facets.push(chip("license", n.license));
  for (const e of n.exposes ?? []) facets.push(chip("exposes", e));
  for (const a of n.architecture ?? []) facets.push(chip("architecture", a));
  if (facets.length) rows.push(`<div class="meta-chips">${facets.join("")}</div>`);

  const url = typeof n.url === "string" ? n.url : undefined;
  const link = url
    ? `<a class="ext-link" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(url)}</a>`
    : "";

  return `
    <span class="type-tag" style="background:${color}">${TYPE_LABEL[n.type] ?? n.type}</span>
    <h2>${escapeHtml(nodeLabel(n))}</h2>
    <code class="node-id">${escapeHtml(n.id)}</code>
    ${rows.join("\n")}
    ${link}
  `;
}

/** Clickable, relation-grouped connection list — traversal without profiles. */
function renderConnections(conns: Connection[]): string {
  if (conns.length === 0) return "";

  const groups = new Map<string, Connection[]>();
  for (const c of conns) {
    const key = `${c.dir}:${c.rel}`;
    (groups.get(key) ?? groups.set(key, []).get(key)!).push(c);
  }

  const sections = [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, items]) => {
      const [dir, rel] = key.split(":") as ["out" | "in", EdgeRel];
      const arrow = dir === "out" ? "→" : "←";
      const heading = `${arrow} ${EDGE_LABEL[rel]}`;
      const rows = items
        .map((c) => {
          const color = TYPE_COLOR[c.node.type] ?? "#666";
          return `<a class="conn" href="#nav:${encodeURIComponent(c.node.id)}">
            <span class="conn-dot" style="background:${color}"></span>
            <span class="conn-label">${escapeHtml(nodeLabel(c.node))}</span>
            <span class="conn-type">${TYPE_LABEL[c.node.type] ?? c.node.type}</span>
          </a>`;
        })
        .join("");
      return `<div class="conn-group">
        <div class="conn-heading" style="--c:${EDGE_COLOR[rel]}">${heading}</div>
        ${rows}
      </div>`;
    })
    .join("");

  return `<div class="connections"><div class="section-label">Connections</div>${sections}</div>`;
}

export interface PanelDeps {
  /** Return the node's display label if it exists, else null (dangling link). */
  resolveWikilink: (id: string) => string | null;
  getConnections: (id: string) => Connection[];
  onNavigate: (id: string) => void;
}

export function createPanel(deps: PanelDeps) {
  const panel = document.getElementById("panel")!;
  const body = document.getElementById("panel-body")!;
  const closeBtn = document.getElementById("panel-close")!;

  closeBtn.addEventListener("click", () => clear());

  body.addEventListener("click", (ev) => {
    const a = (ev.target as HTMLElement).closest("a[href^='#nav:']");
    if (!a) return;
    ev.preventDefault();
    const href = (a as HTMLAnchorElement).getAttribute("href")!;
    deps.onNavigate(decodeURIComponent(href.slice("#nav:".length)));
  });

  function clear() {
    // Drop the current id so an in-flight fetchProfile() bails instead of
    // appending stale prose into the emptied panel (the close button hits this).
    delete panel.dataset.current;
    panel.classList.add("empty");
    body.innerHTML = `<div class="empty-state">
      <div class="empty-glyph">◍</div>
      <p>Select a node to inspect it</p>
      <p class="empty-sub">Agents, papers, repos, benchmarks, orgs &amp; domains</p>
    </div>`;
  }

  async function show(n: GraphNode) {
    panel.classList.remove("empty");
    body.innerHTML = structuredHeader(n) + renderConnections(deps.getConnections(n.id));

    const md = await fetchProfile(n);
    // Bail if a different node was selected while we awaited.
    if (!panel.dataset.current || panel.dataset.current !== n.id) return;
    if (md) {
      const prose = document.createElement("div");
      prose.className = "prose";
      // drop YAML frontmatter — facets are already shown in the header
      const stripped = md.replace(/^---\n[\s\S]*?\n---\n/, "");
      prose.innerHTML = renderMarkdown(stripped, deps.resolveWikilink);
      body.appendChild(prose);
    }
  }

  return {
    show(n: GraphNode) {
      panel.dataset.current = n.id;
      void show(n);
    },
    clear,
  };
}
