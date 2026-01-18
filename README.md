# GenomeMCP

> **AI-powered genomic intelligence through the Model Context Protocol**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Enabled-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ClinVar](https://img.shields.io/badge/Data-ClinVar-orange.svg)](https://www.ncbi.nlm.nih.gov/clinvar/)
[![gnomAD](https://img.shields.io/badge/Data-gnomAD-purple.svg)](https://gnomad.broadinstitute.org/)
[![Reactome](https://img.shields.io/badge/Data-Reactome-red.svg)](https://reactome.org/)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Fnexisdev%2FGenomeMCP&envs=SUPABASE_URL%2CSUPABASE_KEY&optionalEnvs=PORT)

**GenomeMCP** is a research-grade **Model Context Protocol (MCP) server** that enables AI agents to query clinical genomics databases, retrieve supporting scientific literature, analyze population genetics, and visualize biological pathways — all in real-time.

---

## 🖥️ CLI Tool

GenomeMCP includes a beautiful command-line interface with rich formatting and an interactive TUI mode.

### Quick Install

```bash
# Recommended (any platform with Python)
pipx install genomemcp

# macOS (Homebrew)
brew install nexisdev/tap/genomemcp

# Windows (Scoop)
scoop bucket add genomemcp https://github.com/nexisdev/scoop-genomemcp
scoop install genomemcp

# From source
git clone https://github.com/nexisdev/GenomeMCP.git
cd GenomeMCP && ./install.sh
```

**Standalone binaries** available on [GitHub Releases](https://github.com/nexisdev/GenomeMCP/releases).

### CLI Commands

```bash
genomemcp search BRCA1              # 🔍 Search ClinVar
genomemcp variant 12345             # 📋 Get variant report
genomemcp gene TP53                 # 🧬 Get gene info
genomemcp pathway EGFR --visualize  # 🔬 Pathway analysis
genomemcp population 1-55516888-G-GA # 👥 gnomAD frequencies
genomemcp discover "Lynch Syndrome" # 🔗 Discover related genes
genomemcp tui                       # 🖥️ Interactive mode
```

### Theme Options

```bash
genomemcp --theme cyberpunk search BRCA1
genomemcp --theme professional gene TP53
genomemcp --theme minimal pathway EGFR
```

See [CLI Guide](docs/cli_guide.md) for complete documentation.

---

## 🎯 Why GenomeMCP?

| Problem                           | GenomeMCP Solution                           |
| --------------------------------- | -------------------------------------------- |
| AI agents lack genomic knowledge  | Direct ClinVar, gnomAD, Reactome integration |
| No evidence for clinical claims   | Auto-retrieves PubMed abstracts              |
| Variant interpretation is complex | Population frequency + pathway context       |
| Gene-disease links are opaque     | Automatic relationship discovery             |

---

## 🧬 Features

### Core Genomics Tools

- **`search_clinvar(term)`** — Query ClinVar for genes, variants, or diseases
- **`get_variant_report(id)`** — Detailed clinical significance report
- **`get_gene_info(symbol)`** — Gene function, location, and aliases from NCBI Gene
- **`get_supporting_literature(id)`** — PubMed articles linked to a variant

### Population Genetics

- **`get_population_stats(variant)`** — Allele frequency from gnomAD (Genome Aggregation Database)

### Pathway Analysis

- **`get_pathway_info(gene)`** — Reactome biological pathways for a gene
- **`visualize_pathway(gene)`** — Generate Mermaid.js diagrams of gene-pathway relationships

### Discovery & Synthesis

- **`find_related_genes(phenotype)`** — Discover genes associated with a disease
- **`get_genomic_context(gene, position)`** — Identify exon vs intron regions
- **`get_discovery_evidence(phenotype)`** — Aggregate PubMed abstracts for AI reasoning

---

## 🚀 Quick Start

### MCP Server Installation

```bash
# Clone the repository
git clone https://github.com/nexisdev/GenomeMCP.git
cd GenomeMCP

# Install dependencies with uv
uv sync

# Run the MCP server
uv run python src/main.py
```

### CLI Installation

```bash
# Using the install script
./install.sh

# Or with pip
pip install genomemcp[cli]

# Or for development
./setup-dev.sh
source .venv/bin/activate
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "genomemcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/GenomeMCP",
        "run",
        "python",
        "src/main.py"
      ]
    }
  }
}
```

```

### ☁️ Cloud Deployment (Railway)

You can deploy the GenomeMCP server to the cloud with one click. It will be exposed as an SSE (Server-Sent Events) endpoint, ready for remote agents.

1. Click the **Deploy on Railway** button above.
2. Provide your `SUPABASE_URL` and `SUPABASE_KEY` (optional, for persistence).
3. Connect your agent to the deployment URL (e.g. `https://your-app.up.railway.app/sse`).

---

## 📖 Usage Examples

### Search for a Gene Variant

```

User: "What variants are associated with BRCA1?"
Agent uses: search_clinvar("BRCA1")

```

### Get Population Frequency

```

User: "How common is the variant 1-55516888-G-GA?"
Agent uses: get_population_stats("1-55516888-G-GA")
→ Returns gnomAD allele frequency: 0.000123 (0.01%)

```

### Discover Gene-Disease Relationships

```

User: "What genes are linked to Lynch Syndrome?"
Agent uses: find_related_genes("Lynch Syndrome")
→ Returns: MSH2 (12 variants), MLH1 (8 variants), PMS2 (5 variants)

```

### Visualize Pathways

```

User: "Show me the pathways for TP53"
Agent uses: visualize_pathway("TP53")
→ Returns Mermaid diagram:

````

```mermaid
graph TD
    TP53((TP53))
    TP53 --> P_123["Transcriptional Regulation by TP53"]
    TP53 --> P_456["Cell Cycle Checkpoints"]
    TP53 --> P_789["DNA Damage Response"]
````

---

## 🔬 Data Sources

| Source                                           | Description                      | API                      |
| ------------------------------------------------ | -------------------------------- | ------------------------ |
| [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/) | Clinical variant interpretations | NCBI E-utilities         |
| [gnomAD](https://gnomad.broadinstitute.org/)     | Population allele frequencies    | gnomAD GraphQL           |
| [Reactome](https://reactome.org/)                | Biological pathway database      | Reactome Content Service |
| [PubMed](https://pubmed.ncbi.nlm.nih.gov/)       | Scientific literature            | NCBI E-utilities         |
| [NCBI Gene](https://www.ncbi.nlm.nih.gov/gene/)  | Gene annotations                 | NCBI E-utilities         |

---

## 🏗️ Architecture

```
GenomeMCP/
├── src/
│   ├── main.py          # MCP server & tool definitions
│   ├── clinvar.py       # ClinVar & PubMed API client
│   ├── genomics.py      # Exon/Intron mapping
│   ├── population.py    # gnomAD integration
│   ├── pathways.py      # Reactome integration
│   ├── utils.py         # Shared utilities
│   └── cli/             # Command-line interface
│       ├── app.py       # Typer CLI application
│       ├── formatters/  # Rich output formatters
│       ├── tui/         # Textual interactive UI
│       └── config.py    # Theme configuration
├── tests/               # Unit tests
├── docs/                # Documentation
├── install.sh           # Quick install script
├── setup-dev.sh         # Development setup
└── pyproject.toml       # Project configuration
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run CLI tests
uv run pytest tests/test_cli.py -v

# Run specific test suite
uv run pytest tests/test_phase4.py tests/test_phase5.py
```

---

## 📚 Documentation

- [CLI Guide](docs/cli_guide.md) — Command-line interface documentation
- [Tool Reference](docs/tool_reference.md) — Complete API documentation
- [Architecture Guide](docs/architecture_and_capabilities.md) — System design

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🔗 Keywords

`genomics` `bioinformatics` `clinvar` `gnomad` `mcp` `model-context-protocol` `ai-agent` `claude` `variant-interpretation` `population-genetics` `reactome` `pathway-analysis` `pubmed` `ncbi` `gene-discovery` `clinical-genomics` `precision-medicine` `llm-tools` `cli` `tui` `terminal`

---

<p align="center">
  <strong>Built for AI agents. Powered by open genomic data.</strong>
</p>

<div align="center">
  <img src="https://raw.githubusercontent.com/Nexis-AI/branding-assets/refs/heads/main/nex_banner.png" alt="Nexis AI Banner" width="100%" />
</div>
