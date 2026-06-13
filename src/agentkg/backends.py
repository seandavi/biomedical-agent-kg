"""The model-touched stage behind one swappable interface.

A backend exposes `.extract_facets(entry) -> candidate dict` with a fixed shape:
    exposes/architecture/domains : list[str]   (canonicalized + OOV-dropped downstream)
    evaluated_on : list[{benchmark, evidence, source}]   (expensive edge + provenance)
Vendor is a config line (Settings.backend), not architecture — defer the choice until
extraction quality is seen (SPEC philosophy). Mock is the default so the pipeline runs
with no creds; Gemini (Vertex AI) is the live backend.
"""
from __future__ import annotations

import json

from . import cache
from .config import Settings
from .vocab import ARCH, DOMAINS, EXPOSES

# Fixed across ALL entries -> the prompt-cache / context-cache target (SPEC §12.1).
FACET_SYSTEM_PROMPT = (
    "You extract structured facets for biomedical LLM-agent systems from the supplied "
    "text. Reply with ONLY a JSON object, no prose, with keys: "
    '"exposes", "architecture", "domains" (arrays of strings), and "evaluated_on" '
    '(array of {"benchmark","evidence","source"}). Use ONLY these controlled values:\n'
    f"  exposes: {sorted(EXPOSES)}\n"
    f"  architecture: {sorted(ARCH)}\n"
    f"  domains: {sorted(DOMAINS)}\n"
    "Omit any value you are unsure of (under-claim; honesty over completeness). "
    "Include a domain ONLY if the supplied text explicitly evidences that application "
    "area; never infer a domain from the system name alone. "
    "Add an evaluated_on entry only when the text gives an evidence span for it; "
    "set source to where the span came from (e.g. 'abstract' or 'readme'). "
    "Each evaluated_on 'benchmark' MUST be a single named benchmark's short canonical "
    "name (a proper noun like 'BixBench' or 'LAB-Bench'), never a description. If the "
    "text names several benchmarks, emit one entry per benchmark. If the evaluation "
    "target is an unnamed or ad-hoc dataset described only in prose, OMIT it. Each "
    "entry's 'evidence' MUST be the specific span that names THAT benchmark, not a "
    "shared summary sentence."
)

_EMPTY_FACETS = {"exposes": [], "architecture": [], "domains": [], "evaluated_on": []}


def truncate(text, max_chars):
    """Deterministic input-token lever: never ship a whole README/abstract."""
    return text[:max_chars] if text else ""


def build_payload(entry: dict) -> str:
    """Per-entry payload (the only part that varies; system prompt stays cached).
    abstract/readme are populated by the resolve stage in production; absent here."""
    parts = [f"Title: {entry['title']}"]
    if entry.get("venue"):
        parts.append(f"Venue: {entry['venue']}")
    if entry.get("section"):
        parts.append(f"List section: {entry['section']}")
    if entry.get("abstract"):
        parts.append("Abstract:\n" + truncate(entry["abstract"], 4000))
    if entry.get("readme"):
        parts.append("README:\n" + truncate(entry["readme"], 8000))
    return "\n\n".join(parts)


def _normalize_facets(data: dict) -> dict:
    return {k: data.get(k, []) for k in _EMPTY_FACETS}


class MockBackend:
    """Default. No model, no creds. Keys off known systems for eyeball-able output."""

    name = "mock"
    _table = {
        "cellagent": {"exposes": ["library"], "architecture": ["multi_agent"],
                      "domains": ["single_cell"], "evaluated_on": []},
        "biomni": {"exposes": ["library", "mcp"],
                   "architecture": ["multi_agent", "self_evolving", "tool_registry"],
                   "domains": ["multi_omics", "hypothesis_gen"],
                   "evaluated_on": [{"benchmark": "humanity-last-exam",
                                     "evidence": "evaluated on HLE and LAB-Bench",
                                     "source": "abstract"}]},
        "bixbench": {"exposes": ["library"], "architecture": ["single_agent"],
                     "domains": ["multi_omics"],
                     "evaluated_on": [{"benchmark": "bixbench",
                                       "evidence": "defines the BixBench benchmark",
                                       "source": "abstract"}]},
    }

    def extract_facets(self, entry: dict) -> dict:
        t = entry["title"].lower()
        for k, v in self._table.items():
            if k in t:
                return v
        # default candidate: sparse + deliberate OOV ("proteome" -> guard fixes it).
        return {"exposes": ["library"], "architecture": ["single_agent"],
                "domains": ["proteome"], "evaluated_on": []}


class GeminiBackend:
    """Live backend on Google Gemini. Vertex AI when a project is set (ADC auth via
    `gcloud auth application-default login`); else AI Studio key. Latest Flash default."""

    name = "gemini"

    def __init__(self, settings: Settings):
        try:
            from google import genai
            from google.genai import types
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("GeminiBackend needs: uv add google-genai") from e
        self._types = types
        self.model = settings.gemini_model
        if settings.project:
            self.client = genai.Client(
                vertexai=True, project=settings.project, location=settings.location)
        elif settings.google_api_key:
            self.client = genai.Client(api_key=settings.google_api_key)
        else:
            raise RuntimeError(
                "set GOOGLE_CLOUD_PROJECT (Vertex) or GOOGLE_API_KEY (AI Studio)")

    def extract_facets(self, entry: dict) -> dict:
        payload = build_payload(entry)
        # cache key spans model + prompt + payload: edit any -> miss -> re-spend.
        ckey = f"{self.model}\n{FACET_SYSTEM_PROMPT}\n{payload}"
        hit = cache.get("facets", ckey)
        if hit is not None:
            return hit
        cfg = self._types.GenerateContentConfig(
            system_instruction=FACET_SYSTEM_PROMPT,  # fixed -> context-cache candidate
            response_mime_type="application/json",    # force parseable JSON
            temperature=0,                            # determinism boundary
        )
        resp = self.client.models.generate_content(
            model=self.model, contents=payload, config=cfg)
        try:
            facets = _normalize_facets(json.loads(resp.text))
        except (json.JSONDecodeError, TypeError, AttributeError):
            facets = dict(_EMPTY_FACETS)  # bad output -> empty, audited via _review
        cache.put("facets", ckey, facets)
        return facets


def make_backend(settings: Settings):
    name = settings.backend.lower()
    if name == "mock":
        return MockBackend()
    if name in {"gemini", "vertex", "google"}:
        return GeminiBackend(settings)
    raise ValueError(f"unknown backend {name!r} (use: mock | vertex)")
