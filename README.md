# GenomeMCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Enabled-green.svg)](https://modelcontextprotocol.io/)

A **Research-Grade Model Context Protocol (MCP) Server** for high-fidelity genomic intelligence.

## 🧬 Capabilities

### Core Features

- **Intelligent Variant Search**: `search_clinvar("BRCA1")`
- **Deep Evidence Retrieval**: `get_supporting_literature("ID")` (Cites PubMed sources)
- **Biological Context**: `get_gene_info("TP53")`

### 🚀 Bio-Discovery Module

Advanced tools for finding "undiscovered correlations":

1.  **Phenotype Discovery**: `find_related_genes("Lynch Syndrome")` -> Returns ranked candidate genes (e.g., MSH2, MLH1).
2.  **Genomic Mapping**: `get_genomic_context("BRCA1", 150)` -> Identifies "Exon 2" vs "Intron".
3.  **Research Synthesis**: `get_discovery_evidence("Phenotype")` -> Aggregates abstracts for AI reasoning.
4.  **Population Stats**: `get_population_stats("1-123-G-A")` -> Checks variant frequency in gnomAD.
5.  **Pathway Analysis**: `get_pathway_info("TP53")` -> Maps gene to Reactome molecular pathways.
6.  **Pathway Visualization**: `visualize_pathway("TP53")` -> Generates Mermaid.js diagrams.

## 📥 Installation

```bash
git clone https://github.com/nexisdev/GenomeMCP.git
cd GenomeMCP
uv sync
uv run python src/main.py
```

See [docs/](docs/) for full architecture and usage guides.
