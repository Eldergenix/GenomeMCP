
import sys
import os

sys.path.append(os.getcwd())
from src.main import mcp

print("Checking mcp object type:", type(mcp))
print("Has __call__:", hasattr(mcp, "__call__"))

# Check for typically ASGI attrs or methods
if hasattr(mcp, "router") or hasattr(mcp, "starlette_app"):
    print("Likely ASGI compatible via attribute.")
else:
    print("Does not look like standard FastAPI/Starlette app directly.")

# Check for FastMCP specific export
if hasattr(mcp, "_asgi_app"):
    print("Has _asgi_app")
elif hasattr(mcp, "create_asgi_app"):
    print("Has create_asgi_app")
