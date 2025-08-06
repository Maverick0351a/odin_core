#!/bin/bash

# ODIN Protocol Postman Collection Setup Script
# Automates the installation and configuration of ODIN Protocol Postman collections

echo "🚀 ODIN Protocol Postman Plugin Setup"
echo "======================================="

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo "📦 Installing Newman (Postman CLI)..."
    npm install -g newman
    npm install -g newman-reporter-html
else
    echo "✅ Newman is already installed"
fi

# Create postman directory if it doesn't exist
mkdir -p postman
cd postman

echo "📁 Setting up Postman collections..."

# Check if collections exist
if [ ! -f "ODIN_Protocol_Collection.json" ]; then
    echo "❌ ODIN_Protocol_Collection.json not found!"
    echo "Please ensure the collection file is in the postman directory"
    exit 1
fi

if [ ! -f "ODIN_Protocol_Environment.json" ]; then
    echo "❌ ODIN_Protocol_Environment.json not found!"
    echo "Please ensure the environment file is in the postman directory"
    exit 1
fi

# Validate collection files
echo "🔍 Validating collection files..."
if jq empty ODIN_Protocol_Collection.json 2>/dev/null; then
    echo "✅ Collection JSON is valid"
else
    echo "❌ Collection JSON is invalid"
    exit 1
fi

if jq empty ODIN_Protocol_Environment.json 2>/dev/null; then
    echo "✅ Environment JSON is valid"
else
    echo "❌ Environment JSON is invalid"
    exit 1
fi

# Run smoke tests
echo "🧪 Running smoke tests..."
newman run ODIN_Protocol_Tests.json \
    -e ODIN_Protocol_Environment.json \
    --reporters cli,html \
    --reporter-html-export results/smoke-test-report.html \
    --timeout-request 10000 \
    --delay-request 100

if [ $? -eq 0 ]; then
    echo "✅ Smoke tests passed!"
else
    echo "❌ Smoke tests failed"
    echo "Check the HTML report for details: results/smoke-test-report.html"
fi

# Generate usage instructions
cat << EOF > USAGE.md
# ODIN Protocol Postman Plugin Usage

## Quick Start Commands

### Run All Tests
\`\`\`bash
newman run ODIN_Protocol_Collection.json -e ODIN_Protocol_Environment.json
\`\`\`

### Run Specific Test Suite
\`\`\`bash
# Performance tests only
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "⚡ Performance Tests"

# Security tests only  
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "🔒 Security Tests"

# HEL Engine tests only
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "🧠 HEL Engine Tests"
\`\`\`

### Generate HTML Report
\`\`\`bash
newman run ODIN_Protocol_Collection.json \
    -e ODIN_Protocol_Environment.json \
    --reporters html \
    --reporter-html-export odin-test-report.html
\`\`\`

### CI/CD Integration
\`\`\`bash
# For Jenkins/GitHub Actions
newman run ODIN_Protocol_Tests.json \
    -e ODIN_Protocol_Environment.json \
    --reporters junit \
    --reporter-junit-export results/junit-report.xml
\`\`\`

## Environment Variables Required

- \`odin_base_url\`: API base URL
- \`odin_api_token\`: Authentication token
- \`security_token\`: Security validation token

## Test Categories

1. **🧪 Smoke Tests** - Basic connectivity and authentication
2. **⚡ Performance Tests** - Sub-50ms response validation
3. **🔒 Security Tests** - Authentication and HTTPS enforcement
4. **🧠 HEL Engine Tests** - Rule evaluation and processing
5. **🌐 Cross-Model Tests** - Multi-model interoperability

EOF

echo "📝 Generated USAGE.md with detailed instructions"

# Create CI/CD workflow example
mkdir -p .github/workflows
cat << EOF > .github/workflows/odin-postman-tests.yml
name: ODIN Protocol API Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  api-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install Newman
      run: |
        npm install -g newman
        npm install -g newman-reporter-html
        
    - name: Run ODIN Protocol Tests
      run: |
        newman run postman/ODIN_Protocol_Tests.json \\
          -e postman/ODIN_Protocol_Environment.json \\
          --env-var "odin_api_token=\${{ secrets.ODIN_API_TOKEN }}" \\
          --env-var "odin_base_url=\${{ secrets.ODIN_BASE_URL }}" \\
          --reporters cli,junit,html \\
          --reporter-junit-export results/junit-report.xml \\
          --reporter-html-export results/test-report.html
          
    - name: Upload Test Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: results/
        
    - name: Publish Test Results
      uses: dorny/test-reporter@v1
      if: always()
      with:
        name: ODIN Protocol Tests
        path: results/junit-report.xml
        reporter: java-junit
EOF

echo "📋 Created GitHub Actions workflow example"

echo ""
echo "🎉 Setup Complete!"
echo "==================="
echo ""
echo "Next Steps:"
echo "1. Import collections into Postman:"
echo "   - ODIN_Protocol_Collection.json"
echo "   - ODIN_Protocol_Environment.json"
echo ""
echo "2. Configure environment variables:"
echo "   - odin_api_token: Your API token"
echo "   - odin_base_url: API endpoint"
echo ""
echo "3. Run tests with Newman:"
echo "   newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json"
echo ""
echo "📚 Documentation: See README.md for detailed usage"
echo "🔧 CI/CD: See .github/workflows/odin-postman-tests.yml for automation"
echo ""
echo "Happy testing! 🚀"
