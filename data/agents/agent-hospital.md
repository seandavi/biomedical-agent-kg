---
slug: agent-hospital
name: Agent Hospital
type: agent
exposes: [cli, web_ui]
architecture: [multi_agent, self_evolving]
---

Agent Hospital is a multi-agent, self-evolving system built by [[org:wisdom-pan]] that simulates a complete clinical environment. By utilizing LLMs as autonomous agents, the system models the interactions between patients, nurses, and doctors to facilitate the treatment process. The platform exposes both a cli and a web_ui for user interaction and environment management.

The system enables doctor agents to evolve through the treatment of thousands of patient agents, eliminating the need for manual data labeling. This approach targets [[domain:clinical_qa]] and has been evaluated_on the [[benchmark:medqa]] dataset, where the evolved agents have demonstrated performance exceeding state-of-the-art methods.
