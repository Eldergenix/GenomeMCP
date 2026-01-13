# Bio-MCP Enhancement Plan: Research Capabilities

To transform this from a simple look-up tool into a **Research-Grade Bio-AI Agent**, we will add context and evidence layers.

## 1. Deep Evidence Retrieval (PubMed Integration)

**Goal**: Allow researchers to verify variant classifications by reading the underlying literature.

- **New Tool**: `get_supporting_literature(variant_id)`
- **Logic**:
  1. Extract PMIDs (PubMed IDs) from the ClinVar record.
  2. Query NCBI PubMed API (`eutils/esummary.fcgi?db=pubmed`).
  3. Return titles, journals, and publication dates of supporting papers.
- **Benefit**: Provides the **source of truth** behind a "Pathogenic" label.

## 2. Gene Context & Function (NCBI Gene)

**Goal**: Provide biological context for variants in less familiar genes.

- **New Tool**: `get_gene_info(gene_symbol)`
- **Logic**:
  1. Search NCBI Gene DB (`db=gene`).
  2. Retrieve "Summary" (function), "MapLocation", and "Aliases".
- **Benefit**: Helps the agent understand the **mechanism of action** (e.g., "This gene encodes a tumor suppressor...").

## 3. Phenotype-Driven Search

**Goal**: Find variants associated with a specific disease.

- **Enhancement**: Update `search_clinvar` to support explicit phenotype filtering.
- **Logic**: Add logic to append `[dise]` or `[pdis]` tags to the query term if the internal reasoning detects a disease name.

## Implementation Steps

### Phase 1: PubMed Integration

- [ ] Update `src/clinvar.py` to handle `db=pubmed` requests.
- [ ] Add parsing for `citation_list` in ClinVar responses.
- [ ] Create `get_supporting_literature` tool in `src/main.py`.

### Phase 2: Gene Info Tool

- [ ] Create `src/gene.py` (or add to `clinvar.py`) for `db=gene` interactions.
- [ ] Create `get_gene_info` tool in `src/main.py`.

### Phase 3: Verification

- [ ] Update `test_integration.py` to check for citations and gene info.
