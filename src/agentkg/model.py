"""Graph node/edge model + slug helper."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


@dataclass
class Edge:
    src: str
    rel: str
    dst: str
    primary: bool = False
    provenance: dict | None = None  # expensive edges only (SPEC §6)


@dataclass
class Graph:
    nodes: dict = field(default_factory=dict)  # id -> node dict
    edges: list = field(default_factory=list)
    _edge_keys: set = field(default_factory=set)  # (src, rel, dst) seen — dedup

    def add_node(self, _id, _type, **attrs):
        if _id not in self.nodes:
            self.nodes[_id] = {"id": _id, "type": _type, **attrs}
        return _id

    def add_edge(self, e: Edge):
        # An agent recurs across list entries (paper + repo); drop identical edges so
        # the second pass doesn't double them (SPEC §11 dedup on canonical join keys).
        key = (e.src, e.rel, e.dst)
        if key in self._edge_keys:
            return
        self._edge_keys.add(key)
        self.edges.append(asdict(e))
