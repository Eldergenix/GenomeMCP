# Walkthrough - GenomeMCP Server

The **GenomeMCP Server** has been upgraded to a research-grade tool capable of retrieving deep evidence and biological context.

## New Capabilities

### 1. Evidence Retrieval (`get_supporting_literature`)

- **Function**: Automatically finds PubMed articles linked to a specific ClinVar variant.
- **Usage**: Agents can now answer "Why is this classified as Pathogenic?" by citing the actual papers.
- **Backend**: Uses NCBI `elink` (ClinVar -> PubMed) and `esummary` (PubMed details).

### 2. Gene Context (`get_gene_info`)

- **Function**: Retrieves functional descriptions, map locations, and aliases for any gene.
- **Usage**: Provides context for obscure genes (e.g., "What does gene X do?").
- **Backend**: Uses NCBI `gene` database.

### 3. Robustness Improvements

- **Rate-Limit Handling**: Added exponential backoff to handle NCBI's strict API limits (429 errors).
- **Timeouts**: Configured 30s timeouts for stability on slow connections.
- **Parsing**: Enhanced logic to handle various ClinVar XML/JSON schemas.

## Verification

Run the full test suite to verify all features:

```bash
uv run pytest -v
```

**Results**:

- `test_search_clinvar`: ✅
- `test_get_variant_summaries`: ✅
- `test_pubmed_integration`: ✅ (Verifies linking variants to papers)
- `test_gene_integration`: ✅ (Verifies fetching gene summaries like TP53)

## File Manifest

- `src/main.py`: Updated with new tools `get_supporting_literature` and `get_gene_info`.
- `src/clinvar.py`: Added client logic for PubMed and Gene databases, plus retry wrappers.
- `tests/test_integration.py`: Expanded test coverage.

### 4. Deep Analysis & Visualization (Phase 4 & 5)

- **Abstract Fetching**: `get_discovery_evidence` now fetches full abstracts via `efetch` for deeper analysis.
- **Pathway Visualization**: Added `visualize_pathway` tool which generates Mermaid.js diagrams for gene pathways.

**New Tests**:

- `test_phase4.py`: Verifies XML parsing of PubMed abstracts.
- `test_phase5.py`: Verifies Mermaid syntax generation.
