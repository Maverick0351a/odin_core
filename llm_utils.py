from google.cloud import aiplatform
from vertexai.preview.language_models import ChatModel
import json
import logging

logger = logging.getLogger("odin-llm")

def init_gemini(project_id: str, location: str = "us-central1"):
    try:
        aiplatform.init(project=project_id, location=location)
        logger.info("✅ Vertex AI initialized")
    except Exception as e:
        logger.error(f"❌ Failed to init Vertex AI: {e}")
        raise e

def call_gemini(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    try:
        logger.debug(f"Calling Gemini with model: {model_name}")
        model = ChatModel.from_pretrained(f"models/{model_name}")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        
        if not response or not response.text:
            logger.warning("⚠️ Gemini returned empty response")
            return "No response generated"
            
        result = response.text.strip()
        logger.debug(f"Gemini response received: {len(result)} characters")
        return result
        
    except AttributeError as e:
        logger.error(f"❌ Gemini model attribute error: {e}")
        raise Exception(f"Model access error: {e}")
        
    except Exception as e:
        logger.error(f"❌ Gemini call failed: {type(e).__name__}: {e}")
        print(f"❌ Gemini API Error: {type(e).__name__}: {e}")
        raise e

def call_gemini_json(prompt: str) -> dict:
    try:
        response = call_gemini(prompt)
        return json.loads(response)
    except json.JSONDecodeError:
        logger.warning("⚠️ Gemini response was not valid JSON")
        return {"error": "invalid_json", "raw": response}
