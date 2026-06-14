---
slug: colacare
name: ColaCare
type: agent
exposes: [cli, web_ui]
architecture: [multi_agent, rag]
---

ColaCare is a multi-agent framework built by [[org:pku-aicare]] designed to enhance Electronic Health Record (EHR) modeling. By integrating domain-specific expert models with large language models, the system simulates a multidisciplinary clinical team to bridge the gap between structured numerical data and text-based reasoning. It utilizes a meta-agent to orchestrate consultations, providing interpretable decision-making reports for [[domain:clinical_qa]] tasks.

The architecture employs a multi_agent approach supported by a rag module that incorporates medical guidelines to ensure knowledge currency. The system is accessible via a cli and web_ui, and it has demonstrated improved performance in mortality and readmission prediction tasks across multiple real-world EHR datasets.
