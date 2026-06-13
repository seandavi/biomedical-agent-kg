---
slug: kosmos
name: Kosmos
type: agent
exposes: [cli, library]
architecture: [multi_agent]
---

Kosmos is an autonomous AI scientist built by [[org:jimmc414]] designed to facilitate [[domain:scientific_discovery]]. Utilizing a multi_agent architecture, the system automates the research lifecycle by generating hypotheses, designing experiments, and executing code within sandboxed Docker containers. It further supports the research process through literature integration, knowledge graph construction, and discovery validation using the [[benchmark:scholareval]] framework.

The system is available as both a cli and a library, providing flexibility for researchers to integrate autonomous research loops into their workflows. It features multi-provider LLM support, budget enforcement, and real-time streaming capabilities to manage and monitor complex research tasks effectively.
