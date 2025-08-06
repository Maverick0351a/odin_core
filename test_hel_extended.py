#!/usr/bin/env python3
"""
Extended test suite for Hel Rule Engine with PolicyColleague and ActionTriggerColleague.
Tests the complete Mediator Pattern implementation.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hel_rule_engine import HelRuleEngine, HelRuleMediator, create_hel_rule_engine
from hel_colleagues import PolicyColleague, ActionTriggerColleague, Policy, ActionTrigger, PolicyType, ActionType


class TestPolicyColleague:
    """Test cases for PolicyColleague class."""
    
    def test_initialization(self):
        """Test PolicyColleague initialization."""
        colleague = PolicyColleague()
        
        assert colleague.colleague_id == "policy"
        assert len(colleague.policies) == 3  # Default policies
        assert colleague.enforcement_stats["policies_evaluated"] == 0
    
    def test_get_capabilities(self):
        """Test getting policy colleague capabilities."""
        colleague = PolicyColleague()
        capabilities = colleague.get_capabilities()
        
        expected_capabilities = [
            "evaluate_policies",
            "check_compliance",
            "enforce_policy",
            "get_policy_recommendations",
            "audit_policy_violations",
            "policy_management"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
    
    async def test_evaluate_policies_clean_content(self):
        """Test policy evaluation with clean content."""
        colleague = PolicyColleague()
        
        context = {
            "content": "This is clean, appropriate content for testing purposes.",
            "confidence": 0.85,
            "data_source": "user_input"
        }
        
        result = await colleague.handle_request("evaluate_policies", context)
        
        assert result["evaluation_completed"] == True
        assert result["policies_evaluated"] > 0
        assert len(result["violations"]) == 0  # Clean content should not violate policies
        assert result["recommendation"] in ["allow", "warn"]
    
    async def test_evaluate_policies_with_violations(self):
        """Test policy evaluation with content that violates policies."""
        colleague = PolicyColleague()
        
        context = {
            "content": "Contact me at john.doe@email.com or call 555-123-4567",
            "confidence": 0.2,  # Low confidence
            "data_source": "user_input"
        }
        
        result = await colleague.handle_request("evaluate_policies", context)
        
        assert result["evaluation_completed"] == True
        assert len(result["violations"]) > 0 or len(result["warnings"]) > 0
        assert result["enforcement_required"] == (len(result["violations"]) > 0)
    
    async def test_check_compliance(self):
        """Test compliance checking functionality."""
        colleague = PolicyColleague()
        
        context = {
            "content": "Short",  # Below minimum length
            "confidence": 0.9
        }
        
        result = await colleague.handle_request("check_compliance", context)
        
        assert "compliant" in result
        assert "compliance_score" in result
        assert 0.0 <= result["compliance_score"] <= 1.0
    
    async def test_get_policy_recommendations(self):
        """Test policy recommendations."""
        colleague = PolicyColleague()
        
        context = {
            "content": "Test content",
            "confidence": 0.2,  # Low confidence should trigger recommendation
            "data_source": "external_api"
        }
        
        result = await colleague.handle_request("get_policy_recommendations", context)
        
        assert "recommendations" in result
        assert result["recommendation_count"] >= 0
    
    def test_add_policy(self):
        """Test adding custom policies."""
        colleague = PolicyColleague()
        
        custom_policy = Policy(
            policy_id="custom_test_001",
            policy_type=PolicyType.OPERATIONAL,
            name="Custom Test Policy",
            description="Test policy for unit testing",
            rules=["test_rule"],
            enforcement_level="warn"
        )
        
        initial_count = len(colleague.policies)
        colleague.add_policy(custom_policy)
        
        assert len(colleague.policies) == initial_count + 1
        assert "custom_test_001" in colleague.policies
    
    def test_get_policy_stats(self):
        """Test policy statistics."""
        colleague = PolicyColleague()
        stats = colleague.get_policy_stats()
        
        assert "total_policies" in stats
        assert "active_policies" in stats
        assert "policies_by_type" in stats
        assert "enforcement_stats" in stats


class TestActionTriggerColleague:
    """Test cases for ActionTriggerColleague class."""
    
    def test_initialization(self):
        """Test ActionTriggerColleague initialization."""
        colleague = ActionTriggerColleague()
        
        assert colleague.colleague_id == "action_trigger"
        assert len(colleague.triggers) == 4  # Default triggers
        assert colleague.trigger_stats["triggers_evaluated"] == 0
    
    def test_get_capabilities(self):
        """Test getting action trigger colleague capabilities."""
        colleague = ActionTriggerColleague()
        capabilities = colleague.get_capabilities()
        
        expected_capabilities = [
            "evaluate_triggers",
            "execute_action",
            "get_trigger_recommendations",
            "audit_actions",
            "manage_cooldowns",
            "action_management"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
    
    async def test_evaluate_triggers_escalation(self):
        """Test trigger evaluation for escalation scenario."""
        colleague = ActionTriggerColleague()
        
        context = {
            "action": "escalate",
            "priority": "high",
            "trace_id": "test-escalation-001"
        }
        
        result = await colleague.handle_request("evaluate_triggers", context)
        
        assert result["evaluation_completed"] == True
        assert result["triggers_evaluated"] > 0
        # Should trigger escalation action
        triggered_actions = result["triggered_actions"]
        escalation_actions = [a for a in triggered_actions if a["action_type"] == "escalation"]
        assert len(escalation_actions) > 0
    
    async def test_evaluate_triggers_low_confidence(self):
        """Test trigger evaluation for low confidence scenario."""
        colleague = ActionTriggerColleague()
        
        context = {
            "confidence": 0.2,  # Low confidence
            "trace_id": "test-confidence-001"
        }
        
        result = await colleague.handle_request("evaluate_triggers", context)
        
        assert result["evaluation_completed"] == True
        # Should trigger low confidence notification
        triggered_actions = result["triggered_actions"]
        notification_actions = [a for a in triggered_actions if a["action_type"] == "notification"]
        assert len(notification_actions) > 0
    
    async def test_evaluate_triggers_security_violation(self):
        """Test trigger evaluation for security violations."""
        colleague = ActionTriggerColleague()
        
        context = {
            "policy_type": "security",
            "violation_detected": True,
            "trace_id": "test-security-001"
        }
        
        result = await colleague.handle_request("evaluate_triggers", context)
        
        assert result["evaluation_completed"] == True
        # Should trigger security alert
        triggered_actions = result["triggered_actions"]
        alert_actions = [a for a in triggered_actions if a["action_type"] == "alert"]
        assert len(alert_actions) > 0
    
    async def test_cooldown_management(self):
        """Test trigger cooldown functionality."""
        colleague = ActionTriggerColleague()
        
        # Get a trigger and set it as recently triggered
        trigger_id = "high_priority_escalation"
        trigger = colleague.triggers[trigger_id]
        trigger.last_triggered = datetime.now()
        
        # Test cooldown status
        context = {"cooldown_action": "status"}
        result = await colleague.handle_request("manage_cooldowns", context)
        
        assert "cooldown_status" in result
        assert trigger_id in result["cooldown_status"]
        assert result["cooldown_status"][trigger_id]["in_cooldown"] == True
        
        # Test cooldown reset
        reset_context = {"cooldown_action": "reset", "trigger_id": trigger_id}
        reset_result = await colleague.handle_request("manage_cooldowns", reset_context)
        
        assert "message" in reset_result
        assert trigger.last_triggered is None
    
    async def test_execute_specific_action(self):
        """Test executing a specific action by trigger ID."""
        colleague = ActionTriggerColleague()
        
        context = {
            "trigger_id": "audit_logging",
            "trace_id": "test-audit-001"
        }
        
        result = await colleague.handle_request("execute_action", context)
        
        assert result["success"] == True
        assert result["action_type"] == "audit_log"
        assert "details" in result
    
    async def test_get_trigger_recommendations(self):
        """Test trigger recommendations."""
        colleague = ActionTriggerColleague()
        
        context = {
            "confidence": 0.3,
            "action": "escalate"
        }
        
        result = await colleague.handle_request("get_trigger_recommendations", context)
        
        assert "recommendations" in result
        assert result["recommendation_count"] >= 0
    
    def test_add_trigger(self):
        """Test adding custom triggers."""
        colleague = ActionTriggerColleague()
        
        custom_trigger = ActionTrigger(
            trigger_id="custom_test_trigger",
            action_type=ActionType.NOTIFICATION,
            name="Custom Test Trigger",
            description="Test trigger for unit testing",
            conditions=["test_condition"],
            parameters={"test_param": "value"}
        )
        
        initial_count = len(colleague.triggers)
        colleague.add_trigger(custom_trigger)
        
        assert len(colleague.triggers) == initial_count + 1
        assert "custom_test_trigger" in colleague.triggers
    
    def test_get_trigger_stats(self):
        """Test trigger statistics."""
        colleague = ActionTriggerColleague()
        stats = colleague.get_trigger_stats()
        
        assert "total_triggers" in stats
        assert "active_triggers" in stats
        assert "triggers_by_type" in stats
        assert "trigger_stats" in stats


class TestHelRuleEngineWithAllColleagues:
    """Integration tests for Hel Rule Engine with all colleagues."""
    
    def test_initialization_with_all_colleagues(self):
        """Test that Hel Rule Engine initializes with all colleagues."""
        engine = HelRuleEngine()
        
        # Should have all 4 colleagues
        expected_colleagues = ["data_source", "rule_evaluator", "policy", "action_trigger"]
        
        for colleague_id in expected_colleagues:
            assert colleague_id in engine.mediator.colleagues
    
    async def test_comprehensive_evaluation_flow(self):
        """Test complete evaluation flow with all colleagues."""
        engine = HelRuleEngine()
        
        # Context that should trigger multiple colleagues
        context = {
            "content": "This message contains john.doe@email.com and has low confidence",
            "confidence": 0.25,  # Low confidence
            "data_source": "user_input",
            "action": "escalate",
            "priority": "high",
            "trace_id": "comprehensive-test-001"
        }
        
        # Test data source validation
        data_result = await engine.mediator.coordinate_request("validate_data_quality", context)
        assert "quality_score" in data_result
        
        # Test policy evaluation
        policy_result = await engine.mediator.coordinate_request("evaluate_policies", context)
        assert "evaluation_completed" in policy_result
        
        # Test action triggers
        trigger_result = await engine.mediator.coordinate_request("evaluate_triggers", context)
        assert "evaluation_completed" in trigger_result
        
        # Test rule evaluation with strategy
        eval_context = {
            "strategy": "consensus",
            "rule_results": [
                {"action": "escalate", "confidence_level": "high"},
                {"action": "reject", "confidence_level": "medium"}
            ]
        }
        eval_result = await engine.mediator.coordinate_request("evaluate_with_strategy", eval_context)
        assert "consensus" in eval_result
    
    async def test_enhanced_rule_evaluation_with_mediator(self):
        """Test enhanced rule evaluation using the full mediator system."""
        engine = HelRuleEngine()
        
        context = {
            "content": "Test content with potential security issues: admin@company.com",
            "confidence": 0.6,
            "data_source": "external_api",
            "trace_id": "enhanced-eval-001"
        }
        
        # Perform enhanced evaluation
        results = await engine.evaluate_rules_with_mediator(context)
        
        assert isinstance(results, list)
        # Check if any results were enhanced by the mediator
        enhanced_results = [r for r in results if r.get("enhanced_by") == "hel_mediator"]
        
        # Verify the mediator statistics updated
        hel_stats = engine.get_hel_stats()
        assert hel_stats["hel_engine_stats"]["enhanced_evaluations"] > 0
    
    def test_get_comprehensive_stats(self):
        """Test getting comprehensive statistics from Hel engine."""
        engine = HelRuleEngine()
        stats = engine.get_hel_stats()
        
        # Should contain base rule engine stats
        assert "total_rules" in stats
        assert "execution_stats" in stats
        
        # Should contain Hel-specific stats
        assert "hel_engine_stats" in stats
        assert "mediator_stats" in stats
        assert "colleague_capabilities" in stats
        
        # Should have all colleagues in capabilities
        capabilities = stats["colleague_capabilities"]
        expected_colleagues = ["data_source", "rule_evaluator", "policy", "action_trigger"]
        
        for colleague_id in expected_colleagues:
            assert colleague_id in capabilities
    
    async def test_colleague_interaction_coordination(self):
        """Test coordination between different colleagues."""
        engine = HelRuleEngine()
        mediator = engine.mediator
        
        # Test that mediator can coordinate between colleagues
        context = {
            "content": "Multi-colleague test content",
            "confidence": 0.4,
            "data_source": "user_input"
        }
        
        # Validate data quality (DataSourceColleague)
        data_result = await mediator.coordinate_request("validate_data_quality", context)
        assert "quality_score" in data_result
        
        # Check policies (PolicyColleague) 
        policy_result = await mediator.coordinate_request("evaluate_policies", context)
        assert "evaluation_completed" in policy_result
        
        # Evaluate triggers (ActionTriggerColleague)
        trigger_result = await mediator.coordinate_request("evaluate_triggers", context)
        assert "evaluation_completed" in trigger_result
        
        # Use weighted evaluation (RuleEvaluatorColleague)
        eval_context = {
            "strategy": "weighted",
            "rule_results": [{"action": "continue", "confidence_level": "medium"}]
        }
        eval_result = await mediator.coordinate_request("evaluate_with_strategy", eval_context)
        assert "weighted_score" in eval_result
    
    def test_factory_function_with_all_colleagues(self):
        """Test factory function creates engine with all colleagues."""
        engine = create_hel_rule_engine()
        
        # Verify all colleagues are present
        expected_colleagues = ["data_source", "rule_evaluator", "policy", "action_trigger"]
        for colleague_id in expected_colleagues:
            assert colleague_id in engine.mediator.colleagues
        
        # Verify capabilities are available
        capabilities = engine.mediator.get_colleague_capabilities()
        assert len(capabilities) == 4
        
        # Verify each colleague has its expected capabilities
        assert "validate_data_quality" in capabilities["data_source"]
        assert "evaluate_with_strategy" in capabilities["rule_evaluator"]
        assert "evaluate_policies" in capabilities["policy"]
        assert "evaluate_triggers" in capabilities["action_trigger"]


class TestHelRuleEngineIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    async def test_security_incident_scenario(self):
        """Test complete security incident handling scenario."""
        engine = HelRuleEngine()
        
        # Simulate security incident context
        context = {
            "content": "Suspicious activity detected from user@hacker.com trying to access admin panel",
            "confidence": 0.95,  # High confidence in detection
            "data_source": "api_response",  # Use supported data source
            "policy_type": "security",
            "violation_detected": True,
            "action": "escalate",
            "priority": "high",
            "trace_id": "security-incident-001"
        }
        
        # Evaluate data quality
        data_result = await engine.mediator.coordinate_request("validate_data_quality", context)
        assert data_result["meets_threshold"] == True  # Should pass with supported source and long content
        
        # Evaluate security policies  
        policy_result = await engine.mediator.coordinate_request("evaluate_policies", context)
        assert policy_result["evaluation_completed"] == True
        # Should detect email pattern in content
        violations_and_warnings = policy_result["violations"] + policy_result["warnings"]
        assert len(violations_and_warnings) > 0  # Should detect email pattern
        
        # Trigger security actions
        trigger_result = await engine.mediator.coordinate_request("evaluate_triggers", context)
        triggered_actions = trigger_result["triggered_actions"]
        
        # Should trigger both escalation and security alert
        action_types = [a["action_type"] for a in triggered_actions]
        assert "escalation" in action_types
        assert "alert" in action_types
    
    async def test_low_quality_content_scenario(self):
        """Test handling of low quality content scenario."""
        engine = HelRuleEngine()
        
        context = {
            "content": "bad",  # Very short, low quality
            "confidence": 0.1,  # Very low confidence
            "data_source": "user_input",  # Use supported data source
            "trace_id": "low-quality-001"
        }
        
        # Data quality should be poor (due to short content)
        data_result = await engine.mediator.coordinate_request("validate_data_quality", context)
        assert data_result["meets_threshold"] == False
        
        # Should have compliance violations
        policy_result = await engine.mediator.coordinate_request("evaluate_policies", context)
        compliance_result = await engine.mediator.coordinate_request("check_compliance", context)
        assert compliance_result.get("compliant", True) == False  # Should fail compliance
        
        # Should trigger low confidence notifications
        trigger_result = await engine.mediator.coordinate_request("evaluate_triggers", context)
        triggered_actions = trigger_result["triggered_actions"]
        notification_actions = [a for a in triggered_actions if a["action_type"] == "notification"]
        assert len(notification_actions) > 0
    
    async def test_normal_operation_scenario(self):
        """Test normal operation with good content."""
        engine = HelRuleEngine()
        
        context = {
            "content": "This is high quality content that meets all standards and contains no violations",
            "confidence": 0.9,  # High confidence
            "data_source": "user_input",  # Use supported data source  
            "trace_id": "normal-operation-001"
        }
        
        # Data quality should be good
        data_result = await engine.mediator.coordinate_request("validate_data_quality", context)
        assert data_result["meets_threshold"] == True
        
        # Should be compliant
        compliance_result = await engine.mediator.coordinate_request("check_compliance", context)
        assert compliance_result.get("compliant", False) == True
        
        policy_result = await engine.mediator.coordinate_request("evaluate_policies", context)
        assert len(policy_result.get("violations", [])) == 0
        
        # Should trigger minimal actions (mainly audit logging)
        trigger_result = await engine.mediator.coordinate_request("evaluate_triggers", context)
        triggered_actions = trigger_result["triggered_actions"]
        
        # Audit logging should always trigger, but others may not
        action_types = [a["action_type"] for a in triggered_actions]
        assert "audit_log" in action_types


# Test runner function for extended tests
def run_extended_tests():
    """Run all extended tests for Hel Rule Engine with additional colleagues."""
    import time
    
    print("🧪 Running Extended Hel Rule Engine Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    # Test classes to run
    test_classes = [
        TestPolicyColleague,
        TestActionTriggerColleague,
        TestHelRuleEngineWithAllColleagues,
        TestHelRuleEngineIntegrationScenarios
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
    print(f"\n📊 Extended Test Summary")
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
    run_extended_tests()
