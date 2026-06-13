"""Deterministic stages: crawl + cheap-edge parsing of awesome-list markdown.

No model here. `looks_like_agent` is a cheap heuristic stand-in for the LLM classify
stage (SPEC §12.1) — it has a known `*Bench` false-positive that the real classifier
resolves; kept so the pipeline runs end-to-end.
"""
from __future__ import annotations

import pathlib
import re

ENTRY_RE = re.compile(r"^- \*\*\[(?P<title>.+?)\]\((?P<url>.+?)\)\*\*\s*$")
META_RE = re.compile(r"^\s+\*(?P<authors>.+?)\.\*\s*(?P<venue>.+?)\s*$")
HDR_RE = re.compile(r"^(#{2,4})\s+(.*)$")

# heuristic: an entry names a system if it matches one of these shapes near the head.
AGENT_HINT = re.compile(
    r"\b([A-Z][a-zA-Z]*(?:Agent|GPT|Bench|Mni|Master)|[A-Z]{2,}[a-z]*Agent)\b"
)


def crawl(path) -> str:
    return pathlib.Path(path).read_text(encoding="utf-8")


def classify_url(url: str) -> tuple[str, str]:
    """Return (kind, canonical_id), kind in {paper, repo}."""
    if "github.com" in url:
        return "repo", url.rstrip("/")
    m = re.search(r"arxiv\.org/abs/([\d.]+)", url)
    if m:
        return "paper", f"arxiv:{m.group(1)}"
    m = re.search(r"/(10\.\d{4,}/[^\s)]+)", url)  # bare DOI in path
    if m:
        return "paper", f"doi:{m.group(1)}"
    if "biorxiv.org" in url or "doi.org" in url:
        return "paper", "doi:" + url.split("/")[-1]
    return "paper", "url:" + url  # fallback canonical


def parse_entries(md: str):
    section = subsection = None
    lines = md.splitlines()
    for i, line in enumerate(lines):
        h = HDR_RE.match(line)
        if h:
            level = len(h.group(1))
            if level == 3:
                section, subsection = h.group(2), None
            elif level == 4:
                subsection = h.group(2)
            continue
        m = ENTRY_RE.match(line)
        if not m:
            continue
        meta = META_RE.match(lines[i + 1]) if i + 1 < len(lines) else None
        yield {
            "title": m.group("title"), "url": m.group("url"),
            "authors": meta.group("authors") if meta else None,
            "venue": meta.group("venue") if meta else None,
            "section": section, "subsection": subsection,
        }


def looks_like_agent(title: str) -> str | None:
    head = title.split(":")[0].strip()  # "CellAgent: An LLM-driven..." -> "CellAgent"
    if len(head.split()) <= 4 and AGENT_HINT.search(head):
        return head
    m = AGENT_HINT.search(title)
    return m.group(1) if m else None
