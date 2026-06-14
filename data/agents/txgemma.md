---
slug: txgemma
name: TxGemma
type: agent
exposes: [web_ui]
architecture: [multi_agent]
---

TxGemma is a suite of efficient, generalist large language models fine-tuned from Gemma-2, designed to support therapeutic property prediction and interactive reasoning. By synthesizing information across small molecules, proteins, nucleic acids, and diseases, the system facilitates broad applications in [[domain:scientific_discovery]]. The suite features models ranging from 2B to 27B parameters, which demonstrate high data efficiency for downstream tasks like clinical trial adverse event prediction and provide natural language interfaces for mechanistic explanation.

The system also includes Agentic-Tx, a multi_agent framework that manages complex workflows and acquires external knowledge. This agentic system is accessible via a web_ui and has been rigorously evaluated on benchmarks including [[benchmark:humanity-s-last-exam]], [[benchmark:gpqa]], [[benchmark:chembench-preference]], and [[benchmark:chembench-mini]].
