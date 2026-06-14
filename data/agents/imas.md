---
slug: imas
name: IMAS
type: agent
exposes: [web_ui]
architecture: [multi_agent]
---

IMAS is a multi_agent system designed to support rural healthcare delivery by assisting community health workers and registered medical practitioners. The framework utilizes large language models to provide context-sensitive medical assistance, featuring components for translation, medical complexity assessment, expert network integration, and response simplification.

The system is specifically engineered to address [[domain:clinical_qa]] tasks, including clinical triaging and diagnostics, while accounting for cultural nuances and varying literacy levels. Its performance has been validated through evaluations on [[benchmark:medqa]] and [[benchmark:pubmedqa]], and the system is accessible via a web_ui.
