#!/usr/bin/env python3
"""
Basic API tests for ODIN Protocol endpoints.
"""

import pytest
import json
from fastapi.testclient import TestClient


def test_imports():
    """Test that all modules import correctly."""
    # Test configuration
    from config import get_settings
    settings = get_settings()
    assert settings is not None
    assert settings.gemini_project_id == "clarifyai-466505"
    
    # Test main app
    from main import app
    assert app is not None
    
    # Test ODIN SDK
    from odin_sdk import OdinMessage, OdinReflection, OdinSDK
    assert OdinMessage is not None
    assert OdinReflection is not None
    assert OdinSDK is not None
    
    # Test mediator AI
    from mediator_ai import MediatorAI
    mediator = MediatorAI()
    assert mediator is not None
    
    print("✅ All modules import successfully")


def test_health_endpoint():
    """Test the health check endpoint."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code in [200, 503]  # Allow degraded state
    
    data = response.json()
    assert data["service"] == "ODIN Protocol"
    assert data["version"] == "2.0"
    assert "features" in data
    assert "self_reflection_system" in data["features"]
    
    print("✅ Health endpoint working")


def test_config_endpoint():
    """Test the configuration endpoint."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/config")
    assert response.status_code == 200
    
    data = response.json()
    assert "max_conversation_turns" in data
    assert "mediator_confidence_threshold" in data
    assert data["max_conversation_turns"] == 50
    
    print("✅ Config endpoint working")


def test_conversation_viewer():
    """Test the conversation viewer endpoint."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/conversation-viewer")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    content = response.text
    assert "ODIN Protocol 2.0" in content
    assert "Conversation Observatory" in content
    
    print("✅ Conversation viewer working")


def test_demo_data():
    """Test the demo data endpoint."""
    from main import app
    client = TestClient(app)
    
    response = client.get("/conversation-viewer/demo")
    assert response.status_code == 200
    
    data = response.json()
    assert "conversation" in data
    assert "summary" in data
    assert "total_turns" in data["summary"]
    assert "total_reflections" in data["summary"]
    
    print("✅ Demo data endpoint working")


def test_mediator_ai_validation():
    """Test mediator AI input validation."""
    from mediator_ai import MediatorAI
    from odin_sdk import OdinMessage
    
    mediator = MediatorAI()
    
    # Test with invalid message (empty)
    empty_message = OdinMessage()
    
    with pytest.raises(ValueError):
        mediator.evaluate(empty_message)
    
    # Test with invalid iteration count
    from odin_format import create_odin_entry
    valid_message = create_odin_entry(
        dialogue_id="test",
        trace_id="test",
        turn=1,
        source_model="test",
        target_model="test",
        context="test",
        input_raw="test",
        input_repaired="test", 
        input_translated="test",
        response_raw="test",
        response_repaired="test",
        response_translated="test",
        metrics={},
        metadata={}
    )
    
    with pytest.raises(ValueError):
        mediator.evaluate(valid_message, iteration_count=0)
    
    print("✅ Mediator AI validation working")


if __name__ == "__main__":
    print("🧪 Running basic API tests...")
    
    try:
        test_imports()
        test_health_endpoint()
        test_config_endpoint()
        test_conversation_viewer()
        test_demo_data()
        test_mediator_ai_validation()
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
