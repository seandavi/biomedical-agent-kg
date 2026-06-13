---
slug: cellagent
name: CellAgent
type: agent
exposes: [web_ui]
architecture: [multi_agent]
---

CellAgent is an LLM-driven multi-agent framework designed to automate the analysis of [[domain:single_cell]] data. By utilizing a hierarchical decision-making mechanism, the system coordinates specialized biological expert roles—planner, executor, and evaluator—to execute complex data analysis tasks without human intervention.

The framework incorporates a self-iterative optimization mechanism that allows it to autonomously evaluate and refine its outputs. Accessible via a web_ui, CellAgent identifies optimal tools and hyperparameters for diverse biological datasets, including those involving [[domain:spatial]] contexts, to streamline research workflows.
