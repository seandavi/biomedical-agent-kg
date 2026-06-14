---
slug: biodiscoveryagent
name: BioDiscoveryAgent
type: agent
exposes: [cli, library]
architecture: [multi_agent]
---

BioDiscoveryAgent is a multi_agent system built by [[org:stanford-university]] designed to automate the closed-loop design of genetic [[domain:perturbation]] experiments. By leveraging large language models and a suite of integrated tools—including literature search, gene search, and AI-driven critique—the agent navigates hypothesis spaces to identify gene subsets that achieve specific phenotypes without requiring explicit acquisition functions or model training.

The system is available as a library and via a cli, allowing users to execute experiments and analyze biological datasets. It has demonstrated significant improvements in predicting relevant genetic perturbations and gene combinations compared to traditional Bayesian optimization baselines, offering an interpretable framework to accelerate [[domain:scientific_discovery]].
