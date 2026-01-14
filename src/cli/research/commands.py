"""
Research CLI commands for GenomeMCP.

Provides commands for end-to-end scientific research using Denario.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

# Create research subcommand group
research_app = typer.Typer(
    name="research",
    help="🔬 Scientific research tools powered by Denario",
    no_args_is_help=True,
)


def _check_denario():
    """Check if Denario is installed."""
    try:
        import denario
        return True
    except ImportError:
        console.print(Panel(
            "[red]Denario not installed.[/red]\n\n"
            "Install with:\n"
            "  [cyan]pip install genomemcp[research][/cyan]\n\n"
            "Or:\n"
            "  [cyan]pip install denario[/cyan]",
            title="❌ Missing Dependency",
            border_style="red",
        ))
        raise typer.Exit(1)


@research_app.command("init")
def init_project(
    project: str = typer.Option("./genomics_study", "--project", "-p", help="Project directory"),
    phenotype: str = typer.Option(..., "--phenotype", "-ph", help="Disease/phenotype to study"),
    clear: bool = typer.Option(False, "--clear", help="Clear existing project directory"),
):
    """
    🧬 Initialize a new genomics research project.
    
    Fetches ClinVar, gnomAD, and pathway data for the phenotype.
    
    Example:
        genomemcp research init --phenotype "Lynch Syndrome"
    """
    _check_denario()
    
    from .pipeline import GenomicsResearchPipeline
    
    console.print(Panel(
        f"[bold cyan]Initializing Genomics Research Project[/bold cyan]\n\n"
        f"📁 Project: {project}\n"
        f"🧬 Phenotype: {phenotype}",
        border_style="cyan",
    ))
    
    pipeline = GenomicsResearchPipeline(
        project_dir=project,
        phenotype=phenotype,
        clear_project_dir=clear,
    )
    
    # Fetch data and setup
    asyncio.run(pipeline.setup_data())
    
    console.print(f"\n[green]✅ Project initialized at {project}[/green]")
    console.print("[dim]Next: genomemcp research idea --project {project}[/dim]")


@research_app.command("idea")
def generate_idea(
    project: str = typer.Option("./genomics_study", "--project", "-p", help="Project directory"),
    fast: bool = typer.Option(False, "--fast", help="Use fast idea generation mode"),
):
    """
    💡 Generate a research idea/hypothesis.
    
    Uses Denario's multi-agent system to create novel research ideas.
    
    Example:
        genomemcp research idea --project ./my_study
    """
    _check_denario()
    
    from .pipeline import GenomicsResearchPipeline
    
    pipeline = GenomicsResearchPipeline(project_dir=project)
    pipeline.denario.set_all()  # Load existing data
    
    if fast:
        pipeline.generate_idea_fast()
    else:
        pipeline.generate_idea()
    
    console.print(f"\n[green]✅ Idea saved to {project}[/green]")
    console.print("[dim]View with: genomemcp research show idea[/dim]")


@research_app.command("method")
def generate_method(
    project: str = typer.Option("./genomics_study", "--project", "-p", help="Project directory"),
):
    """
    📋 Generate research methodology.
    
    Creates experimental design based on the generated idea.
    
    Example:
        genomemcp research method --project ./my_study
    """
    _check_denario()
    
    from .pipeline import GenomicsResearchPipeline
    
    pipeline = GenomicsResearchPipeline(project_dir=project)
    pipeline.denario.set_all()
    pipeline.generate_method()
    
    console.print(f"\n[green]✅ Methodology saved to {project}[/green]")


@research_app.command("analyze")
def run_analysis(
    project: str = typer.Option("./genomics_study", "--project", "-p", help="Project directory"),
):
    """
    🔬 Run analysis and generate results.
    
    Executes the methodology to produce results and plots.
    
    Example:
        genomemcp research analyze --project ./my_study
    """
    _check_denario()
    
    from .pipeline import GenomicsResearchPipeline
    
    pipeline = GenomicsResearchPipeline(project_dir=project)
    pipeline.denario.set_all()
    pipeline.generate_results()
    
    console.print(f"\n[green]✅ Results saved to {project}[/green]")


@research_app.command("paper")
def generate_paper(
    project: str = typer.Option("./genomics_study", "--project", "-p", help="Project directory"),
    journal: str = typer.Option("APS", "--journal", "-j", help="Journal style (APS, Nature, etc.)"),
):
    """
    📝 Generate a LaTeX research paper.
    
    Creates a complete manuscript from the research results.
    
    Example:
        genomemcp research paper --journal Nature
    """
    _check_denario()
    
    from .pipeline import GenomicsResearchPipeline
    
    pipeline = GenomicsResearchPipeline(project_dir=project)
    pipeline.denario.set_all()
    pipeline.generate_paper(journal=journal)
    
    console.print(f"\n[green]✅ Paper saved to {project}[/green]")


@research_app.command("show")
def show_content(
    content_type: str = typer.Argument(..., help="What to show: idea, method, results"),
    project: str = typer.Option("./genomics_study", "--project", "-p", help="Project directory"),
):
    """
    👁️ Display generated content.
    
    Example:
        genomemcp research show idea
        genomemcp research show method
    """
    _check_denario()
    
    from .pipeline import GenomicsResearchPipeline
    
    pipeline = GenomicsResearchPipeline(project_dir=project)
    pipeline.denario.set_all()
    
    if content_type == "idea":
        pipeline.show_idea()
    elif content_type == "method":
        pipeline.show_method()
    elif content_type == "results":
        pipeline.show_results()
    else:
        console.print(f"[red]Unknown content type: {content_type}[/red]")
        console.print("[dim]Options: idea, method, results[/dim]")


@research_app.command("interactive")
def interactive_mode(
    project: str = typer.Option("./genomics_study", "--project", "-p", help="Project directory"),
):
    """
    🎯 Interactive guided research workflow.
    
    Step-by-step wizard for conducting genomics research.
    """
    _check_denario()
    
    console.print(Panel(
        "[bold cyan]GenomeMCP Research Wizard[/bold cyan]\n\n"
        "I'll guide you through a complete genomics research workflow.",
        border_style="cyan",
    ))
    
    # Get phenotype
    phenotype = Prompt.ask("\n[cyan]Enter disease/phenotype to study[/cyan]")
    
    if not phenotype:
        console.print("[red]Phenotype required.[/red]")
        raise typer.Exit(1)
    
    from .pipeline import GenomicsResearchPipeline
    
    pipeline = GenomicsResearchPipeline(
        project_dir=project,
        phenotype=phenotype,
        clear_project_dir=True,
    )
    
    # Step 1: Fetch data
    console.print("\n[bold]Step 1: Fetching Genomics Data[/bold]")
    asyncio.run(pipeline.setup_data())
    
    # Step 2: Generate idea
    if Confirm.ask("\n[cyan]Generate research idea?[/cyan]", default=True):
        console.print("\n[bold]Step 2: Generating Research Idea[/bold]")
        pipeline.generate_idea_fast()
        pipeline.show_idea()
    
    # Step 3: Generate method
    if Confirm.ask("\n[cyan]Generate methodology?[/cyan]", default=True):
        console.print("\n[bold]Step 3: Generating Methodology[/bold]")
        pipeline.generate_method()
    
    # Step 4: Run analysis
    if Confirm.ask("\n[cyan]Run analysis?[/cyan]", default=True):
        console.print("\n[bold]Step 4: Running Analysis[/bold]")
        pipeline.generate_results()
    
    # Step 5: Generate paper
    if Confirm.ask("\n[cyan]Generate paper?[/cyan]", default=True):
        journal = Prompt.ask("[cyan]Journal style[/cyan]", default="APS")
        console.print("\n[bold]Step 5: Writing Paper[/bold]")
        pipeline.generate_paper(journal=journal)
    
    console.print(Panel(
        f"[green]✅ Research complete![/green]\n\n"
        f"📁 Output: {project}",
        title="🎉 Done",
        border_style="green",
    ))
