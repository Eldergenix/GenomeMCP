import httpx
import logging
from typing import Dict, List, Optional, Any, Tuple
from src.utils import fetch_with_retry

# Re-use the existing base_url logic or import constants if we refactor.
# For now, defining locally to ensure standalone module works.
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

async def fetch_gene_refseq(gene_symbol: str) -> Optional[str]:
    """
    Get the top RefSeq ID (e.g. NM_000059) for a gene symbol.
    """
    # 1. Search Gene DB
    params = {"db": "gene", "term": f"{gene_symbol}[Sym] AND human[Organism]", "retmode": "json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await fetch_with_retry(client, f"{BASE_URL}/esearch.fcgi", params=params)
        if resp.status_code != 200: return None
        try:
            ids = resp.json()["esearchresult"]["idlist"]
            if not ids: return None
            gene_id = ids[0]
            
            # 2. Get Gene Summary to find RefSeq
            # This is complex in e-summary. Alternative: Use 'gene2refseq' or rely on 
            # a heuristic that we want the 'NM_' accession.
            # A distinct approach: Search 'nucleotide' directly for RefSeq mRNA of this gene.
            
            # Better: Search nucleotide for "Gene[Title] AND RefSeq[Filter] AND biomol_mrna[Prop]"
            return await search_nucleotide_refseq(gene_symbol)
        except KeyError:
            return None

async def search_nucleotide_refseq(gene_symbol: str) -> Optional[str]:
    """Find the MANE Select or top RefSeq mRNA for a gene."""
    term = f"{gene_symbol}[Gene Name] AND RefSeq[Filter] AND biomol_mrna[Prop] AND human[Organism]"
    params = {"db": "nucleotide", "term": term, "retmode": "json", "retmax": 1}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{BASE_URL}/esearch.fcgi", params=params)
        if resp.status_code == 200:
            try:
                ids = resp.json()["esearchresult"]["idlist"]
                if ids:
                    return await fetch_accession_from_gi(ids[0])
            except KeyError:
                pass
        
        # Fallback: simpler search if high-specificity one failed
        # Search for "Gene[Sym] AND biomol_mrna[Prop]" without "RefSeq" filter just in case
        fallback = f"{gene_symbol}[Gene Name] AND biomol_mrna[Prop] AND human[Organism]"
        params["term"] = fallback
        resp = await client.get(f"{BASE_URL}/esearch.fcgi", params=params)
        if resp.status_code == 200:
             try:
                ids = resp.json()["esearchresult"]["idlist"]
                if ids:
                    return await fetch_accession_from_gi(ids[0])
             except: pass
    return None

async def fetch_accession_from_gi(gi_id: str) -> Optional[str]:
    """Convert GI number to Accession.Version (e.g. 12345 -> NM_001.2)."""
    params = {"db": "nucleotide", "id": gi_id, "retmode": "json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await fetch_with_retry(client, f"{BASE_URL}/esummary.fcgi", params=params)
        if resp.status_code != 200: return None
        try:
            data = resp.json()
            # Esummary result for nucleotide usually has the accession in 'caption' or 'accessionversion'
            # The structure is result -> uid -> ...
            if "result" in data and gi_id in data["result"]:
                return data["result"][gi_id].get("accessionversion", 
                       data["result"][gi_id].get("caption"))
        except:
            pass
    return None

async def get_exon_structure(accession: str) -> List[Tuple[int, int]]:
    """
    Fetch the Feature Table (ft) for a RefSeq accession and extract Exon regions.
    Returns list of (start, end) tuples.
    """
    params = {"db": "nucleotide", "id": accession, "rettype": "ft", "retmode": "text"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await fetch_with_retry(client, f"{BASE_URL}/efetch.fcgi", params=params)
        if resp.status_code != 200: return []
        
        exons = []
        for line in resp.text.splitlines():
            # FT format is tab indented.
            # Typical line: "   123\t456\texon"
            parts = line.split()
            if len(parts) >= 3 and parts[2] == "exon":
                try:
                    start, end = int(parts[0]), int(parts[1])
                    exons.append((start, end))
                except ValueError:
                    pass
        return sorted(exons)

def identify_region(position: int, exons: List[Tuple[int, int]]) -> str:
    """Determine if a position is Exonic or Intronic."""
    for i, (start, end) in enumerate(exons):
        if start <= position <= end:
            return f"Exon {i+1}"
        
        # Check if it's in the intron BEFORE this exon (if not the first exon)
        if i > 0:
            prev_end = exons[i-1][1]
            if prev_end < position < start:
                return f"Intron {i}" # Intron after Exon i-1
                
    return "Unknown/Intergenic"
