---
slug: llm-peer-review
name: LLM-Peer-Review
type: agent
exposes: [web_ui]
architecture: [single_agent]
---

LLM-Peer-Review is a single_agent system built by [[org:vijaygkr]] designed to facilitate document editing and review. It provides a web_ui that mimics collaborative document review features, allowing users to view, accept, or reject specific AI-generated comments, insertions, and replacements.

The system utilizes Claude 3.5 Sonnet to markup text based on user-provided prompts. It is currently constrained by an 8192 output token limit, which may impact the review of longer documents.
