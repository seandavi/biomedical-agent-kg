# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **Biomedical Agent Knowledge Graph** pipeline — a generated catalog of LLM-based
biomedical/bioinformatics agent systems and the entities worth traversing between them
(papers, repos, benchmarks, orgs, domains, tool collections, databases). The pipeline is
the `agentkg` uv package (`src/agentkg/`); `SPEC.md` is the design source of truth (draft
v0.4) — read it before changing the data model, vocab, or pipeline. `list.md` is the
awesome-list crawl input; `sample_graph.json` is an older example output.

## Running

uv-managed (Python provisioned by uv, ≥3.11). Entry point `agentkg`:

```bash
uv sync                                # install deps + create .venv
uv run agentkg run                     # mock backend (offline) -> graph.json
uv run agentkg run -b vertex           # live Gemini extraction (needs ADC, see .env)
uv run agentkg run -b vertex -n 2      # iterate on first N agents only (token-mindful)
uv run agentkg config                  # print resolved settings
```

Config is layered `.env` > process env > defaults via pydantic-settings (`config.py`):
`KG_*` for app settings, standard `GOOGLE_*` for Vertex (shared with gcloud/ADC). Live
runs use Vertex AI on project `bioc-u24`; Gemini 3.x needs `GOOGLE_CLOUD_LOCATION=global`
(regional endpoints 404). No test suite or linter yet.

`.cache/` holds the iteration token-saver: fetched README/abstracts keyed by url, and
facet outputs keyed by `model+prompt+payload`. Re-running an unchanged prompt costs 0
tokens; editing `FACET_SYSTEM_PROMPT` auto-busts. Delete `.cache/` to force a rebuild.

## Core invariant — fix the generator, never the record

**Everything is generated.** No hand-curated data layer, no per-record override file
(no `corrections.yml`). When output is wrong, you fix the *generator* — the extraction
prompt or `rules.yml` (deterministic, class-level transforms) — then regenerate.
Rules catch **classes, not instances**: `{proteome, proteomic} → proteomics` is allowed;
"Biomni is multi_omics" is not. A per-record patch is a bug, not a fix.

The only human-touched inputs are **extraction prompts** (`backends.FACET_SYSTEM_PROMPT`)
and **`rules.yml`** — currently stood in by `vocab.py`: `DOMAIN_ALIASES`, `guard_vocab()`
(canonicalize + drop OOV), and the class-level reconcile rules in `pipeline.build` (e.g.
`multi_agent` dominates `single_agent` when sources disagree).

## Architecture

Two overlaid graph components: the curated catalog (agents + entities) and the paper
`cites` citation graph (default-OFF overlay — it dominates layout if always on).
**Agents are the spine.** Node vs. attribute rule: you *traverse through* nodes and
*filter on* attributes (benchmark → node; license/stars/language → attribute). A shared
node (specific database, tool collection) exists only once it connects ≥2 agents.

Node types: `Agent`, `Paper`, `Repo`, `Benchmark`, `Org`, `Domain`, `ToolEnv`,
`Database`. Edges: `described_by`, `implemented_by`, `evaluated_on`, `built_by`,
`targets`, `built_on`, `queries`, `cites` (see SPEC §2/§6). `exposes` and `architecture`
are multi-valued **closed-vocab attributes**, NOT edges.

### Pipeline = staged, model-tiered, determinism-bounded

`crawl → parse → resolve → extract facets → expensive edges → rules+vocab guard → emit`.
Stages are tiered by model need (SPEC §12.1): plain fetch/parse and cheap edges use **no
model**; entry-type classification and facet extraction use a **small** model; prose
drafting and expensive edges (`evaluated_on`/`built_on`/`queries`, which carry
`provenance`) use a **large** model.

**The backend seam (`backends.py`):** the model-touched stage sits behind one swappable
interface — `backend.extract_facets(entry) -> candidate dict`. `MockBackend` (default,
offline, keyed off known systems) and `GeminiBackend` (Vertex AI / AI Studio via
`google-genai`) return the **same shape**; vendor is a config line (`Settings.backend`),
not architecture. The fixed `FACET_SYSTEM_PROMPT` holds the vocab — the cache target.

**Determinism boundary:** the backend produces *candidates*; `guard_vocab` + the pipeline
reconcile rules canonicalize them deterministically before serialization. The resolve
stage (`resolve.py`) grounds extraction in real text (arXiv/OpenAlex abstracts, GitHub
READMEs) so facets aren't guessed from titles; failures are non-fatal (empty → the model
under-claims). `resolve.openalex` orgs are the **last remaining mock** in the hot path.

**Recurring agents** (a system appears as both a paper and a repo entry) are merged, not
clobbered: `Graph.add_edge` dedups identical `(src, rel, dst)`, and `build` unions the
multi-valued facets across entries (SPEC §11 dedup discipline).

Classifying entry type is **not a regex** — a known limitation is `*Bench` names
false-positiving as agents (`parse.looks_like_agent`); production does this with the LLM.

### Output shape

`graph.json` = `{nodes: [...], edges: [...]}`; per-node markdown profiles
(`<type>/<slug>.md`: YAML frontmatter + LLM-drafted prose with typed `[[type:slug]]`
wikilinks) are progressive enhancement — the graph is self-sufficient without them.
Frontend is a static Cytoscape.js/sigma.js SPA on Cloudflare Pages (no backend);
a scheduled GitHub Action re-crawls → re-extracts → regenerates → redeploys.

A `_review` log captures low-confidence/vocab-failed extraction. It is **not a human
work queue** — it signals where the *prompt* needs work.

## Conventions

- Vocabularies are **closed** (SPEC §4/§5/§7/§9) and live in `vocab.py` as the
  `EXPOSES`/`ARCH`/`DOMAINS` sets — keep in sync with SPEC. Extending `Domain` or the
  `Database` whitelist is a deliberate edit, never auto-merge from extraction.
- `a2a` = externally addressable by other agents. NOT the same as internally
  multi-agent (that's `architecture ∋ multi_agent`). Don't conflate.
- Expensive edges must carry `{source, evidence}` provenance — it's the audit mechanism
  given nothing is hand-verified.
- Wikilink prefix is required (`[[agent:cellagent]]`); slugs aren't unique across types.
