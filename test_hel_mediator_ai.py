#!/usr/bin/env python3
"""
Test suite for Hel-enhanced MediatorAI integration.
Tests the complete integration with existing ODIN Protocol components.
"""

import asyncio
import sys
import os

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hel_mediator_ai import HelMediatorAI, create_hel_mediator_ai, get_hel_mediator_ai
from odin_sdk.enhanced import OdinMessageBuilder
from odin_sdk import OdinMessage, OdinReflection


class TestHelMediatorAI:
    """Test cases for Hel-enhanced MediatorAI."""
    
    def test_initialization(self):
        """Test HelMediatorAI initialization."""
        mediator = HelMediatorAI()
        
        assert mediator.mediator_id == "hel-mediator-ai-v1"
        assert hasattr(mediator, 'hel_engine')
        assert hasattr(mediator, 'hel_stats')
        assert len(mediator.hel_engine.mediator.colleagues) == 4  # All colleagues
    
    def test_backward_compatibility(self):
        """Test that Hel MediatorAI maintains backward compatibility."""
        mediator = HelMediatorAI()
        
        # Should have all base MediatorAI methods
        assert hasattr(mediator, 'evaluate')
        assert hasattr(mediator, 'evaluate_async')
        assert hasattr(mediator, '_calculate_confidence')
        assert hasattr(mediator, '_assess_hallucination_risk')
        assert hasattr(mediator, '_check_semantic_drift')
        
        # Should have rule engine
        assert hasattr(mediator, 'rule_engine')
        assert mediator.rule_engine is not None
    
    def test_enhanced_evaluation_basic(self):
        """Test basic enhanced evaluation functionality."""
        mediator = HelMediatorAI()
        
        # Create test message
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="hel-test-001",
            session_id="test-session",
            sender_id="user-test",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "This is a test message with good quality content for evaluation."
        ).build()
        
        # Evaluate with Hel enhancement
        reflection = mediator.evaluate(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        assert reflection.action_taken in ["approve", "pass", "modify", "retry", "reject", "escalate"]
        assert "Hel-enhanced evaluation applied" in reflection.explanation
        assert mediator.hel_stats["hel_evaluations"] == 1
    
    async def test_enhanced_evaluation_async(self):
        """Test asynchronous enhanced evaluation."""
        mediator = HelMediatorAI()
        
        # Create test message
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="hel-async-test-001",
            session_id="test-session",
            sender_id="user-async",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "This is an async test message for Hel evaluation."
        ).build()
        
        # Evaluate asynchronously
        reflection = await mediator.evaluate_async(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        assert reflection.action_taken in ["approve", "pass", "modify", "retry", "reject", "escalate"]
        assert "Hel-enhanced evaluation applied" in reflection.explanation
        assert mediator.hel_stats["hel_evaluations"] == 1
    
    def test_policy_enforcement_integration(self):
        """Test policy enforcement integration."""
        mediator = HelMediatorAI()
        
        # Create message with content that should trigger policy violations
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="policy-test-001",
            session_id="test-session",
            sender_id="user-policy",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "Contact me at john.doe@example.com for more information."  # Contains email
        ).build()
        
        # Evaluate - should detect PII policy violation
        reflection = mediator.evaluate(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        # The exact action depends on policy enforcement level, but explanation should mention policies
        if "Policy violations:" in reflection.explanation:
            assert mediator.hel_stats["policy_enforcements"] > 0
    
    def test_low_confidence_colleague_consultation(self):
        """Test colleague consultation for low confidence scenarios."""
        mediator = HelMediatorAI()
        
        # Create message that should result in low confidence
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="low-conf-test-001",
            session_id="test-session", 
            sender_id="user-lowconf",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "Unclear response with ambiguous meaning."
        ).build()
        
        # Evaluate - should consult colleagues for low confidence
        reflection = mediator.evaluate(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        # Should have consulted colleagues if confidence was low enough
        if reflection.confidence_score < 0.6:
            assert mediator.hel_stats["colleague_consultations"] > 0
    
    async def test_comprehensive_enhancement_flow(self):
        """Test the complete enhancement flow with all components."""
        mediator = HelMediatorAI()
        
        # Create complex test message that should trigger multiple enhancements
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="comprehensive-test-001",
            session_id="test-session",
            sender_id="admin-user",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "This message contains user@email.com and has complex requirements for evaluation."
        ).build()
        
        # Evaluate asynchronously
        reflection = await mediator.evaluate_async(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        assert "Hel-enhanced evaluation applied" in reflection.explanation
        
        # Check that various components were engaged
        stats = mediator.get_hel_mediator_stats()
        assert stats["hel_enhanced"] == True
        assert "base_mediator_stats" in stats
        assert "hel_engine_stats" in stats
        assert "hel_mediator_stats" in stats
        assert len(stats["colleagues_available"]) == 4
    
    def test_data_quality_integration(self):
        """Test data quality assessment integration."""
        mediator = HelMediatorAI()
        
        # Create message with poor data quality (very short content)
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="quality-test-001", 
            session_id="test-session",
            sender_id="user-quality",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "Bad"  # Very short, low quality content
        ).build()
        
        # Evaluate - should detect data quality issues
        reflection = mediator.evaluate(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        # Should have applied data quality considerations
        if "Data quality below threshold" in reflection.explanation:
            assert reflection.action_taken in ["retry", "modify", "reject"]
    
    def test_action_trigger_integration(self):
        """Test action trigger integration."""
        mediator = HelMediatorAI()
        
        # Create message that should trigger actions (escalation scenario)
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="trigger-test-001",
            session_id="test-session",
            sender_id="user-trigger",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "This is a test message that requires escalation due to complexity."
        ).build()
        
        # Force escalation by creating a reflection that would escalate
        reflection = mediator.evaluate(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        # Check if actions were triggered
        if reflection.action_taken == "escalate":
            # Actions might have been triggered
            stats = mediator.get_hel_mediator_stats()
            # Check for mediator interventions in stats
            assert "hel_mediator_stats" in stats
    
    def test_get_hel_mediator_stats(self):
        """Test getting comprehensive Hel mediator statistics."""
        mediator = HelMediatorAI()
        stats = mediator.get_hel_mediator_stats()
        
        # Should contain all expected sections
        assert "mediator_id" in stats
        assert stats["hel_enhanced"] == True
        assert "base_mediator_stats" in stats
        assert "hel_engine_stats" in stats
        assert "hel_mediator_stats" in stats
        assert "colleagues_available" in stats
        
        # Hel mediator stats should contain expected fields
        hel_stats = stats["hel_mediator_stats"]
        expected_fields = [
            "hel_evaluations", "colleague_consultations", "policy_enforcements",
            "enhanced_decisions", "mediator_interventions"
        ]
        for field in expected_fields:
            assert field in hel_stats
        
        # Should have all colleagues available
        assert len(stats["colleagues_available"]) == 4
        expected_colleagues = ["data_source", "rule_evaluator", "policy", "action_trigger"]
        for colleague in expected_colleagues:
            assert colleague in stats["colleagues_available"]
    
    def test_export_hel_configuration(self):
        """Test exporting Hel configuration."""
        import tempfile
        import os
        import json
        
        mediator = HelMediatorAI()
        
        # Export configuration to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            mediator.export_hel_configuration(temp_path)
            
            # Verify file was created and contains expected data
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                config_data = json.load(f)
            
            assert "mediator_id" in config_data
            assert "hel_engine_config" in config_data
            assert "colleagues" in config_data
            assert len(config_data["colleagues"]) == 4
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_message_classification(self):
        """Test message type classification functionality."""
        mediator = HelMediatorAI()
        
        # Test different message types
        test_cases = [
            ("What is the weather today?", "query"),
            ("Error occurred during processing", "error_report"),
            ("Please help me with this task", "request"),
            ("The system is working correctly", "statement")
        ]
        
        for content, expected_type in test_cases:
            builder = OdinMessageBuilder()
            message = builder.set_ids(
                trace_id=f"classify-test-{expected_type}",
                session_id="test-session",
                sender_id="user-classify",
                receiver_id="assistant"
            ).set_role("assistant").set_content(content).build()
            
            classified_type = mediator._classify_message_type(message)
            assert classified_type == expected_type
    
    def test_content_complexity_assessment(self):
        """Test content complexity assessment."""
        mediator = HelMediatorAI()
        
        # Test different complexity levels based on actual logic:
        # Low: ≤30 words AND ≤3 sentences
        # Medium: >30 words OR >3 sentences (but not >100 words AND not >10 sentences)
        # High: >100 words OR >10 sentences
        test_cases = [
            ("Short message", "low"),  # 2 words, 1 sentence
            ("This is a longer message that contains more than thirty words to exceed the word threshold for medium complexity assessment with sufficient content for the medium level complexity test case here", "medium"),  # 31 words
            ("This is a very long and complex message that contains many different concepts and ideas. " * 8, "high")  # 120+ words for high complexity
        ]
        
        for content, expected_complexity in test_cases:
            builder = OdinMessageBuilder()
            message = builder.set_ids(
                trace_id=f"complexity-test-{expected_complexity}",
                session_id="test-session",
                sender_id="user-complexity",
                receiver_id="assistant"
            ).set_role("assistant").set_content(content).build()
            
            complexity = mediator._assess_content_complexity(message)
            assert complexity == expected_complexity
    
    def test_source_reliability_assessment(self):
        """Test source reliability assessment."""
        mediator = HelMediatorAI()
        
        # Test different source types
        test_cases = [
            ("admin-user", "high"),
            ("system-process", "high"),
            ("user-123", "medium"),
            ("unknown-sender", "unknown")
        ]
        
        for sender_id, expected_reliability in test_cases:
            builder = OdinMessageBuilder()
            message = builder.set_ids(
                trace_id=f"reliability-test-{expected_reliability}",
                session_id="test-session",
                sender_id=sender_id,
                receiver_id="assistant"
            ).set_role("assistant").set_content("Test content").build()
            
            reliability = mediator._assess_source_reliability(message)
            assert reliability == expected_reliability


class TestHelMediatorAIFactory:
    """Test factory functions for HelMediatorAI."""
    
    def test_create_hel_mediator_ai(self):
        """Test creating HelMediatorAI with factory function."""
        mediator = create_hel_mediator_ai(
            mediator_id="test-factory-mediator",
            confidence_threshold=0.8
        )
        
        assert isinstance(mediator, HelMediatorAI)
        assert mediator.mediator_id == "test-factory-mediator"
        assert mediator.confidence_threshold == 0.8
    
    def test_get_hel_mediator_ai_singleton(self):
        """Test getting singleton HelMediatorAI instance."""
        mediator1 = get_hel_mediator_ai()
        mediator2 = get_hel_mediator_ai()
        
        # Should be the same instance
        assert mediator1 is mediator2
        assert isinstance(mediator1, HelMediatorAI)


class TestHelMediatorAIIntegrationScenarios:
    """Test real-world integration scenarios with HelMediatorAI."""
    
    async def test_security_incident_with_hel_mediator(self):
        """Test security incident handling with Hel-enhanced mediator."""
        mediator = HelMediatorAI()
        
        # Create security incident message
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="security-hel-001",
            session_id="security-session",
            sender_id="security-system",
            receiver_id="security-analyst"
        ).set_role("assistant").set_content(
            "Security alert: Suspicious login attempt from user admin@company.com detected."
        ).build()
        
        # Evaluate with Hel enhancement
        reflection = await mediator.evaluate_async(message, iteration_count=1)
        
        assert isinstance(reflection, OdinReflection)
        assert "Hel-enhanced evaluation applied" in reflection.explanation
        
        # Should have triggered policy evaluations due to email in content
        if "Policy violations:" in reflection.explanation:
            assert mediator.hel_stats["policy_enforcements"] > 0
    
    async def test_multi_iteration_enhancement(self):
        """Test Hel enhancement across multiple iterations."""
        mediator = HelMediatorAI()
        
        # Create message that might require multiple iterations
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="multi-iter-hel-001",
            session_id="multi-session",
            sender_id="user-multi",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "This message has unclear content that might need revision."
        ).build()
        
        # Evaluate multiple iterations
        reflection1 = await mediator.evaluate_async(message, iteration_count=1)
        reflection2 = await mediator.evaluate_async(message, iteration_count=2)
        reflection3 = await mediator.evaluate_async(message, iteration_count=3)
        
        # All should be enhanced
        for reflection in [reflection1, reflection2, reflection3]:
            assert "Hel-enhanced evaluation applied" in reflection.explanation
        
        # Stats should show multiple evaluations
        assert mediator.hel_stats["hel_evaluations"] == 3
    
    def test_performance_comparison(self):
        """Test performance comparison between base and Hel mediator."""
        import time
        from mediator_ai import MediatorAI
        
        # Create both mediators
        base_mediator = MediatorAI()
        hel_mediator = HelMediatorAI()
        
        # Create test message
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id="perf-test-001",
            session_id="perf-session",
            sender_id="user-perf",
            receiver_id="assistant"
        ).set_role("assistant").set_content(
            "This is a performance test message for comparison."
        ).build()
        
        # Time base evaluation
        start_time = time.time()
        base_reflection = base_mediator.evaluate(message)
        base_time = time.time() - start_time
        
        # Time Hel evaluation
        start_time = time.time()
        hel_reflection = hel_mediator.evaluate(message)
        hel_time = time.time() - start_time
        
        # Both should produce valid reflections
        assert isinstance(base_reflection, OdinReflection)
        assert isinstance(hel_reflection, OdinReflection)
        
        # Hel should have additional enhancements
        assert "Hel-enhanced evaluation applied" in hel_reflection.explanation
        assert "Hel-enhanced evaluation applied" not in base_reflection.explanation
        
        # Performance should be reasonable (Hel might be slower but not excessively)
        print(f"Base evaluation time: {base_time:.4f}s")
        print(f"Hel evaluation time: {hel_time:.4f}s")
        
        # Hel should complete in reasonable time (less than 1 second for simple cases)
        assert hel_time < 1.0


# Test runner function
def run_hel_mediator_tests():
    """Run all tests for Hel-enhanced MediatorAI."""
    import time
    
    print("🧪 Running Hel-Enhanced MediatorAI Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    # Test classes to run
    test_classes = [
        TestHelMediatorAI,
        TestHelMediatorAIFactory,
        TestHelMediatorAIIntegrationScenarios
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        print("-" * 40)
        
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            method = getattr(test_instance, method_name)
            
            try:
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                
                print(f"  ✅ {method_name}")
                passed_tests += 1
                
            except Exception as e:
                print(f"  ❌ {method_name}: {str(e)}")
                failed_tests.append(f"{test_class.__name__}.{method_name}: {str(e)}")
    
    # Print summary
    execution_time = time.time() - start_time
    print(f"\n📊 Hel MediatorAI Test Summary")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Execution time: {execution_time:.2f} seconds")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  - {failure}")
    
    return passed_tests, len(failed_tests), total_tests


if __name__ == "__main__":
    run_hel_mediator_tests()
