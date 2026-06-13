---
slug: openscholar
name: OpenScholar
type: agent
exposes: [cli, library, web_ui]
architecture: [rag]
---

OpenScholar is a retrieval-augmented language model built by [[org:akariasai]] to assist scientists in navigating and synthesizing [[domain:literature]]. The system generates responses by searching for relevant papers and grounding its output in those sources.

The platform is accessible via a web_ui, a library, and a cli. It has been evaluated on [[benchmark:scholarqabench]] and includes components for offline retrieval, training, and inference.
