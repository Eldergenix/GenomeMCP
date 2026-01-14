"""
Rich table formatters for GenomeMCP CLI output.

Provides beautiful, structured tables for genomic data display.
"""

from rich.table import Table
from rich.text import Text


def format_clinvar_results(results: list[dict]) -> Table:
    """
    Format ClinVar search results as a rich table.
    
    Args:
        results: List of ClinVar result dictionaries.
        
    Returns:
        Rich Table with formatted results.
    """
    table = Table(
        title="🧬 ClinVar Search Results",
        show_header=True,
        header_style="bold magenta",
        border_style="bright_blue",
        title_style="bold cyan",
        expand=True,
    )
    
    table.add_column("ID", style="cyan", no_wrap=True, width=12)
    table.add_column("Gene", style="green bold", width=12)
    table.add_column("Significance", style="yellow", width=20)
    table.add_column("Condition", style="white", ratio=1)
    
    for result in results:
        # Color-code clinical significance
        sig = result.get("clinical_significance", "Unknown")
        sig_style = _get_significance_style(sig)
        sig_text = Text(sig, style=sig_style)
        
        table.add_row(
            str(result.get("variation_id", "N/A")),
            result.get("gene", "N/A"),
            sig_text,
            result.get("condition", "N/A")[:50],  # Truncate long conditions
        )
    
    return table


def format_gene_info(gene_data: dict) -> Table:
    """
    Format gene information as a detailed table.
    
    Args:
        gene_data: Gene information dictionary from NCBI.
        
    Returns:
        Rich Table with gene details.
    """
    table = Table(
        title=f"🧬 Gene: {gene_data.get('symbol', 'Unknown')}",
        show_header=True,
        header_style="bold green",
        border_style="green",
        title_style="bold cyan",
    )
    
    table.add_column("Property", style="cyan bold", width=20)
    table.add_column("Value", style="white", ratio=1)
    
    properties = [
        ("Symbol", gene_data.get("symbol", "N/A")),
        ("Full Name", gene_data.get("full_name", "N/A")),
        ("Gene ID", str(gene_data.get("gene_id", "N/A"))),
        ("Organism", gene_data.get("organism", "Homo sapiens")),
        ("Chromosome", gene_data.get("chromosome", "N/A")),
        ("Map Location", gene_data.get("map_location", "N/A")),
        ("Summary", _truncate(gene_data.get("summary", "No summary available"), 200)),
    ]
    
    for prop, value in properties:
        table.add_row(prop, str(value))
    
    return table


def format_pathway_results(pathways: list[dict], gene: str) -> Table:
    """
    Format Reactome pathway results as a table.
    
    Args:
        pathways: List of pathway dictionaries from Reactome.
        gene: Gene symbol for the title.
        
    Returns:
        Rich Table with pathway information.
    """
    table = Table(
        title=f"🔬 Pathways for {gene}",
        show_header=True,
        header_style="bold magenta",
        border_style="magenta",
        title_style="bold cyan",
    )
    
    table.add_column("Pathway ID", style="cyan", width=20)
    table.add_column("Pathway Name", style="green", ratio=1)
    table.add_column("Species", style="yellow", width=15)
    
    for pathway in pathways:
        table.add_row(
            pathway.get("stableId", pathway.get("stId", "N/A")),
            pathway.get("displayName", pathway.get("name", "N/A")),
            pathway.get("species", ["Homo sapiens"])[0] if isinstance(pathway.get("species"), list) else "Homo sapiens",
        )
    
    return table


def format_variant_report(report: dict) -> Table:
    """
    Format a detailed variant report as a table.
    
    Args:
        report: Variant report dictionary.
        
    Returns:
        Rich Table with variant details.
    """
    table = Table(
        title="📋 Variant Report",
        show_header=True,
        header_style="bold cyan",
        border_style="cyan",
        title_style="bold yellow",
    )
    
    table.add_column("Field", style="cyan bold", width=25)
    table.add_column("Value", style="white", ratio=1)
    
    fields = [
        ("Variation ID", report.get("variation_id")),
        ("Gene", report.get("gene")),
        ("Clinical Significance", report.get("clinical_significance")),
        ("Review Status", report.get("review_status")),
        ("Condition", report.get("condition")),
        ("Molecular Consequence", report.get("molecular_consequence")),
        ("HGVS Expression", report.get("hgvs")),
        ("Last Evaluated", report.get("last_evaluated")),
    ]
    
    for field, value in fields:
        if value:
            table.add_row(field, str(value))
    
    return table


def format_population_stats(stats: dict) -> Table:
    """
    Format gnomAD population statistics as a table.
    
    Args:
        stats: Population statistics dictionary.
        
    Returns:
        Rich Table with population frequencies.
    """
    table = Table(
        title="👥 Population Frequencies (gnomAD)",
        show_header=True,
        header_style="bold blue",
        border_style="blue",
        title_style="bold cyan",
    )
    
    table.add_column("Population", style="cyan", width=25)
    table.add_column("Allele Frequency", style="yellow", width=15)
    table.add_column("Allele Count", style="green", width=15)
    
    populations = stats.get("populations", [])
    for pop in populations:
        af = pop.get("allele_frequency", 0)
        af_str = f"{af:.6f}" if af else "N/A"
        table.add_row(
            pop.get("population", "Unknown"),
            af_str,
            str(pop.get("allele_count", "N/A")),
        )
    
    return table


def format_related_genes(genes: list[dict], phenotype: str) -> Table:
    """
    Format related genes results as a table.
    
    Args:
        genes: List of gene dictionaries with scores.
        phenotype: The phenotype searched for.
        
    Returns:
        Rich Table with related genes.
    """
    table = Table(
        title=f"🔗 Related Genes: {phenotype}",
        show_header=True,
        header_style="bold green",
        border_style="green",
        title_style="bold cyan",
    )
    
    table.add_column("Rank", style="cyan bold", width=6)
    table.add_column("Gene", style="green bold", width=12)
    table.add_column("Variants", style="yellow", width=10)
    table.add_column("Score", style="magenta", width=10)
    
    for idx, gene in enumerate(genes, 1):
        table.add_row(
            str(idx),
            gene.get("gene", "N/A"),
            str(gene.get("variant_count", 0)),
            f"{gene.get('score', 0):.2f}",
        )
    
    return table


def _get_significance_style(significance: str) -> str:
    """Get style color based on clinical significance."""
    sig_lower = significance.lower() if significance else ""
    if "pathogenic" in sig_lower and "likely" not in sig_lower:
        return "red bold"
    elif "likely pathogenic" in sig_lower:
        return "red"
    elif "benign" in sig_lower and "likely" not in sig_lower:
        return "green bold"
    elif "likely benign" in sig_lower:
        return "green"
    elif "uncertain" in sig_lower or "vus" in sig_lower:
        return "yellow"
    return "white"


def _truncate(text: str, max_length: int) -> str:
    """Truncate text with ellipsis if too long."""
    if not text:
        return "N/A"
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
