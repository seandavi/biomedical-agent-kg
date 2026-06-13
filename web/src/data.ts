import type { ElementDefinition } from "cytoscape";
import type { Graph, GraphEdge, GraphNode } from "./types";
import { nodeLabel } from "./types";

const DATA_URL = `${import.meta.env.BASE_URL}data/graph.json`;

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

  const elements: ElementDefinition[] = [];

  for (const n of graph.nodes) {
    const full = nodeLabel(n);
    // Keep on-graph labels short so dense clusters stay readable; the panel
    // shows the full name/title.
    const label = full.length > 34 ? `${full.slice(0, 32)}…` : full;
    elements.push({
      group: "nodes",
      data: {
        id: n.id,
        type: n.type,
        label,
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
