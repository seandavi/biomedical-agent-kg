---
slug: autonomous-microscopy-experiments
name: Autonomous Microscopy Experiments
type: agent
exposes: [library]
architecture: [multi_agent]
---

AILA is a multi_agent framework designed to automate atomic force microscopy experiments within self-driving laboratories. By leveraging large language models, the system aims to replicate the adaptive decision-making and experimental intuition required for complex tasks such as calibration, feature detection, and mechanical property measurement.

The framework is evaluated on [[benchmark:afmbench]], a suite developed to assess performance across the entire scientific workflow. As a library, AILA serves as a testbed for advancing [[domain:scientific_discovery]], though current assessments highlight significant challenges regarding instruction adherence, multi-agent coordination, and safety alignment in autonomous laboratory settings.
