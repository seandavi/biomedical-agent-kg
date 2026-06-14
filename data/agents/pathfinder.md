---
slug: pathfinder
name: PathFinder
type: agent
exposes: [library]
architecture: [multi_agent]
---

PathFinder is a multi-modal, multi-agent system designed for medical diagnostic decision-making in histopathology. Built by [[org:servo]], the framework emulates the iterative, multi-scale workflow of expert pathologists by utilizing four specialized agents—Triage, Navigation, Description, and Diagnosis—to analyze whole slide images. This collaborative approach allows the system to gather evidence, generate importance maps, and provide comprehensive diagnoses with natural language explanations.

The system targets [[domain:medical_imaging]] and has demonstrated high performance in skin melanoma classification, surpassing state-of-the-art methods and human pathologist benchmarks. PathFinder is available as a library, providing an interpretable and efficient solution for complex diagnostic tasks.
