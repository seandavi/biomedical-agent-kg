"""Tiny on-disk JSON cache. Two uses during prompt iteration:

- namespace "context": fetched README/abstract keyed by url (avoids re-fetch).
- namespace "facets": model output keyed by model+prompt+payload (avoids re-spend).

Editing FACET_SYSTEM_PROMPT changes the facets key -> cache misses -> re-call. Same
prompt + same input -> hit -> 0 tokens. Bust manually by deleting .cache/.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

CACHE_DIR = pathlib.Path(".cache")


def _path(ns: str, key: str) -> pathlib.Path:
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
    d = CACHE_DIR / ns
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{h}.json"


def get(ns: str, key: str):
    p = _path(ns, key)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def put(ns: str, key: str, value) -> None:
    _path(ns, key).write_text(json.dumps(value), encoding="utf-8")
