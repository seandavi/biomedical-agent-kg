import type { EdgeRel, NodeType } from "./types";

/** Per-type node colors. Agents are the spine — given the most saturated hue. */
export const TYPE_COLOR: Record<NodeType, string> = {
  agent: "#e8590c", // spine — warm, dominant
  paper: "#1c7ed6",
  repo: "#343a40",
  benchmark: "#9c36b5",
  org: "#2f9e44",
  domain: "#f08c00",
  toolenv: "#0ca678",
  database: "#3b5bdb",
};

export const TYPE_LABEL: Record<NodeType, string> = {
  agent: "Agent",
  paper: "Paper",
  repo: "Repo",
  benchmark: "Benchmark",
  org: "Org",
  domain: "Domain",
  toolenv: "ToolEnv",
  database: "Database",
};

export const ALL_TYPES: NodeType[] = [
  "agent",
  "paper",
  "repo",
  "benchmark",
  "org",
  "domain",
  "toolenv",
  "database",
];

/** cites is the default-OFF overlay (SPEC §2); everything else is the catalog. */
export const CITES_REL: EdgeRel = "cites";

/** Per-relation edge colors — let the graph be read without clicking. */
export const EDGE_COLOR: Record<EdgeRel, string> = {
  described_by: "#748ffc", // agent → paper
  implemented_by: "#3bc9db", // agent → repo
  evaluated_on: "#f783ac", // agent → benchmark
  built_by: "#69db7c", // agent → org
  targets: "#ffd43b", // agent → domain
  built_on: "#da77f2", // agent → toolenv
  queries: "#4dabf7", // agent → database
  cites: "#39424d", // paper → paper (muted, dashed, default-off)
};

export const EDGE_LABEL: Record<EdgeRel, string> = {
  described_by: "described by",
  implemented_by: "implemented by",
  evaluated_on: "evaluated on",
  built_by: "built by",
  targets: "targets",
  built_on: "built on",
  queries: "queries",
  cites: "cites",
};

export const ALL_RELS: EdgeRel[] = [
  "described_by",
  "implemented_by",
  "evaluated_on",
  "built_by",
  "targets",
  "built_on",
  "queries",
  "cites",
];
