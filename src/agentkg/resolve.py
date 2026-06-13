"""Resolve stage: enrich entries with grounding text + OpenAlex lookups. No model.

`fetch_context` pulls the abstract (arXiv / OpenAlex) or README (GitHub) so the
extraction backend reasons over real content instead of guessing from titles.
Results are url-cached; failures are non-fatal (return {} -> backend under-claims).
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from . import cache
from .log import logger
from .vocab import ORG_ALIASES

_TIMEOUT = 20
_UA = {"User-Agent": "agentkg/0.1 (research pipeline)"}


def _get(url: str, headers: dict | None = None) -> str | None:
    try:
        req = urllib.request.Request(url, headers={**_UA, **(headers or {})})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        logger.debug(f"fetch failed: {url} ({exc})")
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


def repo_health(repo_url: str) -> dict:
    """Freshness/health attributes for a Repo node (SPEC §10). Cached by url — a
    scheduled crawl busts it to refresh. Empty on failure (node still exists)."""
    hit = cache.get("repo", repo_url)
    if hit is not None:
        return hit
    m = re.search(r"github\.com/([^/]+)/([^/#?]+)", repo_url)
    if not m:
        return {}
    owner, repo = m.group(1), m.group(2).removesuffix(".git")
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    raw = _get(f"https://api.github.com/repos/{owner}/{repo}", headers)
    if not raw:
        return {}
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    out = {
        "stars": d.get("stargazers_count"),
        "last_commit": d.get("pushed_at"),  # staleness signal — surfaced, not hidden
        "language": d.get("language"),
        "license": (d.get("license") or {}).get("spdx_id"),
    }
    cache.put("repo", repo_url, out)
    return out


def github_org(repo_url: str) -> dict | None:
    """Freeform building org from the GitHub owner (SPEC §13). ROR null — the alias
    table canonicalizes known owners; the rest pass through as their handle."""
    m = re.search(r"github\.com/([^/#?]+)/", repo_url)
    if not m:
        return None
    owner = m.group(1)
    return {"name": ORG_ALIASES.get(owner.lower(), owner), "ror": None}


def fetch_arxiv_abstract(arxiv_id: str) -> str | None:
    xml = _get(f"http://export.arxiv.org/api/query?id_list={arxiv_id}")
    if not xml:
        return None
    m = re.search(r"<summary>(.*?)</summary>", xml, re.S)
    return " ".join(m.group(1).split()) if m else None


def _openalex_id(cid: str) -> str | None:
    """Map a canonical id to an OpenAlex /works selector. arXiv works are indexed
    under their registered DOI (10.48550/arXiv.<id>)."""
    if cid.startswith("doi:"):
        return "doi:" + cid.split(":", 1)[1]
    if cid.startswith("arxiv:"):
        return "doi:10.48550/arXiv." + cid.split(":", 1)[1]
    return None


def _openalex_work(cid: str) -> dict | None:
    """Fetch + cache the OpenAlex work once; abstract and orgs both derive from it."""
    hit = cache.get("openalex", cid)
    if hit is not None:
        return hit or None  # cached {} means "resolved to nothing"
    oid = _openalex_id(cid)
    if not oid:
        cache.put("openalex", cid, {})
        return None
    mailto = os.environ.get("OPENALEX_MAILTO", "")
    suffix = f"?mailto={mailto}" if mailto else ""
    raw = _get(f"https://api.openalex.org/works/{oid}{suffix}")
    if not raw:
        return None  # transient failure — don't cache, allow retry next run
    try:
        work = json.loads(raw)
    except json.JSONDecodeError:
        return None
    cache.put("openalex", cid, work)
    return work


def _abstract_from_work(work: dict) -> str | None:
    idx = work.get("abstract_inverted_index")
    if not idx:
        return None
    words = sorted((pos, w) for w, ps in idx.items() for pos in ps)
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
        work = _openalex_work(cid)
        ab = _abstract_from_work(work) if work else None
        if ab:
            out["abstract"] = ab
    cache.put("context", url, out)
    return out


def openalex(cid: str) -> dict:
    """Resolve building orgs (feed built_by) + citation signal from OpenAlex.
    GET /works/{id} -> authorships[].institutions[] (display_name, ror), deduped.
    Empty orgs when the work isn't found — built_by is simply omitted (honest)."""
    work = _openalex_work(cid)
    if not work:
        return {"openalex_id": None, "orgs": [], "cited_by_count": None,
                "referenced_works": []}
    seen, orgs = set(), []
    for a in work.get("authorships", []):
        for inst in a.get("institutions", []):
            name, ror = inst.get("display_name"), inst.get("ror")
            key = ror or name
            if not name or key in seen:
                continue
            seen.add(key)
            orgs.append({"name": name, "ror": ror})
    return {
        "openalex_id": work.get("id"),
        "orgs": orgs,
        "cited_by_count": work.get("cited_by_count"),
        "referenced_works": work.get("referenced_works", []),
    }
