# 3. Citation-based agent discovery and provenance

- Status: Accepted
- Date: 2026-06-13

## Context

The catalog is seeded from five curated awesome-lists (SPEC §11). After building the
cocitation overlay (ADR 0002 / SPEC §6.2), we observed that **external papers citing ≥2
catalog agents are enriched for agents the lists missed**: a sample of 67 agent-titled
externals yielded 11 genuine biomedical agents not in any list (PerTurboAgent, MRAgent,
PhenoGraph, Bioinformatics Copilot, VISION, Agentic Lab, DORA AI Scientist, …). The
citation graph is therefore not only a map but a **discovery engine**.

How this compares to a keyword literature review shaped the design:

- **Relevance signal.** Review finds by *vocabulary*; discovery finds by *citation
  position*. "Agent" is overloaded in biomedicine (biological/chemical/contrast agents)
  and real systems self-describe as "framework/copilot/platform", so keyword recall is
  noisy and drifts. "Cites ≥2 known agents" is a strong, wording-independent prior →
  higher precision.
- **Recall.** Discovery is *seed-bounded* (one citation hop): an agent that cites none of
  the catalog is invisible to it, but findable by review. This is discovery's main
  weakness.
- **The fix falls out of the output.** Discovery surfaces **surveys** (papers citing many
  agents), and a survey *is* a curated literature review. Harvesting a survey's reference
  list recovers review-grade recall using discovery's own results.
- **By-product.** Review yields a list; discovery yields the list **plus the graph**
  (lineage, co-citation clusters). The links are the product.
- **Limits to document, not hide:** citation lag (newest agents have no citations yet),
  rich-get-richer/Anglophone/has-a-paper bias, OpenAlex coverage gaps.

A citation-grown catalog is only academically usable if each agent's inclusion is
**traceable and reproducible** — hence first-class provenance.

## Decision

**1. Discovery mechanisms** (run after the seed catalog + cocitation layer):

- **Cocitation promotion.** Classify external papers that cite ≥2 catalog *agents*;
  promote those classified as biomedical `agent` into the catalog (described_by their
  paper, grounded from abstract, facets extracted).
- **Survey harvesting.** When a paper citing ≥2 catalog agents classifies as `paper`
  (a review/survey), harvest its `referenced_works`, classify them, and promote the
  agents. This recovers the recall a pure citation hop misses.
- **Bounded iteration.** Repeat for at most K rounds (default K=1) with a per-round cap;
  newly promoted agents widen the frontier. Stop early when a round promotes nothing.

**2. Provenance (first-class, every node).** Each Agent (and discovered Paper) carries:

```
provenance: { method, round, openalex_id, doi, evidence }
  method   : awesome_list | cocitation | survey_harvest
  round    : 0 = curated seed; n = discovery round
  evidence : awesome_list   -> lists: [<source list ids>]
             cocitation     -> cites_catalog: [<agent ids the paper cited>]
             survey_harvest -> from_survey: <paper id>
```

A run-level **`data/_provenance.json`** records the reproducibility envelope: discovery
parameters (`min_links`, rounds, classify/gate version), the **OpenAlex access date**
(the corpus moves — the snapshot date is required to reproduce), and node counts per
(method, round). The headline figure is "N seed + M discovered over K rounds."

**3. Guards.** Dedup promoted agents into existing ones by slug (a published version of an
already-listed agent must merge, not duplicate). Tighten the classify domain gate so
chemistry/materials agents stay `other`. Promotion obeys the same fix-the-generator rule:
wrong promotions are fixed in the classify prompt, never per-record.

**4. Seed vs. grown is explicit.** `round` lets any consumer (the SPA, an analysis) scope
to the curated seed, the grown catalog, or a specific provenance depth.

## Consequences

- The catalog grows beyond any curated list, self-curating (surveys → `paper`, off-topic
  → `other`), and the growth is auditable per node.
- Provenance makes the build reportable and reproducible — a methods section can state
  exactly how each agent entered and re-derive it from the seed + OpenAlex snapshot.
- "The catalog" becomes a methodological claim (curated-seed + citation-grown), not just a
  list — documented limits (citation lag, citation bias, OpenAlex gaps) travel with it.
- Cost grows with rounds (classify + abstract fetch per candidate); K and the per-round
  cap bound it. Best paired with occasional keyword review for the disconnected/brand-new
  that citations structurally cannot reach.
