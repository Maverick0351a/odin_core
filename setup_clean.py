"""
ODIN Protocol Python SDK Setup
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    """Get version from __init__.py"""
    version_file = os.path.join(os.path.dirname(__file__), 'odin_sdk', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return "1.1.0"  # fallback version

version = "1.1.0"

# Read long description from README
long_description = """
# ODIN Protocol - Heuristic-Empowered Logic Rule System

The definitive Python SDK for the ODIN Protocol HEL Engine - the world's first standardized AI-to-AI communication infrastructure with advanced rule-based decision making.

## Quick Start

```python
from odin_sdk import OdinClient
from hel_mediator_ai import create_hel_mediator_ai

# Initialize HEL-powered system
mediator = create_hel_mediator_ai()
client = OdinClient()

# Create AI-to-AI message
message = client.create_message()
result = mediator.evaluate_message(message)
```

## Features

- Real-Time Decision-Making (sub-50ms response times)
- Self-Healing Communication
- Standardized AI-to-AI Dialogue
- Cross-Model Interoperability
- Enterprise-Level Security

For documentation, visit: https://docs.odin-protocol.com
"""

setup(
    name="odin_protocol",
    version=version,
    author="Travis Johnson",
    author_email="travjohnson831@gmail.com",
    description="ODIN Protocol - Standardized AI-to-AI Communication Infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Maverick0351a/odin_core",
    project_urls={
        "Bug Tracker": "https://github.com/Maverick0351a/odin_core/issues",
        "Documentation": "https://docs.odin-protocol.com",
        "Source Code": "https://github.com/Maverick0351a/odin_core",
        "Billing Support": "mailto:travjohnson831@gmail.com",
        "Enterprise Sales": "mailto:odinprotocol@outlook.com"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pyyaml>=5.4.0",
        "protobuf>=3.19.0",
        "typing-extensions>=4.0.0",
        "pydantic>=1.8.0",
        "flask>=2.0.0",
        "stripe>=5.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.910"
        ],
        "enterprise": [
            "redis>=4.0.0",
            "celery>=5.0.0",
            "sqlalchemy>=1.4.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "odin=main:main",
            "hel=hel_mediator_ai:main"
        ]
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.proto", "*.md", "*.txt"]
    },
    keywords="ai artificial-intelligence communication protocol hel mediator rule-engine automation",
    zip_safe=False,
)
