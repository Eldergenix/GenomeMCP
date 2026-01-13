import httpx
from typing import Dict, List, Optional
from src.utils import fetch_with_retry

REACTOME_CONTENT_URL = "https://reactome.org/ContentService"

async def get_gene_pathways(gene_symbol: str) -> List[Dict[str, str]]:
    """
    Retrieve top-level biological pathways for a given gene.
    
    Args:
        gene_symbol: The gene name (e.g., 'TP53').
        
    Returns:
        List of dictionaries containing 'name' and 'stId' (stable ID).
    """
    # 1. Map Gene Symbol to Reactome ReferenceEntity (via UniProt usually, or simple query)
    # The ContentService search endpoint is good for this.
    
    search_url = f"{REACTOME_CONTENT_URL}/search/query"
    params = {
        "query": gene_symbol,
        "species": "Homo sapiens",
        "types": ["Protein"], # Filter for proteins which map to genes
        "cluster": "true"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Search for the entity
            resp = await fetch_with_retry(client, search_url, params=params)
            if resp.status_code != 200: return []
            
            data = resp.json()
            # Search results are grouped. Usually the first group contains what we want.
            groups = data.get("results", [])
            if not groups: return []
            
            results = groups[0].get("entries", [])
            if not results: return []
            
            # Take the first best hit that matches the symbol likely
            # Reactome search results can be noisy.
            # Best bet: Look for the 'dbId' of the protein.
            
            # Match logic
            entity_id = None
            db_name = None
            
            for res in results:
                name = res.get("name", "").replace('<span class="highlighting" >', '').replace('</span>', '')
                ref_name = res.get("referenceName", "").replace('<span class="highlighting" >', '').replace('</span>', '')
                
                if gene_symbol.upper() == name.upper() or gene_symbol.upper() == ref_name.upper():
                    entity_id = res.get("referenceIdentifier")
                    db_name = res.get("databaseName")
                    break
             
            if not entity_id or db_name != "UniProt":
                # Fallback: if we can't find exact match or it's not UniProt, try first UniProt hit
                for res in results:
                     if res.get("databaseName") == "UniProt":
                         entity_id = res.get("referenceIdentifier")
                         db_name = "UniProt"
                         break
            
            if not entity_id: return []

            # 2. Get Pathways (Mapping endpoint)
            # Endpoint: /data/mapping/{resource}/{identifier}/pathways?species=9606
            pathway_url = f"{REACTOME_CONTENT_URL}/data/mapping/{db_name}/{entity_id}/pathways"
            
            p_resp = await fetch_with_retry(client, pathway_url, params={"species": "9606"})
            if p_resp.status_code != 200: return []
            
            pathways_data = p_resp.json()
            
            # Filter and format
            # We want 'TopLevelPathway' or just significant ones.
            # The API returns a list of Event objects.
            
            output = []
            for p in pathways_data:
                # Only include Pathways (type check if necessary, usually safe)
                if p.get("schemaClass") == "Pathway":
                    output.append({
                        "name": p.get("displayName"),
                        "id": p.get("stId"),
                        "type": p.get("type", "Pathway")
                    })
                    
            return output
            
        except Exception as e:
            print(f"Error fetching Reactome data: {e}")
            return []
