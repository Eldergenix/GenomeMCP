"""
CLI configuration and theming for GenomeMCP.

Provides centralized configuration for CLI appearance and behavior.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class CLITheme:
    """Theme configuration for CLI appearance."""
    
    # Primary colors
    primary: str = "cyan"
    secondary: str = "magenta"
    accent: str = "green"
    
    # Status colors
    success: str = "green"
    error: str = "red"
    warning: str = "yellow"
    info: str = "blue"
    
    # Clinical significance colors
    pathogenic: str = "red bold"
    likely_pathogenic: str = "red"
    benign: str = "green bold"
    likely_benign: str = "green"
    uncertain: str = "yellow"
    
    # Table styles
    table_header: str = "bold magenta"
    table_border: str = "bright_blue"
    table_title: str = "bold cyan"


# Default themes
THEMES = {
    "default": CLITheme(),
    "professional": CLITheme(
        primary="blue",
        secondary="white",
        accent="cyan",
        table_header="bold blue",
        table_border="blue",
    ),
    "cyberpunk": CLITheme(
        primary="magenta",
        secondary="cyan",
        accent="green",
        table_header="bold magenta",
        table_border="bright_magenta",
        table_title="bold cyan",
    ),
    "minimal": CLITheme(
        primary="white",
        secondary="dim",
        accent="cyan",
        table_header="bold",
        table_border="dim",
        table_title="bold",
    ),
}


@dataclass 
class CLIConfig:
    """Global CLI configuration."""
    
    # Display settings
    theme_name: str = "default"
    show_banner: bool = True
    compact_mode: bool = False
    
    # Output settings
    max_results: int = 20
    truncate_text: int = 100
    
    # API settings
    timeout: int = 30
    
    @property
    def theme(self) -> CLITheme:
        """Get the current theme."""
        return THEMES.get(self.theme_name, THEMES["default"])


# Global config instance
_config: Optional[CLIConfig] = None


def get_config() -> CLIConfig:
    """Get the global CLI configuration."""
    global _config
    if _config is None:
        _config = CLIConfig()
    return _config


def set_theme(theme_name: str) -> None:
    """Set the CLI theme."""
    config = get_config()
    if theme_name in THEMES:
        config.theme_name = theme_name


def get_theme() -> CLITheme:
    """Get the current theme."""
    return get_config().theme
