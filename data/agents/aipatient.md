---
slug: aipatient
name: AIPatient
type: agent
exposes: [web_ui]
architecture: [multi_agent, rag]
---

AIPatient is a simulated patient system designed to support medical education and clinical decision-making through an LLM-powered multi-agent architecture. By integrating a rag framework with six task-specific agents, the system replicates high-fidelity doctor-patient interactions and complex medical reasoning. It is grounded in de-identified patient data from the MIMIC-III database to ensure realism in its simulated encounters.

The system exposes a web_ui to facilitate accessibility for clinicians and medical trainees. It specifically targets [[domain:clinical_qa]] tasks, achieving high accuracy and reliability in electronic health record-based evaluations. Through its combination of agentic workflows and structured knowledge, AIPatient provides a robust, stable environment for training and research.
