---
slug: nvidia-biomedical-ai-q-research-agent
name: NVIDIA Biomedical AI-Q Research Agent
type: agent
exposes: [api, web_ui]
architecture: [multi_agent, rag]
---

The NVIDIA Biomedical AI-Q Research Agent is a multi-agent system built by [[org:nvidia-ai-blueprints]] designed to facilitate deep research and virtual screening. It leverages a rag architecture to synthesize information from internal documents and web sources, providing researchers with automated report generation, parallel search capabilities, and human-in-the-loop feedback mechanisms.

The system specifically targets [[domain:drug_discovery]] and [[domain:protein_structure]] workflows by integrating molecular generation and docking tools. Users can interact with the agent through a provided web_ui or integrate its functionalities via an api to support the discovery of novel small-molecule therapies.
