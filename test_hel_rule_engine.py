#!/usr/bin/env python3
"""
Test suite for Hel Rule Engine with Mediator Pattern.
Tests the enhanced rule engine functionality and colleague interactions.
"""

import asyncio
import sys
import os

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hel_rule_engine import (
    HelRuleEngine, HelRuleMediator, DataSourceColleague, RuleEvaluatorColleague,
    BaseColleague, create_hel_rule_engine, get_hel_rule_engine
)
from rules_engine import Rule, RuleCondition, RuleAction, RuleOperator


class TestHelRuleMediator:
    """Test cases for HelRuleMediator class."""
    
    def test_mediator_initialization(self):
        """Test mediator initialization with default colleagues."""
        mediator = HelRuleMediator()
        
        assert mediator.mediator_id.startswith("hel-mediator-")
        assert len(mediator.colleagues) == 2  # DataSource and RuleEvaluator
        assert "data_source" in mediator.colleagues
        assert "rule_evaluator" in mediator.colleagues
    
    def test_colleague_registration(self):
        """Test registering new colleagues."""
        mediator = HelRuleMediator()
        
        # Create a custom colleague
        class TestColleague(BaseColleague):
            def __init__(self):
                super().__init__("test_colleague")
            
            async def handle_request(self, request_type: str, context: dict) -> dict:
                return {"test": "response", "request_type": request_type}
            
            def get_capabilities(self) -> list:
                return ["test_capability"]
        
        test_colleague = TestColleague()
        mediator.register_colleague(test_colleague)
        
        assert "test_colleague" in mediator.colleagues
        assert test_colleague.mediator == mediator
    
    async def test_coordinate_request(self):
        """Test request coordination between colleagues."""
        mediator = HelRuleMediator()
        
        # Test data source request
        context = {
            "content": "Test content for quality assessment",
            "data_source": "user_input"
        }
        
        result = await mediator.coordinate_request("validate_data_quality", context)
        
        assert "quality_score" in result
        assert "meets_threshold" in result
        assert result["source_type"] == "user_input"
    
    async def test_colleague_notification(self):
        """Test colleague notification handling."""
        mediator = HelRuleMediator()
        
        await mediator.handle_colleague_notification(
            "test_colleague", 
            "data_processed", 
            {"items": 5}
        )
        
        assert len(mediator.event_history) == 1
        event = mediator.event_history[0]
        assert event["colleague_id"] == "test_colleague"
        assert event["event_type"] == "data_processed"
        assert event["data"]["items"] == 5
    
    def test_get_colleague_capabilities(self):
        """Test getting colleague capabilities."""
        mediator = HelRuleMediator()
        capabilities = mediator.get_colleague_capabilities()
        
        assert "data_source" in capabilities
        assert "rule_evaluator" in capabilities
        assert "validate_data_quality" in capabilities["data_source"]
        assert "evaluate_with_strategy" in capabilities["rule_evaluator"]
    
    def test_mediator_stats(self):
        """Test mediator statistics."""
        mediator = HelRuleMediator()
        stats = mediator.get_mediator_stats()
        
        assert stats["colleagues_count"] == 2
        assert "data_source" in stats["colleagues"]
        assert "rule_evaluator" in stats["colleagues"]
        assert "capabilities" in stats


class TestDataSourceColleague:
    """Test cases for DataSourceColleague."""
    
    def test_initialization(self):
        """Test DataSourceColleague initialization."""
        colleague = DataSourceColleague()
        
        assert colleague.colleague_id == "data_source"
        assert colleague.data_quality_threshold == 0.8
        assert "user_input" in colleague.supported_sources
    
    def test_get_capabilities(self):
        """Test getting colleague capabilities."""
        colleague = DataSourceColleague()
        capabilities = colleague.get_capabilities()
        
        expected_capabilities = [
            "validate_data_quality",
            "assess_source_reliability", 
            "extract_metadata",
            "data_source_validation"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
    
    async def test_validate_data_quality_good(self):
        """Test data quality validation with good data."""
        colleague = DataSourceColleague()
        
        context = {
            "content": "This is high quality content with sufficient length",
            "data_source": "user_input"
        }
        
        result = await colleague.handle_request("validate_data_quality", context)
        
        assert result["quality_score"] == 0.9
        assert result["meets_threshold"] == True
        assert result["source_type"] == "user_input"
        assert len(result["issues"]) == 0
    
    async def test_validate_data_quality_poor(self):
        """Test data quality validation with poor data."""
        colleague = DataSourceColleague()
        
        context = {
            "content": "short",
            "data_source": "unknown_source"
        }
        
        result = await colleague.handle_request("validate_data_quality", context)
        
        assert result["quality_score"] == 0.3
        assert result["meets_threshold"] == False
        assert len(result["issues"]) > 0
    
    async def test_assess_source_reliability(self):
        """Test source reliability assessment."""
        colleague = DataSourceColleague()
        
        context = {
            "source_id": "trusted_api",
            "historical_accuracy": 0.85
        }
        
        result = await colleague.handle_request("assess_source_reliability", context)
        
        assert result["reliability_score"] >= 0.85
        assert result["source_id"] == "trusted_api"
        assert "is_reliable" in result
    
    async def test_extract_metadata(self):
        """Test metadata extraction."""
        colleague = DataSourceColleague()
        
        context = {
            "content": "Test content",
            "data": {"key": "value"},
            "additional_field": "test"
        }
        
        result = await colleague.handle_request("extract_metadata", context)
        
        metadata = result["extracted_metadata"]
        assert metadata["content_length"] > 0
        assert metadata["has_structured_data"] == True
        assert "content" in metadata["context_keys"]


class TestRuleEvaluatorColleague:
    """Test cases for RuleEvaluatorColleague."""
    
    def test_initialization(self):
        """Test RuleEvaluatorColleague initialization."""
        colleague = RuleEvaluatorColleague()
        
        assert colleague.colleague_id == "rule_evaluator"
        assert "weighted" in colleague.evaluation_strategies
        assert colleague.confidence_weights["high"] == 1.0
    
    def test_get_capabilities(self):
        """Test getting colleague capabilities."""
        colleague = RuleEvaluatorColleague()
        capabilities = colleague.get_capabilities()
        
        expected_capabilities = [
            "evaluate_with_strategy",
            "calculate_rule_confidence",
            "optimize_rule_order",
            "rule_performance_analysis"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
    
    async def test_weighted_evaluation(self):
        """Test weighted evaluation strategy."""
        colleague = RuleEvaluatorColleague()
        
        context = {
            "strategy": "weighted",
            "rule_results": [
                {"action": "approve", "confidence_level": "high"},
                {"action": "continue", "confidence_level": "medium"},
                {"action": "reject", "confidence_level": "low"}
            ]
        }
        
        result = await colleague.handle_request("evaluate_with_strategy", context)
        
        assert "weighted_score" in result
        assert "recommendation" in result
        assert result["evaluation_method"] == "weighted"
        assert 0.0 <= result["weighted_score"] <= 1.0
    
    async def test_consensus_evaluation(self):
        """Test consensus evaluation strategy."""
        colleague = RuleEvaluatorColleague()
        
        context = {
            "strategy": "consensus",
            "rule_results": [
                {"action": "approve"},
                {"action": "approve"},
                {"action": "continue"}
            ]
        }
        
        result = await colleague.handle_request("evaluate_with_strategy", context)
        
        assert result["consensus"] == "approve"
        assert result["agreement_level"] == 2/3
        assert "action_distribution" in result
    
    async def test_calculate_rule_confidence(self):
        """Test rule confidence calculation."""
        colleague = RuleEvaluatorColleague()
        
        context = {
            "rule_name": "test_rule",
            "execution_history": [
                {"success": True},
                {"success": True},
                {"success": False}
            ]
        }
        
        result = await colleague.handle_request("calculate_rule_confidence", context)
        
        assert result["rule_name"] == "test_rule"
        assert 0.0 <= result["confidence_score"] <= 1.0
        assert result["historical_executions"] == 3
        assert result["confidence_level"] in ["high", "medium", "low"]


class TestHelRuleEngine:
    """Test cases for HelRuleEngine class."""
    
    def test_initialization(self):
        """Test HelRuleEngine initialization."""
        engine = HelRuleEngine()
        
        assert isinstance(engine.mediator, HelRuleMediator)
        assert len(engine.hel_handlers) > 0
        assert "hel_data_quality" in engine.hel_handlers
        assert "hel_consensus" in engine.hel_handlers
    
    def test_register_colleague(self):
        """Test registering colleagues with the engine."""
        engine = HelRuleEngine()
        
        class CustomColleague(BaseColleague):
            def __init__(self):
                super().__init__("custom")
            
            async def handle_request(self, request_type: str, context: dict) -> dict:
                return {"custom": "response"}
            
            def get_capabilities(self) -> list:
                return ["custom_capability"]
        
        custom_colleague = CustomColleague()
        engine.register_colleague(custom_colleague)
        
        assert "custom" in engine.mediator.colleagues
    
    async def test_evaluate_rules_with_mediator(self):
        """Test rule evaluation with mediator enhancement."""
        engine = HelRuleEngine()
        
        # Create a rule that requires mediator intervention
        hel_rule = Rule(
            name="hel_data_quality_rule",
            description="Test Hel data quality rule",
            conditions=[
                RuleCondition("content", RuleOperator.IS_NOT_EMPTY, True)
            ],
            action=RuleAction.CUSTOM,
            custom_handler=engine.hel_handlers["hel_data_quality"],
            priority=10
        )
        
        engine.register_rule(hel_rule)
        
        context = {
            "content": "Test content for Hel evaluation",
            "data_source": "user_input",
            "confidence": 0.8
        }
        
        results = await engine.evaluate_rules_with_mediator(context)
        
        assert len(results) > 0
        # Check if any result was enhanced by mediator
        enhanced_results = [r for r in results if r.get("enhanced_by") == "hel_mediator"]
        if enhanced_results:
            assert "mediator_enhancement" in enhanced_results[0]
    
    def test_get_hel_stats(self):
        """Test getting Hel engine statistics."""
        engine = HelRuleEngine()
        stats = engine.get_hel_stats()
        
        assert "hel_engine_stats" in stats
        assert "mediator_stats" in stats
        assert "hel_handlers" in stats
        assert "colleague_capabilities" in stats
    
    def test_factory_functions(self):
        """Test factory functions for creating engine instances."""
        # Test create function
        engine1 = create_hel_rule_engine()
        assert isinstance(engine1, HelRuleEngine)
        
        # Test singleton function
        engine2 = get_hel_rule_engine()
        engine3 = get_hel_rule_engine()
        assert engine2 is engine3  # Should be the same instance


class TestHelRuleEngineIntegration:
    """Integration tests for the complete Hel Rule Engine system."""
    
    async def test_end_to_end_evaluation(self):
        """Test complete end-to-end rule evaluation with mediator."""
        engine = HelRuleEngine()
        
        # Create test context
        context = {
            "content": "High quality test content with sufficient detail",
            "data_source": "user_input",
            "confidence": 0.85,
            "trace_id": "test-hel-001"
        }
        
        # Perform evaluation
        results = await engine.evaluate_rules_with_mediator(context)
        
        # Verify results structure
        assert isinstance(results, list)
        for result in results:
            assert "rule_name" in result
            assert "action" in result
            assert "executed_at" in result
    
    async def test_colleague_interaction_flow(self):
        """Test the full colleague interaction flow."""
        engine = HelRuleEngine()
        mediator = engine.mediator
        
        # Test data source colleague
        data_result = await mediator.coordinate_request(
            "validate_data_quality",
            {"content": "Test content", "data_source": "user_input"}
        )
        assert "quality_score" in data_result
        
        # Test rule evaluator colleague
        eval_result = await mediator.coordinate_request(
            "evaluate_with_strategy",
            {
                "strategy": "weighted",
                "rule_results": [{"action": "approve", "confidence_level": "high"}]
            }
        )
        assert "weighted_score" in eval_result
    
    def test_backward_compatibility(self):
        """Test that Hel engine maintains backward compatibility with base engine."""
        hel_engine = HelRuleEngine()
        
        # Test that all base RuleEngine methods are available
        assert hasattr(hel_engine, 'evaluate_rules')
        assert hasattr(hel_engine, 'register_rule')
        assert hasattr(hel_engine, 'get_stats')
        assert hasattr(hel_engine, 'load_rules_from_config')
        
        # Test basic rule registration
        basic_rule = Rule(
            name="basic_test_rule",
            description="Basic rule for compatibility test",
            conditions=[
                RuleCondition("test_field", RuleOperator.EQ, "test_value")
            ],
            action=RuleAction.CONTINUE,
            priority=50
        )
        
        hel_engine.register_rule(basic_rule)
        assert len(hel_engine.rules) > 0
        
        # Test basic evaluation
        context = {"test_field": "test_value"}
        results = hel_engine.evaluate_rules(context)
        assert isinstance(results, list)


# Test runner function
def run_tests():
    """Run all tests for Hel Rule Engine."""
    import time
    
    print("🧪 Running Hel Rule Engine Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    # Test classes to run
    test_classes = [
        TestHelRuleMediator,
        TestDataSourceColleague, 
        TestRuleEvaluatorColleague,
        TestHelRuleEngine,
        TestHelRuleEngineIntegration
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
    print(f"\n📊 Test Summary")
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
    run_tests()
