---
slug: chatspatial
name: ChatSpatial
type: agent
exposes: [mcp]
architecture: [tool_registry]
---

ChatSpatial is a specialized MCP server designed to facilitate [[domain:spatial]] transcriptomics analysis through natural language. Built by [[org:cafferychen777]], the system utilizes a tool_registry architecture to provide schema-enforced orchestration, replacing ad-hoc code generation with a stable interface for reproducible workflows.

The agent exposes 20 schema-validated mcp tools that manage 65 analytical methods across 15 categories, including data preprocessing, spatial domain identification, deconvolution, and cell-cell communication. It is compatible with any mcp-capable client and supports diverse data formats such as 10x Visium, Xenium, Slide-seq v2, MERFISH, and seqFISH.
