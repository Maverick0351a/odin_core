from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from odin_format import create_odin_entry, save_odin_file
from llm_utils import call_gemini
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any


class DialogueRequest(BaseModel):
    dialogue_id: Optional[str] = Field(default=None, description="Unique dialogue identifier")
    trace_id: Optional[str] = Field(default=None, description="Trace identifier for tracking")
    turn: Optional[int] = Field(default=1, description="Turn number in the dialogue")
    source_model: Dict[str, str] = Field(description="Source model with 'name' key")
    target_model: Dict[str, str] = Field(description="Target model with 'name' key")
    context: Optional[str] = Field(default="general", description="Dialogue context")
    message: str = Field(description="Input message to process")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/dialogue")
async def dialogue(body: DialogueRequest):
    dialogue_id = None
    trace_id = None
    
    try:
        # Step 0: Initialize IDs and validate input
        logger.info("Processing new dialogue request")
        dialogue_id = body.dialogue_id or str(uuid.uuid4())
        trace_id = body.trace_id or dialogue_id
        
        # Validate model structure
        if "name" not in body.source_model:
            raise ValueError("source_model must contain 'name' key")
        if "name" not in body.target_model:
            raise ValueError("target_model must contain 'name' key")
            
        source_model = body.source_model["name"]
        target_model = body.target_model["name"]
        context = body.context
        message = body.message
        turn = body.turn
        
        logger.info(f"Processing dialogue {dialogue_id}, turn {turn}, source: {source_model}, target: {target_model}")

        # Step 1: Input preparation and translation
        try:
            input_repaired = message.strip()
            logger.debug(f"Input prepared: {input_repaired[:100]}...")
            
            input_translated = call_gemini(f"Translate this input for {target_model}: {message}")
            logger.info(f"Input translation completed for dialogue {dialogue_id}")
            
        except Exception as e:
            logger.error(f"Input translation failed for dialogue {dialogue_id}: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail="Input translation failed")

        # Step 2: Generate target model response
        try:
            target_response = call_gemini(f"{target_model}, respond to: {input_translated}")
            response_repaired = target_response.strip()
            response_translated = target_response
            logger.info(f"Target response generated for dialogue {dialogue_id}")
            
        except Exception as e:
            logger.error(f"Target response generation failed for dialogue {dialogue_id}: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail="Response generation failed")

        # Step 3: Calculate healing metrics (simulated for now)
        try:
            healing_metrics = {
                "semantic_drift": 0.05,
                "hallucination_score": 0.02,
                "efficiency_gain": 0.15,
                "translation_quality": 0.92,
                "coherence_score": 0.88
            }
            logger.debug(f"Healing metrics calculated for dialogue {dialogue_id}")
            
        except Exception as e:
            logger.error(f"Metrics calculation failed for dialogue {dialogue_id}: {type(e).__name__}: {e}")
            healing_metrics = {"error": "metrics_calculation_failed"}

        # Step 4: Create ODIN entry for logging
        try:
            base_metadata = {
                "trace_id": trace_id, 
                "timestamp": datetime.now().isoformat(),
                "source_model": source_model,
                "target_model": target_model
            }
            if body.metadata:
                base_metadata.update(body.metadata)
                
            odin_entry = create_odin_entry(
                dialogue_id=dialogue_id,
                turn=turn,
                source_model=source_model,
                target_model=target_model,
                context=context,
                input_raw=message,
                input_repaired=input_repaired,
                input_translated=input_translated,
                response_raw=target_response,
                response_repaired=response_repaired,
                response_translated=response_translated,
                metrics=healing_metrics,
                metadata=base_metadata
            )
            logger.debug(f"ODIN entry created for dialogue {dialogue_id}")
            
        except Exception as e:
            logger.error(f"ODIN entry creation failed for dialogue {dialogue_id}: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail="Log entry creation failed")

        # Step 5: Save ODIN log file
        try:
            log_file_path = save_odin_file(odin_entry)
            logger.info(f"ODIN log saved to {log_file_path} for dialogue {dialogue_id}")
            
        except Exception as e:
            logger.error(f"ODIN log file save failed for dialogue {dialogue_id}: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail="Log file save failed")

        # Step 6: Return structured response
        logger.info(f"Dialogue {dialogue_id} processed successfully")
        return {
            "dialogue_id": dialogue_id,
            "turn": turn,
            "input_translated": input_translated,
            "target_response": target_response,
            "healing_metrics": healing_metrics,
            "log_file": log_file_path,
            "status": "success",
            "trace_id": trace_id
        }

    except HTTPException:
        # Re-raise HTTP exceptions (already handled above)
        raise
        
    except KeyError as e:
        logger.error(f"Missing required key in dialogue {dialogue_id or 'unknown'}: {e}")
        print(f"❌ KeyError in /dialogue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    except ValueError as e:
        logger.error(f"Invalid value in dialogue {dialogue_id or 'unknown'}: {e}")
        print(f"❌ ValueError in /dialogue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    except TypeError as e:
        logger.error(f"Type error in dialogue {dialogue_id or 'unknown'}: {e}")
        print(f"❌ TypeError in /dialogue: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        
    except Exception as e:
        logger.error(f"Unexpected error in dialogue {dialogue_id or 'unknown'}: {type(e).__name__}: {e}")
        print(f"❌ Unexpected error in /dialogue: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
