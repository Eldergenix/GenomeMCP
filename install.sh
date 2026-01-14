#!/usr/bin/env bash
# =============================================================================
# GenomeMCP CLI Installer
# =============================================================================
# One-liner installation script for GenomeMCP CLI
# 
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/nexisdev/GenomeMCP/main/install.sh | bash
#   # OR
#   ./install.sh
# =============================================================================

set -e

echo ""
echo "🧬 GenomeMCP CLI Installer"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}❌ Python 3.10+ is required${NC}"
    echo -e "${YELLOW}   Install from: https://www.python.org/downloads/${NC}"
    exit 1
}

# Check for pipx or pip
check_installer() {
    if command -v pipx &> /dev/null; then
        INSTALLER="pipx"
        echo -e "${GREEN}✅ Using pipx for installation${NC}"
    elif command -v pip3 &> /dev/null; then
        INSTALLER="pip3"
        echo -e "${YELLOW}⚠️  Using pip3 (pipx recommended for CLI tools)${NC}"
    elif command -v pip &> /dev/null; then
        INSTALLER="pip"
        echo -e "${YELLOW}⚠️  Using pip (pipx recommended for CLI tools)${NC}"
    else
        echo -e "${RED}❌ pip or pipx not found${NC}"
        exit 1
    fi
}

# Install GenomeMCP
install_genomemcp() {
    echo ""
    echo -e "${CYAN}📦 Installing GenomeMCP CLI...${NC}"
    echo ""
    
    if [ "$INSTALLER" = "pipx" ]; then
        pipx install "genomemcp[cli]"
    else
        $INSTALLER install --user "genomemcp[cli]"
    fi
}

# Install from local directory (development mode)
install_local() {
    echo ""
    echo -e "${CYAN}📦 Installing GenomeMCP CLI from local directory...${NC}"
    echo ""
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ "$INSTALLER" = "pipx" ]; then
        pipx install -e "$SCRIPT_DIR[cli]"
    else
        $INSTALLER install --user -e "$SCRIPT_DIR[cli]"
    fi
}

# Main installation flow
main() {
    check_python
    check_installer
    
    # Check if running from repository
    if [ -f "pyproject.toml" ] && grep -q "genomemcp" "pyproject.toml" 2>/dev/null; then
        echo -e "${CYAN}📁 Detected local GenomeMCP repository${NC}"
        install_local
    else
        install_genomemcp
    fi
    
    echo ""
    echo "=========================="
    echo -e "${GREEN}✅ Installation Complete!${NC}"
    echo "=========================="
    echo ""
    echo -e "${CYAN}📝 Quick Start:${NC}"
    echo "   genomemcp --help              Show all commands"
    echo "   genomemcp search BRCA1        Search ClinVar"
    echo "   genomemcp pathway TP53        Get pathway info"
    echo "   genomemcp tui                 Interactive mode"
    echo ""
    echo -e "${YELLOW}💡 Tip: Add ~/.local/bin to your PATH if commands aren't found${NC}"
    echo ""
}

main "$@"
