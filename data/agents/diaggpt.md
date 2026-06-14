---
slug: diaggpt
name: DiagGPT
type: agent
exposes: [cli]
architecture: [multi_agent]
---

DiagGPT is a multi_agent dialogue system designed to improve task-oriented dialogue (TOD) in complex diagnostic scenarios. Built by [[org:zzlang-c]], the system utilizes automatic topic management to proactively guide users through information collection and task completion, addressing limitations in standard LLM conversational capabilities.

The framework is specifically designed to support specialized consultations, including [[domain:clinical_qa]]. It provides a cli interface and includes the LLM-TOD dataset for quantitative evaluation across twenty distinct domains, ranging from medical and legal contexts to general service-oriented tasks.
