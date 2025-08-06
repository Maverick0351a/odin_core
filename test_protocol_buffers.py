#!/usr/bin/env python3
"""Test script to verify Protocol Buffer implementation works correctly."""

import os
from datetime import datetime
from odin_format import create_odin_entry, save_odin_file, load_odin_file

def test_protocol_buffer_implementation():
    """Test that Protocol Buffer ODIN messages work end-to-end."""
    print("🧪 Testing Protocol Buffer implementation...")
    
    # Create a test ODIN entry
    print("📝 Creating test ODIN entry...")
    odin_entry = create_odin_entry(
        dialogue_id="test-dialogue-001",
        trace_id="test-trace-001",
        turn=1,
        source_model="gpt-4o",
        target_model="gemini-1.5-flash",
        context="testing protocol buffers",
        input_raw='What is the capital of France?',
        input_repaired='What is the capital of France?',
        input_translated='What is the capital of France?',
        response_raw='The capital of France is Paris.',
        response_repaired='The capital of France is Paris.',
        response_translated='The capital of France is Paris.',
        metrics={
            'semantic_drift': 0.01,
            'hallucination_score': 0.02,
            'efficiency_gain': 0.15
        },
        metadata={'session': 'test-session', 'version': '2.0'}
    )
    
    print(f"✅ Created ODIN entry: {type(odin_entry)}")
    assert odin_entry is not None, "Failed to create ODIN entry"
    
    # Save to binary file
    test_dir = "logs"
    print(f"💾 Saving to binary file in directory: {test_dir}")
    actual_filepath = save_odin_file(odin_entry, test_dir)
    print(f"📁 Actual file path: {actual_filepath}")
    
    # Verify file exists and has content
    assert os.path.exists(actual_filepath), "File not created"
    file_size = os.path.getsize(actual_filepath)
    print(f"✅ File created successfully ({file_size} bytes)")
    assert file_size > 0, "File is empty"
    
    # Load from binary file
    print("📖 Loading from binary file...")
    loaded_entry = load_odin_file(actual_filepath)
    
    assert loaded_entry is not None, "Failed to load ODIN entry"
    print(f"✅ Loaded ODIN entry: {type(loaded_entry)}")
    print(f"   Trace ID: {loaded_entry.trace_id}")
    print(f"   Session ID: {loaded_entry.session_id}")
    print(f"   Sender ID: {loaded_entry.sender_id}")
    print(f"   Receiver ID: {loaded_entry.receiver_id}")
    print(f"   Role: {loaded_entry.role}")
    print(f"   Raw Output: {loaded_entry.raw_output}")
    print(f"   Healed Output: {loaded_entry.healed_output}")
    print(f"   Semantic Drift Score: {loaded_entry.semantic_drift_score}")
    
    # Check context
    if loaded_entry.HasField('context'):
        print(f"   Context:")
        print(f"     Conversation ID: {loaded_entry.context.conversation_id}")
        print(f"     Turn Number: {loaded_entry.context.turn_number}")
        print(f"     Topic: {loaded_entry.context.topic}")
        
    # Check metrics
    if loaded_entry.HasField('metrics'):
        print(f"   Performance Metrics:")
        print(f"     Response Time: {loaded_entry.metrics.response_time_ms} ms")
        print(f"     Coherence Score: {loaded_entry.metrics.coherence_score}")
        print(f"     Relevance Score: {loaded_entry.metrics.relevance_score}")
        print(f"     Token Count: {loaded_entry.metrics.token_count}")
        print(f"     Complexity Score: {loaded_entry.metrics.complexity_score}")
        print(f"     Model Version: {loaded_entry.metrics.model_version}")
    
    # Verify key fields match
    assert loaded_entry.trace_id == "test-trace-001", "Trace ID mismatch"
    assert loaded_entry.sender_id == "gpt-4o", "Sender ID mismatch"
    assert loaded_entry.receiver_id == "gemini-1.5-flash", "Receiver ID mismatch"
    assert "capital of France" in loaded_entry.raw_output, "Raw output content mismatch"
    
    print("🎉 Protocol Buffer implementation working correctly!")

if __name__ == "__main__":
    test_protocol_buffer_implementation()
