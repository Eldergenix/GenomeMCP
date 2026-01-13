# test_genomics_tool.py
import asyncio
from src.main import get_genomic_context

async def run():
    print("Testing get_genomic_context('BRCA1', 150)...")
    # Position 150 is likely Exon 2 or 3 depending on transcript
    res = await get_genomic_context("BRCA1", 150)
    print(res)
    
    # Try a large position likely to be Intronic or deep Exon
    print("\nTesting get_genomic_context('BRCA1', 5000)...")
    res2 = await get_genomic_context("BRCA1", 5000)
    print(res2)

if __name__ == "__main__":
    asyncio.run(run())
