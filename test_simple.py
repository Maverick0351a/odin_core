#!/usr/bin/env python3
"""
Simple ODIN Protocol SDK Test - Quick Launch Validation
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test basic imports"""
    print("🔍 Testing imports...")
    try:
        from odin_sdk import OdinClient
        from odin_sdk.plugins import PluginManager
        from odin_sdk.odin_pb2 import OdinMessage
        print("✅ SDK imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_protobuf():
    """Test protocol buffer functionality"""
    print("🔍 Testing Protocol Buffers...")
    try:
        from odin_sdk.odin_pb2 import OdinMessage
        
        # Create message
        msg = OdinMessage()
        msg.trace_id = "test-123"
        msg.session_id = "session-456"
        msg.sender_id = "sender"
        msg.receiver_id = "receiver"
        msg.raw_output = "Hello ODIN!"
        msg.healed_output = "Hello ODIN!"
        msg.role = "user"
        msg.timestamp = int(time.time())
        
        # Test serialization
        data = msg.SerializeToString()
        
        # Test deserialization
        msg2 = OdinMessage()
        msg2.ParseFromString(data)
        
        assert msg2.trace_id == msg.trace_id
        assert msg2.raw_output == msg.raw_output
        
        print(f"✅ Protobuf works - {len(data)} bytes serialized")
        return True
    except Exception as e:
        print(f"❌ Protobuf failed: {e}")
        return False

def test_sdk_client():
    """Test SDK client creation"""
    print("🔍 Testing SDK Client...")
    try:
        from odin_sdk import OdinClient
        
        client = OdinClient(api_key="test-key", base_url="http://test")
        
        # Test message builder
        msg = client.create_message().set_content("test").build()
        assert msg.raw_output == "test"
        
        print("✅ SDK Client works")
        return True
    except Exception as e:
        print(f"❌ SDK Client failed: {e}")
        return False

def test_plugin_manager():
    """Test plugin manager"""
    print("🔍 Testing Plugin Manager...")
    try:
        from odin_sdk.plugins import PluginManager
        
        manager = PluginManager()
        assert len(manager.plugins) == 0
        
        print("✅ Plugin Manager works")
        return True
    except Exception as e:
        print(f"❌ Plugin Manager failed: {e}")
        return False

def test_rule_engine():
    """Test rule engine"""
    print("🔍 Testing Rule Engine...")
    try:
        from rules_engine import RuleEngine
        
        engine = RuleEngine()
        context = {"test": "value"}
        results = engine.evaluate_rules(context)
        
        print(f"✅ Rule Engine works - {len(results)} results")
        return True
    except Exception as e:
        print(f"❌ Rule Engine failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ODIN Protocol Simple Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_protobuf,
        test_sdk_client,
        test_plugin_manager,
        test_rule_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"   Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - READY FOR LAUNCH! 🚀")
        return True
    else:
        print("⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
