---
slug: funsearch
name: FunSearch
type: agent
exposes: [notebook]
architecture: [multi_agent, self_evolving]
---

FunSearch is a system built by [[org:google-deepmind]] that utilizes a multi_agent, self_evolving architecture to facilitate [[domain:scientific_discovery]]. By leveraging large language models to perform program search, the system generates novel heuristics and functions for complex mathematical and combinatorial problems.

The framework exposes its functionality through a notebook interface, allowing users to explore discovered solutions for problems such as cap sets, admissible sets, and bin packing. The provided implementation includes evolutionary algorithm routines designed to support the adaptation of the pipeline for various language models and execution environments.
