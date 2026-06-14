# Contributing

Thanks for your interest! This project is a **fully generated** knowledge graph of
biomedical LLM-agent systems. The single most important rule shapes everything else:

> **Fix the generator, never the record.**

The graph (`data/graph.json`) and the profiles (`data/agents/*.md`) are *outputs*. Do not
hand-edit them — your change would be erased on the next regeneration. When the output is
wrong, fix the thing that produced it and regenerate. See
[`docs/adr/0001`](docs/adr/0001-record-architecture-decisions.md) and `SPEC.md` for the
design rationale.

## Where to make changes

| If you want to… | Edit… |
|---|---|
| Add/remove agents, fix a misclassification | the **classify prompt** (`src/agentkg/backends.py`) — a class-level rule, not a per-record patch |
| Change how a facet/edge is extracted | the relevant **system prompt** in `backends.py` |
| Canonicalize a class of noisy values | the alias/vocab tables in `src/agentkg/vocab.py` (these are the `rules.yml` stand-in) |
| Add a controlled-vocabulary value (domain, database) | `vocab.py` — a deliberate edit, with a note in the PR (never auto-merged from extraction) |
| Add a crawl source | `src/agentkg/sources.py` |
| Make a structural/architectural decision | write an **ADR** under `docs/adr/` (copy `template.md`) |

If you found a *system* that's missing, the best fix is usually upstream: add it to one of
the [source awesome-lists](README.md#acknowledgements), or let the citation-discovery pass
find it (it often does — see [ADR 0003](docs/adr/0003-citation-based-agent-discovery.md)).

## Running the pipeline

```bash
uv sync
uv run agentkg run                 # mock backend, fully offline -> data/graph.json
uv run agentkg run -b vertex -n 3  # live extraction on a few agents (needs creds; see .env.example)
```

Iterate cheaply: `.cache/` makes re-runs with an unchanged prompt cost zero tokens; editing
a prompt auto-busts its cache. Use `-n N` to bound a live run.

## The web app

```bash
cd web && bun install && bun run dev   # predev mirrors data/ into the SPA
bun run build                          # tsc --noEmit + vite build
```

## Conventions

- Python: match the surrounding style; keep the deterministic/​model-touched boundary clean
  (`vocab.guard_vocab` and the pipeline reconcile rules canonicalize model output).
- Keep `vocab.py` vocabularies in sync with `SPEC.md`.
- TypeScript (`web/`): `bun run build` must pass (`tsc --noEmit`).
- Open a PR with a clear description of *which generator input* you changed and why.

By contributing you agree that your code contributions are licensed under MIT and your data
contributions under CC0 1.0 (see `LICENSE` and `data/LICENSE`).
