# GenomeMCP CLI Guide

A beautiful command-line interface for genomic analysis.

## Installation

```bash
# Quick install
./install.sh

# Or with pip
pip install genomemcp[cli]

# Development mode
./setup-dev.sh
source .venv/bin/activate
```

## Commands

### 🔍 search — Search ClinVar

```bash
genomemcp search BRCA1
genomemcp search "Lynch Syndrome" --limit 20
```

### 📋 variant — Variant Report

```bash
genomemcp variant 12345
genomemcp variant 12345 --literature --max-articles 10
```

### 🧬 gene — Gene Information

```bash
genomemcp gene TP53
genomemcp gene BRCA1
```

### 📍 context — Genomic Context

```bash
genomemcp context BRCA1 150
# Returns: Position 150 falls within: Exon 2
```

### 🔬 pathway — Pathway Analysis

```bash
genomemcp pathway TP53
genomemcp pathway EGFR --visualize
```

### 👥 population — gnomAD Frequencies

```bash
genomemcp population 1-55516888-G-GA
genomemcp population 17-41245466-C-T
```

### 🔗 discover — Gene Discovery

```bash
genomemcp discover "Lynch Syndrome"
genomemcp discover "Cardiomyopathy" --max-genes 10
```

### 📚 evidence — Research Evidence

```bash
genomemcp evidence "Breast Cancer"
genomemcp evidence "Lynch Syndrome" --max-genes 5
```

### 🖥️ tui — Interactive Mode

```bash
genomemcp tui
```

**TUI Keyboard Shortcuts:**

- `s` — Focus search
- `q` — Quit
- `r` — Refresh
- `?` — Help
- `Esc` — Clear search

## Global Options

```bash
genomemcp --version              # Show version
genomemcp --theme cyberpunk ...  # Set theme
genomemcp --no-banner ...        # Hide header
```

## Themes

- **default** — Balanced colors
- **cyberpunk** — Magenta/cyan accents
- **professional** — Blue tones
- **minimal** — Subtle styling

### 🤖 chat — Local LLM Chat

Interact with GenomeMCP using natural language and local AI models (via Ollama).

```bash
# Start chat with default model (qwen2.5:7b)
genomemcp chat

# Use specific model
genomemcp chat --model llama3.1:8b

# Show tool calls (verbose mode)
genomemcp chat --verbose
```

Required: [Ollama](https://ollama.ai) running locally.

### 📋 models — List Models

List available models in Ollama.

```bash
genomemcp models
```

### 🔬 research — Scientific Research (Denario)

End-to-end scientific research workflows powered by Denario agents.
**Note**: Requires Python 3.12+.

```bash
# Initialize a new research project
genomemcp research init --phenotype "Lynch Syndrome"

# Generate novel research idea
genomemcp research idea

# Generate experimental methodology
genomemcp research method

# Run analysis and generate results/plots
genomemcp research analyze

# Write full LaTeX paper
genomemcp research paper --journal Nature

# Interactive guided mode
genomemcp research interactive
```

See the [Research Guide](research_guide.md) for detailed workflows.
