---
slug: mga
name: MGA
type: agent
exposes: [library]
architecture: [single_agent]
---

MGA is a single_agent system designed as a medical generalist agent that utilizes text-guided knowledge transformation to address diverse clinical tasks. By leveraging clinical daily reports as a transmission medium, the agent adapts to various requirements without the need for task-specific downstream branches, reducing model complexity and human inductive bias.

The system is implemented as a library and has been validated on open-source X-ray datasets, including MIMIC-CXR and CheXpert. Its capabilities are focused on tasks within [[domain:clinical_qa]] and [[domain:medical_imaging]], demonstrating the effectiveness of using professional medical language to guide agent behavior.
