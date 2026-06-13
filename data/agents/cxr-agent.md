---
slug: cxr-agent
name: CXR-Agent
type: agent
architecture: [multi_agent]
---

CXR-Agent is a multi_agent system designed for the interpretation of chest X-rays and the generation of radiology reports. By leveraging foundational vision-language models, the system integrates visual data with medical histories to improve the accuracy and safety of automated clinical documentation.

The agent utilizes components such as CheXagent’s vision transformer and BioViL-T’s phrase grounding tools to produce uncertainty-aware reports. This approach addresses common issues like confident hallucinations in [[domain:medical_imaging]], providing localized pathology descriptions based on likelihood to support respiratory specialists in their clinical evaluations.
