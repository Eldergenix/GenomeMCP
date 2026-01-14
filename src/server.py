
# Adapter to serve FastMCP via Uvicorn/Starlette
from src.main import mcp
import os

# FastMCP typically exposes the underlying Starlette/FastAPI app 
# via ._asgi_app or simply by being callable if it inherits.
# We'll try to detect the right entry point.

app = None

# 1. If mcp itself is the ASGI app
if hasattr(mcp, "__call__") and not hasattr(mcp, "run"): 
    # This check is heuristic. FastMCP has a run() method, but might also be callable?
    # Usually it's NOT directly the app.
    pass

# 2. Check for _asgi_app (common internal)
if hasattr(mcp, "_asgi_app"):
    app = mcp._asgi_app

# 3. Check for create_asgi_app (factory)
elif hasattr(mcp, "create_asgi_app"):
    app = mcp.create_asgi_app()

# 4. Fallback: If we can't find it, we might be unable to serve it via Uvicorn standardly 
# without the 'mcp' CLI or a specific adapter.
# However, for FastMCP, it is usually sufficient to use the internal app.
if not app:
    # Attempt to use the object itself, assuming it might work or crash (better to fail fast)
    print("Warning: Could not find explicit ASGI app on MCP object. Trying object itself.")
    app = mcp

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
