---
slug: zodiac
name: Zodiac
type: agent
exposes: [cli, library]
architecture: [multi_agent]
---

Zodiac is a cardiologist-level LLM framework designed to assist in clinical diagnostics by extracting patient data characteristics, detecting arrhythmias, and generating preliminary reports. Built by [[org:gnosisguild]], the system utilizes a multi-agent architecture to process multi-modal patient data, with individual agents fine-tuned on cardiologist-adjudicated datasets to ensure professional clinical standards.

The framework is designed to support [[domain:clinical_qa]] and has been integrated into electrocardiography devices as a form of Software-as-Medical-Device. Zodiac is available for developers as a library and through a cli, providing a specialized solution for medical practice that has been validated against industry-leading models.
