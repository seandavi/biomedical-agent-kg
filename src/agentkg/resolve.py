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
import urllib.parse
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
    # Only cache a HIT. An empty result is usually a transient fetch failure (e.g. the
    # GitHub 60/hr unauth rate limit) — caching it would make the gap permanent. Retry
    # next run instead; set GITHUB_TOKEN to lift the limit and fill READMEs.
    if out:
        cache.put("context", url, out)
    else:
        logger.debug(f"no grounding text for {url} (kind={kind}) — will retry next run")
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


def _wid(openalex_id: str) -> str:
    """Bare OpenAlex work id (W...) from a full id URL."""
    return openalex_id.rstrip("/").split("/")[-1]


def _meta(work: dict) -> dict:
    return {"id": work.get("id"), "title": work.get("title"),
            "year": work.get("publication_year"),
            "cited_by_count": work.get("cited_by_count")}


def citers(openalex_id: str, cap: int = 200) -> list[dict]:
    """Incoming citations: works that CITE openalex_id (one page, capped). Returns
    [{id,title,year,cited_by_count}]. Cached by work id. Powers cocitation mechanism C."""
    wid = _wid(openalex_id)
    hit = cache.get("citers", wid)
    if hit is not None:
        return hit
    mailto = os.environ.get("OPENALEX_MAILTO", "")
    url = (f"https://api.openalex.org/works?filter=cites:{wid}"
           f"&select=id,title,publication_year,cited_by_count&per-page={min(cap, 200)}"
           + (f"&mailto={mailto}" if mailto else ""))
    raw = _get(url)
    if not raw:
        return []  # transient — don't cache
    try:
        results = json.loads(raw).get("results", [])
    except json.JSONDecodeError:
        return []
    out = [_meta(w) for w in results]
    cache.put("citers", wid, out)
    return out


def work_meta(openalex_id: str) -> dict:
    """Title/year/cited_by_count for an external work id (for cocitation nodes whose
    metadata didn't arrive via the citers fetch, i.e. mechanism B). Cached."""
    wid = _wid(openalex_id)
    hit = cache.get("workmeta", wid)
    if hit is not None:
        return hit
    mailto = os.environ.get("OPENALEX_MAILTO", "")
    url = (f"https://api.openalex.org/works/{wid}"
           f"?select=id,title,publication_year,cited_by_count"
           + (f"&mailto={mailto}" if mailto else ""))
    raw = _get(url)
    if not raw:
        return {}
    try:
        out = _meta(json.loads(raw))
    except json.JSONDecodeError:
        return {}
    cache.put("workmeta", wid, out)
    return out


def work_abstract(wid: str) -> tuple[str | None, str | None]:
    """(title, abstract) for an OpenAlex work id — grounds a promoted/harvested agent."""
    mailto = os.environ.get("OPENALEX_MAILTO", "")
    raw = _get(f"https://api.openalex.org/works/{wid}"
               f"?select=title,abstract_inverted_index"
               + (f"&mailto={mailto}" if mailto else ""))
    if not raw:
        return None, None
    try:
        w = json.loads(raw)
    except json.JSONDecodeError:
        return None, None
    return w.get("title"), _abstract_from_work(w)


def work_refs(wid: str) -> list[str]:
    """referenced_works ids for a work (for survey harvesting). Cached."""
    hit = cache.get("workrefs", wid)
    if hit is not None:
        return hit
    mailto = os.environ.get("OPENALEX_MAILTO", "")
    raw = _get(f"https://api.openalex.org/works/{wid}?select=referenced_works"
               + (f"&mailto={mailto}" if mailto else ""))
    if not raw:
        return []
    try:
        refs = json.loads(raw).get("referenced_works", [])
    except json.JSONDecodeError:
        return []
    cache.put("workrefs", wid, refs)
    return refs


def works_titles(ids: list[str]) -> dict:
    """Batch {work_id: title} for up to 50 ids (to pre-filter survey refs by title)."""
    out: dict = {}
    for i in range(0, len(ids), 50):
        chunk = [_wid(x) for x in ids[i:i + 50]]
        mailto = os.environ.get("OPENALEX_MAILTO", "")
        raw = _get("https://api.openalex.org/works?per-page=50&select=id,title"
                   f"&filter=openalex_id:{'|'.join(chunk)}"
                   + (f"&mailto={mailto}" if mailto else ""))
        if not raw:
            continue
        try:
            for w in json.loads(raw).get("results", []):
                out[_wid(w.get("id", ""))] = w.get("title")
        except json.JSONDecodeError:
            pass
    return out


def _name_slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def find_repo(name: str) -> str | None:
    """Best-effort GitHub repo for a promoted agent: search by name, accept only a result
    whose repo name slug-matches the agent name (avoids false matches). Needs a token."""
    target = _name_slug(name)
    if not target or len(target) < 3:
        return None
    hit = cache.get("repofind", target)
    if hit is not None:
        return hit or None  # cached "" means searched, no match
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    raw = _get(f"https://api.github.com/search/repositories?per_page=5&sort=stars"
               f"&q={urllib.parse.quote(name)}+in:name", headers)
    if not raw:
        return None
    try:
        items = json.loads(raw).get("items", [])
    except json.JSONDecodeError:
        return None
    match = next((it.get("html_url") for it in items
                  if _name_slug(it.get("name", "")) == target), None)
    cache.put("repofind", target, match or "")
    return match
