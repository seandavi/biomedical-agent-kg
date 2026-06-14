"""Citation-based agent discovery (ADR 0003).

After the seed catalog + cocitation layer, promote external papers that cite >= min_links
catalog AGENTS and classify as biomedical agents, and harvest agents from the reference
lists of survey papers that cite >= min_links agents. Promoted agents carry provenance
(method / round / evidence) so a citation-grown catalog stays auditable and reproducible.
Single round (K=1); call again on the result to iterate.
"""
from __future__ import annotations

import re
from collections import defaultdict

from . import resolve
from .log import logger
from .model import Edge, slugify

_AGENTISH = re.compile(
    r"\b(agent|agentic|copilot|co-pilot|multi-agent|autonomous|assistant|scientist)\b", re.I)

_TRAILING_STOP = {"for", "of", "the", "a", "an", "and", "to", "in", "with", "via",
                  "using", "based", "that", "which", "on", "from"}


def _good_name(name) -> bool:
    """A promotable agent needs a real proper name, not a title fragment. Reject phrases
    (too many words, lowercase start, trailing stopword) — classify grabs these when a
    paper describes an approach with no named system."""
    name = (name or "").strip()
    if not name or not name[0].isupper():
        return False
    words = name.split()
    return len(words) <= 4 and words[-1].lower() not in _TRAILING_STOP


def _paper_to_agent(g) -> dict:
    m = {}
    for e in g.edges:
        if e["rel"] == "described_by":
            m.setdefault(e["dst"], e["src"])  # paper id -> agent id
    return m


def _external_agent_links(g, paper_to_agent) -> dict:
    """external paper id -> set of catalog AGENT ids it connects via cites."""
    links = defaultdict(set)
    for e in g.edges:
        if e["rel"] != "cites":
            continue
        for ext, other in ((e["src"], e["dst"]), (e["dst"], e["src"])):
            n = g.nodes.get(ext)
            if n and n.get("in_catalog") is False:
                ag = paper_to_agent.get(other)
                if ag:
                    links[ext].add(ag)
    return links


def _attach_repo(g, aid, name, entry):
    """Best-effort: find the agent's GitHub repo, add implemented_by/built_by/owned_by +
    README grounding + repo health. Name-slug match guards against false repos."""
    repo = resolve.find_repo(name)
    if not repo:
        return
    readme = resolve.fetch_readme(repo)
    if readme:
        entry["readme"] = readme
    rid = g.add_node(repo, "repo", url=repo, **resolve.repo_health(repo))
    g.add_edge(Edge(aid, "implemented_by", rid))
    org = resolve.github_org(repo)
    if org:
        oid = g.add_node("org:" + slugify(org["name"]), "org",
                         name=org["name"], ror=org.get("ror"))
        g.add_edge(Edge(aid, "built_by", oid))
        g.add_edge(Edge(rid, "owned_by", oid))


def _promote(g, paper_node_id, name, title, abstract, backend, review_log, apply_facets,
             provenance, ctx):
    aid = "agent:" + slugify(name)
    is_new = aid not in g.nodes
    g.add_node(aid, "agent", name=name, one_liner=title)
    if is_new:
        g.nodes[aid]["provenance"] = provenance  # keep seed provenance on a dedup hit
    # the citing/harvested external paper becomes this agent's described_by paper
    if paper_node_id in g.nodes:
        g.nodes[paper_node_id]["in_catalog"] = True
        g.add_edge(Edge(aid, "described_by", paper_node_id, primary=is_new))
    entry = {"title": title, "abstract": abstract}
    _attach_repo(g, aid, name, entry)
    apply_facets(g, aid, backend.extract_facets(entry), review_log)
    if ctx is not None:
        ctx[aid] = {"abstract": abstract, "readme": entry.get("readme")}
    return is_new


def _harvest_survey(g, survey_id, survey_wid, backend, review_log, apply_facets, ctx,
                    ref_cap):
    """Promote agents from a survey's reference list (the survey is itself a lit review)."""
    refs = resolve.work_refs(survey_wid)
    if not refs:
        return []
    titles = resolve.works_titles(refs)
    targets = [r for r in refs
               if _AGENTISH.search(titles.get(resolve._wid(r), "") or "")][:ref_cap]
    out = []
    for r in targets:
        w = resolve._wid(r)
        node_id = "openalex:" + w
        if node_id in g.nodes and g.nodes[node_id].get("in_catalog") is not False:
            continue
        title, abstract = resolve.work_abstract(w)
        title = title or titles.get(w) or ""
        cls = backend.classify({"title": title, "desc": (abstract or "")[:400]})
        if cls["kind"] == "agent" and _good_name(cls.get("name")):
            if node_id not in g.nodes:
                g.add_node(node_id, "paper", title=title, in_catalog=True)
            prov = {"method": "survey_harvest", "round": 1,
                    "openalex_id": "https://openalex.org/" + w,
                    "evidence": {"from_survey": g.nodes[survey_id].get("id")}}
            if _promote(g, node_id, cls["name"], title, abstract, backend, review_log,
                        apply_facets, prov, ctx):
                out.append(cls["name"])
    return out


def discover(g, backend, review_log, apply_facets, ctx=None, min_links=2, cap=None,
             survey_ref_cap=40):
    """One discovery round. Mutates g in place. Returns the list of promoted agent names."""
    paper_to_agent = _paper_to_agent(g)
    links = _external_agent_links(g, paper_to_agent)
    cands = sorted((c for c in links.items() if len(c[1]) >= min_links),
                   key=lambda t: -len(t[1]))
    if cap:
        cands = cands[:cap]
    logger.info(f"discovery: {len(cands)} external candidates (>= {min_links} agents cited)")
    promoted, harvested = [], []
    for eid, agents in cands:
        node = g.nodes.get(eid)
        if not node or node.get("in_catalog") is not False:
            continue
        wid = eid.split(":", 1)[1]
        title, abstract = resolve.work_abstract(wid)
        title = title or node.get("title") or ""
        cls = backend.classify({"title": title, "desc": (abstract or "")[:400]})
        if cls["kind"] == "agent" and _good_name(cls.get("name")):
            prov = {"method": "cocitation", "round": 1,
                    "openalex_id": "https://openalex.org/" + wid,
                    "evidence": {"cites_catalog": sorted(agents)}}
            if _promote(g, eid, cls["name"], title, abstract, backend, review_log,
                        apply_facets, prov, ctx):
                promoted.append(cls["name"])
        elif cls["kind"] == "paper":
            harvested += _harvest_survey(g, eid, wid, backend, review_log, apply_facets,
                                         ctx, survey_ref_cap)
    logger.info(f"discovery: +{len(promoted)} agents (cocitation), "
                f"+{len(harvested)} (survey harvest)")
    return promoted + harvested
