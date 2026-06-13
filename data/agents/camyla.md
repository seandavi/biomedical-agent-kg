---
slug: camyla
name: Camyla
type: agent
exposes: [cli]
architecture: [multi_agent]
---

Camyla is a multi_agent system built by [[org:yifangao112]] designed to automate the end-to-end research process for [[domain:medical_imaging]]. By taking a dataset as input, the system autonomously generates research hypotheses, executes deep-learning experiments, and produces publication-ready manuscripts. It is accessed via a cli and utilizes a flexible LLM routing layer to manage experiment configurations and code generation.

The system has been evaluated on [[benchmark:camylabench]], a contamination-free benchmark consisting of 31 datasets. Camyla is specifically engineered to advance [[domain:scientific_discovery]] by performing long-horizon orchestration of research tasks, ranging from literature synthesis to the compilation of LaTeX papers.
