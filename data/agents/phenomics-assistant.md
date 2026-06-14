---
slug: phenomics-assistant
name: Phenomics Assistant
type: agent
exposes: [web_ui]
architecture: [rag, single_agent]
---

Phenomics Assistant is a chat-based interface built by [[org:monarch-initiative]] designed to facilitate natural language exploration of the Monarch knowledge graph. By utilizing a single_agent architecture powered by rag, the system enables users to interactively discover complex relationships between diseases, genes, and phenotypes while improving the factual reliability of LLM-generated responses.

The system exposes a web_ui to support its primary function of [[domain:clinical_qa]]. Through this interface, the assistant interprets user queries to retrieve and summarize data from the underlying biomedical database, providing a more accessible way for non-expert users to navigate and query structured knowledge.
