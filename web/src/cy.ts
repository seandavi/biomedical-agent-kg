import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import fcose from "cytoscape-fcose";
import { CITES_REL, EDGE_COLOR, TYPE_COLOR } from "./theme";
import type { EdgeRel } from "./types";

cytoscape.use(fcose);

export const LAYOUT = {
  name: "fcose",
  quality: "proof",
  animate: true,
  animationDuration: 600,
  randomize: true,
  // Tuned for ~235 nodes: stronger repulsion + longer edges spread the dense
  // center; gravity keeps loosely-connected components from drifting off-screen.
  nodeRepulsion: 14000,
  idealEdgeLength: 120,
  nodeSeparation: 110,
  gravity: 0.3,
  gravityRange: 3.0,
  numIter: 3000,
  packComponents: true,
  padding: 50,
} as const;

function nodeColorSelectors() {
  return Object.entries(TYPE_COLOR).map(([type, color]) => ({
    selector: `node[type = "${type}"]`,
    style: { "background-color": color, "border-color": color },
  }));
}

function edgeColorSelectors() {
  return (Object.entries(EDGE_COLOR) as [EdgeRel, string][]).map(([rel, color]) => ({
    selector: `edge[rel = "${rel}"]`,
    style: { "line-color": color, "target-arrow-color": color },
  }));
}

/** Re-run the force layout (used by the "Reset view" button). */
export function runLayout(cy: Core): void {
  cy.layout(LAYOUT as cytoscape.LayoutOptions).run();
}

export function createCy(
  container: HTMLElement,
  elements: ElementDefinition[],
): Core {
  return cytoscape({
    container,
    elements,
    wheelSensitivity: 0.2,
    style: [
      {
        selector: "node",
        style: {
          label: "data(label)",
          color: "#ced4da",
          "font-size": 10,
          "font-family": "system-ui, sans-serif",
          "text-wrap": "wrap",
          "text-max-width": "110px",
          "text-valign": "bottom",
          "text-margin-y": 4,
          "text-opacity": 0, // labels off by default; gated by showLabel below
          "text-outline-color": "#0d1117",
          "text-outline-width": 2,
          width: "data(size)", // degree-scaled in data.ts (hubs bigger)
          height: "data(size)",
          "border-width": 2,
          "border-color": "#0d1117",
          "background-opacity": 1,
        },
      },
      ...nodeColorSelectors(),
      {
        // agents are the spine — bold white labels when shown
        selector: 'node[type = "agent"]',
        style: { "font-weight": "bold", color: "#fff", "font-size": 12 },
      },
      {
        // only well-connected nodes are labeled by default (declutter ~235-node center)
        selector: "node[showLabel = 1]",
        style: { "text-opacity": 1 },
      },
      {
        selector: "edge",
        style: {
          width: 1.5,
          "line-opacity": 0.7,
          "target-arrow-shape": "triangle",
          "arrow-scale": 0.8,
          "curve-style": "bezier",
        },
      },
      ...edgeColorSelectors(),
      {
        // targets (agent→domain) is by far the densest relation; thin + fade it
        // so the rarer structural edges aren't lost in the hairball.
        selector: 'edge[rel = "targets"]',
        style: { width: 1, "line-opacity": 0.4 },
      },
      {
        // primary (canonical) edges read a touch heavier
        selector: "edge[?primary]",
        style: { width: 2.5, "line-opacity": 1 },
      },
      {
        selector: `edge[rel = "${CITES_REL}"]`,
        style: { "line-style": "dashed", width: 1, "line-opacity": 0.5 },
      },
      // --- interaction states (order matters: later wins) ---
      {
        selector: ".faded",
        style: { opacity: 0.1, "text-opacity": 0 },
      },
      {
        // focused edges keep their relation color but read brighter + thicker
        selector: ".neighbor",
        style: { width: 3.5, "line-opacity": 1, opacity: 1 },
      },
      {
        selector: "node.labeled",
        style: { "text-opacity": 1, opacity: 1 },
      },
      {
        selector: "node.hovered",
        style: { opacity: 1, "text-opacity": 1, "border-color": "#fff", "border-width": 3 },
      },
      {
        selector: "node.selected",
        style: {
          "border-color": "#fff",
          "border-width": 4,
          "text-opacity": 1,
          opacity: 1,
          "z-index": 999,
          "font-weight": "bold",
        },
      },
      {
        // filtered-out elements are removed from layout entirely
        selector: ".hidden",
        style: { display: "none" },
      },
    ],
    // No auto-layout: nodes start preset; main.ts runs the force layout only
    // after the first filter pass, so the default-off cites overlay (SPEC §2)
    // doesn't dominate the initial positions.
    layout: { name: "preset" },
  });
}
