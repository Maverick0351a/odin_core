# ODIN Protocol Configuration Guide

## Quick Setup Instructions

### 1. Install Requirements ✅ DONE
- Node.js ✅ Installed
- Newman ✅ Installed  
- Collection files ✅ Ready

### 2. Configure API Credentials

You have 2 options:

#### Option A: Edit the test script (Recommended for testing)
1. Open `test.ps1` in a text editor
2. Replace `"your-api-token-here"` with your actual API token
3. Replace `"https://api.odin-protocol.com"` with your API endpoint
4. Save the file
5. Run: `.\test.ps1`

#### Option B: Edit the environment file (For Postman GUI)
1. Open `ODIN_Protocol_Environment.json` in a text editor
2. Find the line with `"odin_api_token"`
3. Replace `"your-api-token-here"` with your actual token
4. Save the file
5. Import both JSON files into Postman

### 3. Test Commands

#### Basic Health Check:
```
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "Smoke Tests"
```

#### Performance Tests (Validate sub-50ms responses):
```
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "Performance Tests"
```

#### Security Tests:
```
newman run ODIN_Protocol_Tests.json -e ODIN_Protocol_Environment.json --folder "Security Tests"
```

#### Full API Test Suite:
```
newman run ODIN_Protocol_Collection.json -e ODIN_Protocol_Environment.json --reporters html --reporter-html-export results/full-report.html
```

### 4. Test Categories Available

🧪 **Smoke Tests** - Basic connectivity and authentication
⚡ **Performance Tests** - Sub-50ms response validation  
🔒 **Security Tests** - Authentication and HTTPS enforcement
🧠 **HEL Engine Tests** - Rule evaluation and processing
🌐 **Cross-Model Tests** - Multi-model interoperability

### 5. Viewing Results

All test reports are saved in the `results/` folder:
- HTML reports for detailed analysis
- JSON reports for programmatic processing
- Console output for immediate feedback

### 6. Integration with Postman GUI

1. Open Postman application
2. Click "Import" in the top left
3. Select these files:
   - `ODIN_Protocol_Collection.json`
   - `ODIN_Protocol_Environment.json`
4. Choose "ODIN Protocol Environment" from the environment dropdown
5. Start testing with the GUI interface

### 7. Troubleshooting

**Authentication Errors (401):**
- Verify your API token is correct
- Check if the token has expired
- Ensure the base URL is correct

**Timeout Errors:**
- Check your internet connection
- Verify the API endpoint is reachable
- Increase timeout with `--timeout-request 30000`

**Performance Test Failures:**
- Network latency may affect results
- Test against a closer endpoint if available
- Check if the API is under load

### 8. Next Steps

Once testing is working:
1. Integrate into your CI/CD pipeline
2. Set up automated monitoring
3. Create custom test scenarios
4. Generate performance baselines

## Support

- 📖 Full Documentation: See README.md
- 🐛 Issues: Check the HTML reports for detailed error information
- 💼 Enterprise Support: enterprise@odin-protocol.com
