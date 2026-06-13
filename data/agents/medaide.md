---
slug: medaide
name: MedAide
type: agent
exposes: [web_ui]
architecture: [multi_agent, rag]
---

MedAide is a multi-agent framework designed to enhance healthcare intelligence through intent-aware information fusion and coordinated reasoning. By utilizing a regularization-guided module that integrates syntactic constraints with rag, the system decomposes complex queries into structured representations to mitigate hallucinations and information redundancy.

The architecture employs a dynamic intent prototype matching module for adaptive recognition during multi-round dialogues and a rotation agent collaboration mechanism for decision-level information fusion. These capabilities allow MedAide to address complex medical intents, specifically targeting [[domain:clinical_qa]] tasks. The system is accessible via a web_ui and has demonstrated improved medical proficiency and strategic reasoning across multiple benchmarks.
