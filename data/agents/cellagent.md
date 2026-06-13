---
slug: cellagent
name: CellAgent
type: agent
exposes: [web_ui]
architecture: [multi_agent]
---

CellAgent is an LLM-driven multi-agent framework designed to automate the processing and execution of [[domain:single_cell]] data analysis. By utilizing a hierarchical decision-making mechanism, the system coordinates specialized biological expert roles—including a planner, executor, and evaluator—to manage complex analytical workflows without human intervention.

The framework incorporates a self-iterative optimization mechanism that allows it to autonomously evaluate and refine its outputs. Accessible via a web_ui, CellAgent identifies optimal tools and hyperparameters for [[domain:single_cell]] tasks, aiming to reduce the manual workload associated with biological research data analysis.
