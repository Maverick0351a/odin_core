"""
Test file for ODIN Protocol dialogue endpoint
Run with: python -m pytest test_dialogue.py -v
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from odin_core.main import app

client = TestClient(app)

# Test data
VALID_REQUEST = {
    "source_model": {"name": "gpt-4o"},
    "target_model": {"name": "gemini-1.5-flash"},
    "message": "Summarize clause 4",
    "context": "legal summary",
    "turn": 1,
    "metadata": {"session": "test"}
}

class TestDialogueEndpoint:
    
    def test_dialogue_success_path(self):
        """Test successful dialogue processing"""
        with patch('odin_core.llm_utils.call_gemini') as mock_gemini, \
             patch('odin_core.odin_format.create_odin_entry') as mock_create, \
             patch('odin_core.odin_format.save_odin_file') as mock_save:
            
            # Mock successful responses
            mock_gemini.side_effect = [
                "Translated input for gemini-1.5-flash",
                "Clause 4 limits liability to $10,000"
            ]
            mock_create.return_value = {"test": "entry"}
            mock_save.return_value = "/logs/test_dialogue_turn1.odin"
            
            response = client.post("/dialogue", json=VALID_REQUEST)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "dialogue_id" in data
            assert "input_translated" in data
            assert "target_response" in data
            assert "healing_metrics" in data
            assert data["turn"] == 1

    def test_dialogue_missing_source_model_name(self):
        """Test error when source_model missing 'name' key"""
        invalid_request = VALID_REQUEST.copy()
        invalid_request["source_model"] = {"model": "gpt-4o"}  # wrong key
        
        response = client.post("/dialogue", json=invalid_request)
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"

    def test_dialogue_missing_target_model_name(self):
        """Test error when target_model missing 'name' key"""
        invalid_request = VALID_REQUEST.copy()
        invalid_request["target_model"] = {"model": "gemini"}  # wrong key
        
        response = client.post("/dialogue", json=invalid_request)
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"

    def test_dialogue_gemini_translation_failure(self):
        """Test error when Gemini translation fails"""
        with patch('odin_core.llm_utils.call_gemini') as mock_gemini:
            mock_gemini.side_effect = Exception("Gemini API timeout")
            
            response = client.post("/dialogue", json=VALID_REQUEST)
            assert response.status_code == 500
            assert response.json()["detail"] == "Input translation failed"

    def test_dialogue_gemini_response_failure(self):
        """Test error when Gemini response generation fails"""
        with patch('odin_core.llm_utils.call_gemini') as mock_gemini:
            # First call succeeds, second fails
            mock_gemini.side_effect = [
                "Translated input",
                Exception("Gemini overloaded")
            ]
            
            response = client.post("/dialogue", json=VALID_REQUEST)
            assert response.status_code == 500
            assert response.json()["detail"] == "Response generation failed"

    def test_dialogue_odin_logging_failure(self):
        """Test error when ODIN logging fails"""
        with patch('odin_core.llm_utils.call_gemini') as mock_gemini, \
             patch('odin_core.odin_format.create_odin_entry') as mock_create:
            
            mock_gemini.side_effect = ["Translated", "Response"]
            mock_create.side_effect = Exception("Disk full")
            
            response = client.post("/dialogue", json=VALID_REQUEST)
            assert response.status_code == 500
            assert response.json()["detail"] == "Log entry creation failed"

    def test_dialogue_file_save_failure(self):
        """Test error when file save fails"""
        with patch('odin_core.llm_utils.call_gemini') as mock_gemini, \
             patch('odin_core.odin_format.create_odin_entry') as mock_create, \
             patch('odin_core.odin_format.save_odin_file') as mock_save:
            
            mock_gemini.side_effect = ["Translated", "Response"]
            mock_create.return_value = {"test": "entry"}
            mock_save.side_effect = Exception("Permission denied")
            
            response = client.post("/dialogue", json=VALID_REQUEST)
            assert response.status_code == 500
            assert response.json()["detail"] == "Log file save failed"

    def test_dialogue_invalid_json_payload(self):
        """Test validation errors with invalid JSON structure"""
        invalid_requests = [
            {},  # Empty payload
            {"message": "test"},  # Missing required fields
            {"message": "", "source_model": {}, "target_model": {}},  # Empty message
        ]
        
        for invalid_request in invalid_requests:
            response = client.post("/dialogue", json=invalid_request)
            assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    # Simple manual test
    print("Running manual test...")
    response = client.post("/dialogue", json=VALID_REQUEST)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
