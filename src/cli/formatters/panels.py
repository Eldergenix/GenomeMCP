"""
Rich panel formatters for GenomeMCP CLI.

Provides styled panels, headers, and status displays.
"""

from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.style import Style


def create_header_panel() -> Panel:
    """
    Create a branded header panel for the CLI.
    
    Returns:
        Rich Panel with GenomeMCP branding.
    """
    header_text = Text()
    header_text.append("🧬 ", style="bold")
    header_text.append("GenomeMCP", style="bold cyan")
    header_text.append(" - ", style="dim")
    header_text.append("Research-Grade Genomic Intelligence", style="italic green")
    
    return Panel(
        header_text,
        border_style="bright_blue",
        expand=True,
    )


def create_error_panel(message: str, title: str = "Error") -> Panel:
    """
    Create an error panel with styled message.
    
    Args:
        message: Error message to display.
        title: Panel title.
        
    Returns:
        Rich Panel styled for errors.
    """
    return Panel(
        Text(message, style="red"),
        title=f"❌ {title}",
        title_align="left",
        border_style="red",
        expand=True,
    )


def create_success_panel(message: str, title: str = "Success") -> Panel:
    """
    Create a success panel with styled message.
    
    Args:
        message: Success message to display.
        title: Panel title.
        
    Returns:
        Rich Panel styled for success.
    """
    return Panel(
        Text(message, style="green"),
        title=f"✅ {title}",
        title_align="left",
        border_style="green",
        expand=True,
    )


def create_info_panel(message: str, title: str = "Info") -> Panel:
    """
    Create an info panel with styled message.
    
    Args:
        message: Info message to display.
        title: Panel title.
        
    Returns:
        Rich Panel styled for information.
    """
    return Panel(
        Text(message, style="white"),
        title=f"ℹ️  {title}",
        title_align="left",
        border_style="blue",
        expand=True,
    )


def create_warning_panel(message: str, title: str = "Warning") -> Panel:
    """
    Create a warning panel with styled message.
    
    Args:
        message: Warning message to display.
        title: Panel title.
        
    Returns:
        Rich Panel styled for warnings.
    """
    return Panel(
        Text(message, style="yellow"),
        title=f"⚠️  {title}",
        title_align="left",
        border_style="yellow",
        expand=True,
    )


def create_mermaid_panel(mermaid_code: str, title: str = "Pathway Visualization") -> Panel:
    """
    Create a panel displaying Mermaid diagram code.
    
    Args:
        mermaid_code: Mermaid.js diagram syntax.
        title: Panel title.
        
    Returns:
        Rich Panel with formatted Mermaid code.
    """
    from rich.syntax import Syntax
    
    syntax = Syntax(mermaid_code, "text", theme="monokai", line_numbers=False)
    
    return Panel(
        syntax,
        title=f"📊 {title}",
        title_align="left",
        subtitle="(Copy to Mermaid Live Editor: mermaid.live)",
        subtitle_align="right",
        border_style="magenta",
        expand=True,
    )


def create_literature_panel(articles: list[dict]) -> Panel:
    """
    Create a panel displaying scientific literature references.
    
    Args:
        articles: List of article dictionaries with title, authors, pmid.
        
    Returns:
        Rich Panel with formatted literature list.
    """
    text = Text()
    
    for idx, article in enumerate(articles, 1):
        text.append(f"\n[{idx}] ", style="cyan bold")
        text.append(article.get("title", "Untitled"), style="white")
        text.append("\n    ", style="dim")
        
        authors = article.get("authors", [])
        if authors:
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."
            text.append(author_str, style="dim italic")
        
        pmid = article.get("pmid")
        if pmid:
            text.append(f"\n    PMID: {pmid}", style="dim cyan")
        text.append("\n")
    
    return Panel(
        text,
        title="📚 Supporting Literature",
        title_align="left",
        border_style="blue",
        expand=True,
    )
