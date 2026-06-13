"""Biomedical Agent Knowledge Graph pipeline (see SPEC.md).

A staged, mostly-deterministic pipeline that turns awesome-list markdown into a
generated graph. The one model-touched stage (facet/edge extraction) sits behind a
swappable backend; everything else is deterministic Python.
"""

__version__ = "0.1.0"
