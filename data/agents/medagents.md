---
slug: medagents
name: MedAgents
type: agent
exposes: [cli, library]
architecture: [multi_agent]
---

MedAgents is a multi-agent framework developed by [[org:gersteinlab]] designed to enhance zero-shot medical reasoning through a multi-disciplinary collaboration process. The system functions by gathering domain experts to analyze clinical questions, iteratively refining reports through collaborative consultation, and reaching a unanimous final decision.

The framework is accessible via a cli and library, and it has been evaluated on [[domain:clinical_qa]] tasks. Performance assessments include benchmarks such as [[benchmark:medqa]], [[benchmark:medmcqa]], [[benchmark:pubmedqa]], and relevant medical subtasks within [[benchmark:mmlu]].
