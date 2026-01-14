"""
GenomeMCP Interactive TUI Application

A full-screen terminal user interface for genomic analysis.
Built with Textual for rich, interactive experiences.
"""

import asyncio
from typing import List, Dict, Any, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    Input,
    DataTable,
    Static,
    Button,
    TabbedContent,
    TabPane,
    RichLog,
    LoadingIndicator,
    Markdown,
    Label,
    ListItem,
    ListView,
)
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual import on, work

# Import backend modules
from src import clinvar, genomics, pathways, population
from src.cli.tui.chat import ChatWidget
from src.persistence.client import db


# =============================================================================
# Styles & Theme
# =============================================================================

THEME_CSS = """
/* Global & Reset */
Screen {
    background: #1e1e2e; /* Catppuccin Base */
    color: #cdd6f4;      /* Catppuccin Text */
}

/* Typography */
.title {
    text-style: bold;
    color: #89b4fa; /* Blue */
    padding: 1 2;
    background: #181825; /* Mantle */
    dock: top;
}

.subtitle {
    color: #a6adc8; /* Subtext */
    padding-left: 2;
    padding-bottom: 1;
}

/* Basic Layouts */
Container {
    padding: 1;
}

Vertical {
    height: 1fr;
}

Horizontal {
    height: auto;
}

/* Tabs */
TabbedContent {
    background: #1e1e2e;
}

ContentSwitcher {
    background: #1e1e2e;
    padding: 1;
}

TabPane {
    padding: 1;
}

/* Inputs & Buttons */
Input {
    background: #313244; /* Surface0 */
    border: none;
    color: #cdd6f4;
    padding: 1;
    margin-bottom: 1;
}

Input:focus {
    border: tall #89b4fa; /* Blue focus */
}

Button {
    background: #45475a; /* Surface1 */
    color: #cdd6f4;
    border: none;
    height: 3;
    margin-left: 1;
}

Button:hover {
    background: #585b70; /* Surface2 */
}

Button.primary {
    background: #89b4fa;
    color: #1e1e2e;
}

Button.primary:hover {
    background: #b4befe;
}

/* Data Tables */
DataTable {
    background: #1e1e2e;
    border: none;
    height: 1fr;
}

DataTable > .datatable--header {
    background: #313244;
    color: #89b4fa;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #45475a;
    color: #cdd6f4;
}

/* Markdown & Logs */
Markdown {
    background: #181825; /* Mantle */
    padding: 1 2;
    margin: 1;
    border-left: tall #89b4fa;
}

RichLog {
    background: #181825;
    padding: 1;
    border: none;
    scrollbar-background: #1e1e2e;
    scrollbar-color: #45475a;
}

/* Specific Panels */
#search_results, #gene_info, #discovery_list {
    background: #181825;
    padding: 0;
    margin-right: 1;
}

.card {
    background: #181825;
    padding: 1 2;
    margin-bottom: 1;
    border-left: tall #a6e3a1; /* Green */
}

.error-card {
    background: #181825;
    padding: 1 2;
    margin-bottom: 1;
    border-left: tall #f38ba8; /* Red */
    color: #f38ba8;
}

LoadingIndicator {
    color: #89b4fa;
    height: auto;
}
"""

# =============================================================================
# Widgets
# =============================================================================

from textual.message import Message

class SearchBar(Container):
    """Reusable search bar component."""
    
    class Submitted(Message):
        """Message posted when search is submitted."""
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    def __init__(self, placeholder: str, button_label: str = "Search", id: str = None):
        super().__init__(id=id)
        self.placeholder = placeholder
        self.button_label = button_label
        
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Input(placeholder=self.placeholder, id="input_term", classes="search-box")
            yield Button(self.button_label, variant="primary", id="btn_search")

    @on(Input.Submitted)
    def on_submit(self):
        self.post_message(self.Submitted(self.query_one("#input_term").value))
        
    @on(Button.Pressed)
    def on_btn(self):
        self.post_message(self.Submitted(self.query_one("#input_term").value))


class InfoCard(Static):
    """Display information in a card style."""
    
    def __init__(self, title: str, content: str, variant: str = "info"):
        super().__init__()
        self.card_title = title
        self.card_content = content
        self.variant = variant
        
    def compose(self) -> ComposeResult:
        yield Markdown(f"### {self.card_title}\n\n{self.card_content}")


# =============================================================================
# Main Application
# =============================================================================

class GenomeMCPApp(App):
    """
    GenomeMCP Interactive Terminal UI.
    Modernized with a Tabbed Interface and Premium Design.
    """
    
    CSS = THEME_CSS
    TITLE = "🧬 GenomeMCP"
    SUB_TITLE = "Research-Grade Genomic Intelligence"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("1", "switch_tab_assistant", "Assistant"),
        Binding("2", "switch_tab_workspace", "Workspace"),
        Binding("3", "switch_tab_1", "Variant Search"),
        Binding("4", "switch_tab_2", "Gene Intelligence"),
        Binding("5", "switch_tab_3", "Discovery"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with TabbedContent(initial="tab_assistant"):
            
            # --- TAB 0: ASSISTANT ---
            with TabPane("🤖 Assistant", id="tab_assistant"):
                yield ChatWidget()

            # --- TAB 00: WORKSPACE ---
            with TabPane("📂 Workspace", id="tab_workspace"):
                yield Static("Research Workspace & History", classes="title")
                with Horizontal():
                    with Vertical(classes="panel"):
                         yield Label("Recent Activity", classes="subtitle")
                         yield DataTable(id="history_table", cursor_type="row")
                         yield Button("Refresh History", id="btn_refresh_history")
            
            # --- TAB 1: VARIANT SEARCH ---
            with TabPane("🔍 Variant Search", id="tab_search"):
                yield Static("ClinVar Variant Search", classes="title")
                yield SearchBar("Enter gene (e.g., BRCA1) or variant...", id="search_bar")
                
                with Horizontal():
                    # Left: Results Table
                    with Vertical(id="search_results_container", classes="panel"):
                        yield Label("Results", classes="subtitle")
                        yield DataTable(id="variant_table", cursor_type="row")
                        yield LoadingIndicator(id="loading_search")
                    
                    # Right: Details View
                    with VerticalScroll(id="variant_details_container", classes="panel"):
                        yield Label("Details", classes="subtitle")
                        yield Markdown("Select a variant to view details...", id="variant_details")
                        with Horizontal(classes="buttons-row"):
                            yield Button("Pin to Workspace", id="btn_pin_variant", disabled=True)

            # --- TAB 2: GENE INTELLIGENCE ---
            with TabPane("🧬 Gene Intelligence", id="tab_gene"):
                yield Static("Gene & Pathway Analysis", classes="title")
                yield SearchBar("Enter gene symbol (e.g. TP53)...", button_label="Analyze", id="gene_bar")
                
                with Horizontal():
                    with VerticalScroll(id="gene_content"):
                        yield Markdown("_Enter a gene symbol to begin analysis..._ \n\nFeatures:\n- Gene Summary\n- Genomic Context\n- Reactome Pathways", id="gene_report")
                        with Horizontal(classes="buttons-row"):
                            yield Button("Save Report", id="btn_save_gene", disabled=True)
                        yield LoadingIndicator(id="loading_gene")
            
            # --- TAB 3: DISCOVERY ---
            with TabPane("🔬 Discovery", id="tab_discovery"):
                yield Static("Phenotype Discovery & Evidence", classes="title")
                yield SearchBar("Enter phenotype (e.g. Lynch Syndrome)...", button_label="Discover", id="discovery_bar")
                
                with Horizontal():
                     with VerticalScroll(id="discovery_content"):
                         yield Markdown("_Enter a phenotype to discover related genes and evidence..._", id="discovery_report")
                         yield LoadingIndicator(id="loading_discovery")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize widgets."""
        # Setup Variant Table
        table = self.query_one("#variant_table", DataTable)
        table.add_columns("ID", "Gene", "Significance", "Condition")
        
        # Setup History Table
        hist_table = self.query_one("#history_table", DataTable)
        hist_table.add_columns("Time", "Type", "Query")
        
        # Load History
        self.run_worker(self._load_history())
        
        # Hide loading indicators initially
        for indicator in self.query("LoadingIndicator"):
            indicator.display = False

    # --- ACTIONS & HANDLERS ---

    
    def action_switch_tab_assistant(self): self.query_one(TabbedContent).active = "tab_assistant"
    def action_switch_tab_workspace(self): self.query_one(TabbedContent).active = "tab_workspace"
    def action_switch_tab_1(self): self.query_one(TabbedContent).active = "tab_search"
    def action_switch_tab_2(self): self.query_one(TabbedContent).active = "tab_gene"
    def action_switch_tab_3(self): self.query_one(TabbedContent).active = "tab_discovery"

    @on(Button.Pressed, "#btn_refresh_history")
    def on_refresh_history(self):
        self.run_worker(self._load_history())

    async def _load_history(self):
        """Load recent history from Supabase."""
        hist_table = self.query_one("#history_table", DataTable)
        hist_table.clear()
        
        try:
            # Assumes user "local_user" for now, ideally parameterized
            history = await db.get_history("local_user", limit=20)
            for item in history:
                hist_table.add_row(
                    item.get("created_at", "")[:16],
                    item.get("type", ""),
                    item.get("query", ""),
                )
        except Exception as e:
            self.notify(f"Failed to load history: {e}")

    # --- SEARCH HANDLERS ---

    @on(SearchBar.Submitted)
    async def on_search_bar_submitted(self, event: SearchBar.Submitted):
        """Handle search submissions from any search bar."""
        search_id = event.control.id
        
        if search_id == "search_bar":
            await self.handle_variant_search(event.value)
        elif search_id == "gene_bar":
            await self.handle_gene_search(event.value)
        elif search_id == "discovery_bar":
            await self.handle_discovery(event.value)

    async def handle_variant_search(self, query: str):
        if not query: return
        
        self.notify(f"Searching for '{query}'...")
        self.query_one("#loading_search").display = True
        self.query_one("#variant_table", DataTable).clear()
        
        # Run search in background
        self.run_worker(self._perform_variant_search(query))
        
        # Persist search
        self.run_worker(db.add_history_item("local_user", "variant_search", {}, query))

    async def _perform_variant_search(self, query: str):
        try:
            results = await clinvar.search_clinvar(query)
            variants = self._extract_variants(results)
            
            table = self.query_one("#variant_table", DataTable)
            self.variants_cache = variants  # Store for details view
            
            for idx, v in enumerate(variants):
                table.add_row(
                    str(v.get("variation_id", "?")),
                    v.get("gene", "?"),
                    v.get("clinical_significance", "Unknown"),
                    v.get("condition", "Unknown")[:30],
                    key=str(idx)
                )
            
            if not variants:
                self.notify("No variants found.", severity="warning")
                
        except Exception as e:
            self.notify(f"Search failed: {e}", severity="error")
        finally:
            self.query_one("#loading_search").display = False

    @on(DataTable.RowSelected, "#variant_table")
    def on_variant_selected(self, event: DataTable.RowSelected):
        try:
            row_idx = int(event.row_key.value)
            variant = self.variants_cache[row_idx]
            self._display_variant_details(variant)
            
            # Enable Pin Button
            btn = self.query_one("#btn_pin_variant", Button)
            btn.disabled = False
            btn.variant = "default"
            btn.label = "Pin to Workspace"
            
        except (ValueError, IndexError, AttributeError):
            pass

    @on(Button.Pressed, "#btn_pin_variant")
    def on_pin_variant(self):
        # Determine current variant from cache/selection or store state better
        # For simplicity, re-fetching from selected row logic or storing selected index
        table = self.query_one("#variant_table", DataTable)
        if table.cursor_row is not None:
             try:
                 # Map cursor row to cache index (assuming 1:1 map which is true here)
                 variant = self.variants_cache[table.cursor_row]
                 self.run_worker(self._toggle_pin_variant(variant))
             except:
                 pass

    async def _toggle_pin_variant(self, variant):
        vid = str(variant.get("variation_id"))
        is_pinned = await db.toggle_favorite("local_user", "variant", vid, variant)
        
        btn = self.query_one("#btn_pin_variant", Button)
        if is_pinned:
            btn.variant = "success"
            btn.label = "Pinned!"
            self.notify(f"Variant {vid} pinned to Workspace.")
        else:
            btn.variant = "default"
            btn.label = "Pin to Workspace"
            self.notify(f"Variant {vid} removed from Workspace.")

    def _display_variant_details(self, variant: dict):
        md_view = self.query_one("#variant_details", Markdown)
        
        # Construct Markdown Report
        md = f"""
# Variant {variant.get('variation_id')}
**Gene**: {variant.get('gene')}
**Significance**: `{variant.get('clinical_significance')}`

### Conditions
{variant.get('condition')}

### Review Status
{variant.get('review_status', 'N/A')}

### Last Updated
{variant.get('last_updated', 'N/A')}
        """
        md_view.update(md)

    # --- TAB 2: GENE INTELLIGENCE LOGIC ---

    async def handle_gene_search(self, gene_symbol: str):
        if not gene_symbol: return
        
        self.notify(f"Analyzing {gene_symbol}...")
        self.query_one("#loading_gene").display = True
        self.query_one("#gene_report").update("")
        
        self.run_worker(db.add_history_item("local_user", "gene_analysis", {}, gene_symbol))
        self.run_worker(self._perform_gene_analysis(gene_symbol))

    async def _perform_gene_analysis(self, symbol: str):
        try:
            # 1. Get Gene Info
            gene_info = await clinvar.get_gene_info(symbol)
            
            # 2. Get Pathways
            pathway_data = await pathways.get_pathway_info(symbol)
            
            # Render Report
            report = f"# 🧬 Analysis: {symbol.upper()}\n\n"
            
            if gene_info:
                desc = gene_info.get("description", "No description available.")
                report += f"### Summary\n{desc}\n\n"
                report += f"**Location**: {gene_info.get('location', 'Unknown')}\n"
                report += f"**Type**: {gene_info.get('type', 'Unknown')}\n\n"
            
            report += "### 🔬 Reactome Pathways\n"
            if isinstance(pathway_data, list):
                for p in pathway_data[:10]: # Limit to 10
                    report += f"- **{p.get('id')}**: {p.get('name')}\n"
            elif isinstance(pathway_data, dict):
                 report += f"- **{pathway_data.get('id')}**: {pathway_data.get('name')}\n"
            else:
                report += "_No pathway data found._\n"
                
            self.query_one("#gene_report").update(report)
            self.query_one("#btn_save_gene").disabled = False
            
        except Exception as e:
            self.query_one("#gene_report").update(f"Error analyzing gene: {e}")
            self.notify("Gene analysis failed", severity="error")
        finally:
            self.query_one("#loading_gene").display = False

    @on(Button.Pressed, "#btn_save_gene")
    def on_save_gene(self):
         report = self.query_one("#gene_report", Markdown).source
         # Extract symbol roughly or store state. 
         # Assuming user just searched, retrieving from input is safer or storing in class
         symbol = self.query_one("#gene_bar .search-box", Input).value
         if report and symbol:
             self.run_worker(self._save_gene_report(symbol, report))

    async def _save_gene_report(self, symbol, report):
        await db.add_history_item("local_user", "saved_report", {"report": report}, f"Report: {symbol}")
        self.notify(f"Report for {symbol} saved to Workspace.")

    # --- TAB 3: DISCOVERY LOGIC ---

    async def handle_discovery(self, phenotype: str):
        if not phenotype: return
        
        self.notify(f"Discovering for {phenotype}...")
        self.query_one("#loading_discovery").display = True
        self.query_one("#discovery_report").update("")
        
        self.run_worker(db.add_history_item("local_user", "discovery", {}, phenotype))
        self.run_worker(self._perform_discovery(phenotype))

    async def _perform_discovery(self, phenotype: str):
        try:
            # Get evidence
            evidence = await clinvar.get_discovery_evidence(phenotype)
            
            report = f"# 🔬 Discovery: {phenotype}\n\n"
            
            if isinstance(evidence, dict):
                genes = evidence.get("genes", [])
                abstracts = evidence.get("abstracts", [])
                
                report += f"Found **{len(genes)}** candidate genes.\n\n"
                
                report += "### 🧬 Candidate Genes\n"
                for gene in genes[:10]:
                    report += f"- **{gene}**\n"
                
                report += "\n### 📚 Supporting Literature\n"
                for abs in abstracts[:5]:
                    title = abs.get('title', 'Unknown Title')
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{abs.get('id')}/"
                    report += f"- [{title}]({url})\n"
            else:
                report += str(evidence)
                
            self.query_one("#discovery_report").update(report)
            
        except Exception as e:
             self.query_one("#discovery_report").update(f"Error during discovery: {e}")
        finally:
             self.query_one("#loading_discovery").display = False

    # --- HELPERS ---

    def _extract_variants(self, results) -> List[dict]:
        """Normalize variant results."""
        if isinstance(results, list): return results
        if isinstance(results, dict):
            for k in ["variants", "results", "data", "clinvar_results"]:
                if k in results and isinstance(results[k], list): return results[k]
        return []

if __name__ == "__main__":
    app = GenomeMCPApp()
    app.run()
