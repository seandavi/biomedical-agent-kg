/** Shape of graph.json emitted by the agentkg pipeline (SPEC §2/§6). */

export type NodeType =
  | "agent"
  | "paper"
  | "repo"
  | "benchmark"
  | "org"
  | "domain"
  | "toolenv"
  | "database";

export type EdgeRel =
  | "described_by"
  | "implemented_by"
  | "evaluated_on"
  | "built_by"
  | "owned_by"
  | "targets"
  | "built_on"
  | "queries"
  | "cites";

/** How a node entered the catalog (ADR 0003). Agents carry this; round/method
 * distinguishes curated-seed from citation-discovered. */
export interface Provenance {
  method: "awesome_list" | "cocitation" | "survey_harvest";
  round: number; // 0 = curated seed; 1+ = discovery round
  openalex_id?: string;
  evidence?: {
    lists?: string[]; // awesome_list
    cites_catalog?: string[]; // cocitation: agent ids the paper cited
    from_survey?: string; // survey_harvest: the survey paper id
  };
}

/** Every node has id + type; the rest are type-dependent and optional. */
export interface GraphNode {
  id: string;
  type: NodeType;
  // common-ish display fields
  name?: string;
  title?: string;
  one_liner?: string;
  // agent facets (closed-vocab multi-valued attributes)
  exposes?: string[];
  architecture?: string[];
  // type-specific
  venue?: string;
  url?: string;
  ror?: string | null;
  stars?: number;
  language?: string;
  license?: string;
  year?: number;
  cited_by_count?: number;
  in_catalog?: boolean; // external cocitation paper when false (ADR 0003)
  // how this node entered the catalog (ADR 0003)
  provenance?: Provenance;
  // progressive-enhancement profile pointer (SPEC §3.1)
  detail_ref?: string;
  [key: string]: unknown;
}

export interface GraphEdge {
  src: string;
  rel: EdgeRel;
  dst: string;
  primary?: boolean;
  provenance?: { source?: string; evidence?: string } | null;
}

export interface Graph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/** Human-facing label for a node, with sensible fallbacks. */
export function nodeLabel(n: GraphNode): string {
  if (n.name) return n.name;
  if (n.title) return n.title;
  if (n.url) return n.url.replace(/^https?:\/\//, "");
  // strip the typed-id prefix (e.g. "arxiv:2503.10970" -> "2503.10970")
  const colon = n.id.indexOf(":");
  return colon >= 0 ? n.id.slice(colon + 1) : n.id;
}
