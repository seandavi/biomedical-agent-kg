---
slug: chemminer
name: ChemMiner
type: agent
exposes: [library]
architecture: [multi_agent]
---

ChemMiner is a multi_agent system designed to extract high-fidelity chemical data from scientific [[domain:literature]]. Built by [[org:nikki0526]], the framework utilizes specialized agents to perform coreference mapping, multimodal information extraction, and synthesis analysis, enabling the conversion of unstructured text and figures into structured reaction schemas.

The system is available as a library and employs a coreference-first workflow to resolve complex chemical naming conventions and abbreviations. By automating the extraction of reactants, reagents, solvents, and yields, ChemMiner achieves reaction identification performance comparable to human experts while significantly reducing processing time.
