# test_discovery_manual.py
import asyncio
from src.main import find_related_genes

async def run():
    print("Searching for genes related to 'Lynch Syndrome'...")
    res = await find_related_genes("Lynch Syndrome")
    print(res)
    
    print("\nSearching for genes related to 'Dilated Cardiomyopathy'...")
    res2 = await find_related_genes("Dilated Cardiomyopathy")
    print(res2)

    print("\nGenerating Discovery Evidence for 'Lynch Syndrome'...")
    from src.main import get_discovery_evidence
    res3 = await get_discovery_evidence("Lynch Syndrome")
    print(res3)

if __name__ == "__main__":
    asyncio.run(run())
