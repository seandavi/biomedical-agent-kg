# 1. Record architecture decisions

- Status: Accepted
- Date: 2026-06-13

## Context

This project makes a steady stream of design decisions — pipeline structure, model
vendor, the classification taxonomy, catalog scope, org-resolution strategy. Until now
they have lived only in commit messages, `CLAUDE.md`, and `SPEC.md`. Those are good for
*what the code does now*, but they lose the *why* behind a choice and the alternatives
that were rejected, which is exactly what a future contributor (human or agent) needs
when deciding whether a decision still holds.

This matters more than usual here because the pipeline is **fully generated** (SPEC: fix
the generator, never the record). Decisions are encoded in prompts and `rules.yml`-style
transforms, so the reasoning behind a prompt rule is the real artifact — it must be
written down or it is lost on the next regeneration.

## Decision

Adopt **Architecture Decision Records** (Michael Nygard's format) under `docs/adr/`:

- One file per decision, numbered `NNNN-kebab-title.md`, append-only.
- Each ADR has **Status** (Proposed → Accepted → Superseded/Deprecated), **Context**,
  **Decision**, **Consequences**.
- A superseded ADR is kept and its Status links the ADR that replaces it; never edit a
  decision's substance after acceptance — write a new ADR.
- `docs/adr/template.md` is the starting point.

ADRs complement, not duplicate, `SPEC.md` (the data-model spec) and `CLAUDE.md`
(operational guidance): ADRs capture *decisions and their rationale*.

## Consequences

- Low overhead per decision; decisions become discoverable and reviewable in PRs.
- The rationale behind prompt/vocab rules survives regeneration.
- Requires the discipline of writing an ADR when a non-obvious choice is made.
