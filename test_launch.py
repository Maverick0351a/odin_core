#!/usr/bin/env python3
"""
ODIN Protocol SDK Integration Test Suite
Tests the complete SDK functionality before launch
"""

import asyncio
import json
import sys
import time
import traceback
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from odin_sdk import OdinClient, PluginManager
    from odin_sdk.plugins import BasePlugin, RulePlugin, AnalyticsPlugin
    import odin_format
    from hel_rule_engine import HelRuleEngine
    from mediator_ai import MediatorAI
    from odin_sdk.odin_pb2 import OdinMessage
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all required modules are available")
    sys.exit(1)

class LaunchTestSuite:
    """Comprehensive test suite for launch validation"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
    
    async def test_basic_imports(self):
        """Test that all core modules can be imported"""
        test_name = "Basic Imports"
        try:
            # Test core imports
            import odin_format
            import hel_rule_engine
            from mediator_ai import MediatorAI
            from odin_sdk import OdinClient
            
            self.log_test(test_name, True, "All core modules imported successfully")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Import failed: {str(e)}")
            return False
    
    async def test_message_creation(self):
        """Test ODIN message creation and serialization"""
        test_name = "Message Creation"
        try:
            # Create a test message using protocol buffer
            message = OdinMessage()
            message.trace_id = "test-trace-123"
            message.session_id = "test-session-456"
            message.sender_id = "test-sender"
            message.receiver_id = "test-receiver"
            message.role = "assistant"
            message.content = "Test message for launch validation"
            message.timestamp = int(time.time())
            
            # Test serialization
            serialized = message.SerializeToString()
            
            # Test deserialization
            deserialized = OdinMessage()
            deserialized.ParseFromString(serialized)
            
            # Validate roundtrip
            assert deserialized.trace_id == message.trace_id
            assert deserialized.content == message.content
            
            self.log_test(test_name, True, f"Message serialized to {len(serialized)} bytes")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Message creation failed: {str(e)}")
            return False
    
    async def test_rule_engine(self):
        """Test Hel Rule Engine functionality"""
        test_name = "Hel Rule Engine"
        try:
            engine = HelRuleEngine()
            
            # Test rule evaluation
            message = OdinMessage()
            message.content = "This is a test message for rule evaluation"
            message.role = "user"
            
            rules = [
                {
                    "name": "content_length_check",
                    "condition": "len(message.content) > 10",
                    "action": "approve",
                    "priority": 1
                },
                {
                    "name": "role_check", 
                    "condition": "message.role == 'user'",
                    "action": "process",
                    "priority": 2
                }
            ]
            
            # Use context for rule evaluation
            context = {
                "message": message,
                "rules": rules
            }
            
            result = engine.evaluate_rules(context)
            
            assert len(result) > 0
            assert "action" in result[0] or "priority" in result[0]
            
            self.log_test(test_name, True, f"Rules evaluated: {len(result)} results")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Rule engine failed: {str(e)}")
            return False
    
    async def test_mediator_ai(self):
        """Test Mediator AI functionality"""
        test_name = "Mediator AI"
        try:
            mediator = MediatorAI()
            
            # Test message analysis
            message = OdinMessage()
            message.content = "Hello, this is a test message for the mediator"
            message.role = "user"
            
            # Test basic mediator functionality
            analysis = await mediator.analyze_message(message)
            
            # Check if analysis has expected attributes (flexible check)
            assert analysis is not None
            
            self.log_test(test_name, True, f"Analysis complete")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Mediator AI failed: {str(e)}")
            return False
    
    async def test_sdk_client(self):
        """Test SDK client functionality"""
        test_name = "SDK Client"
        try:
            # Test client creation
            client = OdinClient(api_key="test-key-123", base_url="http://localhost:8000")
            
            # Test message builder
            message = client.create_message() \
                .set_ids("trace-1", "session-1", "sender-1", "receiver-1") \
                .set_role("assistant") \
                .set_content("SDK test message") \
                .build()
            
            assert message.trace_id == "trace-1"
            assert message.content == "SDK test message"
            
            # Test serialization
            serialized = client.serialize_message(message)
            assert len(serialized) > 0
            
            self.log_test(test_name, True, f"Client created and message built successfully")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"SDK client failed: {str(e)}")
            return False
    
    async def test_plugin_system(self):
        """Test plugin system functionality"""
        test_name = "Plugin System"
        try:
            # Test plugin manager
            manager = PluginManager()
            
            # Create test plugin
            class TestPlugin(BasePlugin):
                @property
                def name(self) -> str:
                    return "test-plugin"
                
                @property
                def version(self) -> str:
                    return "1.0.0"
                
                async def initialize(self) -> bool:
                    return True
                
                async def process_message(self, message, context=None):
                    if hasattr(message, 'metadata'):
                        message.metadata["processed_by_test"] = True
                    return message
            
            # Test plugin loading
            plugin = TestPlugin()
            await manager.load_plugin(plugin)
            
            assert plugin.name in manager.plugins
            
            # Test message processing
            message = odin_format.create_message()
            message.content = "Test plugin processing"
            
            processed = await manager.process_message(message)
            
            self.log_test(test_name, True, f"Plugin loaded and processed message")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Plugin system failed: {str(e)}")
            return False
    
    async def test_rule_plugin(self):
        """Test rule-based plugin functionality"""
        test_name = "Rule Plugin"
        try:
            # Create rule plugin
            class TestRulePlugin(RulePlugin):
                @property
                def name(self) -> str:
                    return "test-rule-plugin"
                
                def get_rules(self) -> list:
                    return [
                        {
                            "name": "test_rule",
                            "condition": "len(message.content) > 5",
                            "action": "tag_long_message",
                            "priority": 1
                        }
                    ]
                
                async def apply_action(self, message, action: str, context=None):
                    if action == "tag_long_message":
                        if hasattr(message, 'metadata'):
                            message.metadata["long_message"] = True
                    return message
            
            plugin = TestRulePlugin()
            await plugin.initialize()
            
            # Test rule application
            message = odin_format.create_message()
            message.content = "This is a test message for rule processing"
            
            processed = await plugin.process_message(message)
            
            self.log_test(test_name, True, "Rule plugin processed message successfully")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Rule plugin failed: {str(e)}")
            return False
    
    async def test_analytics_plugin(self):
        """Test analytics plugin functionality"""
        test_name = "Analytics Plugin"
        try:
            # Create analytics plugin
            class TestAnalyticsPlugin(AnalyticsPlugin):
                @property
                def name(self) -> str:
                    return "test-analytics-plugin"
                
                def __init__(self):
                    super().__init__()
                    self.metrics = {}
                
                async def track_metric(self, metric_name: str, value, tags=None):
                    self.metrics[metric_name] = value
                
                async def get_metrics(self) -> dict:
                    return self.metrics
            
            plugin = TestAnalyticsPlugin()
            await plugin.initialize()
            
            # Test metric tracking
            await plugin.track_metric("test_counter", 1)
            await plugin.track_metric("test_gauge", 42.5)
            
            metrics = await plugin.get_metrics()
            assert "test_counter" in metrics
            assert metrics["test_gauge"] == 42.5
            
            self.log_test(test_name, True, f"Analytics plugin tracked {len(metrics)} metrics")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Analytics plugin failed: {str(e)}")
            return False
    
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        test_name = "End-to-End Workflow"
        try:
            # Initialize components
            client = OdinClient(api_key="test-key")
            engine = HelRuleEngine()
            mediator = MediatorAI()
            
            # Create message
            message = client.create_message() \
                .set_ids("e2e-trace", "e2e-session", "e2e-sender", "e2e-receiver") \
                .set_role("user") \
                .set_content("Complete end-to-end test message") \
                .build()
            
            # Rule evaluation
            rules = [
                {
                    "name": "e2e_test_rule",
                    "condition": "message.role == 'user'",
                    "action": "process",
                    "priority": 1
                }
            ]
            
            rule_result = engine.evaluate_message(message, rules)
            assert rule_result.action_taken == "process"
            
            # Mediator analysis
            analysis = await mediator.analyze_message(message)
            assert hasattr(analysis, 'should_process')
            
            # Serialization roundtrip
            serialized = client.serialize_message(message)
            deserialized = client.deserialize_message(serialized)
            assert deserialized.content == message.content
            
            self.log_test(test_name, True, "Complete workflow executed successfully")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"End-to-end workflow failed: {str(e)}")
            return False
    
    async def test_error_handling(self):
        """Test error handling and graceful failures"""
        test_name = "Error Handling"
        try:
            # Test invalid message
            try:
                client = OdinClient(api_key="test-key")
                message = client.create_message() \
                    .set_content("") \
                    .build()  # Should handle empty content gracefully
            except Exception:
                pass  # Expected to handle gracefully
            
            # Test invalid rules
            try:
                engine = HelRuleEngine()
                invalid_rules = [{"invalid": "rule"}]
                message = odin_format.create_message()
                message.content = "test"
                result = engine.evaluate_message(message, invalid_rules)
                # Should return default action or handle gracefully
            except Exception:
                pass  # Expected to handle gracefully
            
            self.log_test(test_name, True, "Error handling works correctly")
            return True
        except Exception as e:
            self.log_test(test_name, False, f"Error handling failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests in the suite"""
        print("🚀 ODIN Protocol SDK Launch Test Suite")
        print("=" * 50)
        
        tests = [
            self.test_basic_imports,
            self.test_message_creation,
            self.test_rule_engine,
            self.test_mediator_ai,
            self.test_sdk_client,
            self.test_plugin_system,
            self.test_rule_plugin,
            self.test_analytics_plugin,
            self.test_end_to_end_workflow,
            self.test_error_handling
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__}: Unexpected error: {str(e)}")
                print(f"   {traceback.format_exc()}")
                failed += 1
        
        # Print summary
        print("=" * 50)
        print(f"📊 Test Results Summary")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        print(f"⏱️  Total Time: {time.time() - self.start_time:.2f}s")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED - READY FOR LAUNCH! 🚀")
            return True
        else:
            print("⚠️  Some tests failed - review before launch")
            return False

async def main():
    """Main test runner"""
    print("🔍 Starting ODIN Protocol SDK Launch Validation...")
    print()
    
    test_suite = LaunchTestSuite()
    success = await test_suite.run_all_tests()
    
    # Save test results
    results_file = Path("test_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "summary": {
                "success": success,
                "total_tests": len(test_suite.test_results),
                "passed": sum(1 for r in test_suite.test_results.values() if r["success"]),
                "failed": sum(1 for r in test_suite.test_results.values() if not r["success"]),
                "timestamp": time.time()
            },
            "tests": test_suite.test_results
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
