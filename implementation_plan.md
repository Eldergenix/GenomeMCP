# Implementation Plan - Bio-MCP ClinVar Server

## Goal Description

Build a **Bio-MCP (Model Context Protocol) Server** that functions as an intelligent genomic agent tool. This server will expose tools to query the **ClinVar** database (via NCBI E-utilities) to retrieve and interpret variant clinical significance. This serves as a portfolio artifact (`Bio-Portfolio`) demonstrating "Bio-AI" capabilities and Agentic integration.

## User Review Required

> [!IMPORTANT] > **Tech Stack Selection**: We are using **Python** (with `uv` for management) as it is the standard for Bioinformatics/Data Science.
> **Dependency**: External access to NCBI E-utilities API (public).
> **Supabase Alignment**: This MCP server is designed to be potentially registered in a Supabase-backed Tool Registry, adhering to the "Reasoning Auditor" persona by providing structured, stateless tool execution.

## Proposed Changes

### Project Structure

New directory: `Bio-MCP-ClinVar/`

#### [NEW] [pyproject.toml](file:///Users/0xnexis/Desktop/Stefan-Job-Search/Bio-MCP-ClinVar/pyproject.toml)

- Define project dependencies: `mcp`, `httpx`, `xmltodict` (for E-utilities parsing).

#### [NEW] [src/main.py](file:///Users/0xnexis/Desktop/Stefan-Job-Search/Bio-MCP-ClinVar/src/main.py)

- **MCP Entry Point**: Implements the MCP server using `FastMCP` or standard `mcp` server classes.
- **Tools**:
  - `search_clinvar(term: str)`: Searches ClinVar for a term (gene, variant).
  - `get_variant_details(uid: str)`: Retrieves clinical significance and summary for a specific variant ID.

#### [NEW] [src/clinvar.py](file:///Users/0xnexis/Desktop/Stefan-Job-Search/Bio-MCP-ClinVar/src/clinvar.py)

- **API Client**: Handles HTTP requests to `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`.
- **Parsing**: Converts XML responses to JSON/Dict for the agent.

#### [NEW] [README.md](file:///Users/0xnexis/Desktop/Stefan-Job-Search/Bio-MCP-ClinVar/README.md)

- **Documentation**: Instructions on how to run the server locally and use it with an MCP client (e.g., Claude Desktop or generic MCP client).

## Verification Plan

### Automated Tests

- Create a simple test script `test_server.py` to verify API connectivity and response parsing.
- Run `uv run pytest` (if full tests) or a manual python script.

### Manual Verification

1.  **Install**: Run `uv sync`.
2.  **Run**: Start server `uv run python src/main.py`.
3.  **Inspect**: Use an MCP inspector or dry-run script to call `search_clinvar` and verify output.
