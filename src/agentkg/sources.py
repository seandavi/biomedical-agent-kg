"""SPEC §11 crawl sources — the awesome-lists to harvest. Same system across lists is
deduped downstream on canonical join keys (DOI / repo URL). READMEs are cached by url.
"""
from __future__ import annotations

from . import cache, resolve

SOURCES = [
    "https://github.com/zhoujieli/Awesome-LLM-Agents-Scientific-Discovery",
    "https://github.com/AgenticScience/Awesome-Agent-Scientists",
    "https://github.com/AgenticHealthAI/Awesome-AI-Agents-for-Healthcare",
    "https://github.com/ai-boost/awesome-ai-for-science",
    "https://github.com/tsinghua-fib-lab/Awesome-AI-Scientists",
]


def crawl_sources(urls=None) -> str:
    """Fetch + concatenate each list's README into one markdown blob (cached by url)."""
    parts = []
    for url in urls or SOURCES:
        md = cache.get("listmd", url)
        if md is None:
            md = resolve.fetch_readme(url) or ""
            cache.put("listmd", url, md)
        if md:
            parts.append(f"\n## SOURCE: {url}\n\n{md}\n")
    return "\n".join(parts)
