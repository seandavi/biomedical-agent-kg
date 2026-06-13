import type { ElementDefinition } from "cytoscape";
import { CITES_REL } from "./theme";
import type { Graph, GraphEdge, GraphNode } from "./types";
import { nodeLabel } from "./types";

const DATA_URL = `${import.meta.env.BASE_URL}data/graph.json`;

// Node sizing by catalog degree (cites excluded — it's the default-off overlay).
const SIZE_MIN = 16; // leaf node diameter (px)
const SIZE_MAX = 58; // hub cap
const AGENT_BASE = 26; // agents read larger as the spine, even at degree 0
// Label-by-default thresholds (others reveal on hover/focus) — tuned for ~235
// nodes so the dense center stays legible.
const AGENT_LABEL_MIN_DEGREE = 3;
const HUB_LABEL_MIN_DEGREE = 7;

export async function loadGraph(): Promise<Graph> {
  const res = await fetch(DATA_URL);
  if (!res.ok) {
    throw new Error(`Failed to load ${DATA_URL}: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as Graph;
}

/**
 * Convert graph.json into Cytoscape elements. Edges referencing a missing
 * endpoint are dropped (defensively — a dangling edge would crash cytoscape).
 */
export function toElements(graph: Graph): {
  elements: ElementDefinition[];
  nodeById: Map<string, GraphNode>;
} {
  const nodeById = new Map<string, GraphNode>();
  for (const n of graph.nodes) nodeById.set(n.id, n);

  // Catalog degree per node (cites excluded), for sizing + label gating.
  const degree = new Map<string, number>();
  for (const e of graph.edges) {
    if (e.rel === CITES_REL) continue;
    if (nodeById.has(e.src)) degree.set(e.src, (degree.get(e.src) ?? 0) + 1);
    if (nodeById.has(e.dst)) degree.set(e.dst, (degree.get(e.dst) ?? 0) + 1);
  }

  const elements: ElementDefinition[] = [];

  for (const n of graph.nodes) {
    const full = nodeLabel(n);
    // Keep on-graph labels short so dense clusters stay readable; the panel
    // shows the full name/title.
    const label = full.length > 34 ? `${full.slice(0, 32)}…` : full;
    const deg = degree.get(n.id) ?? 0;
    // sqrt dampens mega-hubs; agents get a higher floor so the spine stays prominent.
    const base = n.type === "agent" ? AGENT_BASE : SIZE_MIN;
    const size = Math.min(SIZE_MAX, Math.round(base + 6 * Math.sqrt(deg)));
    // Default-labeled: well-connected agents, plus any strong hub of any type.
    const showLabel =
      (n.type === "agent" && deg >= AGENT_LABEL_MIN_DEGREE) || deg >= HUB_LABEL_MIN_DEGREE;
    elements.push({
      group: "nodes",
      data: {
        id: n.id,
        type: n.type,
        label,
        degree: deg,
        size,
        showLabel: showLabel ? 1 : 0,
        node: n,
      },
    });
  }

  let dropped = 0;
  graph.edges.forEach((e: GraphEdge, i) => {
    if (!nodeById.has(e.src) || !nodeById.has(e.dst)) {
      dropped++;
      return;
    }
    elements.push({
      group: "edges",
      data: {
        id: `e${i}:${e.src}->${e.dst}:${e.rel}`,
        source: e.src,
        target: e.dst,
        rel: e.rel,
        primary: e.primary ?? false,
        edge: e,
      },
    });
  });

  if (dropped > 0) {
    console.warn(`[data] dropped ${dropped} edge(s) with missing endpoints`);
  }

  return { elements, nodeById };
}
