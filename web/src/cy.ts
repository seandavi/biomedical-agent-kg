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
  nodeRepulsion: 8000,
  idealEdgeLength: 90,
  nodeSeparation: 80,
  padding: 40,
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
          "text-opacity": 0, // non-agent labels off by default (declutter dense clusters)
          "text-outline-color": "#0d1117",
          "text-outline-width": 2,
          width: 24,
          height: 24,
          "border-width": 2,
          "border-color": "#0d1117",
          "background-opacity": 1,
        },
      },
      ...nodeColorSelectors(),
      {
        // agents are the spine — larger, always labeled
        selector: 'node[type = "agent"]',
        style: {
          width: 42,
          height: 42,
          "font-size": 13,
          "font-weight": "bold",
          color: "#fff",
          "text-opacity": 1,
        },
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
    layout: LAYOUT as cytoscape.LayoutOptions,
  });
}
