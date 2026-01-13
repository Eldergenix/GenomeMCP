import pytest
from src.clinvar import search_clinvar, get_variant_summaries

@pytest.mark.asyncio
async def test_search_clinvar_found():
    """Test that we can find IDs for a common gene."""
    term = "BRCA1"
    ids = await search_clinvar(term, max_results=2)
    assert len(ids) > 0, "Should return at least one ID for BRCA1"
    assert isinstance(ids[0], str), "IDs should be strings"

@pytest.mark.asyncio
async def test_search_clinvar_not_found():
    """Test searching for a nonsense term returns empty list."""
    term = "NON_EXISTENT_GENE_XYZ_123"
    ids = await search_clinvar(term)
    assert ids == [], "Should return empty list for nonsense term"

@pytest.mark.asyncio
async def test_get_variant_summaries_real():
    """Test fetching details for a known ClinVar ID."""
    # Using the ID we found earlier in manual testing: 4539802 (BAP1 deletion)
    test_id = "4539802"
    summaries = await get_variant_summaries([test_id])
    
    assert len(summaries) == 1
    item = summaries[0]
    
    assert item["id"] == test_id
    assert "BAP1" in str(item["title"]), "Title should contain the gene name"
    assert "gene_names" in item
    # We expect 'BAP1' to be one of the genes
    assert "BAP1" in item["gene_names"]
    
    # Check our parsing logic for clinical significance
    # Based on our manual test, this was "Likely oncogenic"
    assert item["clinical_significance"] != "Unknown", "Should parse some clinical significance"

@pytest.mark.asyncio
async def test_get_variant_summaries_empty():
    """Test handling of empty ID list."""
    summaries = await get_variant_summaries([])
    assert summaries == []

from src.clinvar import get_linked_pmids, get_pubmed_summaries, search_gene, get_gene_summary

@pytest.mark.asyncio
async def test_pubmed_integration():
    """Test retrieving PMIDs for a known variant and fetching their summaries."""
    # Variant: NM_004656.4(BAP1):c.438-16_443del (ClinVar ID: 4539802)
    vid = "4539802"
    pmids = await get_linked_pmids(vid)
    # Note: Not all records have PMIDs, but checking logic runs safely is key.
    # If no PMIDs, the summary fetch should handle empty list.
    
    # Let's try to fetch summary for a known PMID to be sure summary logic works
    known_pmid = "20301390" # BRCA1 review
    summaries = await get_pubmed_summaries([known_pmid])
    assert len(summaries) == 1
    # Check lowercase title for robustness
    title_lower = summaries[0]["title"].lower()
    assert len(title_lower) > 5, "Should have a valid title"

@pytest.mark.asyncio
async def test_gene_integration():
    """Test retrieving Gene ID and Summary."""
    symbol = "TP53"
    gid = await search_gene(symbol)
    assert gid is not None, "Should find ID for TP53"
    
    info = await get_gene_summary(gid)
    assert info is not None
    # Check "name" roughly matches
    name_lower = info["name"].lower()
    assert "tumor" in name_lower or "p53" in name_lower or "tp53" in name_lower
