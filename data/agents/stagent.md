---
slug: stagent
name: STAgent
type: agent
exposes: [web_ui]
architecture: [multi_agent]
---

STAgent is a multi_agent system built by [[org:liulab-bioelectronics-harvard]] designed to facilitate the analysis of [[domain:spatial]] transcriptomics data. The system provides an end-to-end workflow for processing .h5ad datasets, integrating autonomous reasoning and visual analysis to interpret tissue organization, gene expression patterns, and structural gradients.

The platform exposes a web_ui to support multimodal interactions, allowing researchers to query datasets using text, voice, or image inputs. It features a flexible pipeline that incorporates conflict checking and literature-based synthesis to generate interpretable reports, assisting users in moving from raw data to biological insights without requiring advanced programming expertise.
