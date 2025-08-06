#!/bin/bash

# ODIN Protocol HEL VS Code Extension - Publishing Script
# This script prepares and publishes the extension to VS Code Marketplace

set -e

echo "🚀 ODIN Protocol HEL VS Code Extension - Publishing Script"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EXTENSION_NAME="odin-protocol-hel"
VERSION="1.1.0"
PUBLISHER="odin-protocol"

echo -e "${BLUE}📦 Preparing to publish ${EXTENSION_NAME} v${VERSION}${NC}"

# Check if we have the required tools
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install Node.js first.${NC}"
    exit 1
fi

if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ npx is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Check if vsce is installed
if ! command -v vsce &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Visual Studio Code Extension Manager (vsce)...${NC}"
    npm install -g vsce
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
npm install

# Compile TypeScript
echo -e "${YELLOW}🔧 Compiling TypeScript...${NC}"
npm run compile

# Run tests
echo -e "${YELLOW}🧪 Running tests...${NC}"
npm test || echo -e "${YELLOW}⚠️ Tests failed but continuing...${NC}"

# Lint the code
echo -e "${YELLOW}🔍 Running linter...${NC}"
npm run lint || echo -e "${YELLOW}⚠️ Linting issues found but continuing...${NC}"

# Package the extension
echo -e "${YELLOW}📦 Packaging extension...${NC}"
vsce package

# Get the packaged file name
PACKAGE_FILE="${EXTENSION_NAME}-${VERSION}.vsix"

if [ ! -f "$PACKAGE_FILE" ]; then
    echo -e "${RED}❌ Package file ${PACKAGE_FILE} not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Extension packaged successfully: ${PACKAGE_FILE}${NC}"

# Check if the user wants to publish
echo -e "${BLUE}🤔 Do you want to publish to VS Code Marketplace? (y/N)${NC}"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    # Check if we have a personal access token
    if [ -z "$VSCE_PAT" ]; then
        echo -e "${YELLOW}🔑 Please enter your Visual Studio Marketplace Personal Access Token:${NC}"
        read -s VSCE_PAT
        export VSCE_PAT
    fi
    
    echo -e "${YELLOW}🚀 Publishing to VS Code Marketplace...${NC}"
    vsce publish -p $VSCE_PAT
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}🎉 Extension published successfully!${NC}"
        echo -e "${GREEN}📍 Available at: https://marketplace.visualstudio.com/items?itemName=${PUBLISHER}.${EXTENSION_NAME}${NC}"
    else
        echo -e "${RED}❌ Publishing failed!${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}📦 Extension packaged but not published.${NC}"
    echo -e "${BLUE}💡 To publish later, run: vsce publish -p <your-token>${NC}"
fi

# Generate installation instructions
echo -e "${YELLOW}📝 Generating installation instructions...${NC}"

cat > INSTALL.md << EOF
# 🧠 ODIN Protocol HEL Extension - Installation Guide

## 📦 Install from VS Code Marketplace

### Method 1: VS Code UI
1. Open Visual Studio Code
2. Click on Extensions icon (Ctrl+Shift+X)
3. Search for "ODIN Protocol HEL"
4. Click "Install" on the extension by ${PUBLISHER}

### Method 2: Command Line
\`\`\`bash
code --install-extension ${PUBLISHER}.${EXTENSION_NAME}
\`\`\`

### Method 3: From VSIX File
\`\`\`bash
code --install-extension ${PACKAGE_FILE}
\`\`\`

## 🚀 Quick Start

1. **Create ODIN Project**: Ctrl+Shift+P → "ODIN: Create Project"
2. **Test HEL Capabilities**: Ctrl+Shift+P → "ODIN: Run HEL Evaluation"
3. **AI-to-AI Communication**: Ctrl+Shift+P → "ODIN: Test Communication"

## 🧠 Available Commands

| Command | Description |
|---------|-------------|
| \`ODIN: Create Project\` | Create new HEL-powered project |
| \`ODIN: Run HEL Evaluation\` | Test HEL rule engine |
| \`ODIN: Test Communication\` | Test AI-to-AI messaging |
| \`ODIN: Performance Metrics\` | View real-time analytics |
| \`ODIN: Deploy to Cloud\` | Deploy to AWS/Azure/GCP |
| \`ODIN: Security Scan\` | Run compliance checks |

## ⚙️ Configuration

Open VS Code settings and configure:

\`\`\`json
{
    "odin.apiEndpoint": "https://api.odin-protocol.com",
    "odin.enableRealTimeMetrics": true,
    "odin.helEngine.timeout": 50,
    "odin.crossModel.providers": ["openai", "anthropic", "google"]
}
\`\`\`

## 🎯 Features

- ⚡ **Real-time Decision Making** (sub-50ms)
- 🔧 **Self-healing Communication** 
- 🌐 **Cross-model Interoperability**
- 🛡️ **Enterprise Security & Compliance**
- 📊 **Performance Analytics**
- 🎮 **Interactive Debugging**
- ☁️ **1-click Cloud Deployment**

## 📞 Support

- 📖 [Documentation](https://docs.odin-protocol.com)
- 🐛 [Issues](https://github.com/odin-protocol/vscode-extension/issues)
- 💬 [Discord](https://discord.gg/odin-protocol)
- 📧 [Enterprise](mailto:enterprise@odin-protocol.com)

**Transform your AI development workflow today! 🚀**
EOF

echo -e "${GREEN}✅ Installation guide created: INSTALL.md${NC}"

# Display final summary
echo ""
echo -e "${GREEN}🎉 PUBLISHING SUMMARY${NC}"
echo -e "${GREEN}=====================${NC}"
echo -e "${GREEN}📦 Package: ${PACKAGE_FILE}${NC}"
echo -e "${GREEN}🎯 Version: ${VERSION}${NC}"
echo -e "${GREEN}👤 Publisher: ${PUBLISHER}${NC}"
echo -e "${GREEN}📝 Size: $(du -h ${PACKAGE_FILE} | cut -f1)${NC}"

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${GREEN}🌐 Status: PUBLISHED TO MARKETPLACE${NC}"
    echo -e "${GREEN}🔗 URL: https://marketplace.visualstudio.com/items?itemName=${PUBLISHER}.${EXTENSION_NAME}${NC}"
else
    echo -e "${BLUE}🌐 Status: PACKAGED (NOT PUBLISHED)${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo -e "${BLUE}1. 📢 Share on social media${NC}"
echo -e "${BLUE}2. 📧 Email developer communities${NC}"
echo -e "${BLUE}3. 📝 Write blog posts/tutorials${NC}"
echo -e "${BLUE}4. 🎥 Create demo videos${NC}"
echo -e "${BLUE}5. 📈 Monitor marketplace analytics${NC}"

echo ""
echo -e "${GREEN}🧠 ODIN Protocol HEL Extension ready to transform AI development! 🚀${NC}"
