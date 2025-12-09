#!/bin/bash
################################################################################
# OhMyClaude Installation Script
################################################################################
#
# This script installs OhMyClaude - Claude Code one-click configuration tool.
# It performs the following steps:
#   1. Checks prerequisites (Python 3.10+)
#   2. Installs OhMyClaude package via pipx or pip
#   3. Verifies installation
#   4. Provides next steps guidance
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ohmyclaude/ohmyclaude/main/install.sh | bash -s -- --yes
#   ./install.sh            # Interactive installation
#   ./install.sh --yes      # Non-interactive (auto-yes to prompts)
#   ./install.sh --help     # Show help message
#
# Note: When piping to bash, use --yes flag for non-interactive mode
#
################################################################################

set -e  # Exit on error

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Package info
readonly PACKAGE_NAME="ohmyclaude"
readonly MIN_PYTHON_MAJOR=3
readonly MIN_PYTHON_MINOR=10

# Installation options
AUTO_YES=false
USE_PIPX=false

# Auto-detect non-interactive mode (piped input)
if [[ ! -t 0 ]] || [[ ! -t 1 ]]; then
    AUTO_YES=true
fi

################################################################################
# Helper Functions
################################################################################

print_header() {
    printf "%b\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    printf "%b\n" "${CYAN}$1${NC}"
    printf "%b\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    printf "%b\n" "${GREEN}[OK] $1${NC}"
}

print_error() {
    printf "%b\n" "${RED}[ERROR] $1${NC}"
}

print_warning() {
    printf "%b\n" "${YELLOW}[WARN] $1${NC}"
}

print_info() {
    printf "%b\n" "${BLUE}[INFO] $1${NC}"
}

print_step() {
    printf "%b\n" "${CYAN}>>> $1${NC}"
}

confirm() {
    if [ "$AUTO_YES" = true ]; then
        return 0
    fi

    local prompt="$1"
    local default="${2:-y}"

    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi

    read -p "$prompt" -r response
    response=${response:-$default}

    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

################################################################################
# Prerequisite Checks
################################################################################

check_python() {
    print_step "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        print_info "Please install Python 3.10 or higher from https://www.python.org/"
        exit 1
    fi

    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    local major_version=$(echo "$python_version" | cut -d. -f1)
    local minor_version=$(echo "$python_version" | cut -d. -f2)

    if [ "$major_version" -lt "$MIN_PYTHON_MAJOR" ] || \
       ([ "$major_version" -eq "$MIN_PYTHON_MAJOR" ] && [ "$minor_version" -lt "$MIN_PYTHON_MINOR" ]); then
        print_error "Python $python_version found, but Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+ is required"
        print_info "Please upgrade Python from https://www.python.org/"
        exit 1
    fi

    print_success "Python $python_version"
}

check_pipx() {
    print_step "Checking pipx..."

    if command -v pipx &> /dev/null; then
        local pipx_version=$(pipx --version 2>&1)
        print_success "pipx $pipx_version (recommended)"
        USE_PIPX=true
        return 0
    else
        print_warning "pipx not found, will use pip"
        USE_PIPX=false
        return 1
    fi
}

check_pip() {
    print_step "Checking pip..."

    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_error "pip is not installed"
        print_info "Please install pip: https://pip.pypa.io/en/stable/installation/"
        exit 1
    fi

    local pip_cmd="pip3"
    if ! command -v pip3 &> /dev/null; then
        pip_cmd="pip"
    fi

    local pip_version=$($pip_cmd --version 2>&1 | awk '{print $2}')
    print_success "pip $pip_version"
}

################################################################################
# Installation Functions
################################################################################

install_with_pipx() {
    print_step "Installing $PACKAGE_NAME with pipx..."

    if pipx install "$PACKAGE_NAME"; then
        print_success "$PACKAGE_NAME installed successfully with pipx"
        return 0
    else
        print_warning "pipx installation failed, trying pip..."
        return 1
    fi
}

install_with_pip() {
    print_step "Installing $PACKAGE_NAME with pip..."

    local pip_cmd="pip3"
    if ! command -v pip3 &> /dev/null; then
        pip_cmd="pip"
    fi

    if $pip_cmd install --user "$PACKAGE_NAME"; then
        print_success "$PACKAGE_NAME installed successfully with pip"
    else
        print_error "Failed to install $PACKAGE_NAME"
        print_info "Try installing manually: pip install $PACKAGE_NAME"
        exit 1
    fi
}

verify_installation() {
    print_step "Verifying installation..."

    # Check if ohmyclaude command is available
    if ! command -v ohmyclaude &> /dev/null; then
        # Try omc alias
        if ! command -v omc &> /dev/null; then
            print_warning "Command not found in PATH"
            print_info "You may need to restart your terminal or add ~/.local/bin to PATH"
            print_info "Run: export PATH=\"\$HOME/.local/bin:\$PATH\""
            return 1
        fi
    fi

    # Check version
    local version=$(ohmyclaude --version 2>&1 || omc --version 2>&1)
    print_success "Installed: $version"

    return 0
}

################################################################################
# Main Installation Flow
################################################################################

show_help() {
    cat << EOF
OhMyClaude Installation Script

Usage:
    ./install.sh [OPTIONS]

Options:
    --yes       Non-interactive mode (auto-yes to all prompts)
    --help      Show this help message

Description:
    Installs OhMyClaude - Claude Code one-click configuration tool.
    Supports installation via pipx (recommended) or pip.

Requirements:
    - Python 3.10 or higher
    - pip or pipx

Examples:
    ./install.sh              # Interactive installation
    ./install.sh --yes        # Non-interactive installation

    # Or install directly from GitHub:
    curl -fsSL https://raw.githubusercontent.com/ohmyclaude/ohmyclaude/main/install.sh | bash

For more information:
    https://github.com/ohmyclaude/ohmyclaude
EOF
    exit 0
}

show_logo() {
    printf "%b" "${CYAN}"
    cat << 'EOF'
   ___  _     __  __        ____ _                 _
  / _ \| |__ |  \/  |_   _ / ___| | __ _ _   _  __| | ___
 | | | | '_ \| |\/| | | | | |   | |/ _` | | | |/ _` |/ _ \
 | |_| | | | | |  | | |_| | |___| | (_| | |_| | (_| |  __/
  \___/|_| |_|_|  |_|\__, |\____|_|\__,_|\__,_|\__,_|\___|
                     |___/
EOF
    printf "%b\n" "${NC}"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --yes|-y)
                AUTO_YES=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Run './install.sh --help' for usage information"
                exit 1
                ;;
        esac
    done
}

main() {
    # Parse command line arguments
    parse_args "$@"

    # Print header (skip clear in non-interactive mode)
    if [[ -t 1 ]] && [[ -n "$TERM" ]]; then
        clear
    fi
    show_logo
    print_header "OhMyClaude Installation"
    echo ""
    print_info "Claude Code one-click configuration tool"
    print_info "https://github.com/ohmyclaude/ohmyclaude"
    echo ""

    if [ "$AUTO_YES" != true ]; then
        if ! confirm "Continue with installation?"; then
            print_info "Installation cancelled"
            exit 0
        fi
        echo ""
    fi

    # Phase 1: Check prerequisites
    print_header "Phase 1: Checking Prerequisites"
    check_python
    check_pipx || check_pip
    echo ""

    # Phase 2: Install package
    print_header "Phase 2: Installing OhMyClaude"
    if [ "$USE_PIPX" = true ]; then
        install_with_pipx || install_with_pip
    else
        install_with_pip
    fi
    echo ""

    # Phase 3: Verify installation
    print_header "Phase 3: Verifying Installation"
    verify_installation
    echo ""

    # Phase 4: Next steps
    print_header "Installation Complete!"
    echo ""
    print_success "OhMyClaude is now installed!"
    echo ""
    print_info "Quick Start:"
    echo "  1. Run setup wizard:        ohmyclaude setup"
    echo "  2. Check configuration:     ohmyclaude doctor"
    echo "  3. Switch API provider:     ohmyclaude switch glm"
    echo ""
    print_info "Available Presets:"
    echo "  - starter:   Minimal setup (~3,300 tokens)"
    echo "  - standard:  Recommended (~5,500 tokens)"
    echo "  - full:      All features (~8,800 tokens)"
    echo ""
    print_info "Documentation:"
    echo "  - GitHub: https://github.com/ohmyclaude/ohmyclaude"
    echo "  - README: ohmyclaude --help"
    echo ""
    print_success "Happy coding with Claude Code!"
    echo ""
}

# Run main function
main "$@"
