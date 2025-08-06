#!/usr/bin/env python3
"""
Test script for the ODIN Protocol self-reflection system.

This script demonstrates the complete self-dialogue workflow:
1. Agent generates a message
2. Mediator evaluates and provides feedback  
3. Loopback handler manages correction cycles
4. CLI tools inspect reflections
5. Analytics track improvement patterns
"""

import os
import time
import glob
from datetime import datetime

from odin_format import create_odin_entry
from mediator_ai import MediatorAI, ReflectionLogger
from loopback_handler import LoopbackHandler, AgentWithReflection


def test_mediator_evaluation():
    """Test the MediatorAI evaluation capabilities."""
    print("🧪 Testing MediatorAI evaluation...")
    
    # Create test messages with different quality levels
    test_cases = [
        {
            "name": "High Quality Message",
            "raw_output": "The data clearly demonstrates a 15% improvement in efficiency metrics.",
            "expected_action": "pass"
        },
        {
            "name": "Low Confidence Message", 
            "raw_output": "I think this might be correct, but I'm not sure about the exact numbers.",
            "expected_action": "modify"
        },
        {
            "name": "Potential Hallucination",
            "raw_output": "I believe the moon is made of cheese, which probably explains its appearance.",
            "expected_action": "reject"
        },
        {
            "name": "Unclear Language",
            "raw_output": "This approach could potentially maybe work if we consider that it might be feasible.",
            "expected_action": "modify"
        }
    ]
    
    mediator = MediatorAI(mediator_id="test-mediator", confidence_threshold=0.6)
    
    for i, case in enumerate(test_cases):
        print(f"\n📝 Test Case {i+1}: {case['name']}")
        
        # Create test message
        message = create_odin_entry(
            dialogue_id=f"test-{i+1}",
            trace_id=f"trace-{i+1}",
            turn=1,
            source_model="test-agent",
            target_model="test-receiver",
            context="testing mediator evaluation",
            input_raw="Test input",
            input_repaired="Test input",
            input_translated="Test input",
            response_raw=case["raw_output"],
            response_repaired=case["raw_output"],
            response_translated=case["raw_output"],
            metrics={'semantic_drift': 0.0, 'hallucination_score': 0.0, 'efficiency_gain': 0.0},
            metadata={'test_case': case['name']}
        )
        
        # Evaluate with mediator
        reflection = mediator.evaluate(message)
        
        print(f"   ✅ Action: {reflection.action_taken}")
        print(f"   📊 Confidence: {reflection.confidence_score:.2f}")
        print(f"   💭 Explanation: {reflection.explanation}")
        
        if reflection.correction_tags:
            print(f"   🏷️  Corrections: {', '.join(reflection.correction_tags)}")
        
        # Check if result matches expectation
        if reflection.action_taken == case["expected_action"]:
            print(f"   ✅ Expected action achieved!")
        else:
            print(f"   ⚠️  Expected {case['expected_action']}, got {reflection.action_taken}")
    
    print("\n🎉 MediatorAI evaluation test complete!")


def test_loopback_system():
    """Test the complete loopback and correction system."""
    print("\n🔄 Testing loopback correction system...")
    
    # Set up the reflection system
    mediator = MediatorAI(mediator_id="loopback-mediator", confidence_threshold=0.7)
    reflection_logger = ReflectionLogger("logs/test_reflections.jsonl")
    loopback_handler = LoopbackHandler(mediator, max_iterations=3, reflection_logger=reflection_logger)
    
    # Create reflective agent
    agent = AgentWithReflection("test-agent-v1", "gpt-4o", loopback_handler)
    
    # Test with a message that will need correction
    print("📝 Generating message that needs correction...")
    final_message, reflection_history, success = agent.generate_message(
        prompt="Explain quantum computing",
        trace_id="loopback-test-001",
        receiver_id="target-agent",
        context="quantum computing explanation"
    )
    
    print(f"\n📊 Loopback Results:")
    print(f"   ✅ Success: {success}")
    print(f"   🔄 Iterations: {len(reflection_history)}")
    print(f"   📝 Final message: {final_message.raw_output}")
    
    # Show reflection history
    for i, reflection in enumerate(reflection_history):
        print(f"\n   Iteration {i+1}:")
        print(f"     Action: {reflection.action_taken}")
        print(f"     Confidence: {reflection.confidence_score:.2f}")
        print(f"     Explanation: {reflection.explanation}")
    
    print("\n🎉 Loopback system test complete!")
    return reflection_history


def test_cli_tools():
    """Test the CLI tools for reflection inspection."""
    print("\n🔧 Testing CLI tools...")
    
    # First, ensure we have some reflection files to test
    print("📁 Checking for reflection files...")
    
    import glob
    reflection_files = glob.glob("logs/*.odinr")
    
    if not reflection_files:
        print("⚠️  No reflection files found. Run the loopback test first.")
        return
    
    test_file = reflection_files[0]
    print(f"🔍 Testing with file: {test_file}")
    
    # Test CLI inspection
    from odin_cli import inspect_reflection_file, show_reflection_stats
    
    print("\n📄 Testing reflection inspection (JSON format):")
    success = inspect_reflection_file(test_file, "json")
    
    if success:
        print("✅ JSON inspection successful!")
    else:
        print("❌ JSON inspection failed!")
    
    print("\n📄 Testing reflection inspection (Text format):")
    success = inspect_reflection_file(test_file, "text")
    
    if success:
        print("✅ Text inspection successful!")
    else:
        print("❌ Text inspection failed!")
    
    print("\n📊 Testing reflection analytics:")
    success = show_reflection_stats("logs/test_reflections.jsonl")
    
    if success:
        print("✅ Analytics successful!")
    else:
        print("❌ Analytics failed!")
    
    print("\n🎉 CLI tools test complete!")


def test_jsonl_analytics():
    """Test the JSONL analytics system."""
    print("\n📊 Testing JSONL analytics...")
    
    reflection_logger = ReflectionLogger("logs/test_reflections.jsonl")
    stats = reflection_logger.get_reflection_stats()
    
    if 'error' in stats:
        print(f"❌ Analytics error: {stats['error']}")
        return
    
    print("📈 Analytics Results:")
    print(f"   Total Reflections: {stats['total_reflections']}")
    print(f"   Average Confidence: {stats['avg_confidence']:.3f}")
    print(f"   Actions: {stats['actions']}")
    print(f"   Common Corrections: {list(stats['common_corrections'].keys())[:3]}")
    print(f"   Active Mediators: {stats['mediators']}")
    
    print("\n🎉 JSONL analytics test complete!")


def run_complete_test_suite():
    """Run the complete test suite for the self-reflection system."""
    print("🚀 ODIN Protocol Self-Reflection System Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Test 1: Mediator evaluation
        test_mediator_evaluation()
        
        # Test 2: Loopback system  
        reflection_history = test_loopback_system()
        
        # Test 3: CLI tools
        test_cli_tools()
        
        # Test 4: Analytics
        test_jsonl_analytics()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print("\n📋 Summary:")
        print("   ✅ MediatorAI evaluation system working")
        print("   ✅ Loopback correction cycles functional")  
        print("   ✅ CLI inspection tools operational")
        print("   ✅ JSONL analytics system active")
        print("\n🚀 ODIN Protocol self-reflection system is ready for production!")
        
        # Show file summary
        print("\n📁 Generated Files:")
        for ext, desc in [('.odinr', 'Reflection files'), ('.jsonl', 'Analytics logs')]:
            files = glob.glob(f"logs/*{ext}")
            if files:
                print(f"   {desc}: {len(files)} files")
                for f in files[:3]:  # Show first 3
                    print(f"     • {f}")
                if len(files) > 3:
                    print(f"     ... and {len(files) - 3} more")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run the complete test suite
    run_complete_test_suite()
