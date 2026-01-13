from mcp.server.fastmcp import FastMCP
from src import clinvar

# Initialize FastMCP server
mcp = FastMCP("GenomeMCP", dependencies=["httpx", "xmltodict"])

@mcp.tool()
async def search_clinvar(term: str) -> str:
    """
    Search ClinVar for a genomic term (e.g., 'BRCA1') or a disease/phenotype (e.g., 'Cystic Fibrosis').
    
    Args:
        term: The gene symbol, variant name, or condition to search for.
    """
    # Simple heuristic to detect phenotype search vs gene search
    # If the term looks like a disease name (multi-word, standard English), we can append [dise]
    # But usually standard search works well. 
    # Let's trust the user's input primarily, but if it looks like a gene (all caps, short), we might not want [dise].
    # For now, we pass 'term' as is, but we could improve this later.
    
    # 1. Search for IDs
    ids = await clinvar.search_clinvar(term, max_results=5)
    if not ids:
        return f"No results found in ClinVar for term: '{term}'"

    # 2. Get details
    summaries = await clinvar.get_variant_summaries(ids)
    
    # 3. Format output for the agent
    if not summaries:
        return f"Found IDs {ids}, but failed to retrieve details."

    output_lines = [f"Found {len(summaries)} results for '{term}':\n"]
    
    for item in summaries:
        gene_str = ", ".join(item.get("gene_names", [])) if isinstance(item.get("gene_names"), list) else str(item.get("gene_names", ""))
        
        line = (
            f"- **{item['title']}** (ID: {item['id']})\n"
            f"  - Clinical Significance: {item['clinical_significance']}\n"
            f"  - Genes: {gene_str}\n"
            f"  - Accession: {item['accession']}\n"
            f"  - Last Updated: {item['last_updated']}\n"
        )
        output_lines.append(line)
        
    return "\n".join(output_lines)

@mcp.tool()
async def get_variant_report(variant_id: str) -> str:
    """
    Get a detailed report for a specific ClinVar Variant ID.
    
    Args:
        variant_id: The numeric ID of the ClinVar record (e.g., '12345').
    """
    summaries = await clinvar.get_variant_summaries([variant_id])
    if not summaries:
        return f"No details found for Variant ID: {variant_id}"
    
    item = summaries[0]
    # In a full app, this might fetch even more deep links/citations, 
    # but for this demo, the summary structure is returned as a formatted block.
    
    report = f"""
# ClinVar Variant Report: {item['title']}

- **ClinVar ID**: {item['id']}
- **Accession**: {item['accession']}
- **Clinical Significance**: {item['clinical_significance']}
- **Last Updated**: {item['last_updated']}

## Genes
{item.get('gene_names', 'N/A')}

## Description
This variant is listed in the ClinVar database. The clinical significance indicates its relevance to health conditions.
    """
    return report.strip()

@mcp.tool()
async def get_supporting_literature(variant_id: str, max_results: int = 5) -> str:
    """
    Retrieve supporting scientific literature (PubMed articles) for a specific ClinVar Variant ID.
    Useful for verifying the evidence behind a clinical classification.
    
    Args:
        variant_id: The numeric ID of the ClinVar record.
        max_results: Maximum number of summaries to retrieve (default: 5).
    """
    # 1. Find linked PMIDs
    pmids = await clinvar.get_linked_pmids(variant_id)
    if not pmids:
        return f"No directly linked PubMed articles found for ClinVar ID: {variant_id}"
    
    # 2. Get summaries
    # Limit to top max_results to avoid context bloat
    top_pmids = pmids[:max_results]
    papers = await clinvar.get_pubmed_summaries(top_pmids)
    
    if not papers:
        return f"Found PMIDs {top_pmids} but failed to retrieve details."
        
    output_lines = [f"Found {len(top_pmids)} supporting papers (showing top 5):\n"]
    
    for p in papers:
        authors = ", ".join(p['authors'][:3])
        if len(p['authors']) > 3:
            authors += " et al."
            
        line = (
            f"- **{p['title']}**\n"
            f"  - {p['journal']} ({p['pubdate']})\n"
            f"  - Authors: {authors}\n"
            f"  - PMID: {p['id']}\n"
        )
        output_lines.append(line)
        
    return "\n".join(output_lines)

@mcp.tool()
async def get_gene_info(gene_symbol: str) -> str:
    """
    Retrieve biological context and function for a gene (NCBI Gene).
    Useful for understanding the mechanism of action.
    """
    # 1. Search for Gene ID
    gene_id = await clinvar.search_gene(gene_symbol)
    if not gene_id:
        return f"Could not find Gene ID for symbol: {gene_symbol}"
        
    # 2. Get Summary
    info = await clinvar.get_gene_summary(gene_id)
    if not info:
        return f"Found Gene ID {gene_id} for '{gene_symbol}' but failed to retrieve details."
        
    report = f"""
# Gene Report: {info['name']} ({gene_symbol})

- **Gene ID**: {info['id']}
- **Description**: {info['description']}
- **Location**: {info['map_location']}

## Summary
{info['summary']}

## Aliases
{info['other_aliases']}
    """
    return report.strip()

from src import genomics

@mcp.tool()
async def get_genomic_context(gene_symbol: str, position: int) -> str:
    """
    Identify if a specific genomic position falls within an **Exon** (coding) or **Intron** (non-coding) region.
    Uses the latest RefSeq mRNA transcript for the gene.
    
    Args:
        gene_symbol: Standard gene name (e.g., 'BRCA1').
        position: The coordinate to check (1-based relative to transcript start, or genomic if specified, but simplistic here).
                  *Note: This basic tool assumes position relative to the mRNA start for now (cDNA).*
    """
    # 1. Find RefSeq
    acc = await genomics.fetch_gene_refseq(gene_symbol)
    if not acc:
        return f"Could not find a Reference Sequence (mRNA) for gene: {gene_symbol}"
        
    # 2. Get Structure
    exons = await genomics.get_exon_structure(acc)
    if not exons:
        return f"Found RefSeq {acc} but could not retrieve Exon table."
        
    # 3. Identify Region
    region_type = genomics.identify_region(position, exons)
    
    return f"""
# Genomic Context: {gene_symbol}
- **Reference Sequence**: {acc}
- **Query Position**: {position}
- **Identified Region**: **{region_type}**

*Note: Mapping is based on RefSeq {acc} feature table.*
    """.strip()

@mcp.tool()
async def find_related_genes(phenotype_or_disease: str) -> str:
    """
    Discover genes associated with a specific disease or phenotype.
    Returns a ranked list of genes based on the frequency of ClinVar variant associations.
    
    Args:
        phenotype_or_disease: The disease name (e.g. 'Lynch Syndrome', 'Cardiomyopathy').
    """
    results = await clinvar.get_related_genes_by_phenotype(phenotype_or_disease)
    
    if not results:
        return f"No genes found associated with phenotype '{phenotype_or_disease}' in the top 50 ClinVar hits."
    
    lines = [f"# Genes associated with '{phenotype_or_disease}'"]
    lines.append("(Ranked by variant frequency in top search results)")
    for gene, count in results:
        lines.append(f"- **{gene}**: {count} variants")
        
    return "\n".join(lines)

@mcp.tool()
async def get_discovery_evidence(phenotype: str, max_genes: int = 3) -> str:
    """
    Retrieve a corpus of scientific abstracts required for AI Synthesis.
    Finds genes related to the phenotype, then finds recent papers linked to those genes.
    
    Args:
        phenotype: Disease/Phenotype name.
        max_genes: Number of top candidate genes to analyze (default: 3).
    """
    # 1. Find Genes
    genes = await clinvar.get_related_genes_by_phenotype(phenotype, max_limit=20)
    if not genes:
        return f"No genes found for {phenotype}."
        
    top_genes = genes[:max_genes] # Focus on top genes per user request
    
    report_lines = [f"# Research Evidence: {phenotype}"]
    report_lines.append(f"Top Candidate Genes: {', '.join([g[0] for g in top_genes])}")
    
    for gene_sym, count in top_genes:
        report_lines.append(f"\n## Gene: {gene_sym} ({count} variants)")
        
        # Get Gene ID
        gid = await clinvar.search_gene(gene_sym)
        if not gid: continue
        
        # Get PMIDs
        pmids = await clinvar.get_gene_pmids(gid, max_results=3)
        if not pmids:
            report_lines.append("- No direct PubMed links found in NCBI Gene.")
            continue
            
        # Get Abstracts (Deep Analysis)
        papers = await clinvar.get_pubmed_abstracts(pmids)
        for p in papers:
            report_lines.append(f"- **{p['title']}** ({p['pubdate']})")
            report_lines.append(f"  *Journal*: {p['journal']}")
            report_lines.append(f"  *PMID*: {p['id']}")
            
            # Truncate abstract if too long
            abstract = p.get('abstract', 'No abstract.')
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            report_lines.append(f"  *Abstract*: {abstract}")
            
    return "\n".join(report_lines)

from src import population
from src import pathways

@mcp.tool()
async def get_population_stats(variant_str: str) -> str:
    """
    Get allele frequency for a variant from gnomAD (Genome Aggregation Database).
    
    Args:
        variant_str: Variant in 'CHROM-POS-REF-ALT' format (e.g. "1-55516888-G-GA").
                     Positions should be GRCh38.
    """
    try:
        parts = variant_str.split("-")
        if len(parts) != 4:
            return "Invalid variant format. Expected: CHROM-POS-REF-ALT (e.g., '1-55516888-G-GA')"
            
        chrom, pos_str, ref, alt = parts
        pos = int(pos_str)
        
        stats = await population.fetch_gnomad_frequency(chrom, pos, ref, alt)
        
        if not stats:
            return f"No gnomAD data found for variant: {variant_str} (or API error)."
            
        return f"""
# Population Frequency (gnomAD)
- **Variant**: {variant_str}
- **Source**: {stats['source']}
- **Allele Frequency (AF)**: {stats['af']:.6f}
- **Allele Count (AC)**: {stats['ac']}
- **Total Number (AN)**: {stats['an']}
        """.strip()
        
    except ValueError:
        return "Invalid Position (must be integer)."
    except Exception as e:
        return f"Error processing request: {str(e)}"

@mcp.tool()
async def get_pathway_info(gene_symbol: str) -> str:
    """
    Retrieve biological pathways associated with a gene (Reactome).
    Useful for understanding the functional impact of a gene.
    
    Args:
        gene_symbol: The gene name (e.g., 'TP53').
    """
    pathways_list = await pathways.get_gene_pathways(gene_symbol)
    
    if not pathways_list:
        return f"No pathways found for gene '{gene_symbol}' (or API connection failed)."
        
    lines = [f"# Biological Pathways: {gene_symbol}", ""]
    
    # Sort by likely importance (heuristic: shortest names often top-level, or just list)
    # Just listing top 10 to avoid bloat
    for p in pathways_list[:10]:
        lines.append(f"- **{p['name']}** (ID: {p['id']})")
        
    if len(pathways_list) > 10:
        lines.append(f"\n... and {len(pathways_list) - 10} more.")
        
    return "\n".join(lines)

@mcp.tool()
async def visualize_pathway(gene_symbol: str) -> str:
    """
    Generate a visual representation of biological pathways for a gene.
    Returns Mermaid.js graph syntax.
    
    Args:
        gene_symbol: The gene name (e.g., 'TP53').
    """
    pathways_list = await pathways.get_gene_pathways(gene_symbol)
    
    if not pathways_list:
        return f"No pathways found for {gene_symbol}."
        
    # Generate Mermaid
    lines = ["graph TD"]
    # Clean gene name for node ID
    gene_node = gene_symbol.replace(" ", "_").replace("-", "_")
    lines.append(f"    {gene_node}(({gene_symbol}))")
    
    for p in pathways_list[:10]: # Limit to top 10
        pid = p['id'].replace("R-HSA-", "") # Shorten ID
        pname = p['name'].replace('"', "'") # Escape quotes
        # Create a safe node ID - remove special chars
        safe_pid = pid.replace("-", "_").replace(".", "_")
        node_id = f"P_{safe_pid}"
        
        lines.append(f"    {gene_node} --> {node_id}[\"{pname}\"]")
        
    mermaid_block = "```mermaid\n" + "\n".join(lines) + "\n```"
    return mermaid_block

if __name__ == "__main__":
    mcp.run()
