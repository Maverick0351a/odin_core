# ODIN Protocol - AI-to-AI Communication Infrastructure

[![PyPI version](https://badge.fury.io/py/odin-protocol.svg)](https://pypi.org/project/odin-protocol/)
[![VS Code Extension](https://img.shields.io/vscode-marketplace/v/travisjohnson.odin-protocol-hel)](https://marketplace.visualstudio.com/items?itemName=travisjohnson.odin-protocol-hel)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The definitive Python SDK for the ODIN Protocol HEL Engine - the world's first standardized AI-to-AI communication infrastructure with advanced rule-based decision making.

## 🚀 Quick Start

```bash
# Install from PyPI
pip install odin_protocol

# Or use VS Code Extension
# Search "ODIN Protocol HEL" in VS Code marketplace
```

```python
from hel_mediator_ai import create_hel_mediator_ai
from odin_sdk import OdinClient

# Initialize HEL-powered system
mediator = create_hel_mediator_ai()
client = OdinClient()

# Create AI-to-AI message
message = client.create_message(
    content="Analyze quarterly financial data",
    trace_id="trace-1",
    session_id="session-1"
)

# HEL system evaluates and routes automatically
result = mediator.evaluate(message)
print(f"Action: {result.action_taken}")
print(f"Confidence: {result.confidence_score}")
```

## 🧠 Core Features

- **Real-Time Decision-Making** - Sub-50ms response times
- **Self-Healing Communication** - Auto-detection and repair
- **Standardized AI-to-AI Dialogue** - Universal .odin format
- **Cross-Model Interoperability** - Works with GPT, Claude, Gemini
- **Enterprise Security** - SOC2, GDPR, HIPAA compliance
- **International Support** - Brazil, Germany, India, Japan markets

## 💰 Pricing

- **Individual**: $9/month (R$49 Brazil, €8 Germany, ₹747 India)
- **Enterprise**: $99/month with dedicated support
- **University**: Free with citation requirements

## 📚 Resources

- [Documentation](https://docs.odin-protocol.com)
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=travisjohnson.odin-protocol-hel)
- [PyPI Package](https://pypi.org/project/odin-protocol/)
- [Enterprise Sales](mailto:odinprotocol@outlook.com)
- [Billing Support](mailto:travjohnson831@gmail.com)

## 🏢 Company

Johnson Technologies (USA) - Leading AI Infrastructure Solutions

---

© 2024 Johnson Technologies. MIT License.
