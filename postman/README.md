# ODIN Protocol Postman Plugin

![ODIN Protocol](https://img.shields.io/badge/ODIN%20Protocol-v1.1.0-blue)
![Postman](https://img.shields.io/badge/Postman-Compatible-orange)
![API](https://img.shields.io/badge/API-Ready-green)

A comprehensive Postman collection for testing and integrating with the ODIN Protocol HEL Rule System - the world's first standardized AI-to-AI communication infrastructure.

## 🚀 Quick Start

### 1. Import Collection & Environment

1. **Download the files:**
   - `ODIN_Protocol_Collection.json` - Main API collection
   - `ODIN_Protocol_Environment.json` - Environment variables

2. **Import into Postman:**
   - Open Postman
   - Click "Import" → Select both JSON files
   - Choose "ODIN Protocol Environment" from environment dropdown

3. **Configure Authentication:**
   - Set your `odin_api_token` in the environment variables
   - Update `odin_base_url` if using a different endpoint

### 2. Test Your First Request

```bash
# Start with the Health Check
GET {{base_url}}/{{api_version}}/health/communication

# Then try HEL Rule Evaluation
POST {{base_url}}/{{api_version}}/hel/evaluate
```

## 🧠 What's Included

### 8 Core Capability Test Suites

#### 1. **🧠 HEL Rule Engine**
- **Evaluate Rule Set** - Test real-time decision making (<50ms)
- **Get Rule Set Status** - Monitor rule performance
- **Create Custom Rule** - Define custom validation logic

#### 2. **🔧 Self-Healing Communication** 
- **Test Communication Health** - Check system status
- **Trigger Auto-Repair** - Test automatic failure recovery

#### 3. **📐 Standardized AI-to-AI Dialogue**
- **Send ODIN Message** - Use universal .odin format
- **Validate Message Format** - Ensure compliance

#### 4. **🎯 Precision Control**
- **Apply Logical Operators** - Test 100+ logical operators
- **Complex Routing Logic** - Advanced message routing

#### 5. **🚨 Error Prevention & Detection**
- **Run Anomaly Detection** - Proactive issue identification
- **Get Error Analytics** - Comprehensive error insights

#### 6. **📊 Structured Logging & Analytics**
- **Query System Logs** - Advanced log filtering
- **Get Performance Metrics** - Real-time analytics

#### 7. **🌐 Cross-Model Interoperability**
- **Test Multi-Model Communication** - GPT, Claude, Gemini integration
- **Get Model Compatibility Matrix** - Provider compatibility

#### 8. **🛡️ Enterprise Security**
- **Validate Security Compliance** - SOC2, GDPR, HIPAA checks
- **Test Encryption Status** - End-to-end encryption validation

### 📈 Performance Benchmarks
- **Response Time Validation** - Verify sub-50ms performance
- **Throughput Testing** - Validate 1000+ messages/second
- **Reliability Testing** - Confirm 99.9% uptime

## 🔧 Advanced Features

### Automatic Test Validation
Every request includes automatic validation:
- ✅ Response time under 50ms
- ✅ ODIN protocol headers present
- ✅ JSON structure validation
- ✅ Trace ID tracking

### Environment Variables
```json
{
  "odin_base_url": "https://api.odin-protocol.com",
  "odin_api_token": "your-token-here",
  "environment": "production",
  "security_token": "your-security-token",
  "rule_set_id": "default-rule-set"
}
```

### Pre-request Scripts
- Auto-generates trace IDs for request tracking
- Sets timestamps for time-sensitive operations
- Logs request details for debugging

### Post-response Tests
- Validates ODIN Protocol compliance
- Checks performance requirements
- Logs response metrics

## 📊 Real-World Use Cases

### Financial Services Integration
```javascript
// Test high-priority financial message routing
{
  "message": {
    "priority": "high",
    "content": "Execute trade: BUY 1000 AAPL",
    "compliance_required": true
  }
}
```

### Healthcare Data Processing
```javascript
// HIPAA-compliant patient data handling
{
  "security_level": "hipaa",
  "data_type": "patient_record",
  "encryption": "required"
}
```

### Manufacturing Automation
```javascript
// Supply chain coordination
{
  "workflow": "supply_chain_optimization",
  "priority": "urgent",
  "automation_level": "full"
}
```

## 🎯 Performance Validation

The collection automatically validates key performance metrics:

- **Sub-50ms Response Times** ⚡
- **99.9% Reliability** 🛡️
- **Enterprise Security** 🔒
- **Cross-Model Compatibility** 🌐

## 🔐 Security Testing

### Compliance Validation
- **SOC2 Type II** certification checks
- **GDPR** data handling validation
- **HIPAA** healthcare compliance
- **End-to-end encryption** verification

### Authentication Methods
- Bearer token authentication
- API key validation
- Security token for compliance checks
- Role-based access control testing

## 📈 Analytics & Monitoring

### Built-in Monitoring
- Real-time performance metrics
- Error rate tracking
- Throughput analysis
- Anomaly detection alerts

### Reporting Features
- Comprehensive test reports
- Performance benchmarking
- Compliance audit trails
- Usage analytics

## 🚀 Integration Examples

### Enterprise Workflow
```bash
1. Health Check → Communication Status
2. Rule Evaluation → Business Logic Processing  
3. Multi-Model Coordination → Cross-AI Communication
4. Performance Validation → SLA Compliance
5. Security Audit → Compliance Verification
```

### Development Workflow
```bash
1. Message Format Validation
2. Custom Rule Creation
3. Logic Operator Testing
4. Error Scenario Simulation
5. Performance Benchmarking
```

## 🔧 Customization

### Adding Custom Tests
1. Duplicate existing request
2. Modify endpoint and payload
3. Update test validation scripts
4. Configure environment variables

### Environment Setup
- **Development**: `dev.odin-protocol.com`
- **Staging**: `staging.odin-protocol.com`  
- **Production**: `api.odin-protocol.com`

## 📚 Documentation Links

- 📖 [Full API Documentation](https://docs.odin-protocol.com)
- 🧠 [Interactive Demo](https://huggingface.co/spaces/odin-protocol/demo)
- 🐙 [GitHub Repository](https://github.com/odin-protocol/python-sdk)
- 💼 [Enterprise Contact](mailto:enterprise@odin-protocol.com)

## 🆘 Support

- **Technical Issues**: Create issue in GitHub repository
- **Enterprise Support**: enterprise@odin-protocol.com
- **Community**: Join our Discord/Slack channels
- **Documentation**: docs.odin-protocol.com

## 📄 License

This Postman collection is provided under the same license as the ODIN Protocol SDK.

---

**The future of AI coordination starts here. Test it with Postman. 🚀**

*Solving the $50B coordination problem, one API call at a time.*
