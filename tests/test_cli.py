"""
Tests for GenomeMCP CLI commands.

Tests command-line interface functionality using Typer's test runner.
"""

import pytest
from typer.testing import CliRunner

from src.cli.app import app

runner = CliRunner()


class TestCLIBasics:
    """Test basic CLI functionality."""
    
    def test_help_command(self):
        """Test that --help shows available commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "GenomeMCP" in result.stdout
        assert "search" in result.stdout
        assert "variant" in result.stdout
        assert "pathway" in result.stdout
    
    def test_version_command(self):
        """Test that --version shows version info."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout or "GenomeMCP" in result.stdout
    
    def test_no_args_shows_help(self):
        """Test that running without args shows help."""
        result = runner.invoke(app, [])
        # Typer's no_args_is_help returns exit code 2
        assert result.exit_code == 2 or result.exit_code == 0


class TestSearchCommand:
    """Test the search command."""
    
    def test_search_help(self):
        """Test search command help."""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "Search ClinVar" in result.stdout
    
    def test_search_requires_term(self):
        """Test that search requires a term argument."""
        result = runner.invoke(app, ["search"])
        assert result.exit_code != 0  # Should fail without term


class TestVariantCommand:
    """Test the variant command."""
    
    def test_variant_help(self):
        """Test variant command help."""
        result = runner.invoke(app, ["variant", "--help"])
        assert result.exit_code == 0
        assert "variant" in result.stdout.lower()
    
    def test_variant_requires_id(self):
        """Test that variant requires an ID argument."""
        result = runner.invoke(app, ["variant"])
        assert result.exit_code != 0


class TestGeneCommand:
    """Test the gene command."""
    
    def test_gene_help(self):
        """Test gene command help."""
        result = runner.invoke(app, ["gene", "--help"])
        assert result.exit_code == 0
        assert "gene" in result.stdout.lower()


class TestPathwayCommand:
    """Test the pathway command."""
    
    def test_pathway_help(self):
        """Test pathway command help."""
        result = runner.invoke(app, ["pathway", "--help"])
        assert result.exit_code == 0
        assert "pathway" in result.stdout.lower()
        assert "--visualize" in result.stdout


class TestPopulationCommand:
    """Test the population command."""
    
    def test_population_help(self):
        """Test population command help."""
        result = runner.invoke(app, ["population", "--help"])
        assert result.exit_code == 0
        assert "population" in result.stdout.lower() or "gnomAD" in result.stdout


class TestDiscoverCommand:
    """Test the discover command."""
    
    def test_discover_help(self):
        """Test discover command help."""
        result = runner.invoke(app, ["discover", "--help"])
        assert result.exit_code == 0
        assert "discover" in result.stdout.lower() or "genes" in result.stdout.lower()


class TestThemeOption:
    """Test theme option."""
    
    def test_theme_option_accepted(self):
        """Test that theme option is accepted."""
        result = runner.invoke(app, ["--theme", "cyberpunk", "--help"])
        assert result.exit_code == 0


class TestNoBannerOption:
    """Test no-banner option."""
    
    def test_no_banner_option_accepted(self):
        """Test that no-banner option is accepted."""
        result = runner.invoke(app, ["--no-banner", "--help"])
        assert result.exit_code == 0
