---
slug: cxr-agent
name: CXR-Agent
type: agent
exposes: [cli, mcp, web_ui]
architecture: [multi_agent, rag, tool_registry]
---

CXR-Agent is a system built by [[org:gowthamaan-aerobiosys]] designed for chest X-ray interpretation and uncertainty-aware radiology reporting. It utilizes a multi_agent architecture with rag and a tool_registry to orchestrate vision-language models, aiming to improve the accuracy and safety of AI-generated reports within the field of [[domain:medical_imaging]].

The system provides a unified conversational interface that supports [[domain:clinical_qa]] through multiple access points, including a web_ui, cli, and mcp. By integrating components like CheXagent and BioViL-T, the agent processes scans and medical histories to generate reports that localize and describe pathologies based on their likelihood.
