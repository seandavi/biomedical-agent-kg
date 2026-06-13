# agentkg-web

Static SPA for the Biomedical Agent Knowledge Graph. Reads the pipeline's
generated `graph.json` (+ optional `<type>/<slug>.md` profiles) and renders it as
an interactive Cytoscape.js graph. No backend — deploys as static files to
Cloudflare Pages.

## Stack

- **Vite + TypeScript** (run with **bun**)
- **Cytoscape.js** + `cytoscape-fcose` force layout
- **marked** for rendering generated profile prose

## Develop

```bash
bun install
bun run dev        # predev syncs ../graph.json -> public/data/, then serves :5173
```

`bun run sync-data` mirrors the generator output (`../graph.json` and any
`<type>/` profile dirs at the repo root) into `public/data/`. It runs
automatically before `dev` and `build`. Regenerate the graph with
`uv run agentkg run` (repo root), then re-sync.

## Build & preview

```bash
bun run build      # tsc --noEmit + vite build -> dist/
bun run preview
```

`dist/` is the Cloudflare Pages publish directory.

## Verify (headless smoke test)

```bash
bun run dev &                 # in one shell
bun run scripts/verify.ts     # loads the page, asserts graph + panel render
```

Uses the Playwright Chromium at `~/.cache/ms-playwright/`; override the binary
with `CHROMIUM=/path/to/chrome` or the URL with `URL=...`.

## How it maps to the SPEC

- **Agents are the spine** — rendered larger; warm/dominant color.
- **Node vs. attribute** — node types are traversable nodes; `exposes` /
  `architecture` are closed-vocab attributes surfaced as *filters*, not edges.
- **`cites` overlay** is a default-OFF toggle (it dominates layout when on).
- **Profiles are progressive enhancement** — the panel renders a node's
  `detail_ref` markdown if present, else falls back to `one_liner` + facets. We
  never guess a profile path (no `detail_ref` ⇒ no profile yet).
- **Wikilinks** `[[type:slug]]` in profile prose resolve to selecting +
  recentering that node; unresolvable links render as plain text (SPEC §3.2).
