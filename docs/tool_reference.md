# Bio-MCP Tool Reference

This document provides detailed specifications for the tools exposed by the Bio-MCP ClinVar Server.

## 1. `search_clinvar`

**Description**: The primary entry point for discovery. Queries the ClinVar database for variants matching a term.

- **Arguments**:
  - `term` (string): The search query. Can be:
    - Gene Symbol (`BRCA1`, `TP53`)
    - Specific Variant (`NM_000059.3:c.68_69delAG`)
    - Disease/Phenotype (`Lynch syndrome`, `Cystic Fibrosis`)
- **Returns**: A formatted string list of the top 5 matching variants.

## 2. `get_variant_report`

**Description**: Generates a comprehensive report for a single variant.

- **Arguments**: `variant_id` (string).

## 3. `get_supporting_literature`

**Description**: Contextualizes a variant by retrieving the scientific evidence linked to it.

- **Arguments**:
  - `variant_id` (string).
  - `max_results` (int, optional): Maximum number of summaries to retrieve (default: 5).
- **Workflow**: `elink` (ClinVar -> PubMed) -> `esummary`.

## 4. `get_gene_info`

**Description**: Provides biological grounding for a gene symbol (Function, Location, Aliases).

- **Arguments**: `gene_symbol` (string).

---

## 5. `find_related_genes` (Bio-Discovery)

**Description**: Discovers genes frequently associated with a specific disease phenotype. useful for identifying candidate genes for a complex condition.

- **Arguments**:
  - `phenotype_or_disease` (string): e.g., "Dilated Cardiomyopathy".
- **Returns**: A ranked list of genes based on variant frequency in ClinVar search results.

**Example Output**:

```markdown
# Genes associated with 'Lynch Syndrome'

(Ranked by variant frequency)

- **MSH2**: 15 variants
- **MLH1**: 12 variants
- **EPCAM**: 4 variants
```

## 6. `get_genomic_context` (Bio-Discovery)

**Description**: Maps a specific genomic position to its structural context (Exon vs. Intron) using NCBI Nucleotide reference sequences.

- **Arguments**:
  - `gene_symbol` (string): e.g., "BRCA1".
  - `position` (int): Coordinate relative to the transcript start.
- **Returns**: Identification of the region (e.g., "Exon 2", "Intron 4").

**Example Output**:

```markdown
# Genomic Context: BRCA1

- **Reference Sequence**: NM_001408467.1
- **Identified Region**: **Exon 2**
```

## 7. `get_discovery_evidence` (Bio-Discovery)

**Description**: Generates a research corpus for AI synthesis. Chains phenotype search -> gene identification -> deep literature retrieval.

- **Arguments**:
  - `phenotype` (string): e.g., "Brugada Syndrome".
  - `max_genes` (int, optional): Number of top candidate genes to analyze (default: 3).
- **Returns**: A structured report containing:
  1. Top candidate genes.
  2. summaries of recent PubMed papers linked to those genes.
- **Use Case**: Feed this output into an LLM context window to ask: "What latent mechanisms connect these genes?"

## 8. `get_population_stats`

**Description**: Retrieves allele frequency data from gnomAD (Genome Aggregation Database) to determine how common a variant is in the general population.

- **Arguments**:
  - `variant_str` (string): Variant in `CHROM-POS-REF-ALT` format (GRCh38 coordinates). Example: `1-55516888-G-GA`.
- **Returns**: A summary of Allele Frequency (AF), Allele Count (AC), and total number of alleles (AN).

**Example Output**:

```markdown
# Population Frequency (gnomAD)

- **Variant**: 1-55516888-G-GA
- **Allele Frequency (AF)**: 0.000032
- **Allele Count (AC)**: 2
```

## 9. `get_pathway_info`

**Description**: Maps a gene to its biological pathways using Reactome data. Crucial for understanding the downstream effects of a gene function.

- **Arguments**:
  - `gene_symbol` (string): e.g., "TP53".
- **Returns**: A list of pathway names and IDs.

**Example Output**:

```markdown
# Biological Pathways: TP53

- **Cell Cycle Checkpoints** (ID: R-HSA-69620)
- **DNA Repair** (ID: R-HSA-73894)
```
