"""Resolve stage: enrich entries with grounding text + OpenAlex lookups. No model.

`fetch_context` pulls the abstract (arXiv / OpenAlex) or README (GitHub) so the
extraction backend reasons over real content instead of guessing from titles.
Results are url-cached; failures are non-fatal (return {} -> backend under-claims).
"""
from __future__ import annotations

import os
import re
import urllib.error
import urllib.request

from . import cache

_TIMEOUT = 20
_UA = {"User-Agent": "agentkg/0.1 (research pipeline)"}


def _get(url: str, headers: dict | None = None) -> str | None:
    try:
        req = urllib.request.Request(url, headers={**_UA, **(headers or {})})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def fetch_readme(repo_url: str) -> str | None:
    m = re.search(r"github\.com/([^/]+)/([^/#?]+)", repo_url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2).removesuffix(".git")
    headers = {"Accept": "application/vnd.github.raw+json"}
    if os.environ.get("GITHUB_TOKEN"):  # optional: raises the unauth rate limit
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    return _get(f"https://api.github.com/repos/{owner}/{repo}/readme", headers)


def fetch_arxiv_abstract(arxiv_id: str) -> str | None:
    xml = _get(f"http://export.arxiv.org/api/query?id_list={arxiv_id}")
    if not xml:
        return None
    m = re.search(r"<summary>(.*?)</summary>", xml, re.S)
    return " ".join(m.group(1).split()) if m else None


def fetch_openalex_abstract(doi: str) -> str | None:
    import json

    mailto = os.environ.get("OPENALEX_MAILTO", "")
    suffix = f"?mailto={mailto}" if mailto else ""
    raw = _get(f"https://api.openalex.org/works/doi:{doi}{suffix}")
    if not raw:
        return None
    try:
        idx = json.loads(raw).get("abstract_inverted_index")
    except json.JSONDecodeError:
        return None
    if not idx:
        return None
    words = sorted(((pos, w) for w, ps in idx.items() for pos in ps))
    return " ".join(w for _, w in words)


def fetch_context(url: str, kind: str, cid: str) -> dict:
    """Return {readme|abstract: text} for an entry, cached by url. Empty on failure."""
    hit = cache.get("context", url)
    if hit is not None:
        return hit
    out: dict = {}
    if kind == "repo":
        rd = fetch_readme(url)
        if rd:
            out["readme"] = rd
    elif cid.startswith("arxiv:"):
        ab = fetch_arxiv_abstract(cid.split(":", 1)[1])
        if ab:
            out["abstract"] = ab
    elif cid.startswith("doi:"):
        ab = fetch_openalex_abstract(cid.split(":", 1)[1])
        if ab:
            out["abstract"] = ab
    cache.put("context", url, out)
    return out


def openalex(paper_id: str) -> dict:
    """Org/citation resolve — still MOCK (orgs feed built_by). Real call shape:
    GET https://api.openalex.org/works/{id} -> authorships[].institutions[].ror."""
    return {
        "orgs": [{"name": "Stanford University", "ror": "https://ror.org/00f54p054"}],
        "cited_by_count": 42,
        "referenced_works": [],
    }
