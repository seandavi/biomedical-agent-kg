"""Assembly: crawl -> parse cheap edges -> resolve -> facets (backend) -> guard -> emit.

Deterministic except the backend.extract_facets call; guard_vocab re-imposes the
determinism boundary after it.
"""
from __future__ import annotations

import json

from . import resolve
from .backends import MockBackend, make_backend
from .config import Settings
from .model import Edge, Graph, slugify
from .parse import classify_url, crawl, looks_like_agent, parse_entries
from .vocab import ARCH, DOMAIN_ALIASES, DOMAINS, EXPOSES, guard_vocab


def build(md: str, review_log: list, backend=None, limit=None) -> Graph:
    backend = backend or MockBackend()
    g = Graph()
    agents_done = 0
    for e in parse_entries(md):
        kind, cid = classify_url(e["url"])
        agent_name = looks_like_agent(e["title"])

        if not agent_name:
            g.add_node(cid, "paper", title=e["title"], venue=e["venue"])
            continue

        if limit is not None and agents_done >= limit:
            break  # iteration budget: stop after N agents
        agents_done += 1

        aid = "agent:" + slugify(agent_name)
        g.add_node(aid, "agent", name=agent_name, one_liner=e["title"])

        # ground the model in real text (skip for offline mock runs)
        if getattr(backend, "name", None) != "mock":
            e = {**e, **resolve.fetch_context(e["url"], kind, cid)}

        # --- cheap edges (deterministic) ---
        if kind == "paper":
            pid = g.add_node(cid, "paper", title=e["title"], venue=e["venue"])
            g.add_edge(Edge(aid, "described_by", pid, primary=True))
            for o in resolve.openalex(cid)["orgs"]:
                oid = g.add_node("org:" + slugify(o["name"]), "org",
                                 name=o["name"], ror=o.get("ror"))
                g.add_edge(Edge(aid, "built_by", oid))
        else:
            rid = g.add_node(cid, "repo", url=cid)
            g.add_edge(Edge(aid, "implemented_by", rid))

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
    return g


def summarize(g: Graph) -> dict:
    n_by_type, e_by_rel = {}, {}
    for n in g.nodes.values():
        n_by_type[n["type"]] = n_by_type.get(n["type"], 0) + 1
    for e in g.edges:
        e_by_rel[e["rel"]] = e_by_rel.get(e["rel"], 0) + 1
    return {"nodes": n_by_type, "edges": e_by_rel}


def run(settings: Settings, backend=None, limit=None) -> tuple[Graph, list]:
    """Full pipeline: read list, build graph, write graph.json. Returns (graph, review)."""
    backend = backend or make_backend(settings)
    review: list = []
    g = build(crawl(settings.list_path), review, backend, limit=limit)
    out = {"nodes": list(g.nodes.values()), "edges": g.edges}
    settings.out_path.write_text(json.dumps(out, indent=2))
    return g, review
