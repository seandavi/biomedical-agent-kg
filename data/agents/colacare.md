---
slug: colacare
name: ColaCare
type: agent
exposes: [web_ui]
architecture: [multi_agent, rag]
---

ColaCare is a multi-agent framework designed to enhance Electronic Health Record modeling by integrating domain-specific expert models with large language models. Utilizing a multidisciplinary team approach, the system employs DoctorAgents and a MetaAgent to collaboratively analyze patient data, bridging the gap between structured numerical records and text-based clinical reasoning.

The system incorporates a retrieval-augmented generation module grounded in the Merck Manual of Diagnosis and Therapy to provide evidence-based support. By facilitating collaborative consultations and debates, ColaCare addresses complex tasks such as [[domain:clinical_qa]], mortality outcome prediction, and readmission forecasting. The platform is accessible via a web_ui to support clinical decision-making and precision medicine.
