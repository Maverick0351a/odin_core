#!/usr/bin/env python3
"""
ODIN Protocol Buffer Compiler
Generates Python SDK from .proto files
"""

import subprocess
import sys
import os
from pathlib import Path

def ensure_protoc_installed():
    """Check if protoc is installed and available"""
    try:
        result = subprocess.run(['protoc', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Found {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ protoc not found. Please install Protocol Buffers compiler.")
        print("   Windows: Download from https://github.com/protocolbuffers/protobuf/releases")
        print("   Or use: conda install protobuf")
        return False

def create_odin_sdk_directory():
    """Create the odin_sdk directory if it doesn't exist"""
    sdk_dir = Path("odin_sdk")
    sdk_dir.mkdir(exist_ok=True)
    
    # Create __init__.py to make it a Python package
    init_file = sdk_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""ODIN Protocol SDK - Generated from Protocol Buffers"""\n')
    
    return sdk_dir

def compile_proto_files():
    """Compile .proto files to Python SDK"""
    if not ensure_protoc_installed():
        return False
    
    sdk_dir = create_odin_sdk_directory()
    
    # Find all .proto files
    proto_files = list(Path(".").glob("*.proto"))
    
    if not proto_files:
        print("❌ No .proto files found in current directory")
        return False
    
    print(f"📦 Compiling {len(proto_files)} proto file(s)...")
    
    for proto_file in proto_files:
        print(f"🔨 Compiling {proto_file}...")
        
        try:
            # Run protoc to generate Python code
            subprocess.run([
                'protoc',
                f'--python_out={sdk_dir}',
                '--pyi_out={sdk_dir}',  # Generate type stubs
                str(proto_file)
            ], check=True)
            
            print(f"✅ Generated {sdk_dir}/{proto_file.stem}_pb2.py")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to compile {proto_file}: {e}")
            return False
    
    # Generate enhanced SDK wrapper
    generate_enhanced_sdk(sdk_dir)
    
    print("🎉 ODIN SDK compilation complete!")
    return True

def generate_enhanced_sdk(sdk_dir: Path):
    """Generate enhanced SDK wrapper with type hints and utilities"""
    
    enhanced_sdk = f'''"""
ODIN Protocol SDK - Enhanced Wrapper
Auto-generated enhanced SDK with type hints and utilities
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import time

# Import generated protobuf classes
try:
    from .odin_pb2 import (
        OdinMessage, 
        HealingMetadata, 
        ConversationContext, 
        PerformanceMetrics,
        OdinMessageBatch
    )
except ImportError:
    # Fallback for direct execution
    from odin_pb2 import (
        OdinMessage, 
        HealingMetadata, 
        ConversationContext, 
        PerformanceMetrics,
        OdinMessageBatch
    )

class OdinMessageBuilder:
    """Builder class for creating ODIN messages with type safety"""
    
    def __init__(self):
        self.message = OdinMessage()
        self.message.timestamp = int(time.time() * 1000)  # Default to current time
    
    def set_ids(self, trace_id: str, session_id: str, 
                sender_id: str, receiver_id: str) -> 'OdinMessageBuilder':
        """Set core identification fields"""
        self.message.trace_id = trace_id
        self.message.session_id = session_id
        self.message.sender_id = sender_id
        self.message.receiver_id = receiver_id
        return self
    
    def set_role(self, role: str) -> 'OdinMessageBuilder':
        """Set the role (assistant, tool, user, mediator)"""
        self.message.role = role
        return self
    
    def set_content(self, raw_output: str, healed_output: Optional[str] = None) -> 'OdinMessageBuilder':
        """Set message content"""
        self.message.raw_output = raw_output
        self.message.healed_output = healed_output or raw_output
        return self
    
    def set_semantic_drift(self, score: float) -> 'OdinMessageBuilder':
        """Set semantic drift score (0.0-1.0)"""
        self.message.semantic_drift_score = max(0.0, min(1.0, score))
        return self
    
    def set_healing_metadata(self, method: str, confidence: float, 
                           source_doc_id: str = "", notes: str = "",
                           applied_rules: List[str] = None,
                           iteration_count: int = 1) -> 'OdinMessageBuilder':
        """Set healing metadata"""
        self.message.healing_metadata.method = method
        self.message.healing_metadata.confidence = max(0.0, min(1.0, confidence))
        self.message.healing_metadata.source_document_id = source_doc_id
        self.message.healing_metadata.notes = notes
        self.message.healing_metadata.iteration_count = iteration_count
        
        if applied_rules:
            self.message.healing_metadata.applied_rules.extend(applied_rules)
        
        return self
    
    def set_conversation_context(self, conversation_id: str, turn_number: int,
                               conversation_type: str = "dialogue",
                               topic: str = "", key_themes: List[str] = None,
                               emotional_state: str = "neutral") -> 'OdinMessageBuilder':
        """Set conversation context"""
        self.message.context.conversation_id = conversation_id
        self.message.context.turn_number = turn_number
        self.message.context.conversation_type = conversation_type
        self.message.context.topic = topic
        self.message.context.emotional_state = emotional_state
        
        if key_themes:
            self.message.context.key_themes.extend(key_themes)
        
        return self
    
    def set_performance_metrics(self, response_time_ms: int = 0,
                              coherence_score: float = 0.0,
                              relevance_score: float = 0.0,
                              token_count: int = 0,
                              complexity_score: float = 0.0,
                              model_version: str = "") -> 'OdinMessageBuilder':
        """Set performance metrics"""
        self.message.metrics.response_time_ms = response_time_ms
        self.message.metrics.coherence_score = max(0.0, min(1.0, coherence_score))
        self.message.metrics.relevance_score = max(0.0, min(1.0, relevance_score))
        self.message.metrics.token_count = token_count
        self.message.metrics.complexity_score = max(0.0, min(1.0, complexity_score))
        self.message.metrics.model_version = model_version
        return self
    
    def build(self) -> OdinMessage:
        """Build and return the ODIN message"""
        return self.message

class OdinSDK:
    """Main SDK class for ODIN Protocol operations"""
    
    @staticmethod
    def create_message() -> OdinMessageBuilder:
        """Create a new ODIN message builder"""
        return OdinMessageBuilder()
    
    @staticmethod
    def serialize_message(message: OdinMessage) -> bytes:
        """Serialize ODIN message to binary format"""
        return message.SerializeToString()
    
    @staticmethod
    def deserialize_message(data: bytes) -> OdinMessage:
        """Deserialize binary data to ODIN message"""
        message = OdinMessage()
        message.ParseFromString(data)
        return message
    
    @staticmethod
    def save_message(message: OdinMessage, filepath: str) -> bool:
        """Save ODIN message to file"""
        try:
            with open(filepath, 'wb') as f:
                f.write(OdinSDK.serialize_message(message))
            return True
        except Exception as e:
            print(f"Error saving message: {{e}}")
            return False
    
    @staticmethod
    def load_message(filepath: str) -> Optional[OdinMessage]:
        """Load ODIN message from file"""
        try:
            with open(filepath, 'rb') as f:
                return OdinSDK.deserialize_message(f.read())
        except Exception as e:
            print(f"Error loading message: {{e}}")
            return None
    
    @staticmethod
    def create_batch(messages: List[OdinMessage], batch_id: str = "") -> OdinMessageBatch:
        """Create a batch of ODIN messages"""
        batch = OdinMessageBatch()
        batch.messages.extend(messages)
        batch.batch_id = batch_id or f"batch_{{int(time.time())}}"
        batch.batch_timestamp = int(time.time() * 1000)
        return batch

# Export main classes
__all__ = [
    'OdinMessage', 'HealingMetadata', 'ConversationContext', 
    'PerformanceMetrics', 'OdinMessageBatch',
    'OdinMessageBuilder', 'OdinSDK'
]
'''
    
    # Write the enhanced SDK
    enhanced_file = sdk_dir / "enhanced.py"
    enhanced_file.write_text(enhanced_sdk)
    
    print(f"✅ Generated enhanced SDK: {enhanced_file}")

if __name__ == "__main__":
    success = compile_proto_files()
    sys.exit(0 if success else 1)
