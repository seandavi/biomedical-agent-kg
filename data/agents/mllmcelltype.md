---
slug: mllmcelltype
name: mLLMCelltype
type: agent
exposes: [api, library, notebook, web_ui]
architecture: [multi_agent]
---

mLLMCelltype is a multi-agent framework designed for automated cell type annotation in [[domain:single_cell]] transcriptomics. Built by [[org:cafferychen777]], the system utilizes a consensus-based approach that integrates predictions from multiple large language models to improve annotation accuracy and provide uncertainty metrics without requiring reference datasets.

The platform is accessible via an api, library, notebook, and web_ui, allowing for integration into existing analysis workflows. Its performance has been validated through [[benchmark:yang-et-al-2025]], demonstrating the efficacy of its multi-model consensus methodology.
