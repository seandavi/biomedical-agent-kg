---
slug: bioagents
name: BioAgents
type: agent
exposes: [api]
architecture: [multi_agent, rag]
---

BioAgents is a multi-agent system designed to streamline complex bioinformatics workflows through a combination of small language models and retrieval augmented generation. Built by [[org:bio-xyz]], the system is optimized for local operation and personalization using proprietary data, providing nuanced guidance for tasks that typically require specialized expertise.

The system targets applications across [[domain:literature]], [[domain:scientific_discovery]], and [[domain:genomics_db]]. It is evaluated on [[benchmark:bixbench]] and exposes its functionality via an api, enabling users to perform conceptual genomics tasks with performance comparable to human experts.
