---
slug: pasa
name: PaSa
type: agent
exposes: [web_ui]
architecture: [multi_agent]
---

PaSa is a multi_agent system built by [[org:bytedance]] designed to facilitate comprehensive academic paper search. The system utilizes a Crawler agent to autonomously navigate search tools and citation networks, while a Selector agent evaluates retrieved papers against specific user criteria. Users can interact with the system through a web_ui.

The agent is optimized using reinforcement learning on the [[benchmark:autoscholarquery]] dataset, which contains 35k synthetic academic queries. Its performance is assessed using [[benchmark:realscholarquery]], a benchmark of real-world research queries within the [[domain:literature]] domain.
