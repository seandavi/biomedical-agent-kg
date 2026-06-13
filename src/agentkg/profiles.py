"""Profile generation (SPEC §3.1): one Markdown file per agent — YAML frontmatter
(structured facets) + an LLM-drafted prose body with typed [[type:slug]] wikilinks.

Progressive enhancement: the graph is self-sufficient without these. Backfillable and
re-runnable. Emitted wikilinks are validated against real node ids; unresolved ones are
logged to the review list (SPEC §3.2 — a link pointing nowhere is an extraction signal).
"""
from __future__ import annotations

import pathlib
import re

from .log import logger

# node types with clean type:slug ids that wikilinks can target
LINKABLE = {"agent", "benchmark", "domain", "org"}
_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def _neighbors(graph, aid: str):
    out = []
    for e in graph.edges:
        if e["src"] == aid:
            n = graph.nodes.get(e["dst"])
            if n and n["type"] in LINKABLE:
                out.append((e["rel"], n["id"], n.get("name")))
    return out


def _frontmatter(node: dict) -> str:
    lines = ["---", f"slug: {node['id'].split(':', 1)[1]}",
             f"name: {node['name']}", "type: agent"]
    if node.get("exposes"):
        lines.append(f"exposes: [{', '.join(node['exposes'])}]")
    if node.get("architecture"):
        lines.append(f"architecture: [{', '.join(node['architecture'])}]")
    lines.append("---")
    return "\n".join(lines)


def _prompt(node: dict, nbrs, context: dict) -> str:
    L = [f"System: {node['name']}",
         f"Summary: {node.get('one_liner')}",
         f"exposes: {node.get('exposes')}",
         f"architecture: {node.get('architecture')}",
         "Linkable neighbors (use the exact wikilink when you mention the entity):"]
    L += [f"  - {rel} [[{nid}]] = {name}" for rel, nid, name in nbrs] or ["  (none)"]
    if context.get("abstract"):
        L.append("Abstract:\n" + context["abstract"][:3000])
    if context.get("readme"):
        L.append("README:\n" + context["readme"][:4000])
    return "\n".join(L)


def generate(graph, ctx: dict, backend, review_log: list, limit=None,
             outdir="agents") -> list[str]:
    """Draft profiles for up to `limit` agents; write <outdir>/<slug>.md. Returns paths."""
    out = pathlib.Path(outdir)
    out.mkdir(exist_ok=True)
    valid = set(graph.nodes)
    agents = [n for n in graph.nodes.values() if n["type"] == "agent"]
    written = []
    for node in agents[: limit if limit else None]:
        aid = node["id"]
        nbrs = _neighbors(graph, aid)
        body = backend.draft_profile(_prompt(node, nbrs, ctx.get(aid, {})))
        bad = [link for link in _WIKILINK.findall(body) if link not in valid]
        for link in bad:
            review_log.append({"agent": aid, "bad_wikilink": link})
        path = out / f"{aid.split(':', 1)[1]}.md"
        path.write_text(_frontmatter(node) + "\n\n" + body.strip() + "\n",
                        encoding="utf-8")
        written.append(str(path))
        logger.info(f"profile: {path}" + (f"  ({len(bad)} bad wikilinks)" if bad else ""))
    return written
