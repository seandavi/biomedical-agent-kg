---
slug: geneagent
name: GeneAgent
type: agent
exposes: [cli, notebook, web_ui]
architecture: [single_agent]
---

GeneAgent is a single_agent system built by [[org:ncbi-nlp]] designed to facilitate gene set knowledge discovery. By integrating a self-verification mechanism, the agent autonomously interacts with various [[domain:genomics_db]] via Web APIs to perform fact verification. This process reduces hallucinations and provides evidence-based insights, ensuring the generation of reliable analytical narratives for functional genomics.

The system supports [[domain:scientific_discovery]] by annotating gene functions and interpreting biological processes, effectively bridging the gap between raw LLM outputs and established [[domain:literature]]. GeneAgent is accessible through a cli, notebook, and web_ui, allowing users to analyze gene sets and derive novel functional insights.
