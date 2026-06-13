import type { Core, NodeSingular } from "cytoscape";
import { ALL_TYPES, CITES_REL, TYPE_COLOR, TYPE_LABEL } from "./theme";
import type { GraphNode, NodeType } from "./types";

interface FacetToken {
  field: "exposes" | "architecture";
  value: string;
}

export interface FilterState {
  apply: () => void;
}

/**
 * Attribute filters (SPEC: filter ON attributes, traverse THROUGH nodes).
 * Node-type toggles double as the color legend; agent facets narrow agents
 * only; text search matches label/id/one_liner; cites overlay defaults OFF.
 */
export function createFilters(cy: Core, nodes: GraphNode[]): FilterState {
  const typeBox = document.getElementById("type-filters")!;
  const facetBox = document.getElementById("facet-filters")!;
  const searchInput = document.getElementById("search") as HTMLInputElement;
  const citesToggle = document.getElementById("cites-toggle") as HTMLInputElement;
  const statsEl = document.getElementById("stats")!;

  // Only show type chips for types actually present in the data.
  const presentTypes = new Set(nodes.map((n) => n.type));
  const enabledTypes = new Set<NodeType>(
    ALL_TYPES.filter((t) => presentTypes.has(t)),
  );

  for (const type of ALL_TYPES) {
    if (!presentTypes.has(type)) continue;
    const count = nodes.filter((n) => n.type === type).length;
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip active";
    chip.dataset.type = type;
    chip.innerHTML = `<span class="dot" style="background:${TYPE_COLOR[type]}"></span>${TYPE_LABEL[type]} <span class="count">${count}</span>`;
    chip.addEventListener("click", () => {
      if (enabledTypes.has(type)) enabledTypes.delete(type);
      else enabledTypes.add(type);
      chip.classList.toggle("active", enabledTypes.has(type));
      apply();
    });
    typeBox.appendChild(chip);
  }

  // Build facet pool from agent attributes, grouped by kind (exposes / architecture).
  const selectedFacets = new Set<FacetToken>(); // membership by object identity
  let anyFacet = false;

  for (const field of ["exposes", "architecture"] as const) {
    const values = new Set<string>();
    for (const n of nodes) {
      if (n.type !== "agent") continue;
      for (const v of n[field] ?? []) values.add(v);
    }
    if (values.size === 0) continue;
    anyFacet = true;

    const group = document.createElement("div");
    group.className = "facet-group";
    const sub = document.createElement("div");
    sub.className = "facet-sublabel";
    sub.textContent = field;
    group.appendChild(sub);

    const row = document.createElement("div");
    row.className = "chips";
    for (const value of [...values].sort()) {
      const ft: FacetToken = { field, value };
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip facet";
      chip.textContent = ft.value;
      chip.addEventListener("click", () => {
        if (selectedFacets.has(ft)) selectedFacets.delete(ft);
        else selectedFacets.add(ft);
        chip.classList.toggle("active", selectedFacets.has(ft));
        apply();
      });
      row.appendChild(chip);
    }
    group.appendChild(row);
    facetBox.appendChild(group);
  }

  if (!anyFacet) {
    facetBox.innerHTML = `<span class="muted">none in data</span>`;
  }

  searchInput.addEventListener("input", () => apply());
  citesToggle.addEventListener("change", () => apply());

  function agentMatchesFacets(n: GraphNode): boolean {
    if (selectedFacets.size === 0) return true;
    for (const { field, value } of selectedFacets) {
      if ((n[field] ?? []).includes(value)) return true; // OR within facets
    }
    return false;
  }

  function nodeVisible(n: GraphNode, query: string): boolean {
    if (!enabledTypes.has(n.type)) return false;
    if (n.type === "agent" && !agentMatchesFacets(n)) return false;
    if (query) {
      const hay = [n.id, n.name, n.title, n.one_liner]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      if (!hay.includes(query)) return false;
    }
    return true;
  }

  function apply() {
    const query = searchInput.value.trim().toLowerCase();
    const citesOn = citesToggle.checked;

    let visibleNodes = 0;
    cy.nodes().forEach((el: NodeSingular) => {
      const n = el.data("node") as GraphNode;
      const vis = nodeVisible(n, query);
      el.toggleClass("hidden", !vis);
      if (vis) visibleNodes++;
    });

    let visibleEdges = 0;
    cy.edges().forEach((el) => {
      const rel = el.data("rel");
      const endpointsVisible =
        !el.source().hasClass("hidden") && !el.target().hasClass("hidden");
      const relOk = rel !== CITES_REL || citesOn;
      const vis = endpointsVisible && relOk;
      el.toggleClass("hidden", !vis);
      if (vis) visibleEdges++;
    });

    statsEl.textContent = `${visibleNodes} nodes · ${visibleEdges} edges shown`;
  }

  return { apply };
}
