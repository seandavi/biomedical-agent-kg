import { ALL_RELS, CITES_REL, EDGE_COLOR, EDGE_LABEL } from "./theme";
import type { GraphEdge } from "./types";

/**
 * Floating edge-type legend in the graph corner. Lists only relations present
 * in the data so the graph reads without clicking. cites renders dashed.
 */
export function createEdgeLegend(host: HTMLElement, edges: GraphEdge[]): void {
  const present = new Set(edges.map((e) => e.rel));
  const rels = ALL_RELS.filter((r) => present.has(r));
  if (rels.length === 0) return;

  const box = document.createElement("div");
  box.id = "edge-legend";
  box.innerHTML =
    `<div class="legend-title">Relations</div>` +
    rels
      .map((rel) => {
        const dashed = rel === CITES_REL ? " dashed" : "";
        return `<div class="legend-row">
          <span class="legend-line${dashed}" style="--c:${EDGE_COLOR[rel]}"></span>
          <span class="legend-label">${EDGE_LABEL[rel]}</span>
        </div>`;
      })
      .join("");
  host.appendChild(box);
}
