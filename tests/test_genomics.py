import pytest
from src.genomics import fetch_gene_refseq, get_exon_structure, identify_region

@pytest.mark.asyncio
async def test_refseq_lookup():
    """Verify we can find a RefSeq accession for BRCA1."""
    acc = await fetch_gene_refseq("BRCA1")
    assert acc is not None, "Should find RefSeq for BRCA1"
    assert acc.startswith("NM_"), f"Accession {acc} should start with NM_"

@pytest.mark.asyncio
async def test_exon_structure_fetch():
    """Verify we can fetch exon features for a known RefSeq."""
    # Using a stable, older RefSeq for TP53 to ensure test stability if possible, 
    # but dynamic finding is what we built. Let's use the one we find.
    acc = await fetch_gene_refseq("TP53")
    assert acc, "Need TP53 accession for test"
    
    exons = await get_exon_structure(acc)
    assert len(exons) > 1, "TP53 should have multiple exons"
    
    # Test logic
    # First exon start should be integer
    assert isinstance(exons[0][0], int)

@pytest.mark.asyncio
async def test_region_identification():
    """Test the coordinate math."""
    # Mock exons: (10, 20), (30, 40)
    # 15 -> Exon 1
    # 25 -> Intron 1
    # 5 -> Unknown
    exons = [(10, 20), (30, 40)]
    
    assert identify_region(15, exons) == "Exon 1"
    assert identify_region(25, exons) == "Intron 1"
    assert "Unknown" in identify_region(5, exons)
