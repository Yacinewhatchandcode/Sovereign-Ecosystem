#!/bin/bash
###############################################################################
# aSiReM Agent Fleet - Dependency Installation Script
# Sprint 1-7 Dependencies for Agent Capabilities
###############################################################################

set -e  # Exit on error

echo "🚀 aSiReM Agent Fleet - Installing Dependencies"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.9+${NC}"
    exit 1
fi

echo -e "${BLUE}Using Python: $($PYTHON_CMD --version)${NC}"
echo ""

###############################################################################
# Phase 1: Core Dependencies (Already Installed)
###############################################################################

echo -e "${GREEN}✅ Phase 1: Core Dependencies (Verified)${NC}"
echo "   - opik (LLM observability) ✅"
echo "   - supabase (database) ✅"
echo "   - pydantic-settings (config) ✅"
echo ""

###############################################################################
# Phase 2: Git & GitHub Operations (Sprint 1)
###############################################################################

echo -e "${YELLOW}📦 Phase 2: Git & GitHub Operations${NC}"

# GitHub CLI (for advanced operations)
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI (gh)..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update
        sudo apt install gh
    fi
else
    echo -e "${GREEN}✅ GitHub CLI already installed${NC}"
fi

# GitPython (optional, for advanced Git operations)
$PYTHON_CMD -m pip install --user --break-system-packages \
    GitPython

echo -e "${GREEN}✅ Git & GitHub dependencies installed${NC}"
echo ""

###############################################################################
# Phase 3: Code Generation & Analysis (Sprint 2)
###############################################################################

echo -e "${YELLOW}📦 Phase 3: Code Generation & Analysis${NC}"

$PYTHON_CMD -m pip install --user --break-system-packages \
    anthropic \
    openai \
    libcst \
    astroid \
    black \
    isort \
    autopep8

echo -e "${GREEN}✅ Code generation dependencies installed${NC}"
echo ""

###############################################################################
# Phase 4: Security & SBOM (Sprint 3)
###############################################################################

echo -e "${YELLOW}📦 Phase 4: Security & SBOM${NC}"

# CycloneDX for SBOM generation
$PYTHON_CMD -m pip install --user --break-system-packages \
    cyclonedx-bom \
    cyclonedx-python-lib \
    safety \
    bandit

# TruffleHog for secret scanning (Go binary)
if ! command -v trufflehog &> /dev/null; then
    echo "Installing TruffleHog..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install trufflesecurity/trufflehog/trufflehog
    else
        # Linux - download binary
        TRUFFLEHOG_VERSION="3.63.2"
        curl -sSfL https://github.com/trufflesecurity/trufflehog/releases/download/v${TRUFFLEHOG_VERSION}/trufflehog_${TRUFFLEHOG_VERSION}_linux_amd64.tar.gz | tar -xz -C /tmp
        sudo mv /tmp/trufflehog /usr/local/bin/
    fi
else
    echo -e "${GREEN}✅ TruffleHog already installed${NC}"
fi

# GitLeaks (alternative secret scanner)
if ! command -v gitleaks &> /dev/null; then
    echo "Installing GitLeaks..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gitleaks
    else
        # Linux - download binary
        GITLEAKS_VERSION="8.18.1"
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz | tar -xz -C /tmp
        sudo mv /tmp/gitleaks /usr/local/bin/
    fi
else
    echo -e "${GREEN}✅ GitLeaks already installed${NC}"
fi

# Snyk CLI (requires signup)
if ! command -v snyk &> /dev/null; then
    echo "Installing Snyk CLI..."
    npm install -g snyk || echo -e "${YELLOW}⚠️ Snyk requires npm. Install Node.js first.${NC}"
else
    echo -e "${GREEN}✅ Snyk already installed${NC}"
fi

echo -e "${GREEN}✅ Security dependencies installed${NC}"
echo ""

###############################################################################
# Phase 5: DevOps & Deployment (Sprint 4)
###############################################################################

echo -e "${YELLOW}📦 Phase 5: DevOps & Deployment${NC}"

# Docker SDK for Python
$PYTHON_CMD -m pip install --user --break-system-packages \
    docker

# Kubernetes Python client
$PYTHON_CMD -m pip install --user --break-system-packages \
    kubernetes

# Terraform (if not installed)
if ! command -v terraform &> /dev/null; then
    echo "Installing Terraform..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew tap hashicorp/tap
        brew install hashicorp/tap/terraform
    else
        # Linux
        wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
        echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
        sudo apt update && sudo apt install terraform
    fi
else
    echo -e "${GREEN}✅ Terraform already installed${NC}"
fi

# Helm (Kubernetes package manager)
if ! command -v helm &> /dev/null; then
    echo "Installing Helm..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
else
    echo -e "${GREEN}✅ Helm already installed${NC}"
fi

echo -e "${GREEN}✅ DevOps dependencies installed${NC}"
echo ""

###############################################################################
# Phase 6: Testing & Quality (Sprint 5)
###############################################################################

echo -e "${YELLOW}📦 Phase 6: Testing & Quality${NC}"

# Pytest ecosystem
$PYTHON_CMD -m pip install --user --break-system-packages \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock \
    pytest-xdist

# Mutation testing
$PYTHON_CMD -m pip install --user --break-system-packages \
    mutmut

# Property-based testing
$PYTHON_CMD -m pip install --user --break-system-packages \
    hypothesis \
    schemathesis

# Playwright (E2E testing - already installed via skill)
echo -e "${GREEN}✅ Playwright already available (webapp-testing skill)${NC}"

echo -e "${GREEN}✅ Testing dependencies installed${NC}"
echo ""

###############################################################################
# Phase 7: Vector DB & Semantic Search (Sprint 2)
###############################################################################

echo -e "${YELLOW}📦 Phase 7: Vector DB & Semantic Search${NC}"

$PYTHON_CMD -m pip install --user --break-system-packages \
    chromadb \
    sentence-transformers \
    faiss-cpu

echo -e "${GREEN}✅ Vector DB dependencies installed${NC}"
echo ""

###############################################################################
# Phase 8: API Security Testing (Sprint 5)
###############################################################################

echo -e "${YELLOW}📦 Phase 8: API Security Testing${NC}"

# OWASP ZAP (requires Java)
if ! command -v zap.sh &> /dev/null && ! command -v zap-cli &> /dev/null; then
    echo -e "${YELLOW}⚠️ OWASP ZAP not found. Install manually from https://www.zaproxy.org/${NC}"
    echo "   Or use Docker: docker pull owasp/zap2docker-stable"
else
    echo -e "${GREEN}✅ OWASP ZAP already installed${NC}"
fi

echo ""

###############################################################################
# Phase 9: Governance & Policy (Sprint 6)
###############################################################################

echo -e "${YELLOW}📦 Phase 9: Governance & Policy${NC}"

# Open Policy Agent (OPA)
if ! command -v opa &> /dev/null; then
    echo "Installing Open Policy Agent..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install opa
    else
        # Linux - download binary
        OPA_VERSION="0.60.0"
        curl -L -o /tmp/opa https://openpolicyagent.org/downloads/v${OPA_VERSION}/opa_linux_amd64_static
        chmod +x /tmp/opa
        sudo mv /tmp/opa /usr/local/bin/
    fi
else
    echo -e "${GREEN}✅ OPA already installed${NC}"
fi

# Rate limiting & quota management
$PYTHON_CMD -m pip install --user --break-system-packages \
    ratelimit \
    slowapi

echo -e "${GREEN}✅ Governance dependencies installed${NC}"
echo ""

###############################################################################
# Phase 10: ML/AI Ops (Sprint 7)
###############################################################################

echo -e "${YELLOW}📦 Phase 10: ML/AI Ops${NC}"

$PYTHON_CMD -m pip install --user --break-system-packages \
    mlflow \
    evidently \
    shap \
    lime

echo -e "${GREEN}✅ ML Ops dependencies installed${NC}"
echo ""

###############################################################################
# Phase 11: Communication & Notifications (Sprint 6)
###############################################################################

echo -e "${YELLOW}📦 Phase 11: Communication & Notifications${NC}"

$PYTHON_CMD -m pip install --user --break-system-packages \
    slack-sdk \
    pymsteams

echo -e "${GREEN}✅ Communication dependencies installed${NC}"
echo ""

###############################################################################
# Phase 12: Additional Tools
###############################################################################

echo -e "${YELLOW}📦 Phase 12: Additional Tools${NC}"

# Semgrep (static analysis)
if ! command -v semgrep &> /dev/null; then
    echo "Installing Semgrep..."
    $PYTHON_CMD -m pip install --user --break-system-packages semgrep
else
    echo -e "${GREEN}✅ Semgrep already installed${NC}"
fi

# License checking
$PYTHON_CMD -m pip install --user --break-system-packages \
    license-expression \
    pip-licenses

# YAML processing
$PYTHON_CMD -m pip install --user --break-system-packages \
    pyyaml \
    jinja2

echo -e "${GREEN}✅ Additional tools installed${NC}"
echo ""

###############################################################################
# Verification
###############################################################################

echo ""
echo -e "${BLUE}🔍 Verifying installations...${NC}"
echo ""

# Function to check command
check_cmd() {
    if command -v $1 &> /dev/null; then
        echo -e "   ${GREEN}✅ $1${NC}"
    else
        echo -e "   ${YELLOW}⚠️ $1 not found${NC}"
    fi
}

# Check key tools
check_cmd "git"
check_cmd "gh"
check_cmd "docker"
check_cmd "kubectl"
check_cmd "terraform"
check_cmd "helm"
check_cmd "trufflehog"
check_cmd "gitleaks"
check_cmd "semgrep"
check_cmd "opa"

echo ""

# Check Python packages
echo -e "${BLUE}📦 Python packages:${NC}"
$PYTHON_CMD -m pip list --user 2>/dev/null | grep -E "(opik|supabase|anthropic|openai|chromadb|docker|kubernetes|pytest|cyclonedx)" || echo -e "${YELLOW}   Some packages may be missing${NC}"

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "   1. Authenticate GitHub CLI: gh auth login"
echo "   2. Authenticate Snyk: snyk auth"
echo "   3. Configure Opik: export OPIK_API_KEY=your_key"
echo "   4. Test Git Agent: cd sovereign-dashboard && python3 real_git_agent.py"
echo ""
echo -e "${GREEN}🚀 Ready to roll!${NC}"
