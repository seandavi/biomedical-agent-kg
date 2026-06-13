"""Assembly: crawl -> parse cheap edges -> resolve -> facets (backend) -> guard -> emit.

Deterministic except the backend.extract_facets call; guard_vocab re-imposes the
determinism boundary after it.
"""
from __future__ import annotations

import json

from . import profiles, resolve, sources
from .backends import MockBackend, make_backend
from .config import Settings
from .log import logger
from .model import Edge, Graph, slugify
from .parse import classify_url, crawl, parse_entries
from .vocab import ARCH, DOMAIN_ALIASES, DOMAINS, EXPOSES, guard_vocab


def build(md: str, review_log: list, backend=None, limit=None, context_sink=None) -> Graph:
    backend = backend or MockBackend()
    g = Graph()
    agents_done = 0
    paper_refs: dict = {}  # paper cid -> (openalex_id, [referenced_work_ids]) for cites
    online = getattr(backend, "name", None) != "mock"  # mock stays fully offline
    for e in parse_entries(md):
        if limit is not None and agents_done >= limit:
            break  # iteration budget: stop after N agents (bounds classify spend too)
        url_kind, cid = classify_url(e["url"])
        cls = backend.classify(e)  # LLM (or regex for mock); not classify_url
        etype, name = cls.get("kind"), cls.get("name")

        if etype != "agent" or not name:
            if etype == "benchmark" and name:
                g.add_node("benchmark:" + slugify(name), "benchmark", name=name)
            else:  # paper / other -> paper node (kept only if something links it)
                g.add_node(cid, "paper", title=e["title"], venue=e["venue"])
                if online:
                    oa = resolve.openalex(cid)
                    paper_refs[cid] = (oa.get("openalex_id"),
                                       oa.get("referenced_works", []))
            continue

        agents_done += 1
        logger.info(f"agent [{agents_done}]: {name}")

        aid = "agent:" + slugify(name)
        g.add_node(aid, "agent", name=name, one_liner=e["title"])

        # ground the model in real text (skip for offline mock runs)
        if online:
            e = {**e, **resolve.fetch_context(e["url"], url_kind, cid)}
            if context_sink is not None:
                context_sink[aid] = {"abstract": e.get("abstract"),
                                     "readme": e.get("readme")}

        # --- cheap edges (deterministic) ---
        if url_kind == "paper":
            pid = g.add_node(cid, "paper", title=e["title"], venue=e["venue"])
            g.add_edge(Edge(aid, "described_by", pid, primary=True))
            if online:
                oa = resolve.openalex(cid)
                paper_refs[cid] = (oa.get("openalex_id"), oa.get("referenced_works", []))
                for o in oa["orgs"]:
                    oid = g.add_node("org:" + slugify(o["name"]), "org",
                                     name=o["name"], ror=o.get("ror"))
                    g.add_edge(Edge(aid, "built_by", oid))
        else:
            health = resolve.repo_health(cid) if online else {}
            rid = g.add_node(cid, "repo", url=cid, **health)
            g.add_edge(Edge(aid, "implemented_by", rid))
            # freeform built_by from the GitHub owner (OpenAlex lacks preprint affils)
            org = resolve.github_org(cid) if online else None
            if org:
                oid = g.add_node("org:" + slugify(org["name"]), "org",
                                 name=org["name"], ror=org.get("ror"))
                g.add_edge(Edge(aid, "built_by", oid))

        # --- facets + expensive edge (backend-swappable) ---
        f = backend.extract_facets(e)
        exp, d1 = guard_vocab(f["exposes"], EXPOSES)
        arch, d2 = guard_vocab(f["architecture"], ARCH)
        dom, d3 = guard_vocab(f["domains"], DOMAINS, DOMAIN_ALIASES)
        # An agent may recur (paper + repo entries): UNION multi-valued facets across
        # entries instead of letting the last extraction clobber the first.
        node = g.nodes[aid]
        node["exposes"] = sorted(set(node.get("exposes", [])) | set(exp))
        arch_set = set(node.get("architecture", [])) | set(arch)
        # rules.yml-style class rule: single_agent / multi_agent are mutually exclusive;
        # when sources disagree, the more specific multi_agent dominates.
        if {"single_agent", "multi_agent"} <= arch_set:
            arch_set.discard("single_agent")
            review_log.append({"agent": aid, "rule": "single_agent dominated by multi_agent"})
        node["architecture"] = sorted(arch_set)
        for dn in dom:
            did = g.add_node("domain:" + dn, "domain", name=dn)
            g.add_edge(Edge(aid, "targets", did))
        for ev in f["evaluated_on"]:
            bid = g.add_node("benchmark:" + slugify(ev["benchmark"]), "benchmark",
                             name=ev["benchmark"])
            g.add_edge(Edge(aid, "evaluated_on", bid,
                            provenance={"source": ev["source"], "evidence": ev["evidence"]}))
        for d in (d1 + d2 + d3):
            review_log.append({"agent": aid, "dropped_or_aliased": d})

    # cites overlay (SPEC §6.2): catalog-internal Paper->Paper edges from OpenAlex
    # referenced_works. Only edges between papers BOTH in the catalog are kept — never
    # pull external refs in (they would explode and dominate layout). Default-off is a
    # rendering concern; the data is always present.
    oaid_to_cid = {oaid: c for c, (oaid, _) in paper_refs.items() if oaid}
    for c, (_, refs) in paper_refs.items():
        for r in refs:
            tgt = oaid_to_cid.get(r)
            if tgt and tgt != c:
                g.add_edge(Edge(c, "cites", tgt))

    # prune orphans: a node you cannot traverse to/from earns no place (SPEC §1 — nodes
    # are things you traverse *through*). Drops unlinked survey papers and benchmarks no
    # catalog agent is evaluated on; they return as soon as an edge connects them.
    degree: dict = {}
    for ed in g.edges:
        degree[ed["src"]] = degree.get(ed["src"], 0) + 1
        degree[ed["dst"]] = degree.get(ed["dst"], 0) + 1
    pruned = [nid for nid in g.nodes if not degree.get(nid)]
    for nid in pruned:
        del g.nodes[nid]
    review_log.extend({"pruned_orphan": nid} for nid in pruned)
    cites_n = sum(1 for ed in g.edges if ed["rel"] == "cites")
    logger.info(f"built {agents_done} agents, {len(g.nodes)} nodes, {len(g.edges)} "
                f"edges (cites={cites_n}); pruned {len(pruned)} orphans")
    return g


def summarize(g: Graph) -> dict:
    n_by_type, e_by_rel = {}, {}
    for n in g.nodes.values():
        n_by_type[n["type"]] = n_by_type.get(n["type"], 0) + 1
    for e in g.edges:
        e_by_rel[e["rel"]] = e_by_rel.get(e["rel"], 0) + 1
    return {"nodes": n_by_type, "edges": e_by_rel}


def run(settings: Settings, backend=None, limit=None, n_profiles=0,
        use_sources=False) -> tuple[Graph, list, list]:
    """Full pipeline: read list (local file or SPEC §11 sources), build graph, write
    graph.json, optionally draft N agent profiles. Returns (graph, review, paths)."""
    backend = backend or make_backend(settings)
    review: list = []
    ctx: dict = {}
    src = "SPEC §11 sources" if use_sources else str(settings.list_path)
    logger.info(f"crawl: {src}")
    md = sources.crawl_sources() if use_sources else crawl(settings.list_path)
    logger.info(f"crawled {len(md)} chars; building (backend={backend.name}, limit={limit})")
    g = build(md, review, backend, limit=limit, context_sink=ctx)
    out = {"nodes": list(g.nodes.values()), "edges": g.edges}
    settings.out_path.parent.mkdir(parents=True, exist_ok=True)
    settings.out_path.write_text(json.dumps(out, indent=2))
    settings.review_path.write_text(json.dumps(review, indent=2))
    written: list = []
    if n_profiles:
        written = profiles.generate(g, ctx, backend, review, limit=n_profiles)
    return g, review, written
