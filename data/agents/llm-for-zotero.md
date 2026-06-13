---
slug: llm-for-zotero
name: llm-for-zotero
type: agent
exposes: [skills, web_ui]
architecture: [multi_agent]
---

llm-for-zotero is a research agent system built by [[org:yilewang]] that integrates large language models directly into the Zotero reader. It targets [[domain:literature]] workflows, allowing users to summarize papers, inspect figures, and compare sources without leaving their library. The system supports various backends, including API providers, local models, and web-based chat services.

Utilizing a multi_agent architecture, the system exposes a web_ui and a range of skills to facilitate library-wide tasks such as searching, tagging, metadata management, and note-editing. Users can save research notes and conversations directly to Zotero or local Markdown folders, ensuring grounded answers with citations that link back to source passages.
