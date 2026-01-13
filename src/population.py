import httpx
from typing import Optional, Dict, Any
from src.utils import fetch_with_retry

GNOMAD_API_URL = "https://gnomad.broadinstitute.org/api"

async def fetch_gnomad_frequency(chrom: str, pos: int, ref: str, alt: str, genome_build: str = "GRCh38") -> Optional[Dict[str, Any]]:
    """
    Fetch allele frequency from gnomAD GraphQL API.
    
    Args:
        chrom: Chromosome (e.g., '1', 'X').
        pos: Position (1-based).
        ref: Reference allele.
        alt: Alternate allele.
        genome_build: 'GRCh37' or 'GRCh38' (default).
    """
    # Dataset ID mapping
    dataset_id = "gnomad_r3" if genome_build == "GRCh38" else "gnomad_r2_1"
    
    # Construct variant ID string for gnomAD format: "1-55516888-G-GA"
    # Note: gnomAD expects NO "chr" prefix in the variant ID string usually, 
    # but the dataset search might be flexible. Standard is CHROM-POS-REF-ALT.
    clean_chrom = chrom.replace("chr", "")
    variant_id = f"{clean_chrom}-{pos}-{ref}-{alt}"

    query = """
    query getVariant($variantId: String!, $datasetId: DatasetId!) {
        variant(variantId: $variantId, dataset: $datasetId) {
            exome {
                ac
                an
                af
            }
            genome {
                ac
                an
                af
            }
        }
    }
    """
    
    variables = {
        "variantId": variant_id,
        "datasetId": dataset_id
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                GNOMAD_API_URL, 
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"}
            )
            resp.raise_for_status()
            data = resp.json()
            
            if "errors" in data:
                # Variant might not exist
                return None
                
            variant_data = data.get("data", {}).get("variant")
            if not variant_data:
                return None
                
            # Prefer Genome data, fallback to Exome
            genome_data = variant_data.get("genome")
            exome_data = variant_data.get("exome")
            
            result = {}
            if genome_data:
                result["source"] = "genome"
                result["af"] = genome_data.get("af")
                result["ac"] = genome_data.get("ac")
                result["an"] = genome_data.get("an")
            elif exome_data:
                result["source"] = "exome"
                result["af"] = exome_data.get("af")
                result["ac"] = exome_data.get("ac")
                result["an"] = exome_data.get("an")
            else:
                return None
                
            return result
            
        except httpx.HTTPError:
            return None
        except Exception as e:
            print(f"Error fetching gnomAD data: {e}")
            return None
