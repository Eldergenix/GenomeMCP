
import os
import asyncio
from typing import List, Dict, Any, Optional
from mcp import McpError
from supabase import create_client, Client

class SupabaseManager:
    """
    Manages persistence for GenomeMCP using Supabase.
    Stores user history, saved items, and chat sessions.
    """
    
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.client: Optional[Client] = None
        self._enabled = False

        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                self._enabled = True
            except Exception as e:
                print(f"Warning: Failed to initialize Supabase client: {e}")
        else:
            print("Warning: SUPABASE_URL or SUPABASE_KEY not set. Persistence disabled.")

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    async def add_history_item(self, user_id: str, item_type: str, content: Dict[str, Any], query: str):
        """Add an item to the user's search history."""
        if not self._enabled: return
        
        try:
            data = {
                "user_id": user_id,
                "type": item_type,
                "query": query,
                "content": content
            }
            # Run in executor to avoid blocking main thread with sync supabase calls if any
            # The python supabase client is sync by default for many ops, wrapping in thread is safer for TUI
            await asyncio.to_thread(self._insert_history, data)
        except Exception as e:
            print(f"Error adding history: {e}")

    def _insert_history(self, data: Dict[str, Any]):
        self.client.table("user_history").insert(data).execute()

    async def get_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve user history."""
        if not self._enabled: return []

        try:
            response = await asyncio.to_thread(
                lambda: self.client.table("user_history")
                        .select("*")
                        .eq("user_id", user_id)
                        .order("created_at", desc=True)
                        .limit(limit)
                        .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []

    async def toggle_favorite(self, user_id: str, item_type: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Toggle an item as favorite. Returns True if now favorited, False if removed."""
        if not self._enabled: return False

        try:
            # Check if exists
            exists_response = await asyncio.to_thread(
                lambda: self.client.table("favorites")
                        .select("id")
                        .eq("user_id", user_id)
                        .eq("item_type", item_type)
                        .eq("item_id", item_id)
                        .execute()
            )
            
            if exists_response.data:
                # Remove
                await asyncio.to_thread(
                    lambda: self.client.table("favorites")
                            .delete()
                            .eq("id", exists_response.data[0]['id'])
                            .execute()
                )
                return False
            else:
                # Add
                payload = {
                    "user_id": user_id,
                    "item_type": item_type,
                    "item_id": item_id,
                    "data": data
                }
                await asyncio.to_thread(
                    lambda: self.client.table("favorites").insert(payload).execute()
                )
                return True

        except Exception as e:
            print(f"Error toggling favorite: {e}")
            return False

# Global instance
db = SupabaseManager()
