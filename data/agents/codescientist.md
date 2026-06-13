---
slug: codescientist
name: CodeScientist
type: agent
exposes: [api, web_ui]
architecture: [multi_agent]
---

CodeScientist, built by [[org:allenai]], is an end-to-end system designed to facilitate [[domain:scientific_discovery]] through semi-automated experimentation. Utilizing a multi_agent architecture, the system generates novel research ideas by applying genetic mutations to combinations of scientific literature and code. It features an Experiment Builder that automatically implements, executes, and debugs Python-based experiments within a containerized environment, ultimately producing comprehensive reports and meta-analyses.

The system supports both human-in-the-loop and fully-automatic operational modes, providing flexibility for researchers to guide or automate the discovery process. Users can interact with the platform via an api or a web_ui to manage ideation lists, execute experiments, and review generated raw data and logs.
