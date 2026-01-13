import pytest
from unittest.mock import MagicMock, patch
from src.main import visualize_pathway

@pytest.mark.asyncio
async def test_visualize_pathway():
    # Mock pathways response
    mock_pathways = [
        {"id": "R-HSA-123", "name": "Pathway One", "type": "Pathway"},
        {"id": "R-HSA-456", "name": "Pathway Two", "type": "Pathway"}
    ]
    
    with patch("src.pathways.get_gene_pathways") as mock_get:
        mock_get.return_value = mock_pathways
        
        # Test
        result = await visualize_pathway("TESTGENE")
        
        assert "graph TD" in result
        assert "TESTGENE((TESTGENE))" in result
        assert "P_123" in result
        assert "Pathway One" in result
        assert "```mermaid" in result
