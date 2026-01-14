#!/usr/bin/env python3
"""
GenomeMCP CLI - Research-Grade Genomic Intelligence Interface

A beautiful command-line interface for genomic analysis with support for:
- ClinVar variant search and reporting
- Gene information and pathway analysis
- Population frequency lookups (gnomAD)
- Discovery and evidence synthesis

Usage:
    genomemcp search BRCA1
    genomemcp variant 12345
    genomemcp pathway TP53 --visualize
    genomemcp tui
"""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import __version__
from .config import get_config, set_theme, CLIConfig
from .formatters.panels import (
    create_header_panel,
    create_error_panel,
    create_success_panel,
    create_info_panel,
    create_mermaid_panel,
    create_literature_panel,
)
from .formatters.tables import (
    format_clinvar_results,
    format_gene_info,
    format_pathway_results,
    format_variant_report,
    format_population_stats,
    format_related_genes,
)

# Initialize Typer app with rich markup
app = typer.Typer(
    name="genomemcp",
    help="🧬 GenomeMCP CLI - Research-Grade Genomic Intelligence",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)

# Register research subcommand (optional dependency)
try:
    from .research.commands import research_app
    app.add_typer(research_app, name="research")
except ImportError:
    pass  # Denario not installed

# Rich console for output
console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[cyan]GenomeMCP CLI[/cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit."
    ),
    theme: Optional[str] = typer.Option(
        None, "--theme", "-t",
        help="Color theme: default, professional, cyberpunk, minimal"
    ),
    no_banner: bool = typer.Option(
        False, "--no-banner",
        help="Hide the banner header."
    ),
):
    """
    🧬 GenomeMCP CLI - Research-Grade Genomic Intelligence
    
    A powerful command-line interface for genomic analysis, providing access to
    ClinVar, gnomAD, Reactome, and more.
    """
    if theme:
        set_theme(theme)
    
    config = get_config()
    config.show_banner = not no_banner


# =============================================================================
# ClinVar Search Commands
# =============================================================================

@app.command("search")
def search_clinvar(
    term: str = typer.Argument(..., help="Gene, variant, or disease to search for"),
    limit: int = typer.Option(10, "--limit", "-n", help="Maximum results to display"),
):
    """
    🔍 Search ClinVar for genes, variants, or diseases.
    
    Examples:
        genomemcp search BRCA1
        genomemcp search "Lynch Syndrome" --limit 20
    """
    _show_banner_if_enabled()
    
    with _spinner("Searching ClinVar..."):
        from src import clinvar
        results = asyncio.run(clinvar.search_clinvar(term))
    
    if not results or "error" in str(results).lower():
        console.print(create_error_panel(f"No results found for '{term}'"))
        raise typer.Exit(1)
    
    # Parse results - handle different response formats
    variants = _extract_variants(results)
    
    if not variants:
        console.print(create_info_panel(f"No variants found for search term: {term}"))
        return
    
    # Limit results
    variants = variants[:limit]
    
    # Display as table
    table = format_clinvar_results(variants)
    console.print(table)
    console.print(f"\n[dim]Showing {len(variants)} result(s)[/dim]")


@app.command("variant")
def get_variant(
    variant_id: str = typer.Argument(..., help="ClinVar Variant ID"),
    literature: bool = typer.Option(False, "--literature", "-l", help="Include supporting literature"),
    max_articles: int = typer.Option(5, "--max-articles", help="Max literature articles to fetch"),
):
    """
    📋 Get detailed report for a specific ClinVar variant.
    
    Examples:
        genomemcp variant 12345
        genomemcp variant 12345 --literature
    """
    _show_banner_if_enabled()
    
    with _spinner("Fetching variant report..."):
        from src import clinvar
        report = asyncio.run(clinvar.get_variant_report(variant_id))
    
    if not report or "error" in str(report).lower():
        console.print(create_error_panel(f"Could not fetch variant {variant_id}"))
        raise typer.Exit(1)
    
    table = format_variant_report(report)
    console.print(table)
    
    if literature:
        with _spinner("Fetching supporting literature..."):
            articles = asyncio.run(clinvar.get_supporting_literature(variant_id, max_articles))
        
        if articles and isinstance(articles, list):
            console.print(create_literature_panel(articles))


# =============================================================================
# Gene Information Commands
# =============================================================================

@app.command("gene")
def get_gene(
    gene_symbol: str = typer.Argument(..., help="Gene symbol (e.g., BRCA1, TP53)"),
):
    """
    🧬 Get detailed gene information from NCBI.
    
    Examples:
        genomemcp gene BRCA1
        genomemcp gene TP53
    """
    _show_banner_if_enabled()
    
    with _spinner(f"Fetching gene info for {gene_symbol}..."):
        from src import clinvar
        gene_data = asyncio.run(clinvar.get_gene_info(gene_symbol))
    
    if not gene_data or "error" in str(gene_data).lower():
        console.print(create_error_panel(f"Could not find gene: {gene_symbol}"))
        raise typer.Exit(1)
    
    table = format_gene_info(gene_data)
    console.print(table)


@app.command("context")
def get_context(
    gene_symbol: str = typer.Argument(..., help="Gene symbol"),
    position: int = typer.Argument(..., help="Genomic position (cDNA)"),
):
    """
    📍 Identify if position is in Exon or Intron region.
    
    Examples:
        genomemcp context BRCA1 150
        genomemcp context TP53 200
    """
    _show_banner_if_enabled()
    
    with _spinner("Mapping genomic context..."):
        from src import genomics
        context = asyncio.run(genomics.get_genomic_context(gene_symbol, position))
    
    if not context or "error" in str(context).lower():
        console.print(create_error_panel(f"Could not map position for {gene_symbol}"))
        raise typer.Exit(1)
    
    region = context.get("region", "Unknown")
    region_num = context.get("region_number", "")
    
    emoji = "📦" if "exon" in region.lower() else "🔗"
    msg = f"{emoji} Position {position} in {gene_symbol} falls within: [bold]{region} {region_num}[/bold]"
    console.print(create_success_panel(msg, title="Genomic Context"))


# =============================================================================
# Pathway Analysis Commands
# =============================================================================

@app.command("pathway")
def get_pathway(
    gene_symbol: str = typer.Argument(..., help="Gene symbol"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="Show Mermaid diagram"),
):
    """
    🔬 Get Reactome pathway information for a gene.
    
    Examples:
        genomemcp pathway TP53
        genomemcp pathway BRCA1 --visualize
    """
    _show_banner_if_enabled()
    
    with _spinner(f"Fetching pathways for {gene_symbol}..."):
        from src import pathways
        pathway_data = asyncio.run(pathways.get_pathway_info(gene_symbol))
    
    if not pathway_data or "error" in str(pathway_data).lower():
        console.print(create_error_panel(f"No pathways found for {gene_symbol}"))
        raise typer.Exit(1)
    
    pathways_list = pathway_data if isinstance(pathway_data, list) else [pathway_data]
    table = format_pathway_results(pathways_list, gene_symbol)
    console.print(table)
    
    if visualize:
        with _spinner("Generating visualization..."):
            mermaid = asyncio.run(pathways.visualize_pathway(gene_symbol))
        
        if mermaid and "error" not in str(mermaid).lower():
            console.print(create_mermaid_panel(mermaid, f"Pathways for {gene_symbol}"))


# =============================================================================
# Population Statistics Commands
# =============================================================================

@app.command("population")
def get_population(
    variant: str = typer.Argument(..., help="Variant in CHROM-POS-REF-ALT format"),
):
    """
    👥 Get gnomAD population frequencies for a variant.
    
    Examples:
        genomemcp population 1-55516888-G-GA
        genomemcp population 17-41245466-C-T
    """
    _show_banner_if_enabled()
    
    with _spinner("Fetching gnomAD data..."):
        from src import population
        stats = asyncio.run(population.get_population_stats(variant))
    
    if not stats or "error" in str(stats).lower():
        console.print(create_error_panel(f"No population data for variant: {variant}"))
        raise typer.Exit(1)
    
    table = format_population_stats(stats)
    console.print(table)


# =============================================================================
# Discovery Commands
# =============================================================================

@app.command("discover")
def discover_genes(
    phenotype: str = typer.Argument(..., help="Disease or phenotype to search"),
    max_genes: int = typer.Option(5, "--max-genes", "-n", help="Max genes to discover"),
):
    """
    🔗 Discover genes related to a disease/phenotype.
    
    Examples:
        genomemcp discover "Lynch Syndrome"
        genomemcp discover "Cardiomyopathy" --max-genes 10
    """
    _show_banner_if_enabled()
    
    with _spinner(f"Discovering genes for '{phenotype}'..."):
        from src import clinvar
        genes = asyncio.run(clinvar.find_related_genes(phenotype))
    
    if not genes or "error" in str(genes).lower():
        console.print(create_error_panel(f"No genes found for: {phenotype}"))
        raise typer.Exit(1)
    
    genes_list = genes if isinstance(genes, list) else [genes]
    genes_list = genes_list[:max_genes]
    
    table = format_related_genes(genes_list, phenotype)
    console.print(table)


@app.command("evidence")
def get_evidence(
    phenotype: str = typer.Argument(..., help="Disease or phenotype"),
    max_genes: int = typer.Option(3, "--max-genes", help="Number of genes to analyze"),
):
    """
    📚 Retrieve scientific evidence for AI synthesis.
    
    Finds genes related to phenotype and gathers recent literature.
    
    Examples:
        genomemcp evidence "Lynch Syndrome"
        genomemcp evidence "Breast Cancer" --max-genes 5
    """
    _show_banner_if_enabled()
    
    with _spinner("Synthesizing discovery evidence..."):
        from src import clinvar
        evidence = asyncio.run(clinvar.get_discovery_evidence(phenotype, max_genes))
    
    if not evidence or "error" in str(evidence).lower():
        console.print(create_error_panel(f"Could not synthesize evidence for: {phenotype}"))
        raise typer.Exit(1)
    
    # Display evidence summary
    if isinstance(evidence, dict):
        genes = evidence.get("genes", [])
        abstracts = evidence.get("abstracts", [])
        
        console.print(create_info_panel(
            f"Found {len(genes)} candidate genes with {len(abstracts)} supporting abstracts",
            title=f"Evidence for: {phenotype}"
        ))
        
        if abstracts:
            console.print(create_literature_panel(abstracts[:10]))  # Limit display
    else:
        console.print(create_success_panel(str(evidence)[:500], title="Evidence"))


# =============================================================================
# TUI Command
# =============================================================================

@app.command("tui")
def launch_tui():
    """
    🖥️ Launch interactive Terminal UI.
    
    Full-screen interface with search, navigation, and visualization.
    Press 'q' to quit.
    """
    try:
        from .tui.app import GenomeMCPApp
        app = GenomeMCPApp()
        app.run()
    except ImportError:
        console.print(create_error_panel(
            "Textual is required for TUI mode.\n"
            "Install with: pip install genomemcp[cli]"
        ))
        raise typer.Exit(1)


# =============================================================================
# Local LLM Chat Command
# =============================================================================

@app.command("chat")
def chat_mode(
    model: str = typer.Option("qwen2.5:7b", "--model", "-m", help="Ollama model name"),
    backend: str = typer.Option("ollama", "--backend", "-b", help="LLM backend: ollama or llamacpp"),
    verbose: bool = typer.Option(False, "--verbose", help="Show tool calls"),
):
    """
    🤖 Chat with local LLM using GenomeMCP tools.
    
    Requires Ollama running locally with the specified model.
    
    Setup:
        curl -fsSL https://ollama.ai/install.sh | sh
        ollama pull qwen2.5:7b
    
    Examples:
        genomemcp chat
        genomemcp chat --model llama3.1:8b
        genomemcp chat --verbose
    """
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich.panel import Panel
    
    _show_banner_if_enabled()
    
    # Check backend availability
    console.print("[cyan]🔌 Connecting to LLM backend...[/cyan]")
    
    try:
        from .llm import get_client
        from .agent import GenomicsAgent, ChatSession
        
        llm = get_client(backend=backend, model=model)
        
        # Check if available
        is_available = asyncio.run(llm.is_available())
        if not is_available:
            console.print(create_error_panel(
                f"LLM backend '{backend}' not available.\n\n"
                "For Ollama:\n"
                "  1. Install: curl -fsSL https://ollama.ai/install.sh | sh\n"
                "  2. Start: ollama serve\n"
                "  3. Pull model: ollama pull qwen2.5:7b"
            ))
            raise typer.Exit(1)
        
        console.print(f"[green]✓ Connected to {llm.name}[/green]")
        
    except ImportError as e:
        console.print(create_error_panel(
            f"LLM dependencies not installed.\n"
            f"Install with: pip install genomemcp[llm]\n\n"
            f"Error: {e}"
        ))
        raise typer.Exit(1)
    
    # Create agent
    agent = GenomicsAgent(llm, verbose=verbose)
    session = ChatSession(agent)
    
    console.print()
    console.print(Panel(
        "[bold cyan]GenomeMCP Chat[/bold cyan]\n\n"
        "Ask genomics questions. I'll use ClinVar, gnomAD, Reactome, and PubMed.\n\n"
        "[dim]Type 'exit' or 'quit' to end the session.[/dim]",
        border_style="cyan",
    ))
    console.print()
    
    # Chat loop
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
            
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break
            
            if not user_input.strip():
                continue
            
            # Get response
            with _spinner("Thinking..."):
                response = asyncio.run(session.chat(user_input))
            
            # Display response
            console.print()
            console.print("[bold green]🧬 GenomeMCP[/bold green]")
            console.print(Markdown(response))
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command("models")
def list_models(
    backend: str = typer.Option("ollama", "--backend", "-b", help="LLM backend"),
):
    """
    📋 List available LLM models.
    
    Shows models available in Ollama for use with the chat command.
    """
    _show_banner_if_enabled()
    
    try:
        from .llm.ollama import OllamaClient
        
        client = OllamaClient()
        is_available = asyncio.run(client.is_available())
        
        if not is_available:
            console.print(create_error_panel("Ollama is not running. Start with: ollama serve"))
            raise typer.Exit(1)
        
        models = asyncio.run(client.list_models())
        
        if not models:
            console.print(create_info_panel(
                "No models found. Pull one with:\n  ollama pull qwen2.5:7b"
            ))
            return
        
        console.print("[bold cyan]Available Models:[/bold cyan]\n")
        for model in models:
            console.print(f"  • {model}")
        
        console.print(f"\n[dim]Use with: genomemcp chat --model <name>[/dim]")
        
    except ImportError:
        console.print(create_error_panel("LLM dependencies not installed."))
        raise typer.Exit(1)


# =============================================================================
# Helper Functions
# =============================================================================

def _show_banner_if_enabled():
    """Show the header banner if enabled in config."""
    config = get_config()
    if config.show_banner:
        console.print(create_header_panel())
        console.print()


def _spinner(message: str):
    """Create a progress spinner context manager."""
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[cyan]{message}[/cyan]"),
        transient=True,
        console=console,
    )


def _extract_variants(results) -> list[dict]:
    """Extract variant list from various result formats."""
    if isinstance(results, list):
        return results
    elif isinstance(results, dict):
        # Try common keys
        for key in ["variants", "results", "data", "clinvar_results"]:
            if key in results and isinstance(results[key], list):
                return results[key]
        # Return as single-item list if it looks like a variant
        if "variation_id" in results or "gene" in results:
            return [results]
    return []


def cli():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli()
