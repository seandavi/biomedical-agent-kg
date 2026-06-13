---
slug: txagent
name: TxAgent
type: agent
exposes: [library, skills, web_ui]
architecture: [multi_agent, rag, tool_registry]
---

TxAgent is an AI agent designed for therapeutic reasoning, developed by [[org:harvard-medical-school]]. Utilizing a multi_agent architecture with rag and a tool_registry, the system integrates a library of 211 tools to perform multi-step reasoning and real-time biomedical knowledge retrieval. It is built to support tasks in [[domain:drug_discovery]] and [[domain:clinical_qa]], enabling the analysis of drug interactions, contraindications, and personalized treatment strategies.

The system exposes its capabilities through a library, skills, and a web_ui. Its performance has been evaluated on the [[benchmark:drugpc]], [[benchmark:brandpc]], [[benchmark:genericpc]], [[benchmark:treatmentpc]], and [[benchmark:descriptionpc]] benchmarks. By synthesizing evidence from diverse biomedical sources, TxAgent iteratively refines recommendations based on patient-specific characteristics and clinical objectives.
