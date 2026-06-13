---
slug: txagent
name: TxAgent
type: agent
exposes: [library, skills, web_ui]
architecture: [multi_agent, rag, tool_registry]
---

TxAgent is an AI agent designed for therapeutic reasoning, developed by [[org:harvard-medical-school]]. It utilizes a multi-agent, rag, and tool-registry architecture to perform multi-step reasoning and real-time biomedical knowledge retrieval. The system exposes a library, skills, and a web_ui to facilitate the analysis of drug interactions, contraindications, and personalized treatment strategies.

The agent is built to address [[domain:clinical_qa]] by synthesizing evidence from diverse biomedical sources and executing structured function calls. Its performance is evaluated on the [[benchmark:drugpc]], [[benchmark:brandpc]], [[benchmark:genericpc]], [[benchmark:treatmentpc]], and [[benchmark:descriptionpc]] benchmarks.
