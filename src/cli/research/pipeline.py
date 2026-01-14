"""
Genomics Research Pipeline using Denario.

Wraps Denario multi-agent system with GenomeMCP genomics tools.
"""

import asyncio
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class GenomicsResearchPipeline:
    """
    End-to-end genomics research pipeline using Denario.
    
    Combines GenomeMCP's genomics tools (ClinVar, gnomAD, Reactome)
    with Denario's multi-agent research system.
    
    Example:
        pipeline = GenomicsResearchPipeline(
            project_dir="./my_study",
            phenotype="Lynch Syndrome"
        )
        await pipeline.setup_data()
        idea = pipeline.generate_idea()
        method = pipeline.generate_method()
        results = pipeline.generate_results()
        pipeline.generate_paper(journal="APS")
    """
    
    def __init__(
        self,
        project_dir: str,
        phenotype: Optional[str] = None,
        clear_project_dir: bool = False,
    ):
        self.project_dir = Path(project_dir)
        self.phenotype = phenotype
        self.clear_project_dir = clear_project_dir
        self._denario = None
        self._data_fetched = False
        
        # Store genomics data
        self.genes = []
        self.variants = []
        self.pathways = []
        self.population_data = {}
    
    @property
    def denario(self):
        """Lazy load Denario to avoid import if not needed."""
        if self._denario is None:
            try:
                from denario import Denario
                self._denario = Denario(
                    project_dir=str(self.project_dir),
                    clear_project_dir=self.clear_project_dir,
                )
            except ImportError:
                raise ImportError(
                    "Denario not installed. Install with:\n"
                    "  pip install genomemcp[research]\n"
                    "or:\n"
                    "  pip install denario"
                )
        return self._denario
    
    async def fetch_genomics_data(self) -> dict:
        """
        Fetch genomics data for the phenotype using GenomeMCP tools.
        
        Returns:
            Dictionary containing genes, variants, pathways data.
        """
        if not self.phenotype:
            raise ValueError("Phenotype must be set to fetch genomics data")
        
        from src import clinvar, pathways as pathways_module, population
        
        console.print(f"[cyan]🧬 Fetching data for: {self.phenotype}[/cyan]")
        
        # Discover related genes
        console.print("[dim]  Finding related genes...[/dim]")
        self.genes = await clinvar.find_related_genes(self.phenotype)
        if isinstance(self.genes, list) and len(self.genes) > 0:
            console.print(f"[green]  ✓ Found {len(self.genes)} genes[/green]")
        
        # Search ClinVar for variants
        console.print("[dim]  Searching ClinVar...[/dim]")
        self.variants = await clinvar.search_clinvar(self.phenotype)
        if isinstance(self.variants, list):
            console.print(f"[green]  ✓ Found {len(self.variants)} variants[/green]")
        
        # Get pathway info for top gene
        if self.genes and len(self.genes) > 0:
            top_gene = self.genes[0].get("gene", self.genes[0]) if isinstance(self.genes[0], dict) else str(self.genes[0])
            console.print(f"[dim]  Getting pathways for {top_gene}...[/dim]")
            try:
                self.pathways = await pathways_module.get_pathway_info(top_gene)
                console.print(f"[green]  ✓ Found pathway data[/green]")
            except Exception:
                self.pathways = []
        
        self._data_fetched = True
        
        return {
            "genes": self.genes,
            "variants": self.variants,
            "pathways": self.pathways,
        }
    
    def create_data_description(self) -> str:
        """
        Create a markdown data description for Denario.
        
        Returns:
            Markdown string describing the genomics data.
        """
        if not self._data_fetched:
            raise ValueError("Must call fetch_genomics_data() first")
        
        # Format genes
        gene_list = ""
        if self.genes:
            for i, g in enumerate(self.genes[:10]):
                if isinstance(g, dict):
                    gene_list += f"- {g.get('gene', 'Unknown')}: {g.get('variant_count', 0)} variants\n"
                else:
                    gene_list += f"- {g}\n"
        
        # Format variant count
        variant_count = len(self.variants) if isinstance(self.variants, list) else 0
        
        # Format pathways
        pathway_list = ""
        if self.pathways:
            pathways_data = self.pathways if isinstance(self.pathways, list) else [self.pathways]
            for p in pathways_data[:5]:
                if isinstance(p, dict):
                    pathway_list += f"- {p.get('name', 'Unknown')}\n"
        
        description = f"""# Genomics Research Data: {self.phenotype}

## Data Sources
- ClinVar: Clinical variant database
- gnomAD: Population allele frequencies
- Reactome: Biological pathways
- PubMed: Scientific literature

## Available Tools
Use the following GenomeMCP functions for analysis:
- `search_clinvar(term)` - Query clinical variants
- `get_variant_report(id)` - Detailed variant info
- `get_gene_info(symbol)` - Gene annotations
- `get_population_stats(variant)` - gnomAD frequencies
- `get_pathway_info(gene)` - Reactome pathways
- `find_related_genes(phenotype)` - Gene discovery

## Discovered Genes
{gene_list if gene_list else "No genes discovered yet."}

## ClinVar Variants
Found {variant_count} variants associated with {self.phenotype}.

## Biological Pathways
{pathway_list if pathway_list else "No pathway data available."}

## Research Focus
Analyze the gene-phenotype relationships and variant pathogenicity
for {self.phenotype} using the genomics data above.
"""
        return description
    
    async def setup_data(self):
        """
        Fetch genomics data and configure Denario with data description.
        """
        await self.fetch_genomics_data()
        description = self.create_data_description()
        self.denario.set_data_description(description)
        
        # Save data description to project
        desc_path = self.project_dir / "input_files" / "data_description.md"
        desc_path.parent.mkdir(parents=True, exist_ok=True)
        desc_path.write_text(description)
        
        console.print(f"[green]✅ Data description saved to {desc_path}[/green]")
    
    def generate_idea(self, **kwargs):
        """Generate a research idea using Denario agents."""
        console.print("[cyan]💡 Generating research idea...[/cyan]")
        return self.denario.get_idea(**kwargs)
    
    def generate_idea_fast(self, **kwargs):
        """Generate idea quickly using idea-maker/hater method."""
        console.print("[cyan]💡 Generating idea (fast mode)...[/cyan]")
        return self.denario.get_idea_fast(**kwargs)
    
    def generate_method(self, **kwargs):
        """Generate research methodology using Denario agents."""
        console.print("[cyan]📋 Generating methodology...[/cyan]")
        return self.denario.get_method(**kwargs)
    
    def generate_results(self, **kwargs):
        """Run analysis and generate results using Denario agents."""
        console.print("[cyan]🔬 Running analysis...[/cyan]")
        return self.denario.get_results(**kwargs)
    
    def generate_paper(self, journal: str = "APS", **kwargs):
        """Generate LaTeX paper using Denario agents."""
        console.print(f"[cyan]📝 Writing paper ({journal} format)...[/cyan]")
        from denario import Journal
        journal_enum = getattr(Journal, journal.upper(), Journal.APS)
        return self.denario.get_paper(journal=journal_enum, **kwargs)
    
    def show_idea(self):
        """Display the generated idea."""
        self.denario.show_idea()
    
    def show_method(self):
        """Display the generated methodology."""
        self.denario.show_method()
    
    def show_results(self):
        """Display the generated results."""
        self.denario.show_results()
