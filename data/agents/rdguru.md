---
slug: rdguru
name: RDguru
type: agent
exposes: [web_ui]
architecture: [multi_agent, rag]
---

RDguru is a conversational intelligent agent designed to support clinical decision-making for rare diseases. Utilizing a multi-agent architecture and retrieval-augmented generation, the system integrates authoritative knowledge sources to provide evidence-traceable responses and professional consultations. It is accessible via a web_ui to assist clinicians with knowledge Q&A, automated phenotype annotation, and differential diagnosis.

The system employs a multi-source fusion diagnostic model that combines GPT-4, PheLR, and phenotype matching to improve diagnostic recall. By facilitating multi-round, phenotype-oriented questioning, RDguru helps refine diagnostic prioritization, specifically targeting [[domain:clinical_qa]] tasks. Evaluations indicate that the agent outperforms standard models in generating clinically aligned descriptions and improving diagnostic accuracy for rare disease cases.
