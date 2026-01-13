# Bio-Discovery Expansion Plan: Intelligent Correlation & Mapping

To enable the identification of potentially related genes, exon/intron regions, and "undiscovered correlations," we need to move beyond simple lookups into **multi-hop reasoning** and **data synthesis**.

## 1. Goal Description

Build a **Bio-Discovery Module** that allows the agent to:

1.  **Identify Related Genes**: Find genes sharing similar phenotypes or pathways.
2.  **Map Genomic Context**: Distinguish Exon vs. Intron regions for variants (using NCBI Nucleotide/Gene).
3.  **Synthesize Hypotheses**: Use AI to analyze co-occurrences in PubMed literature and propose novel correlations.
4.  **Visualize**: Generate Mermaid diagrams mapping Gene <-> Phenotype <-> Paper.

## 2. Proposed Architecture

### A. New Tool: `find_related_genes(phenotype)`

- **Logic**:
  1. Query ClinVar for all variants associated with `phenotype`.
  2. Extract unique Gene Symbols from results.
  3. Rank genes by citation frequency (count of papers linkage).
- **Output**: Ranked list of genes (e.g., "For Lynch Syndrome: MSH2, MLH1, PMS2... and potentially related candidate EPCAM").

### B. New Tool: `get_genomic_context(gene, variant_position)`

- **Logic**:
  1. Query NCBI Gene to get the Reference Sequence (RefSeq) ID (e.g., `NM_000059`).
  2. Query NCBI Nucleotide (`efetch`) to get the Feature Table.
  3. Determine if `variant_position` falls within an **Exon** or **Intron** feature.
- **Benefit**: "This variant is in Intron 4, known for splice-site regulation."

### C. New Tool: `analyze_correlations(genes_list)` (AI Synthesis)

- **Logic**:
  1. Fetch abstracts for the top 5 papers co-mentioning these genes.
  2. Formatting the prompt for the LLM (internal logic) to ask: "What latent mechanisms connect these genes?"
  3. Return a structured "Hypothesis" block.

### D. New Tool: `visualize_pathway(genes_list)`

- **Logic**: Generate a **Mermaid.js** graph definition showing:
  `Gene A --> [Interaction] --> Gene B`
  `Gene A --> [Phenotype X]`

## 3. Implementation Phases

### Phase 1: Genomic Context (Exon/Intron)

- [ ] Add `src/genomics.py` to handle NCBI Nucleotide fetching.
- [ ] Implement coordinates parsing to map a position to Exon/Intron.

### Phase 2: Phenotype Clustering

- [ ] Upgrade `src/clinvar.py` to aggregate results by Gene.

### Phase 3: AI Analysis Tools

- [ ] Implement `generate_hypothesis` tool that aggregates literature summaries for the Agent to reason over.

## 4. User Review Required

> [!IMPORTANT] > **Complexity Warning**: Mapping exact Exon/Intron boundaries requires precise RefSeq version matching (e.g., hg19 vs hg38). We will implementation a **best-effort** mapping using the latest RefSeq data from NCBI.
