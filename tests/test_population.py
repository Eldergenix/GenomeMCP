import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath("."))

from src import population

class TestPopulation(unittest.IsolatedAsyncioTestCase):
    @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_fetch_gnomad_frequency_success(self, mock_post):
        # Mock response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "variant": {
                    "genome": {
                        "af": 0.0001,
                        "ac": 2,
                        "an": 20000
                    }
                }
            }
        }
        mock_post.return_value = mock_resp
        
        result = await population.fetch_gnomad_frequency("1", 12345, "A", "G")
        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "genome")
        self.assertEqual(result["af"], 0.0001)

    @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_fetch_gnomad_frequency_not_found(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": {"variant": None}}
        mock_post.return_value = mock_resp
        
        result = await population.fetch_gnomad_frequency("1", 99999, "A", "G")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
