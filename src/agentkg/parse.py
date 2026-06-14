"""Deterministic stages: crawl + cheap-edge parsing of awesome-list markdown.

No model here. `looks_like_agent` is a cheap heuristic stand-in for the LLM classify
stage (SPEC §12.1) — it has a known `*Bench` false-positive that the real classifier
resolves; kept so the pipeline runs end-to-end.
"""
from __future__ import annotations

import pathlib
import re

# Permissive: any bulleted list item (real awesome-lists vary in style). The first
# http(s) markdown link in the item is the entry; the rest of the line is its blurb.
# Anchor-only ToC links (](#section)) are skipped — the link must be a real URL.
ENTRY_RE = re.compile(r"^\s*[-*+]\s+(?P<body>.*\S)\s*$")
LINK_RE = re.compile(r"\[(?P<title>[^\]]+)\]\((?P<url>https?://[^)\s]+)\)")
HDR_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")

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


SOURCE_RE = re.compile(r"^<!--KGSOURCE (.+?)-->\s*$")


def parse_entries(md: str):
    section = subsection = source = None
    for line in md.splitlines():
        sm = SOURCE_RE.match(line)
        if sm:  # provenance marker emitted by sources.crawl_sources
            source = sm.group(1)
            continue
        h = HDR_RE.match(line)
        if h:
            txt = h.group(2).strip()
            if len(h.group(1)) <= 2:        # h1/h2 -> section
                section, subsection = txt, None
            else:                           # deeper -> subsection
                subsection = txt
            continue
        m = ENTRY_RE.match(line)
        if not m:
            continue
        lm = LINK_RE.search(m.group("body"))
        if not lm:
            continue
        title = lm.group("title").strip().strip("*").strip()
        desc = LINK_RE.sub(" ", m.group("body")).strip(" -—:·|*\t")
        yield {
            "title": title, "url": lm.group("url"), "desc": desc or None,
            "authors": None, "venue": None, "source": source,
            "section": section, "subsection": subsection,
        }


def looks_like_agent(title: str) -> str | None:
    head = title.split(":")[0].strip()  # "CellAgent: An LLM-driven..." -> "CellAgent"
    if len(head.split()) <= 4 and AGENT_HINT.search(head):
        return head
    m = AGENT_HINT.search(title)
    return m.group(1) if m else None
