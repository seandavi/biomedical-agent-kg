import "./style.css";
import { initAbout } from "./about";
import { initAnalytics, track } from "./analytics";
import { createCy, runLayout } from "./cy";
import { loadGraph, toElements } from "./data";
import { createFilters } from "./filters";
import { createEdgeLegend } from "./legend";
import { type Connection, createPanel } from "./panel";
import type { GraphNode } from "./types";
import { nodeLabel } from "./types";

async function main() {
  initAnalytics();
  const container = document.getElementById("graph")!;

  let graph;
  try {
    graph = await loadGraph();
  } catch (err) {
    container.innerHTML = `<div class="load-error">Could not load the graph.<br><code>${String(err)}</code><br>Run <code>uv run agentkg run</code> then <code>bun run sync-data</code>.</div>`;
    return;
  }

  void initAbout(graph);

  const { elements, nodeById } = toElements(graph);
  const cy = createCy(container, elements);
  // expose for debugging / headless verification
  (window as unknown as { cy: typeof cy }).cy = cy;

  // Adjacency index for the panel's traversable Connections list.
  const connIndex = new Map<string, Connection[]>();
  const push = (id: string, c: Connection) => {
    const list = connIndex.get(id);
    if (list) list.push(c);
    else connIndex.set(id, [c]);
  };
  for (const e of graph.edges) {
    const src = nodeById.get(e.src);
    const dst = nodeById.get(e.dst);
    if (!src || !dst) continue;
    push(e.src, { rel: e.rel, dir: "out", node: dst });
    push(e.dst, { rel: e.rel, dir: "in", node: src });
  }

  const panel = createPanel({
    resolveWikilink: (id) => {
      const n = nodeById.get(id);
      return n ? nodeLabel(n) : null;
    },
    getConnections: (id) => connIndex.get(id) ?? [],
    onNavigate: (id) => selectNode(id, { recenter: true, via: "panel" }),
  });

  const filters = createFilters(cy, graph.nodes);
  filters.apply();
  // Lay out AFTER the first filter pass so hidden (default-off cites) edges are
  // excluded from layout and don't dominate the initial positions (SPEC §2).
  runLayout(cy);

  createEdgeLegend(container, graph.edges);
  panel.clear(); // render the styled empty state on first paint

  function clearFocus() {
    cy.elements().removeClass("selected neighbor labeled faded");
  }

  function focus(id: string) {
    clearFocus();
    const node = cy.getElementById(id);
    if (node.empty()) return;
    // dim everything, then spotlight the node + its closed neighborhood
    const nbh = node.closedNeighborhood();
    cy.elements().addClass("faded");
    nbh.removeClass("faded");
    nbh.nodes().addClass("labeled");
    node.addClass("selected");
    node.connectedEdges().addClass("neighbor");
  }

  function selectNode(id: string, opts: { recenter?: boolean; via?: string } = {}) {
    const node = cy.getElementById(id);
    if (node.empty()) return;
    focus(id);
    const data = node.data("node") as GraphNode;
    panel.show(data);
    track("select_node", { node_type: data.type, node_id: id, via: opts.via ?? "graph" });
    if (opts.recenter) {
      cy.animate({ center: { eles: node }, zoom: Math.max(cy.zoom(), 1) }, { duration: 350 });
    }
  }

  cy.on("tap", "node", (ev) => selectNode(ev.target.id(), { via: "graph" }));
  cy.on("tap", (ev) => {
    if (ev.target === cy) {
      clearFocus();
      panel.clear();
    }
  });

  // hover affordance: reveal the label (and un-dim) without committing a selection
  cy.on("mouseover", "node", (ev) => {
    ev.target.addClass("hovered labeled");
    container.style.cursor = "pointer";
  });
  cy.on("mouseout", "node", (ev) => {
    const n = ev.target;
    n.removeClass("hovered");
    // Keep the label only if the node belongs to the current focus (any non-faded
    // node while a focus is active); otherwise keep the default-labeled hubs.
    const focusActive = cy.elements(".faded").nonempty();
    const keepLabel = focusActive ? !n.hasClass("faded") : n.data("showLabel") === 1;
    if (!keepLabel) n.removeClass("labeled");
    container.style.cursor = "default";
  });

  document.getElementById("fit-btn")!.addEventListener("click", () => {
    runLayout(cy);
    track("reset_view");
  });

  // narrow-screen sidebar drawer
  const menuBtn = document.getElementById("menu-btn")!;
  menuBtn.addEventListener("click", () => document.body.classList.toggle("nav-open"));
  // close the drawer after picking a node on small screens
  cy.on("tap", "node", () => document.body.classList.remove("nav-open"));
}

void main();
