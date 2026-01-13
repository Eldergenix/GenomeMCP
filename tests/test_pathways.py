import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src import pathways

class TestPathways(unittest.IsolatedAsyncioTestCase):
    @patch("src.pathways.fetch_with_retry")
    async def test_get_gene_pathways_success(self, mock_fetch):
        # Mock Search Response (first call)
        mock_search_resp = MagicMock()
        mock_search_resp.status_code = 200
        mock_search_resp.json.return_value = {
            "results": [
                {
                    "entries": [
                        {
                            "name": "TP53",
                            "referenceName": "TP53",
                            "referenceIdentifier": "P04637",
                            "databaseName": "UniProt",
                            "dbId": 12345
                        }
                    ]
                }
            ]
        }
        
        # Mock Pathways Response (second call)
        mock_path_resp = MagicMock()
        mock_path_resp.status_code = 200
        mock_path_resp.json.return_value = [
            {
                "displayName": "Pathway A",
                "stId": "R-HSA-111",
                "schemaClass": "Pathway"
            },
            {
                "displayName": "Pathway B",
                "stId": "R-HSA-222",
                "schemaClass": "Pathway"
            }
        ]
        
        # Configure side_effect to return different responses
        mock_fetch.side_effect = [mock_search_resp, mock_path_resp]
        
        result = await pathways.get_gene_pathways("TP53")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Pathway A")
        self.assertEqual(result[0]["id"], "R-HSA-111")

if __name__ == "__main__":
    unittest.main()
