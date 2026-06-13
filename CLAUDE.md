# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Design-stage repo for a **Biomedical Agent Knowledge Graph** — a generated catalog of
LLM-based biomedical/bioinformatics agent systems and the entities worth traversing
between them (papers, repos, benchmarks, orgs, domains, tool collections, databases).
Currently three files: the spec (`SPEC.md`), a runnable pipeline stub (`parse_stub.py`),
and a sample output (`sample_graph.json`). No build system, no deps beyond Python stdlib,
not a git repo yet.

`SPEC.md` is the source of truth (draft v0.4). Read it before changing the data model,
vocab, or pipeline — `parse_stub.py` is a concrete, partial realization of it.

## Running

```bash
python3 parse_stub.py        # reads list.md (NOT present) -> writes graph.json, summary to stderr
```

The stub crawls a local `list.md` (an awesome-list markdown file) that is not checked in;
supply one to run end-to-end, or point `crawl()` at a path. `sample_graph.json` is a
committed example of the output shape (67 nodes / 27 edges). No test suite, linter, or
package config exists yet.

## Core invariant — fix the generator, never the record

**Everything is generated.** No hand-curated data layer, no per-record override file
(no `corrections.yml`). When output is wrong, you fix the *generator* — the extraction
prompt or `rules.yml` (deterministic, class-level transforms) — then regenerate.
Rules catch **classes, not instances**: `{proteome, proteomic} → proteomics` is allowed;
"Biomni is multi_omics" is not. A per-record patch is a bug, not a fix.

The only human-touched inputs in the production pipeline are **extraction prompts** and
**`rules.yml`**. In the stub, `rules.yml` is stood in by `DOMAIN_ALIASES` and the
`guard_vocab()` deterministic vocab filter.

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

**Determinism boundary:** everything model-touched produces *candidates*; `rules.yml` +
vocab guards canonicalize them deterministically before serialization. Same inputs +
prompts + rules → stable graph. In `parse_stub.py` the deterministic stages
(`parse_entries`, `classify_url`, `guard_vocab`, assembly) run for real; `MOCK_openalex`
and `MOCK_extract_facets` are written with the **exact production call shape** but return
mock data so the graph assembles without SDK credit or off-allowlist API calls. Going
live = swapping the two `MOCK_*` functions.

Classifying entry type is **not a regex** — a known stub failure is `*Bench` names
false-positiving as agents (`AGENT_HINT` in the stub); production does this with the LLM.

### Output shape

`graph.json` = `{nodes: [...], edges: [...]}`; per-node markdown profiles
(`<type>/<slug>.md`: YAML frontmatter + LLM-drafted prose with typed `[[type:slug]]`
wikilinks) are progressive enhancement — the graph is self-sufficient without them.
Frontend is a static Cytoscape.js/sigma.js SPA on Cloudflare Pages (no backend);
a scheduled GitHub Action re-crawls → re-extracts → regenerates → redeploys.

A `_review` log captures low-confidence/vocab-failed extraction. It is **not a human
work queue** — it signals where the *prompt* needs work.

## Conventions

- Vocabularies are **closed** (SPEC §4/§5/§7/§9). Extending `Domain` or the `Database`
  whitelist is a deliberate PR edit, never auto-merge from extraction. The stub mirrors
  these as the `EXPOSES`/`ARCH`/`DOMAINS` sets — keep them in sync with SPEC.
- `a2a` = externally addressable by other agents. NOT the same as internally
  multi-agent (that's `architecture ∋ multi_agent`). Don't conflate.
- Expensive edges must carry `{source, evidence}` provenance — it's the audit mechanism
  given nothing is hand-verified.
- Wikilink prefix is required (`[[agent:cellagent]]`); slugs aren't unique across types.
