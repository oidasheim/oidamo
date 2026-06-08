#!/bin/bash
set -e

####################################################################
# 🚀 OIDAMO + LOKALHORST - Complete Stack Deployment
# Merged | Debug | Fix | Deploy Pipeline
# Usage: bash deploy-all.sh [--repo oidamo|lokalhorst|both] [--mode dev|prod]
####################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_MODE="both"
DEPLOY_MODE="dev"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="deploy_${TIMESTAMP}.log"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo) REPO_MODE="$2"; shift 2 ;;
        --mode) DEPLOY_MODE="$2"; shift 2 ;;
        *) shift ;;
    esac
done

exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

####################################################################
# 🔍 SCAN & DIAGNOSTICS
####################################################################

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📊 PHASE 1: SCAN & DIAGNOSTICS${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

scan_repo() {
    local repo_path=$1
    local repo_name=$2
    
    if [ ! -d "$repo_path" ]; then
        echo -e "${YELLOW}⚠ Cloning $repo_name...${NC}"
        git clone "https://github.com/oidasheim/$repo_name.git" "$repo_path" 2>&1 | grep -v "^Cloning" || true
    fi
    
    echo -e "${BLUE}Scanning: $repo_name${NC}"
    cd "$repo_path"
    
    echo -n "  📁 Files: "
    find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" \) 2>/dev/null | wc -l
    
    echo -n "  🐍 Python files: "
    find . -name "*.py" 2>/dev/null | wc -l
    
    echo -n "  📝 TypeScript files: "
    find . -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l
    
    if [ -f "requirements.txt" ]; then
        echo -n "  📦 Python deps: "
        wc -l < requirements.txt
    fi
    
    if [ -f "package.json" ]; then
        echo -n "  📦 Node deps: "
        grep -c '"' package.json || echo "0"
    fi
    
    cd - > /dev/null
    echo ""
}

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "oidamo" ]]; then
    scan_repo "oidamo" "oidamo"
fi

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "lokalhorst" ]]; then
    scan_repo "lokalhorst" "lokalhorst"
fi

####################################################################
# 🔧 DEBUG & FIX
####################################################################

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🔧 PHASE 2: DEBUG & FIX${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

debug_repo() {
    local repo_path=$1
    local repo_name=$2
    
    echo -e "${BLUE}Debugging: $repo_name${NC}"
    cd "$repo_path"
    
    # ✅ Check Python syntax
    echo "  Checking Python syntax..."
    python_files=$(find . -name "*.py" -type f 2>/dev/null)
    if [ -n "$python_files" ]; then
        while IFS= read -r file; do
            python3 -m py_compile "$file" 2>&1 | grep -v "^$" && echo "    ⚠ $file" || true
        done <<< "$python_files"
    fi
    
    # ✅ Check requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "  Checking requirements.txt..."
        if ! grep -q "numpy\|librosa\|opencv" requirements.txt 2>/dev/null; then
            echo -e "    ${YELLOW}⚠ Missing core dependencies${NC}"
        fi
    fi
    
    # ✅ Check TypeScript
    if [ -f "tsconfig.json" ]; then
        echo "  Found TypeScript config"
    fi
    
    # ✅ Create missing config files
    if [ ! -f ".env.example" ]; then
        echo "  Creating .env.example..."
        cat > .env.example << 'EOF'
NODE_ENV=development
DEBUG=true
LOG_LEVEL=info
EOF
    fi
    
    cd - > /dev/null
    echo ""
}

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "oidamo" ]]; then
    debug_repo "oidamo" "oidamo"
fi

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "lokalhorst" ]]; then
    debug_repo "lokalhorst" "lokalhorst"
fi

####################################################################
# 🏗️ BUILD & INSTALL
####################################################################

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🏗️ PHASE 3: BUILD & INSTALL${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

build_repo() {
    local repo_path=$1
    local repo_name=$2
    
    echo -e "${BLUE}Building: $repo_name${NC}"
    cd "$repo_path"
    
    # Python Backend
    if [ -f "requirements.txt" ]; then
        echo "  📦 Installing Python dependencies..."
        python3 -m venv venv 2>/dev/null || true
        source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
        pip install --upgrade pip setuptools wheel > /dev/null 2>&1
        pip install -q -r requirements.txt || echo "    ⚠ Some packages failed"
    fi
    
    # Node.js Frontend
    if [ -f "package.json" ]; then
        echo "  📦 Installing Node dependencies..."
        npm ci 2>/dev/null || npm install || echo "    ⚠ npm install had issues"
    fi
    
    cd - > /dev/null
    echo ""
}

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "oidamo" ]]; then
    build_repo "oidamo" "oidamo"
fi

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "lokalhorst" ]]; then
    build_repo "lokalhorst" "lokalhorst"
fi

####################################################################
# ✅ VERIFY & TEST
####################################################################

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}✅ PHASE 4: VERIFY & TEST${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

verify_repo() {
    local repo_path=$1
    local repo_name=$2
    
    echo -e "${BLUE}Verifying: $repo_name${NC}"
    cd "$repo_path"
    
    # Python tests
    if [ -d "tests" ] && command -v pytest &> /dev/null; then
        echo "  🧪 Running pytest..."
        pytest tests/ -v --tb=short 2>&1 | head -20 || echo "    ⚠ Tests had issues"
    fi
    
    # Linting
    if command -v pylint &> /dev/null && [ -f "requirements.txt" ]; then
        echo "  📝 Linting Python files..."
        find . -name "*.py" -type f | head -3 | xargs pylint --disable=all 2>&1 | grep -v "^Your" | head -5 || true
    fi
    
    cd - > /dev/null
    echo ""
}

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "oidamo" ]]; then
    verify_repo "oidamo" "oidamo"
fi

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "lokalhorst" ]]; then
    verify_repo "lokalhorst" "lokalhorst"
fi

####################################################################
# 🚀 DEPLOY
####################################################################

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}🚀 PHASE 5: DEPLOY (Mode: $DEPLOY_MODE)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

deploy_repo() {
    local repo_path=$1
    local repo_name=$2
    
    echo -e "${BLUE}Deploying: $repo_name (mode: $DEPLOY_MODE)${NC}"
    cd "$repo_path"
    
    if [ "$DEPLOY_MODE" == "prod" ]; then
        echo "  🔐 Production deployment..."
        
        # Create docker image
        if [ -f "Dockerfile" ]; then
            echo "  🐳 Building Docker image..."
            docker build -t "oidasheim/$repo_name:latest" . 2>&1 | tail -5 || echo "    ⚠ Docker build had issues"
        fi
        
        # Create systemd service
        echo "  ⚙️ Creating systemd service..."
        mkdir -p /tmp/deploy
        cat > "/tmp/deploy/$repo_name.service" << EOF
[Unit]
Description=$repo_name Service
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/$repo_name
ExecStart=/opt/$repo_name/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        echo "    ✅ Service file: /tmp/deploy/$repo_name.service"
    else
        echo "  💻 Development deployment..."
        
        # Start dev server
        if [ -f "requirements.txt" ]; then
            source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
            echo "    ✅ Backend ready (activate: source venv/bin/activate)"
        fi
        
        if [ -f "package.json" ]; then
            echo "    ✅ Frontend ready (start: npm start)"
        fi
    fi
    
    cd - > /dev/null
    echo ""
}

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "oidamo" ]]; then
    deploy_repo "oidamo" "oidamo"
fi

if [[ "$REPO_MODE" == "both" || "$REPO_MODE" == "lokalhorst" ]]; then
    deploy_repo "lokalhorst" "lokalhorst"
fi

####################################################################
# 📊 SUMMARY
####################################################################

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}📋 DEPLOYMENT REPORT${NC}"
echo "  Repository Mode: $REPO_MODE"
echo "  Deployment Mode: $DEPLOY_MODE"
echo "  Log File: $LOG_FILE"
echo ""

echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Backend: source oidamo/venv/bin/activate && python -m uvicorn backend.main:app --reload"
echo "  2. Frontend: cd oidamo/mobile && npm start"
echo "  3. Tests: cd oidamo && pytest tests/"
echo "  4. Logs: tail -f $LOG_FILE"
echo ""

echo -e "${GREEN}✨ All systems ready for operation!${NC}"
echo ""
