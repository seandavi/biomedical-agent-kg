---
slug: toursynbio
name: TourSynbio
type: agent
exposes: [web_ui]
architecture: [multi_agent]
---

TourSynbio is a multi-modal large model and agent framework designed to bridge text and protein sequences for protein engineering. By treating protein sequences as a natural language, the system eliminates the need for external protein encoders, instead utilizing a post-trained and instruction fine-tuned model based on InternLM2-7B. The framework is evaluated on [[benchmark:proteinlmbench]], where it demonstrates advanced capabilities in understanding and analyzing biological sequences.

The system features a multi-agent architecture that integrates various deep learning models to perform tasks such as mutation analysis, inverse folding, and [[domain:protein_structure]] prediction. Users can interact with these capabilities through a unified web_ui, which facilitates complex protein engineering workflows. The efficacy of the framework has been validated through wet lab case studies, showing improvements in enzyme modification and catalysis efficiency.
