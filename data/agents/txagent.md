---
slug: txagent
name: TxAgent
type: agent
exposes: [library, skills, web_ui]
architecture: [multi_agent, rag, tool_registry]
---

TxAgent is a multi-agent system built by [[org:harvard-medical-school]] designed to provide personalized treatment recommendations through multi-step reasoning and real-time knowledge retrieval. Utilizing a rag architecture and a tool_registry containing 211 specialized tools, the system analyzes drug interactions, contraindications, and patient-specific strategies. It is accessible via a library, a suite of skills, and a web_ui.

The system targets applications in [[domain:clinical_qa]] and [[domain:drug_discovery]]. Its performance is validated across five benchmarks: [[benchmark:drugpc]], [[benchmark:brandpc]], [[benchmark:genericpc]], [[benchmark:treatmentpc]], and [[benchmark:descriptionpc]]. By synthesizing evidence from biomedical sources, TxAgent ensures that its therapeutic outputs align with clinical guidelines and real-world evidence.
