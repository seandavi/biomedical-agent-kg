/** About modal: live catalog stats (from the graph + data/_provenance.json), a short
 * methods summary, acknowledgements, and links. Full methods live in the README. */
import type { Graph } from "./types";

const REPO = "https://github.com/seandavi/biomedical-agent-kg";

const SOURCE_LISTS: [string, string][] = [
  ["zhoujieli/Awesome-LLM-Agents-Scientific-Discovery", "https://github.com/zhoujieli/Awesome-LLM-Agents-Scientific-Discovery"],
  ["AgenticScience/Awesome-Agent-Scientists", "https://github.com/AgenticScience/Awesome-Agent-Scientists"],
  ["AgenticHealthAI/Awesome-AI-Agents-for-Healthcare", "https://github.com/AgenticHealthAI/Awesome-AI-Agents-for-Healthcare"],
  ["ai-boost/awesome-ai-for-science", "https://github.com/ai-boost/awesome-ai-for-science"],
  ["tsinghua-fib-lab/Awesome-AI-Scientists", "https://github.com/tsinghua-fib-lab/Awesome-AI-Scientists"],
];

interface ProvenanceManifest {
  agents_by_provenance?: Record<string, number>;
  openalex_access_date?: string;
}

function stat(value: string | number, label: string): string {
  return `<div class="stat"><span class="stat-num">${value}</span><span class="stat-label">${label}</span></div>`;
}

export async function initAbout(graph: Graph): Promise<void> {
  const overlay = document.getElementById("about")!;
  const openBtn = document.getElementById("about-btn")!;
  const closeBtn = document.getElementById("about-close")!;
  const bodyEl = document.getElementById("about-body")!;

  const agents = graph.nodes.filter((n) => n.type === "agent").length;

  let seed = 0;
  let discovered = 0;
  let accessDate = "";
  try {
    const p: ProvenanceManifest = await fetch(
      `${import.meta.env.BASE_URL}data/_provenance.json`,
    ).then((r) => r.json());
    for (const [k, v] of Object.entries(p.agents_by_provenance ?? {})) {
      if (k.includes("round0")) seed += v;
      else discovered += v;
    }
    accessDate = p.openalex_access_date ?? "";
  } catch {
    seed = agents; // manifest absent — show what we can
  }

  const acks = SOURCE_LISTS.map(
    ([name, url]) => `<li><a href="${url}" target="_blank" rel="noreferrer">${name}</a></li>`,
  ).join("");

  bodyEl.innerHTML = `
    <h2>Biomedical Agent Knowledge Graph</h2>
    <p class="about-lead">A generated, navigable catalog of LLM-based agent systems for
    biomedicine and bioinformatics, and the papers, repos, benchmarks, orgs, tools, and
    databases that connect them.</p>

    <div class="stat-grid">
      ${stat(agents, "agents")}
      ${stat(seed, "from curated lists")}
      ${stat(discovered, "discovered via citations")}
      ${stat(graph.nodes.length, "nodes")}
      ${stat(graph.edges.length, "edges")}
    </div>

    <h3>How it's built</h3>
    <p>A pipeline crawls five community awesome-lists, classifies and grounds each system in
    its README or paper abstract, extracts a typed graph, then <strong>grows itself</strong>
    by mining the citation network — promoting papers that cite ≥2 catalog agents and
    harvesting the reference lists of surveys. Every agent records its provenance
    (curated-seed vs. citation-discovered). Nothing is hand-edited: the data is regenerated
    from the sources${accessDate ? ` (OpenAlex snapshot ${accessDate})` : ""}.</p>
    <p><a href="${REPO}#how-it-works" target="_blank" rel="noreferrer">Full methods &amp; diagram →</a></p>

    <h3>Acknowledgements</h3>
    <p class="about-sub">Seeded from these community-curated lists:</p>
    <ul class="about-acks">${acks}</ul>
    <p class="about-sub">Built on open metadata from
      <a href="https://openalex.org" target="_blank" rel="noreferrer">OpenAlex</a>,
      <a href="https://arxiv.org" target="_blank" rel="noreferrer">arXiv</a>, and
      <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a>.</p>

    <h3>License</h3>
    <p class="about-sub">Code MIT · data
      <a href="${REPO}/blob/main/data/LICENSE" target="_blank" rel="noreferrer">CC0 1.0</a>
      (public domain). Underlying papers and repositories keep their own licenses.</p>

    <div class="about-footer">
      <a class="about-link" href="${REPO}" target="_blank" rel="noreferrer">★ GitHub</a>
      <span>Built by <a href="https://github.com/seandavi" target="_blank" rel="noreferrer">Sean Davis</a></span>
    </div>
  `;

  const open = () => overlay.removeAttribute("hidden");
  const close = () => overlay.setAttribute("hidden", "");
  openBtn.addEventListener("click", open);
  closeBtn.addEventListener("click", close);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !overlay.hasAttribute("hidden")) close();
  });
}
