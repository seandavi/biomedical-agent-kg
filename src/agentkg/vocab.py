"""Controlled vocabularies (SPEC §4/§5/§7) + the deterministic vocab guard.

These mirror SPEC; extending a vocab is a deliberate edit here, never auto-merged from
extraction. The guard canonicalizes via class-level aliases (the rules.yml stand-in)
and drops out-of-vocab values — the determinism boundary after the model stage.
"""
from __future__ import annotations

EXPOSES = {"library", "cli", "mcp", "a2a", "skills", "web_ui", "api", "notebook"}
ARCH = {"single_agent", "multi_agent", "rag", "self_evolving", "tool_registry"}
DOMAINS = {
    "single_cell", "spatial", "proteomics", "genomics_db", "multi_omics",
    "perturbation", "drug_discovery", "medical_imaging", "clinical_qa",
    "literature", "hypothesis_gen", "protein_structure",
    # general scientific-discovery / research-automation (not biomedicine-specific) —
    # lets broad-scope agents be tagged + filtered rather than dropped (ADR 0002).
    "scientific_discovery",
}

# Shared public Database whitelist (SPEC §9). A Database node exists ONLY for these
# named, public, shared resources that create cross-system edges; anything else an agent
# queries is folded into a ToolEnv's db_count (or dropped), never its own node.
DATABASES = {
    "clinvar", "gnomad", "geo", "sra", "uniprot", "openalex", "pubmed",
    "clinicaltrials", "gwas_catalog", "cpic", "alphamissense", "civic", "oncokb",
}

DB_ALIASES = {
    "gene expression omnibus": "geo",
    "sequence read archive": "sra",
    "clinical trials": "clinicaltrials", "clinicaltrials.gov": "clinicaltrials",
    "gwas catalog": "gwas_catalog", "the gwas catalog": "gwas_catalog",
    "uniprotkb": "uniprot",
}

# rules.yml stand-in: alias tables catching CLASSES of extraction noise (SPEC §1.3).
DOMAIN_ALIASES = {
    "proteome": "proteomics", "proteomic": "proteomics",
    "scrna": "single_cell", "single-cell": "single_cell",
    "multiomics": "multi_omics", "multi-omics": "multi_omics",
}

# GitHub owner -> canonical org name (SPEC §13: freeform-with-aliases org resolution).
# Used when OpenAlex carries no affiliation (e.g. arXiv preprints). Unlisted owners
# fall through as their literal owner handle. ROR is left null (freeform, not strict).
ORG_ALIASES = {
    "mims-harvard": "Harvard Medical School",
    "snap-stanford": "Stanford University",
    "ncbi": "National Center for Biotechnology Information",
}


def guard_vocab(values, vocab, aliases=None):
    """Return (kept_sorted_unique, dropped). Aliased then membership-filtered."""
    out, dropped = [], []
    for v in values:
        v2 = (aliases or {}).get(v.lower(), v.lower())
        (out if v2 in vocab else dropped).append(v2)
    return sorted(set(out)), dropped
