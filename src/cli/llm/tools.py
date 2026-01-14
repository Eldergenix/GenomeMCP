"""
Tool definitions for GenomeMCP LLM integration.

Defines the tools available to the LLM for genomics analysis.
Format follows OpenAI function calling specification.
"""

# System prompt for genomics agent
GENOMICS_SYSTEM_PROMPT = """You are a genomics research assistant powered by GenomeMCP.
You have access to tools for querying clinical genomics databases:

- ClinVar: Clinical variant interpretations
- gnomAD: Population allele frequencies  
- Reactome: Biological pathways
- PubMed: Scientific literature
- NCBI Gene: Gene annotations

When answering questions about genes, variants, or diseases:
1. Use the appropriate tool to fetch accurate data
2. Cite your sources (ClinVar ID, PubMed ID, etc.)
3. Explain clinical significance in plain language
4. Be precise about uncertainty

If a question is outside genomics scope, politely redirect to genomics topics."""


# Tool definitions in OpenAI function calling format
GENOMICS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_clinvar",
            "description": "Search ClinVar for genes, variants, or diseases. Returns clinical variant interpretations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "Search term: gene symbol (BRCA1), variant, or disease name (Lynch Syndrome)"
                    }
                },
                "required": ["term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_variant_report",
            "description": "Get detailed clinical report for a specific ClinVar variant ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_id": {
                        "type": "string",
                        "description": "ClinVar Variation ID (e.g., '12345')"
                    }
                },
                "required": ["variant_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_gene_info",
            "description": "Get gene information from NCBI Gene: function, location, and aliases.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_symbol": {
                        "type": "string",
                        "description": "Gene symbol (e.g., 'TP53', 'BRCA1')"
                    }
                },
                "required": ["gene_symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_supporting_literature",
            "description": "Get PubMed articles linked to a ClinVar variant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_id": {
                        "type": "string",
                        "description": "ClinVar Variation ID"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum articles to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["variant_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_population_stats",
            "description": "Get gnomAD population allele frequencies for a variant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_str": {
                        "type": "string",
                        "description": "Variant in CHROM-POS-REF-ALT format (e.g., '1-55516888-G-GA')"
                    }
                },
                "required": ["variant_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pathway_info",
            "description": "Get Reactome biological pathways for a gene.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_symbol": {
                        "type": "string",
                        "description": "Gene symbol (e.g., 'TP53')"
                    }
                },
                "required": ["gene_symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "visualize_pathway",
            "description": "Generate Mermaid.js diagram of gene pathways.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_symbol": {
                        "type": "string",
                        "description": "Gene symbol (e.g., 'TP53')"
                    }
                },
                "required": ["gene_symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_related_genes",
            "description": "Discover genes associated with a disease or phenotype.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phenotype_or_disease": {
                        "type": "string",
                        "description": "Disease name (e.g., 'Lynch Syndrome', 'Cardiomyopathy')"
                    }
                },
                "required": ["phenotype_or_disease"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_genomic_context",
            "description": "Identify if a position is in an Exon or Intron region.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_symbol": {
                        "type": "string",
                        "description": "Gene symbol"
                    },
                    "position": {
                        "type": "integer",
                        "description": "Genomic position (cDNA)"
                    }
                },
                "required": ["gene_symbol", "position"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_discovery_evidence",
            "description": "Aggregate PubMed abstracts for genes related to a phenotype. Useful for AI synthesis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phenotype": {
                        "type": "string",
                        "description": "Disease/phenotype name"
                    },
                    "max_genes": {
                        "type": "integer",
                        "description": "Number of top genes to analyze (default: 3)",
                        "default": 3
                    }
                },
                "required": ["phenotype"]
            }
        }
    },
]


def get_tool_definitions() -> list[dict]:
    """Return the list of tool definitions for LLM."""
    return GENOMICS_TOOLS


def get_tool_names() -> list[str]:
    """Return list of available tool names."""
    return [t["function"]["name"] for t in GENOMICS_TOOLS]
