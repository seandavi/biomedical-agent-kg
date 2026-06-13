---
slug: sragent
name: SRAgent
type: agent
---

SRAgent is a system designed for agentic workflows focused on retrieving and processing data from the Sequence Read Archive. Developed by [[org:arcinstitute]], the system utilizes a hierarchical agent structure to perform tasks such as dataset summarization, metadata extraction, and accession conversion.

The framework integrates multiple tools, including the Entrez API, SRA BigQuery, and direct sequence data analysis via sra-stat and fastq-dump. Additionally, it features a dedicated papers agent to locate and download manuscripts linked to specific SRA accessions. The system supports optional SQL database integration for tracking processing progress and is utilized in the scBaseCount project.
