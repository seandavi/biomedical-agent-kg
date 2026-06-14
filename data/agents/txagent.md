---
slug: txagent
name: TxAgent
type: agent
exposes: [library, skills, web_ui]
architecture: [multi_agent, rag, tool_registry]
---

TxAgent is a biomedical AI agent built by [[org:harvard-medical-school]] designed to provide personalized treatment recommendations through multi-step reasoning and real-time knowledge retrieval. Utilizing a multi_agent architecture with rag and a tool_registry, the system accesses a toolbox of 211 tools to analyze drug interactions, contraindications, and patient-specific strategies. It is accessible via a library, skills, and a web_ui.

The system focuses on tasks within [[domain:clinical_qa]] and [[domain:drug_discovery]]. Its performance is validated across five benchmarks: [[benchmark:drugpc]], [[benchmark:brandpc]], [[benchmark:genericpc]], [[benchmark:treatmentpc]], and [[benchmark:descriptionpc]]. By synthesizing evidence from biomedical sources, TxAgent aims to improve therapeutic decision-making and reduce adverse events.
