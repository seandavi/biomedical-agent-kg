---
slug: popper
name: POPPER
type: agent
exposes: [library, notebook]
architecture: [multi_agent]
---

POPPER is a multi_agent framework built by [[org:stanford-university]] designed for the rigorous automated validation of free-form hypotheses. By applying the principle of falsification, the system utilizes LLM agents to design and execute experiments that test measurable implications, incorporating a sequential testing framework to ensure strict Type-I error control.

The system is available as a library and includes a notebook for demonstration. It targets [[domain:scientific_discovery]] and has been evaluated on [[benchmark:targetval]] and [[benchmark:discoverybench]].
