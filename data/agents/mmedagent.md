---
slug: mmedagent
name: MMedAgent
type: agent
exposes: [library, web_ui]
architecture: [multi_agent, rag, tool_registry]
---

MMedAgent is a multimodal medical AI agent designed to perform diverse medical tasks by integrating a wide spectrum of specialized tools. Developed by [[org:wangyixinxin]], the system utilizes a multi_agent architecture supported by rag and a tool_registry to process information across various modalities, specifically targeting [[domain:medical_imaging]] tasks such as VQA, classification, grounding, and segmentation.

The system is provided as a library and includes a web_ui for user interaction. It leverages established models and data sources to handle clinical inputs including MRI, CT, X-ray, and histology, while also supporting medical report generation and retrieval augmented generation.
