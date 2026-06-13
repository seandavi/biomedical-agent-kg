---
slug: agent-hospital
name: Agent Hospital
type: agent
exposes: [web_ui]
architecture: [multi_agent, self_evolving]
---

Agent Hospital is a multi-agent, self-evolving system that simulates a complete clinical environment. By utilizing LLMs as autonomous agents, the platform models the interactions between patients, nurses, and doctors to facilitate the treatment of illness. The system features a web_ui and allows doctor agents to evolve through continuous practice without requiring manual data labeling.

This framework targets [[domain:clinical_qa]] by enabling agents to gain experience through the treatment of tens of thousands of patient simulations. The effectiveness of these evolved agents is demonstrated by their performance on the [[benchmark:medqa]] dataset, where they outperform existing state-of-the-art medical agent methods.
