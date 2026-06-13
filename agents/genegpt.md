---
slug: genegpt
name: GeneGPT
type: agent
exposes: [cli, library]
architecture: [single_agent, tool_registry]
---

GeneGPT is a single_agent system built by the [[org:national-center-for-biotechnology-information]] designed to improve the accuracy of biomedical information retrieval. By utilizing a tool_registry architecture, the system teaches LLMs to execute NCBI Web API calls through in-context learning and a specialized decoding algorithm, effectively reducing hallucinations when querying complex biological data.

The system is available as a library and via a cli, and it has been evaluated on the [[benchmark:geneturing]] suite. It is specifically engineered to navigate and extract information from [[domain:literature]] and other specialized databases, demonstrating the ability to generalize across multi-hop reasoning tasks.
