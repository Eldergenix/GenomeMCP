
import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.persistence.client import db

async def verify():
    print("--- Verifying Persistence Layer ---")
    
    if not os.environ.get("SUPABASE_URL"):
        print("❌ SUPABASE_URL not set. Skipping persistence verification.")
        return

    if db.is_enabled:
        print("✅ Supabase Client Initialized")
    else:
        print("❌ Supabase Client Failed to Initialize")
        return

    # test history
    try:
        print("Testing add_history_item...")
        await db.add_history_item("test_user", "verification_test", {"status": "ok"}, "verifying persistence")
        print("✅ add_history_item success")
    except Exception as e:
        print(f"❌ add_history_item failed: {e}")

    try:
        print("Testing get_history...")
        history = await db.get_history("test_user", limit=1)
        if history and history[0]['query'] == "verifying persistence":
            print("✅ get_history success")
        else:
            print(f"❌ get_history failed or mismatch: {history}")
    except Exception as e:
         print(f"❌ get_history failed: {e}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(verify())
