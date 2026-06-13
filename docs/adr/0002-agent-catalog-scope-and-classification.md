# 2. Agent catalog scope and classification taxonomy

- Status: Accepted
- Date: 2026-06-13

## Context

Crawling the five SPEC §11 awesome-lists yields ~634 entries. The first full pass
classified **232 of them as "agents"** — but on inspection most were not agents at all:
foundation models (AlphaFold, ESM, scGPT, Geneformer), ML tools and libraries (Cellpose,
napari, MONAI, scvi-tools), structure/docking/segmentation models (RFdiffusion,
ProteinMPNN, MedSAM), datasets, and even non-biomedical systems (BirdNET, PlantNet). The
awesome-lists are "AI for science," so they are dominated by models and tooling, not
agents.

The catalog's spine is **biomedical LLM agent systems** (SPEC §1). Without a precise
notion of "agent" and a scope boundary, the catalog is ~75% noise. A first domain gate
(biomedical-only) was not enough — it filtered *topic* but not *kind*, leaving foundation
models and tools in.

A residual question remained: general scientific-discovery and literature agents
(AI-Researcher, Curie, The AI Scientist, OpenScholar, PaperQA2, SciMon) are genuine LLM
agents but not biomedicine-specific. Drop them or keep them?

## Decision

**1. A strict definition of "agent."** An `agent` is an *LLM-based agentic system*: its
defining feature is using an LLM to reason, plan, and act (calling tools, multi-step
workflows, orchestrating sub-agents). The following are explicitly **not** agents and
classify as `other`, even when biomedical:

- foundation / pretrained models, ML methods, model architectures;
- software tools, libraries, packages, pipelines, viewers;
- structure-prediction / docking / segmentation / design models;
- datasets (including size-suffix names like `PathGen-1.6M`);
- SKILL.md / capability "skills" collections (these are SPEC §8 `ToolEnv` skill-sets, a
  future node type, not agents);
- general-purpose agent frameworks (CAMEL, AutoGen, LangChain).

**2. Domain gate.** Label `agent`/`benchmark` only if the primary application is
biomedicine, bioinformatics, healthcare, clinical medicine, or molecular/cell/genomic
life-science. Exclude ecology, agriculture, materials, chemistry-only, physics, etc.

**3. General scientific-discovery agents: tag, don't drop.** Keep broad-scope research /
literature agents in the catalog, but make them **filterable** by tagging them with a
domain (`scientific_discovery`, or `literature` for literature tools) rather than
excluding them. Rationale: the source lists *are* scientific-discovery lists; many such
agents are used in biomedicine; the boundary is genuinely fuzzy, and filtering preserves
information that exclusion would destroy. `scientific_discovery` is added to the `Domain`
closed vocab (SPEC §7) by deliberate edit.

**4. Fix the generator.** All of the above is enforced in the **classify** system prompt
and the `Domain` vocab — never by per-record edits. Misclassifications are addressed by
tightening the prompt (a class-level fix) and regenerating; the `_review` log surfaces
where the prompt still needs work.

## Consequences

- The catalog collapses from 232 to ~78 genuine agents — a set small and clean enough for
  a deeper per-agent dive.
- General-science agents are retained but filterable; a consumer (e.g. the SPA) can scope
  to strictly-biomedical via domain facets.
- The agent/model boundary is a model judgment encoded in a prompt; it will drift at the
  margins. That is accepted and made auditable via `_review` + regeneration, per the
  fix-the-generator discipline. Reversible: change the prompt/vocab, re-run.
- Foundation models and tools that are *connected to* agents are out of scope as nodes for
  now; if a `ToolEnv`/model node type is later added (SPEC §8), some may return as
  non-agent nodes.
