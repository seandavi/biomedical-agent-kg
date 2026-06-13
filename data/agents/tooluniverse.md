---
slug: tooluniverse
name: ToolUniverse
type: agent
exposes: [api, cli, library, mcp, skills]
architecture: [multi_agent, tool_registry]
---

ToolUniverse is a multi-agent system built by [[org:harvard-medical-school]] designed to democratize the creation of AI scientist systems. It utilizes a tool registry and a standardized AI-Tool Interaction Protocol to enable large language models to identify and execute tools across diverse scientific domains, including [[domain:drug_discovery]], [[domain:literature]], and [[domain:multi_omics]].

The system exposes its functionality through an api, cli, library, mcp, and a collection of skills. It integrates over 1,000 machine learning models, datasets, and scientific packages, supporting both programmatic access for developers and native integration with the Model Context Protocol for AI agent workflows.
