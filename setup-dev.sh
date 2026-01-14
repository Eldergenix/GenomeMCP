#!/usr/bin/env bash
# =============================================================================
# GenomeMCP Development Environment Setup
# =============================================================================
# Sets up the development environment with all dependencies
#
# Usage:
#   ./setup-dev.sh
# =============================================================================

set -e

echo ""
echo "🛠️  GenomeMCP Development Setup"
echo "================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check for uv (recommended) or pip
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✅ Using uv for dependency management${NC}"
    TOOL="uv"
elif command -v pip &> /dev/null; then
    echo -e "${YELLOW}⚠️  Using pip (uv recommended: https://github.com/astral-sh/uv)${NC}"
    TOOL="pip"
else
    echo "❌ Neither uv nor pip found"
    exit 1
fi

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo ""
    echo -e "${CYAN}📦 Creating virtual environment...${NC}"
    if [ "$TOOL" = "uv" ]; then
        uv venv
    else
        python3 -m venv .venv
    fi
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo ""
echo -e "${CYAN}📦 Installing dependencies...${NC}"
if [ "$TOOL" = "uv" ]; then
    uv sync --all-extras
else
    pip install -e ".[all]"
fi

echo ""
echo "================================"
echo -e "${GREEN}✅ Development environment ready!${NC}"
echo "================================"
echo ""
echo -e "${CYAN}📝 Next steps:${NC}"
echo "   source .venv/bin/activate     Activate the environment"
echo "   genomemcp --help              Test the CLI"
echo "   pytest tests/                 Run tests"
echo ""
echo -e "${CYAN}🧬 CLI Commands:${NC}"
echo "   genomemcp search BRCA1        Search ClinVar"
echo "   genomemcp gene TP53           Get gene info"
echo "   genomemcp pathway EGFR        Pathway analysis"
echo "   genomemcp tui                 Interactive mode"
echo ""
