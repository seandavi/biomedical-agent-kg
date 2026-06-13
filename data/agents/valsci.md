---
slug: valsci
name: Valsci
type: agent
exposes: [api, web_ui]
architecture: [rag]
---

Valsci is an open-source, self-hostable agent built by [[org:bricee98]] to automate the verification of scientific claims. By utilizing a rag architecture, the system integrates with the Semantic Scholar database to ground its analyses in verifiable published findings, effectively reducing hallucinations and improving citation accuracy.

The platform targets [[domain:literature]] review workflows by combining structured bibliometric scoring—such as H-index and citation counts—with guided chain-of-thought prompting. Valsci supports high-throughput asynchronous processing and is accessible via both an api and a web_ui, allowing users to validate claims against a wide range of OpenAI-compatible LLM backends.
