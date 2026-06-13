---
slug: malade
name: Malade
type: agent
exposes: [library]
architecture: [multi_agent, rag]
---

Malade is a multi-agent library designed for pharmacovigilance, specifically focusing on the extraction of adverse drug events from diverse text sources. By utilizing a rag architecture, the system augments LLM queries with relevant data to identify drug-outcome associations and provide supporting explanations.

The system is engineered to synthesize information from sources such as [[domain:literature]] and drug labels. It is designed to support tasks within [[domain:clinical_qa]] by extracting structured associations and assessing their strength, demonstrating efficacy in identifying adverse events from complex narrative data.
