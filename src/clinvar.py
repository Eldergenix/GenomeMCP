import httpx
import xmltodict
import json
from typing import List, Dict, Any, Optional, Tuple
import asyncio

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DB = "clinvar"

async def _fetch_with_retry(client: httpx.AsyncClient, url: str, params: Dict[str, Any], retries: int = 3) -> httpx.Response:
    """Execute GET request with rate-limit handling."""
    for i in range(retries):
        response = await client.get(url, params=params)
        if response.status_code == 429:
            # NCBI rate limit: 3 requests/sec without API key.
            # Wait exponentially: 0.5s, 1.5s, 4.5s
            wait_time = 0.5 * (3 ** i)
            # print(f"Rate limited (429). Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
            continue
        response.raise_for_status()
        return response
    # Final attempt
    return await client.get(url, params=params)

async def search_clinvar(term: str, max_results: int = 5) -> List[str]:
    """
    Search ClinVar for a given term (gene, variant, condition) and return a list of IDs.
    """
    params = {
        "db": DB,
        "term": term,
        "retmode": "json",
        "retmax": max_results,
        "usehistory": "y"
    }
    
    async with httpx.AsyncClient() as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/esearch.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        
        # safely extract id list
        try:
            id_list = data["esearchresult"]["idlist"]
            return id_list
        except KeyError:
            return []

async def get_linked_pmids(clinvar_id: str) -> List[str]:
    """
    Use ELink to find PubMed articles linked to a ClinVar UID.
    """
    params = {
        "dbfrom": "clinvar",
        "db": "pubmed",
        "id": clinvar_id,
        "retmode": "json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/elink.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        
        try:
            linksets = data.get("linksets", [])
            pmids = []
            for ls in linksets:
                if "linksetdbs" in ls:
                    for db_entry in ls["linksetdbs"]:
                        if db_entry["db"] == "pubmed":
                            pmids.extend(db_entry.get("links", []))
            return list(set(pmids)) # deduplicate
        except KeyError:
            return []

async def get_gene_pmids(gene_id: str, max_results: int = 5) -> List[str]:
    """Find PMIDs linked to a Gene ID."""
    params = {
        "dbfrom": "gene",
        "db": "pubmed",
        "id": gene_id,
        "retmode": "json",
        # "cmd": "neighbor" # neighbor is default for elink
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/elink.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        
        try:
            # Similar to clinvar link parsing
            linksets = data.get("linksets", [])
            pmids = []
            for ls in linksets:
                for db in ls.get("linksetdbs", []):
                    if db["db"] == "pubmed":
                        pmids.extend(db["links"])
            return pmids[:max_results]
        except KeyError:
            return []

async def search_gene(gene_symbol: str) -> Optional[str]:
    """
    Find the NCBI Gene ID for a gene symbol.
    """
    params = {
        "db": "gene",
        "term": f"{gene_symbol}[Sym]",
        "retmode": "json",
    }
    async with httpx.AsyncClient() as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/esearch.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        try:
            ids = data["esearchresult"]["idlist"]
            if ids:
                return ids[0] # Return top match
        except KeyError:
            pass
    return None

async def get_gene_summary(gene_id: str) -> Optional[Dict[str, Any]]:
    """
    Get summary for a gene ID.
    """
    params = {
        "db": "gene",
        "id": gene_id,
        "retmode": "json",
    }
    async with httpx.AsyncClient() as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/esummary.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        try:
            result_dict = data["result"]
            if "uids" in result_dict:
                del result_dict["uids"]
            
            if gene_id in result_dict:
                summary = result_dict[gene_id]
                return {
                    "id": gene_id,
                    "name": summary.get("name", "N/A"),
                    "description": summary.get("description", "N/A"),
                    "summary": summary.get("summary", "No summary provided."),
                    "map_location": summary.get("maplocation", "Unknown"),
                    "other_aliases": summary.get("otheraliases", "")
                }
        except KeyError:
            pass
    return None

async def get_pubmed_summaries(pmids: List[str]) -> List[Dict[str, Any]]:
    """
    Retrieve summary information for a list of PubMed IDs.
    """
    if not pmids:
        return []
    
    ids_str = ",".join(pmids)
    params = {
        "db": "pubmed",
        "id": ids_str,
        "retmode": "json",
        "version": "2.0"
    }
    
    async with httpx.AsyncClient() as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/esummary.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        
        try:
            result_dict = data["result"]
            if "uids" in result_dict:
                del result_dict["uids"]
            
            papers = []
            for uid, summary in result_dict.items():
                parsed = {
                    "id": uid,
                    "title": summary.get("title", "N/A"),
                    "journal": summary.get("source", "N/A"),
                    "pubdate": summary.get("pubdate", "N/A"),
                    "authors": [a.get("name", "") for a in summary.get("authors", [])]
                }
                papers.append(parsed)
            return papers
        except KeyError:
             return []

async def get_pubmed_abstracts(pmids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch full abstracts for a list of PMIDs using efetch.
    Returns dictionaries with 'id', 'title', 'abstract', 'journal', 'pubdate'.
    """
    if not pmids:
        return []

    ids_str = ",".join(pmids)
    params = {
        "db": "pubmed",
        "id": ids_str,
        "retmode": "xml"
    }

    async with httpx.AsyncClient() as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/efetch.fcgi", params=params)
        response.raise_for_status()

        try:
            data = xmltodict.parse(response.text)
            articles = []
            
            # structure: PubmedArticleSet -> PubmedArticle (list or dict)
            article_set = data.get("PubmedArticleSet", {})
            if not article_set:
                return []
                
            pubmed_articles = article_set.get("PubmedArticle", [])
            
            if isinstance(pubmed_articles, dict):
                pubmed_articles = [pubmed_articles]
                
            for pa in pubmed_articles:
                medline = pa.get("MedlineCitation", {})
                pmid_struct = medline.get("PMID", {})
                pmid = pmid_struct.get("#text") if isinstance(pmid_struct, dict) else str(pmid_struct)
                
                article = medline.get("Article", {})
                title = article.get("ArticleTitle", "N/A")
                journal = article.get("Journal", {}).get("Title", "N/A")
                
                pubdate_struct = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                year = pubdate_struct.get("Year", "")
                month = pubdate_struct.get("Month", "")
                pubdate = f"{year} {month}".strip()
                
                abstract_data = article.get("Abstract", {}).get("AbstractText", [])
                abstract_text = ""
                
                if isinstance(abstract_data, str):
                    abstract_text = abstract_data
                elif isinstance(abstract_data, list):
                    parts = []
                    for item in abstract_data:
                        if isinstance(item, str):
                            parts.append(item)
                        elif isinstance(item, dict):
                            text = item.get("#text", "")
                            label = item.get("@Label")
                            if label:
                                parts.append(f"{label}: {text}")
                            else:
                                parts.append(text)
                    abstract_text = "\n".join(parts)
                elif isinstance(abstract_data, dict):
                     text = abstract_data.get("#text", "")
                     label = abstract_data.get("@Label")
                     if label:
                         abstract_text = f"{label}: {text}"
                     else:
                         abstract_text = text
                
                if abstract_text == "":
                    abstract_text = "No abstract available."

                articles.append({
                    "id": pmid,
                    "title": title,
                    "journal": journal,
                    "pubdate": pubdate,
                    "abstract": abstract_text
                })
            return articles
            
        except Exception as e:
            # print(f"Error parsing PubMed XML: {e}")
            return []

async def get_variant_summaries(ids: List[str]) -> List[Dict[str, Any]]:
    """
    Retrieve summary information for a list of ClinVar IDs.
    """
    if not ids:
        return []
    
    ids_str = ",".join(ids)
    params = {
        "db": DB,
        "id": ids_str,
        "retmode": "json",
        "version": "2.0"
    }
    
    async with httpx.AsyncClient() as client:
        response = await _fetch_with_retry(client, f"{BASE_URL}/esummary.fcgi", params=params)
        response.raise_for_status()
        data = response.json()
        
        # The result key usually contains uids as keys
        try:
            result_dict = data["result"]
            # remove 'uids' list from the dict to iterate over actual items
            if "uids" in result_dict:
                del result_dict["uids"]
            
            summaries = []
            for uid, summary in result_dict.items():
                # Extract consistent fields useful for an agent
                # Extract gene symbols
                genes_list = summary.get("genes", [])
                gene_names = []
                if isinstance(genes_list, list):
                    gene_names = [g.get("symbol", "") for g in genes_list if isinstance(g, dict)]
                elif isinstance(genes_list, dict):
                    # sometimes it's a single dict if xml conversion did something weird, 
                    # but here we deal with json from NCBI directly usually yielding lists
                    gene_names = [genes_list.get("symbol", "")]

                # Extract PubMed IDs
                citations = summary.get("variation_xrefs", [])
                pmids = []
                # variation_xrefs might be a list of dicts, check for db_source="PubMed"
                # Actually, in recent e-summary, there is often a dedicated 'citations' or 'supporting_submissions' section
                # But 'variation_xrefs' is a common place for external links.
                # Let's check typical 'pubmed' keys if present in top level
                # Warning: E-utilities structure for ClinVar varies.
                # A reliable way is often missing in summary, but let's try to find it.
                # Simpler approach: return the raw set of IDs if we can find them.
                # For now, let's look for 'trait_set' -> 'trait_xrefs' or similar, 
                # but often best is independent calls if we had the SCV. 
                # HOWEVER, for this "Bio-MCP" demo, we will check if 'parameter' fields exist or usage of clinical_assertion_list.
                # Let's fallback to returning empty list if not simple.
                
                # REVISION: We will expose a separate tool `get_supporting_literature` which might need to do a linked search.
                # ELink is better for finding papers linked to a ClinVar record.
                # We will implement `get_linked_pmids` helper.

                parsed = {
                    "id": uid,
                    "title": summary.get("title", "N/A"),
                    "clinical_significance": _extract_clinical_significance(summary),
                    "gene_names": gene_names,
                    "variation_set": summary.get("variation_set", []),
                    "accession": summary.get("accession_version", "N/A"),
                    "last_updated": summary.get("update_date", "N/A")
                }
                summaries.append(parsed)
            return summaries
        except KeyError:
             return []

def _extract_clinical_significance(summary: Dict[str, Any]) -> str:
    """Helper to extract cleaner clinical significance string."""
    # The structure varies, but often 'germline_classification' or 'clinical_significance' 
    # provides the needed info in newer valid 2.0 e-summary responses.
    
    # Check for 'germline_classification'
    if "germline_classification" in summary:
        gc = summary["germline_classification"]
        if isinstance(gc, dict) and gc.get("description"):
            return gc["description"]

    # Check for 'oncogenicity_classification'
    if "oncogenicity_classification" in summary:
        oc = summary["oncogenicity_classification"]
        if isinstance(oc, dict) and oc.get("description"):
            return oc["description"]
            
    # Check for 'clinical_impact_classification'
    if "clinical_impact_classification" in summary:
        cic = summary["clinical_impact_classification"]
        if isinstance(cic, dict) and cic.get("description"):
            return cic["description"]
    
    # Fallback to older fields
    if "clinical_significance" in summary:
        return str(summary["clinical_significance"])
        
    return "Unknown"

async def get_related_genes_by_phenotype(phenotype: str, max_limit: int = 50) -> List[Tuple[str, int]]:
    """
    Find genes frequently associated with a given phenotype in ClinVar.
    Returns a list of (GeneSymbol, frequency_count) sorted by frequency.
    """
    # 1. Search for variants with this phenotype
    ids = await search_clinvar(phenotype, max_results=max_limit)
    if not ids:
        return []
        
    # 2. Fetch summaries to extract genes
    summaries = await get_variant_summaries(ids)
    
    gene_counts = {}
    for s in summaries:
        # s['gene_names'] is a List[str]
        for gene in s.get('gene_names', []):
            if not gene: continue
            gene = gene.upper()
            gene_counts[gene] = gene_counts.get(gene, 0) + 1
            
    # 3. Sort by frequency
    sorted_genes = sorted(gene_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_genes
