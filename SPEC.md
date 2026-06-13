# Biomedical Agent Knowledge Graph — Data Spec

**Status:** draft v0.4 · **Artifact type:** fully generated; the *pipeline* is maintained, not the data

A curated catalog of LLM-based biomedical/bioinformatics **agent systems**, with
external connections worth traversing. Agent systems are the spine.

**Everything is generated.** `graph.json` and the per-agent profiles
(`agents/<slug>.md`, frontmatter + LLM-drafted prose) are all produced by the
pipeline. There is **no hand-curated data layer** and no per-record override file.
When output is wrong, you fix the *generator* — the extraction prompt or
`rules.yml` (deterministic, class-level transforms) — and regenerate. Errors are
addressed where the fix generalizes, never patched per-record.

---

## 1. Design principles

1. **Nodes are things you traverse *through*; attributes are things you filter *on*.**
   If linking to an entity lets you reach something non-obvious from another agent,
   it's a node. Otherwise it's an attribute. (License → attribute. Benchmark → node.)
2. **Fully generated; fix the generator, not the record.** All data is produced by the
   pipeline. The only human-touched inputs are extraction prompts and `rules.yml`.
   No `corrections.yml`, no hand-edited records.
3. **Rules catch classes, not instances.** A rule maps `{proteome, proteomic,
   proteomics-research} → proteomics`; it never says "Biomni is multi_omics." The
   former generalizes and is written once; the latter would rot.
4. **Friction-driven granularity.** Add a shared-resource node (a specific database,
   a specific tool) only when it connects ≥2 agents. Until then it stays a count.
5. **Honesty over completeness.** A modality the paper calls "future work" is not the
   same as a shipped one. Prefer to under-claim. Dead repos stay visible. Since
   nothing is hand-verified, **provenance on expensive edges is how quality is
   spot-checked** (§6).

---

## 2. Node types

| Type        | Canonical key            | Role                                    |
|-------------|--------------------------|-----------------------------------------|
| `Agent`     | slug                     | spine — the agent system                |
| `Paper`     | DOI / arXiv / bioRxiv ID | intellectual artifact + lineage         |
| `Repo`      | GitHub URL               | code artifact + health/freshness signal |
| `Benchmark` | slug (controlled)        | shared evaluation target                |
| `Org`       | ROR (via OpenAlex)       | building lab/institution                |
| `Domain`    | slug (controlled vocab)  | primary browse axis                     |
| `ToolEnv`   | slug                     | tool/database *collection* (not tools)  |
| `Database`  | slug (curated whitelist) | shared public data resource             |

Explicitly **not** nodes (they are attributes): license, language, star count,
individual minor tools/libraries (scanpy, pandas), individual minor databases.

---

## 3. Agent node

```yaml
Agent:
  slug: biomni                      # stable id
  name: Biomni
  aliases: [Biomni-A1]
  one_liner: General-purpose biomedical AI agent.
  # ---- facets (filter/color on these; do NOT traverse) ----
  exposes: [library, mcp]           # closed vocab §4
  architecture: [multi_agent, self_evolving]  # closed vocab §5
  # ---- edges (traverse through these; see §6) ----
  # described_by, implemented_by, evaluated_on, built_by,
  # targets, built_on, queries  -> stored as edge records, not inline
```

`exposes` and `architecture` are **multi-valued, closed-vocab attributes**, not edges.
Everything in §6 is an edge record.

### 3.1 Generated profiles (textual richness) — derived & optional

**The graph is self-sufficient without any markdown.** Every node carries `one_liner`;
the SPA can run with zero profile files. Profiles are *progressive enhancement*,
generated and backfilled after the graph exists — never a prerequisite.

The substance, when present, lives in one **generated** markdown file per node,
`<type>/<slug>.md`: YAML frontmatter (structured facets, also consumed when building
the graph) plus an **LLM-drafted prose body**. A node *optionally* gains a `detail_ref`
pointer once its file is generated; the SPA fetches and renders it in the right-hand
panel on node click, falling back to `one_liner` if absent (Pages serves it static,
parsed client-side).

**Any node type *can* have a markdown counterpart; generation is opt-in per type.**
Start with `agents/` (where prose value is highest). Backfill `benchmarks/`, `orgs/`,
etc. later only if they earn a body — orgs/domains/databases are bodyless node records
until proven otherwise. Backfill = "run the profile pass over nodes lacking one";
incremental, re-runnable, non-blocking.

Both frontmatter and body are generated from the list entry + paper abstract + README.
Weak description → improve the summarization prompt, not the file. Files are
version-controlled and diffable, so regenerations are reviewable in PRs.

### 3.2 Wikilink convention (in-panel navigation)

Prose bodies are made navigable: the pipeline writes typed wikilinks into the prose,
and the SPA resolves a clicked link to selecting + recentering that node (turning the
side panel from a dead-end blob into a way to traverse).

```
[[type:slug]]               → [[agent:cellagent]]  [[benchmark:bixbench]]
[[type:slug|display text]]  → [[agent:biomni|Biomni's environment]]
```

- **Typed prefix is required** — slugs aren't unique across types (a paper and an agent
  may collide); `type:slug` resolves unambiguously to a node id.
- Papers use canonical id: `[[paper:10.1101-2025.xx]]`.
- A link that doesn't resolve to a real node → rendered as plain text and logged to
  `_review` (a generated link pointing nowhere is an extraction signal).

Wikilinks are generated for navigation, not authored. (A future option: cross-check
inline wikilinks against structured edges as an audit signal — deferred; not needed
for v1.)

---

## 4. Controlled vocab: `exposes` (interface modality)

A system commonly exposes several. Presence-only for v1; add `status` later only
where the gap is glaring (friction-driven).

| Value      | Meaning                                                        |
|------------|----------------------------------------------------------------|
| `library`  | importable package (Python/R)                                  |
| `cli`      | command-line entry point                                       |
| `mcp`      | exposes an MCP server / MCP tools                              |
| `a2a`      | **externally addressable** by other agents (interop protocol) |
| `skills`   | SKILL.md-style composable capability files                    |
| `web_ui`   | hosted interface / chatbot                                     |
| `api`      | hosted REST/HTTP service                                       |
| `notebook` | Jupyter / notebook-native                                      |

**`a2a` discipline:** reserve for *externally exposed* agent interop (the system can
be driven by other agents). "Internally multi-agent" is NOT a2a — that's
`architecture ∋ multi_agent`. Don't conflate "I orchestrate sub-agents" with
"I can be orchestrated."

Optional future shape if status matters:
`exposes: [{modality: mcp, status: available}, {modality: a2a, status: planned}]`
where `status ∈ {available, announced, planned}`.

---

## 5. Controlled vocab: `architecture`

| Value           | Meaning                                            |
|-----------------|----------------------------------------------------|
| `single_agent`  | one LLM loop                                        |
| `multi_agent`   | internal planner/executor/verifier decomposition   |
| `rag`           | retrieval-augmented over literature/structured data |
| `self_evolving` | learns/updates its own tools or workflows           |
| `tool_registry` | built on a shared external tool registry            |

---

## 6. Edge types

| Edge            | From → To           | Extraction cost | Notes                              |
|-----------------|---------------------|-----------------|------------------------------------|
| `described_by`  | Agent → Paper       | cheap           | link present in list; see canonical flag |
| `implemented_by`| Agent → Repo        | cheap           | link present in list               |
| `evaluated_on`  | Agent → Benchmark   | **expensive**   | read paper/README; LLM + provenance |
| `built_by`      | Agent → Org         | medium          | OpenAlex author→institution        |
| `targets`       | Agent → Domain      | medium          | map to controlled vocab            |
| `built_on`      | Agent → ToolEnv     | **expensive**   | read paper/README; LLM + provenance |
| `queries`       | Agent → Database    | **expensive**   | curated whitelist only             |
| `cites`         | Paper → Paper       | medium          | OpenAlex; **first-class** (see §6.2) |

**Canonical paper flag.** `described_by` is many-to-many (preprint → revision →
benchmark companion). Exactly one edge per agent carries `primary: true` — the UI's
default citation and "the paper." Pipeline picks primary by heuristic (peer-reviewed
> latest preprint > earliest), refinable in prompt/rules.

**Provenance on expensive edges.** Every `evaluated_on` / `built_on` / `queries` edge
records `{source: <list-or-paper>, evidence: <span>}`. Not for display — it's how you
audit extraction quality and decide where the prompt needs tightening, given nothing
is hand-verified.

### 6.2 The `cites` layer

`cites` (Paper → Paper, from OpenAlex) makes the graph two overlaid components: the
curated catalog (agents + entities) and the paper citation graph. This is the richest
view but the citation edges will **dominate layout** if always on.

**Rendering requirement (not just data):** the citation layer must be toggleable and
default **off**. The catalog is the primary view; `cites` is an opt-in overlay.

**Phasing:** ship `described_by` + `implemented_by` first (near-free). Layer
`built_by` / `targets` next (OpenAlex + vocab). Add expensive `evaluated_on` /
`built_on` / `queries` with provenance. `cites` last, behind the toggle.

---

## 7. Controlled vocab: `Domain`

Closed taxonomy (curated, not seeded-from-extraction). Seed set:

`single_cell` · `spatial` · `proteomics` · `genomics_db` · `multi_omics` ·
`perturbation` · `drug_discovery` · `medical_imaging` · `clinical_qa` ·
`literature` · `hypothesis_gen` · `protein_structure`

Extend deliberately via PR, not auto-merge.

---

## 8. `ToolEnv` (collection node)

Tool/database *collections*, never individual tools. Avoids hairball where
high-degree nodes (scanpy, NCBI) dominate and mean nothing.

```yaml
ToolEnv:
  slug: biomni-e1
  name: Biomni-E1
  tool_count: 150        # attribute, not 150 edges
  db_count: 59           # attribute, not 59 edges
  kind: environment      # environment | tool_registry | skill_set
```

Examples: `biomni-e1` (environment), `tooluniverse` (registry, 600+),
`labclaw` (skill_set, 211 SKILL.md).

---

## 9. `Database` whitelist (shared public resources only)

Individual-database nodes are reserved for **named, public, shared** resources that
create cross-system edges. A node only exists once ≥2 agents touch it.

Seed whitelist: `clinvar` · `gnomad` · `geo` · `sra` · `uniprot` · `openalex` ·
`pubmed` · `clinicaltrials` · `gwas_catalog` · `cpic` · `alphamissense` · `civic` ·
`oncokb`

Anything not on the whitelist → folded into the owning `ToolEnv`'s `db_count`.

---

## 10. `Repo` attributes (freshness / health)

```yaml
Repo:
  url: https://github.com/snap-stanford/Biomni
  stars: 0          # refreshed each crawl
  license: ~
  last_commit: ~    # staleness signal — dead repos stay visible
  language: ~
```

A scheduled crawl refreshes these; a stale `last_commit` is surfaced in the UI, not
hidden. This is the answer to landscape-map rot.

---

## 11. Sources (awesome-lists to crawl)

| List                                              | Emphasis                  |
|---------------------------------------------------|---------------------------|
| zhoujieli/Awesome-LLM-Agents-Scientific-Discovery | bioinformatics agents     |
| AgenticScience/Awesome-Agent-Scientists           | agents-for-science        |
| AgenticHealthAI/Awesome-AI-Agents-for-Healthcare  | healthcare + MCP servers  |
| ai-boost/awesome-ai-for-science                   | tooling / infra / MCP     |
| tsinghua-fib-lab/Awesome-AI-Scientists            | AI-scientist survey       |

Same system appears across lists → dedup on `described_by` DOI / `implemented_by`
repo URL as canonical join keys.

---

## 12. Pipeline shape

```
crawl lists ──► LLM extraction ──► resolve ──────────────► graph.json + agents/<slug>.md
  (raw md)       (facets, edges,     (DOI / repo URL /         (ALL generated)
                  prose drafts)       OpenAlex, citations)
                     ▲
                     │
              prompts + rules.yml   ← the ONLY human-touched inputs
              (improved when output is visibly wrong; class-level, not per-record)
                                                      │
                                                      ▼
                                  Cytoscape.js / sigma.js SPA on Cloudflare Pages
                                  (frontend-only; reads static graph.json + .md)
```

Scheduled GitHub Action re-crawls → re-extracts → regenerates everything → redeploys
Pages. No backend. No hand-edited data. Same shape as the research-passport SPA and the
omicidx federated catalog — but here the manifests are generated, not authored.

A `_review` log captures extraction that failed vocab guards or looked low-confidence.
It is **not a human work queue** — it's a signal for where the *prompt* needs work.

---

## 12.1 Runtime & execution model

The pipeline is a **headless, scheduled job** — the canonical Claude Agent SDK
workload (high input / low output: fetch large markdown + abstracts, emit terse JSON
+ short prose). It runs non-interactively via the SDK, not in a chat session.

**Billing posture (as of June 2026):** from June 15, 2026, Agent SDK / headless /
GitHub Actions usage draws from the plan's **separate monthly credit pool** (Max 20x:
$200/mo, no rollover), metered at API rates, *not* competing with interactive
sessions. This workload is cheap relative to that budget; the cheap-edge pass needs no
model at all. Two cost levers to use:

- **Prompt caching** — the extractor's system prompt + vocab definitions are fixed
  across all entries; cache reads bill at ~0.1× input. Structure the extraction call
  so the static instructions are cached and only the per-entry payload varies.
- **Model tiering** — mechanical extraction (facets, cheap edges) on a small/fast
  model; reserve a larger model only for prose drafting and the expensive edges where
  judgment matters. (Same tiered-model discipline as the Claude Code subagent setup.)

**Stages, by model need:**

| Stage                              | Model? | Notes                              |
|------------------------------------|--------|------------------------------------|
| crawl lists → raw markdown         | no     | plain fetch                        |
| parse entries (title/url/meta)     | no     | deterministic; regular markdown    |
| **classify entry type**            | small  | agent vs paper vs benchmark — NOT a regex (stub finding: `*Bench` names false-positive as agents) |
| cheap edges (paper/repo links)     | no     | deterministic once type known      |
| resolve (DOI / repo / OpenAlex)    | no     | API calls                          |
| extract facets (exposes/arch/dom)  | small  | structured output, vocab-guarded   |
| expensive edges (+ provenance)     | large  | read abstract/README; cite span    |
| draft profile prose + wikilinks    | large  | per node; backfillable             |
| apply `rules.yml` + vocab guards   | no     | deterministic post-process         |
| emit graph.json + `<type>/<slug>.md` | no   | serialize                          |

Determinism boundary: everything model-touched produces *candidates*; `rules.yml`
canonicalizes and vocab-guards them deterministically before serialization, so the
same inputs + same prompts + same rules yield a stable graph (modulo model
nondeterminism, which provenance + `_review` make auditable).

---


## 13. Open questions

Resolved: ✅ fully-generated (no curation) · ✅ canonical `primary` paper flag ·
✅ `cites` first-class + default-off toggle · ✅ provenance on expensive edges ·
✅ LLM-drafted profiles · ✅ markdown derived/optional, graph self-sufficient ·
✅ wikilinks as generated in-panel navigation (`[[type:slug]]`).

Still open:
- [ ] `exposes` status (presence-only vs. {available/announced/planned}) — defer to
      presence-only for v1.
- [ ] Org resolution: ROR-strict (clean, drops startups/labs like FutureHouse,
      ScienceMachine) vs. freeform-with-aliases (messier, complete). Leaning freeform
      + alias table in `rules.yml`.
- [ ] Canonical-paper heuristic: confirm peer-reviewed > latest-preprint > earliest.
- [ ] `_review` log format — confidence threshold that routes an edge into it.
