"""Citation layer (SPEC §6.2) — three mechanisms, all under one friction rule: an
EXTERNAL paper earns a node only if it connects >= min_links catalog papers.

  A  catalog paper cites catalog paper        -> cites edge (0 new nodes)
  B  >=2 catalog papers cite external X        -> add X, catalog -> X edges
  C  external X cites >=2 catalog papers        -> add X, X -> catalog edges

A/B use referenced_works (already fetched). C fetches incoming citers from OpenAlex.
External nodes carry in_catalog=False so the SPA can style/hide them when the (default
-off) citation overlay is closed. One hop only — external papers are leaves.
"""
from __future__ import annotations

from collections import defaultdict

from . import resolve
from .log import logger
from .model import Edge


def build_citation_layer(g, paper_refs: dict, review_log: list, min_links: int = 2) -> None:
    oaid_to_cid = {oaid: cid for cid, (oaid, _) in paper_refs.items() if oaid}
    catalog = set(oaid_to_cid)
    # external openalex id -> {catalog cid: direction}; 'out' = catalog cites external
    # (mechanism B), 'in' = external cites catalog (mechanism C)
    ext: dict[str, dict] = defaultdict(dict)
    meta: dict[str, dict] = {}

    # A (internal) + B (shared references): walk each catalog paper's references
    for cid, (oaid, refs) in paper_refs.items():
        for r in refs:
            if r in catalog:                      # A: catalog -> catalog
                tgt = oaid_to_cid[r]
                if tgt != cid:
                    g.add_edge(Edge(cid, "cites", tgt))
            else:                                 # B candidate: catalog -> external
                ext[r][cid] = "out"

    # C (connectors): incoming citers of each catalog paper
    for cid, (oaid, _refs) in paper_refs.items():
        if not oaid:
            continue
        for x in resolve.citers(oaid):
            xid = x.get("id")
            if not xid:
                continue
            if xid in catalog:                    # A (other direction): catalog -> catalog
                src = oaid_to_cid[xid]
                if src != cid:
                    g.add_edge(Edge(src, "cites", cid))
            else:                                 # C candidate: external -> catalog
                ext[xid][cid] = "in"
                meta[xid] = x

    # add externals that connect >= min_links distinct catalog papers
    added = edges = 0
    for oaid, conns in ext.items():
        if len(conns) < min_links:
            continue
        m = meta.get(oaid) or resolve.work_meta(oaid)
        nid = "openalex:" + resolve._wid(oaid)
        g.add_node(nid, "paper", title=m.get("title"), year=m.get("year"),
                   cited_by_count=m.get("cited_by_count"), in_catalog=False)
        added += 1
        for cid, direction in conns.items():
            if direction == "out":
                g.add_edge(Edge(cid, "cites", nid))   # catalog cites external (B)
            else:
                g.add_edge(Edge(nid, "cites", cid))   # external cites catalog (C)
            edges += 1
    total = sum(1 for e in g.edges if e["rel"] == "cites")
    logger.info(f"cocitation: +{added} external papers, {edges} external cites edges; "
                f"{total} cites total (min_links={min_links})")
