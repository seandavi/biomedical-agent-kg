---
slug: ideasynth
name: IdeaSynth
type: agent
exposes: [api, web_ui]
architecture: [single_agent]
---

IdeaSynth is a single_agent system built by [[org:abhi3114-glitch]] designed to transform user browsing history into structured startup concepts. By utilizing local machine learning models for semantic clustering and cloud-based LLMs for ideation, the system identifies latent user interests and synthesizes them into actionable business opportunities.

The platform exposes its functionality through an api and a web_ui, supported by a decoupled client-server architecture. It integrates a Chrome extension for secure data extraction, a FastAPI backend for processing and vectorization, and a Next.js frontend for interactive data visualization.
