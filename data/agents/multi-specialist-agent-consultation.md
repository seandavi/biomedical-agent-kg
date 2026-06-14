---
slug: multi-specialist-agent-consultation
name: Multi-Specialist Agent Consultation
type: agent
exposes: [library, web_ui]
architecture: [multi_agent]
---

The Agent-derived Multi-Specialist Consultation (AMSC) framework is a multi_agent system designed to simulate real-world clinical diagnostic processes. By employing tuning-free LLM-based agents as medical practitioners, the system adaptively fuses probability distributions across potential diseases to generate diagnoses based on patient symptom descriptions.

This approach targets [[domain:clinical_qa]] by modeling collaborative consultations between general practitioners and domain-specific specialists. The system is accessible via a library and web_ui, offering an efficient alternative to traditional models by reducing the need for extensive parameter updating and training time.
