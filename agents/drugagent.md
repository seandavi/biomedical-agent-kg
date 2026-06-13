---
slug: drugagent
name: DrugAgent
type: agent
exposes: [library]
architecture: [multi_agent, rag]
---

DrugAgent is a multi-agent LLM system designed to improve the accuracy and interpretability of drug-target interaction (DTI) prediction. By utilizing a coordinator-based architecture that integrates Chain-of-Thought and ReAct frameworks, the system synthesizes evidence from machine learning predictions, knowledge graphs, and scientific [[domain:literature]] to support complex reasoning in [[domain:drug_discovery]].

The system functions as a library that leverages specialized agents to provide transparent, human-interpretable rationales for its predictions. Experimental results on kinase inhibitor datasets demonstrate that this multi-agent approach significantly enhances performance compared to non-reasoning models, offering a reliable tool for clinical decision-making and regulatory compliance.
