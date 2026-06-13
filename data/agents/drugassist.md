---
slug: drugassist
name: DrugAssist
type: agent
exposes: [web_ui]
architecture: [single_agent]
---

DrugAssist is a single_agent system built by [[org:blazerye]] designed for molecule optimization. It leverages a large language model, specifically a fine-tuned version of Llama2-7B-Chat, to assist in tasks related to [[domain:drug_discovery]].

The system provides a web_ui for user interaction and supports deployment via quantized models for varied hardware configurations. Users can access the underlying model weights and the MolOpt-Instructions dataset to facilitate training and evaluation of molecular optimization results.
