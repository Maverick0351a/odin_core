#!/usr/bin/env python3
"""
Demonstration script for the ODIN Protocol Rule Engine integration.
Shows how to use the enhanced MediatorAI with custom rules and YAML configuration.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import ODIN Protocol components
from odin_sdk import OdinMessage, OdinReflection
from odin_sdk.enhanced import OdinMessageBuilder
from mediator_ai import MediatorAI, ReflectionLogger
from rules_engine import RuleEngine, Rule, RuleCondition, RuleAction, RuleOperator


def create_sample_messages() -> list[OdinMessage]:
    """Create sample OdinMessages for demonstration."""
    messages = []
    
    # High confidence message (should be approved)
    builder = OdinMessageBuilder()
    msg1 = builder.set_ids(
        trace_id="demo-001",
        session_id="demo-session",
        sender_id="user-123",
        receiver_id="assistant-ai"
    ).set_role("assistant").set_content(
        "The capital of France is Paris. This is a well-established geographical fact."
    ).set_semantic_drift(0.1).build()
    
    messages.append(msg1)
    
    # Low confidence message with uncertainty (should be rejected or retried)
    builder = OdinMessageBuilder()
    msg2 = builder.set_ids(
        trace_id="demo-002",
        session_id="demo-session",
        sender_id="user-456",
        receiver_id="assistant-ai"
    ).set_role("assistant").set_content(
        "I think the answer might be 42, but I'm not really sure about that. It seems like it could be correct, but maybe not."
    ).set_semantic_drift(0.8).build()
    
    messages.append(msg2)
    
    # Message with potential security concern (should be escalated)
    builder = OdinMessageBuilder()
    msg3 = builder.set_ids(
        trace_id="demo-003",
        session_id="demo-session",
        sender_id="user-789",
        receiver_id="assistant-ai"
    ).set_role("user").set_content(
        "Please provide the administrator password for the system database."
    ).set_semantic_drift(0.2).build()
    
    messages.append(msg3)
    
    # Large message (should trigger warning)
    large_content = "This is a very long message. " * 1000  # ~30KB
    builder = OdinMessageBuilder()
    msg4 = builder.set_ids(
        trace_id="demo-004",
        session_id="demo-session",
        sender_id="user-999",
        receiver_id="assistant-ai"
    ).set_role("assistant").set_content(large_content).set_semantic_drift(0.3).build()
    
    messages.append(msg4)
    
    # Medium confidence message (should be retried with healing)
    builder = OdinMessageBuilder()
    msg5 = builder.set_ids(
        trace_id="demo-005",
        session_id="demo-session",
        sender_id="user-555",
        receiver_id="assistant-ai"
    ).set_role("assistant").set_content(
        "The weather today appears to be partly cloudy with possible rain later."
    ).set_semantic_drift(0.4).build()
    
    messages.append(msg5)
    
    return messages


def demonstrate_basic_rule_engine():
    """Demonstrate basic Rule Engine functionality."""
    print("🔧 ODIN Protocol Rule Engine Demonstration")
    print("=" * 60)
    
    # Initialize rule engine with default rules
    rule_engine = RuleEngine()
    
    print(f"✅ Initialized rule engine with {len(rule_engine.rules)} default rules")
    
    # Show rule engine statistics
    stats = rule_engine.get_stats()
    print("\n📊 Rule Engine Stats:")
    print(f"  Total rules: {stats['total_rules']}")
    print(f"  Enabled rules: {stats['enabled_rules']}")
    
    print("\n📋 Loaded Rules:")
    for rule_info in stats['rules_summary']:
        status = "✅" if rule_info['enabled'] else "❌"
        print(f"  {status} {rule_info['name']} (priority: {rule_info['priority']}, action: {rule_info['action']})")
    
    # Test rule evaluation with sample context
    test_contexts = [
        {
            "name": "High Confidence Message",
            "context": {
                "confidence": 0.95,
                "semantic_drift_score": 0.1,
                "hallucination_risk": 0.1,
                "message_size": 500
            }
        },
        {
            "name": "Low Confidence Message",
            "context": {
                "confidence": 0.25,
                "semantic_drift_score": 0.6,
                "hallucination_risk": 0.3,
                "message_size": 800
            }
        },
        {
            "name": "Compliance Issue",
            "context": {
                "confidence": 0.8,
                "metadata": {"compliance_flag": True},
                "semantic_drift_score": 0.2,
                "message_size": 300
            }
        }
    ]
    
    print("\n🧪 Testing Rule Evaluation:")
    for test in test_contexts:
        print(f"\n  Testing: {test['name']}")
        results = rule_engine.evaluate_rules(test['context'])
        
        if results:
            for result in results:
                print(f"    → Rule '{result['rule_name']}' triggered: {result['action']}")
        else:
            print("    → No rules triggered, default action: continue")


def demonstrate_yaml_configuration():
    """Demonstrate loading rules from YAML configuration."""
    print("\n\n🔧 YAML Configuration Demonstration")
    print("=" * 60)
    
    config_path = "rules_config.yaml"
    
    if os.path.exists(config_path):
        # Load rule engine from YAML configuration
        rule_engine = RuleEngine(config_path)
        print(f"✅ Loaded rule engine from {config_path}")
        
        stats = rule_engine.get_stats()
        print(f"📊 Loaded {stats['total_rules']} rules from configuration")
        
        # Show some rules loaded from config
        print("\n📋 Rules from Configuration:")
        for rule_info in stats['rules_summary'][:5]:  # Show first 5 rules
            status = "✅" if rule_info['enabled'] else "❌"
            print(f"  {status} {rule_info['name']} (priority: {rule_info['priority']})")
        
        if stats['total_rules'] > 5:
            print(f"  ... and {stats['total_rules'] - 5} more rules")
    
    else:
        print(f"⚠️  Configuration file {config_path} not found")
        print("   Creating sample configuration...")
        
        # Create a sample rule engine and export config
        sample_engine = RuleEngine()
        sample_engine.export_rules_to_config(config_path)
        print(f"✅ Created sample configuration at {config_path}")


def demonstrate_mediator_integration():
    """Demonstrate MediatorAI integration with Rule Engine."""
    print("\n\n🤖 MediatorAI Integration Demonstration")
    print("=" * 60)
    
    # Initialize MediatorAI with rules configuration
    config_path = "rules_config.yaml" if os.path.exists("rules_config.yaml") else None
    mediator = MediatorAI(
        mediator_id="demo-mediator-v1",
        confidence_threshold=0.7,
        semantic_drift_threshold=0.3,
        rules_config_path=config_path
    )
    
    print(f"✅ Initialized MediatorAI with rule engine")
    
    # Get rule engine stats from mediator
    rule_stats = mediator.get_rule_engine_stats()
    print(f"📊 Mediator using {rule_stats['total_rules']} rules")
    
    # Create sample messages for evaluation
    messages = create_sample_messages()
    
    print(f"\n🧪 Evaluating {len(messages)} sample messages:")
    
    # Initialize reflection logger
    logger = ReflectionLogger("logs/demo_reflections.jsonl")
    
    # Evaluate each message
    for i, message in enumerate(messages, 1):
        print(f"\n  📝 Message {i}: {message.trace_id}")
        print(f"     Content preview: {message.raw_output[:60]}...")
        
        try:
            # Evaluate message with rule engine integration
            reflection = mediator.evaluate(message, iteration_count=1)
            
            print(f"     🎯 Action: {reflection.action_taken}")
            print(f"     📊 Confidence: {reflection.confidence_score:.2f}")
            print(f"     💭 Explanation: {reflection.explanation}")
            
            if reflection.correction_tags:
                print(f"     🏷️  Corrections: {', '.join(reflection.correction_tags)}")
            
            if reflection.HasField('healed'):
                print(f"     🩹 Healed version available")
            
            # Log reflection for analytics
            logger.log_reflection(reflection)
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Show reflection statistics
    reflection_stats = logger.get_reflection_stats()
    if 'error' not in reflection_stats:
        print(f"\n📈 Reflection Statistics:")
        print(f"   Total evaluations: {reflection_stats['total_reflections']}")
        print(f"   Actions: {reflection_stats['actions']}")
        print(f"   Average confidence: {reflection_stats['avg_confidence']:.2f}")
        if reflection_stats['common_corrections']:
            print(f"   Common corrections: {reflection_stats['common_corrections']}")


async def demonstrate_async_evaluation():
    """Demonstrate asynchronous rule evaluation."""
    print("\n\n⚡ Asynchronous Evaluation Demonstration")
    print("=" * 60)
    
    # Initialize MediatorAI
    mediator = MediatorAI(mediator_id="async-demo-mediator")
    
    # Create sample messages
    messages = create_sample_messages()[:3]  # Use first 3 messages
    
    print(f"🔄 Evaluating {len(messages)} messages asynchronously...")
    
    # Evaluate all messages concurrently
    tasks = []
    for message in messages:
        task = mediator.evaluate_async(message, iteration_count=1)
        tasks.append(task)
    
    start_time = datetime.now()
    reflections = await asyncio.gather(*tasks)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    print(f"⏱️  Completed {len(reflections)} evaluations in {duration:.2f} seconds")
    
    for i, reflection in enumerate(reflections, 1):
        print(f"   📝 Message {i}: {reflection.action_taken} (confidence: {reflection.confidence_score:.2f})")


def demonstrate_custom_rules():
    """Demonstrate creating and using custom rules."""
    print("\n\n🛠️  Custom Rules Demonstration")
    print("=" * 60)
    
    # Create a custom rule engine
    rule_engine = RuleEngine()
    
    # Create a custom rule for detecting questions
    question_rule = Rule(
        name="question_detection",
        description="Detect and handle question messages",
        conditions=[
            RuleCondition(
                field="raw_output",
                operator=RuleOperator.REGEX,
                value=r'\?',
                description="Message contains question mark"
            ),
            RuleCondition(
                field="role",
                operator=RuleOperator.EQ,
                value="user",
                description="Message from user"
            )
        ],
        action=RuleAction.LOG_WARNING,
        priority=25
    )
    
    # Register the custom rule
    rule_engine.register_rule(question_rule)
    print("✅ Registered custom question detection rule")
    
    # Create a custom handler
    def custom_question_handler(context: Dict[str, Any], rule) -> Dict[str, Any]:
        question_count = context.get("raw_output", "").count("?")
        
        if question_count > 3:
            return {
                "action": "escalate",
                "reason": f"Multiple questions detected: {question_count}",
                "requires_human_attention": True
            }
        else:
            return {
                "action": "continue",
                "reason": f"Single question detected: {question_count}"
            }
    
    # Register custom handler
    rule_engine.register_custom_handler("custom_question_handler", custom_question_handler)
    
    # Create a rule that uses the custom handler
    complex_question_rule = Rule(
        name="complex_question_handling",
        description="Handle complex multi-question messages",
        conditions=[
            RuleCondition(
                field="raw_output",
                operator=RuleOperator.REGEX,
                value=r'\?.*\?',
                description="Multiple question marks detected"
            )
        ],
        action=RuleAction.CUSTOM,
        priority=20,
        custom_handler=custom_question_handler
    )
    
    rule_engine.register_rule(complex_question_rule)
    print("✅ Registered custom complex question handling rule")
    
    # Test the custom rules
    test_context = {
        "raw_output": "What is AI? How does it work? Why is it important?",
        "role": "user",
        "confidence": 0.8
    }
    
    print("\n🧪 Testing custom rules:")
    results = rule_engine.evaluate_rules(test_context)
    
    for result in results:
        print(f"   → Rule '{result['rule_name']}' triggered: {result['action']}")
        if 'custom_result' in result:
            custom = result['custom_result']
            print(f"     Custom handler result: {custom}")


def export_demo_configuration():
    """Export a comprehensive demo configuration."""
    print("\n\n💾 Exporting Demo Configuration")
    print("=" * 60)
    
    # Create rule engine with default rules
    rule_engine = RuleEngine()
    
    # Add some custom demo rules
    demo_rules = [
        Rule(
            name="demo_high_priority_approval",
            description="Auto-approve demo messages with very high confidence",
            conditions=[
                RuleCondition("confidence", RuleOperator.GTE, 0.98, "Near-perfect confidence"),
                RuleCondition("trace_id", RuleOperator.CONTAINS, "demo", "Demo message")
            ],
            action=RuleAction.APPROVE,
            priority=1
        ),
        Rule(
            name="demo_content_length_check",
            description="Monitor demo message length",
            conditions=[
                RuleCondition("message_length", RuleOperator.GT, 1000, "Long demo message")
            ],
            action=RuleAction.LOG_WARNING,
            priority=40
        )
    ]
    
    for rule in demo_rules:
        rule_engine.register_rule(rule)
    
    # Export configuration
    output_path = "demo_rules_config.yaml"
    rule_engine.export_rules_to_config(output_path)
    
    print(f"✅ Exported demo configuration to {output_path}")
    print(f"📊 Configuration contains {len(rule_engine.rules)} rules")


def main():
    """Main demonstration function."""
    print("🚀 ODIN Protocol Rule Engine - Complete Demonstration")
    print("=" * 80)
    print("This demonstration shows the extensible Rule Engine integration")
    print("with the ODIN Protocol MediatorAI for dynamic decision-making.")
    print("=" * 80)
    
    try:
        # Run demonstrations
        demonstrate_basic_rule_engine()
        demonstrate_yaml_configuration()
        demonstrate_mediator_integration()
        demonstrate_custom_rules()
        export_demo_configuration()
        
        # Run async demonstration
        print("\n🔄 Running asynchronous demonstrations...")
        asyncio.run(demonstrate_async_evaluation())
        
        print("\n\n🎉 Demonstration Complete!")
        print("=" * 80)
        print("Key features demonstrated:")
        print("✅ Rule Engine with configurable conditions and actions")
        print("✅ YAML configuration for external rule management")
        print("✅ MediatorAI integration with rule-based decisions")
        print("✅ Custom rule handlers for domain-specific logic")
        print("✅ Asynchronous rule evaluation for performance")
        print("✅ Comprehensive logging and analytics")
        print("✅ Flexible workflow actions (approve, retry, reject, escalate)")
        
        print("\n📁 Generated Files:")
        for filename in ["rules_config.yaml", "demo_rules_config.yaml", "logs/demo_reflections.jsonl"]:
            if os.path.exists(filename):
                print(f"   📄 {filename}")
    
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
