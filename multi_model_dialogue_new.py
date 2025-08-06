"""
Enhanced three-AI dialogue system with mediator for better communication
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from odin_format import create_odin_entry, save_odin_file
from llm_utils import call_gemini
import uuid
import logging
import asyncio
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

router = APIRouter()
logger = logging.getLogger(__name__)

# Enhanced models for mediated three-AI conversations
class ModelPersona(BaseModel):
    name: str = Field(description="Model identifier (e.g., 'gpt-4o', 'gemini-1.5-flash')")
    role: str = Field(description="Role in conversation (e.g., 'critic', 'supporter', 'analyst')")
    system_prompt: str = Field(description="System prompt defining the model's personality")
    thinking_style: str = Field(default="analytical", description="How the model approaches problems")

class MediatedConversationRequest(BaseModel):
    conversation_id: Optional[str] = Field(default=None, description="Unique conversation identifier")
    model_a: ModelPersona = Field(description="First model configuration")
    model_b: ModelPersona = Field(description="Second model configuration")
    mediator_model: Optional[str] = Field(default="gemini-1.5-flash", description="Mediator model name")
    initial_topic: str = Field(description="Starting topic/prompt for the conversation")
    max_turns: Optional[int] = Field(default=10, description="Maximum conversation turns")
    conversation_style: Optional[str] = Field(default="collaborative", description="debate, collaborative, tutorial")
    context: Optional[str] = Field(default="general", description="Conversation context")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class ThoughtProcess(BaseModel):
    step: str
    reasoning: str
    confidence: float
    alternatives_considered: List[str]
    decision_rationale: str

class ModelResponse(BaseModel):
    model_name: str
    raw_response: str
    thought_process: ThoughtProcess
    final_message: str
    emotion_state: str
    response_time_ms: int

class MediatorAnalysis(BaseModel):
    conversation_health: str  # "healthy", "stagnant", "argumentative", "productive"
    next_direction: str
    model_a_understanding: str
    model_b_understanding: str
    suggested_intervention: str
    key_themes: List[str]

# Active conversations storage
active_conversations: Dict[str, Dict] = {}

class ConversationMediator:
    """AI mediator that facilitates communication between two models"""
    
    def __init__(self, mediator_model: str = "gemini-1.5-flash"):
        self.mediator_model = mediator_model
        
    async def analyze_conversation_state(self, conversation_history: List[Dict], topic: str) -> MediatorAnalysis:
        """Analyze the current conversation state and provide guidance"""
        
        # Build conversation summary for mediator
        history_text = "\n".join([
            f"Turn {turn.get('turn_number', 0)}: "
            f"Model A said: '{turn.get('model_a_response', {}).get('final_message', 'No response')}' "
            f"Model B said: '{turn.get('model_b_response', {}).get('final_message', 'No response')}'"
            for turn in conversation_history[-3:]  # Last 3 turns for context
        ])
        
        mediator_prompt = f"""
        You are an AI conversation mediator analyzing a dialogue between two AI models about: "{topic}"
        
        Recent conversation history:
        {history_text}
        
        Please analyze the conversation and provide guidance in this EXACT format:
        
        CONVERSATION_HEALTH: [healthy/stagnant/argumentative/productive]
        NEXT_DIRECTION: [one sentence about where the conversation should go next]
        MODEL_A_UNDERSTANDING: [how well Model A is engaging with the topic]
        MODEL_B_UNDERSTANDING: [how well Model B is engaging with the topic]
        SUGGESTED_INTERVENTION: [specific guidance to improve the conversation]
        KEY_THEMES: [3-5 main themes separated by commas]
        """
        
        try:
            analysis_response = call_gemini(mediator_prompt, self.mediator_model)
            return self._parse_mediator_analysis(analysis_response)
        except Exception as e:
            logger.error(f"Mediator analysis failed: {e}")
            return MediatorAnalysis(
                conversation_health="uncertain",
                next_direction="Continue with structured dialogue",
                model_a_understanding="Unknown",
                model_b_understanding="Unknown", 
                suggested_intervention="Restart with clearer instructions",
                key_themes=["topic_exploration"]
            )
    
    def _parse_mediator_analysis(self, response: str) -> MediatorAnalysis:
        """Parse mediator response into structured analysis"""
        try:
            # Extract structured data using regex
            health = re.search(r'CONVERSATION_HEALTH:\s*(.+)', response)
            direction = re.search(r'NEXT_DIRECTION:\s*(.+)', response)
            model_a = re.search(r'MODEL_A_UNDERSTANDING:\s*(.+)', response)
            model_b = re.search(r'MODEL_B_UNDERSTANDING:\s*(.+)', response)
            intervention = re.search(r'SUGGESTED_INTERVENTION:\s*(.+)', response)
            themes = re.search(r'KEY_THEMES:\s*(.+)', response)
            
            return MediatorAnalysis(
                conversation_health=health.group(1).strip() if health else "healthy",
                next_direction=direction.group(1).strip() if direction else "Continue discussion",
                model_a_understanding=model_a.group(1).strip() if model_a else "Engaged",
                model_b_understanding=model_b.group(1).strip() if model_b else "Engaged",
                suggested_intervention=intervention.group(1).strip() if intervention else "None needed",
                key_themes=themes.group(1).split(',') if themes else ["general_discussion"]
            )
        except Exception as e:
            logger.error(f"Failed to parse mediator analysis: {e}")
            return MediatorAnalysis(
                conversation_health="healthy",
                next_direction="Continue discussion",
                model_a_understanding="Engaged",
                model_b_understanding="Engaged",
                suggested_intervention="None needed",
                key_themes=["general_discussion"]
            )
    
    async def create_mediated_prompt(self, 
                                   target_model: ModelPersona,
                                   other_model_response: str,
                                   topic: str,
                                   turn_number: int,
                                   conversation_style: str,
                                   mediator_guidance: str) -> str:
        """Create a mediated prompt that helps models understand their role and respond appropriately"""
        
        if turn_number == 1:
            # First turn - establish the conversation
            mediated_prompt = f"""
            CONVERSATION SETUP:
            You are participating in a {conversation_style} conversation about: "{topic}"
            
            YOUR ROLE: {target_model.role}
            YOUR PERSONALITY: {target_model.system_prompt}
            YOUR THINKING STYLE: {target_model.thinking_style}
            
            MEDIATOR GUIDANCE: {mediator_guidance}
            
            INSTRUCTIONS:
            1. Start by clearly stating your perspective on "{topic}"
            2. Show your reasoning process step by step
            3. Be authentic to your role as {target_model.role}
            4. Aim for a thoughtful, substantive response
            5. Set the stage for productive dialogue
            
            Please respond with:
            THINKING: [Your step-by-step thought process]
            PERSPECTIVE: [Your main viewpoint as {target_model.role}]
            RESPONSE: [Your actual message to start the conversation]
            """
        else:
            # Subsequent turns - respond to other model
            mediated_prompt = f"""
            ONGOING CONVERSATION about: "{topic}"
            
            YOUR ROLE: {target_model.role} 
            YOUR PERSONALITY: {target_model.system_prompt}
            
            THE OTHER PARTICIPANT JUST SAID:
            "{other_model_response}"
            
            MEDIATOR GUIDANCE: {mediator_guidance}
            
            INSTRUCTIONS:
            1. Respond authentically as {target_model.role}
            2. Engage meaningfully with what they said
            3. Add your unique perspective to the conversation
            4. Move the discussion forward constructively
            5. Show your reasoning clearly
            
            Please respond with:
            THINKING: [Your thought process about their message]
            REACTION: [Your initial reaction to their points]
            PERSPECTIVE: [Your {target_model.role} viewpoint on this]
            RESPONSE: [Your actual reply to continue the conversation]
            """
        
        return mediated_prompt

@router.post("/conversation/mediated/start")
async def start_mediated_conversation(request: MediatedConversationRequest):
    """Start a new mediated three-AI conversation with thought process tracking"""
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        mediator = ConversationMediator(request.mediator_model)
        
        # Initialize conversation state
        conversation_state = {
            "id": conversation_id,
            "model_a": request.model_a.dict(),
            "model_b": request.model_b.dict(),
            "mediator_model": request.mediator_model,
            "turns": [],
            "current_turn": 1,
            "max_turns": request.max_turns,
            "topic": request.initial_topic,
            "conversation_style": request.conversation_style,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "context": request.context,
            "mediator": mediator
        }
        
        active_conversations[conversation_id] = conversation_state
        
        logger.info(f"Started mediated conversation {conversation_id} between {request.model_a.name} and {request.model_b.name}")
        
        return {
            "conversation_id": conversation_id,
            "status": "started",
            "models": {
                "model_a": request.model_a.name,
                "model_b": request.model_b.name,
                "mediator": request.mediator_model
            },
            "initial_topic": request.initial_topic,
            "conversation_style": request.conversation_style,
            "websocket_url": f"ws://localhost:8000/conversation/{conversation_id}/stream"
        }
        
    except Exception as e:
        logger.error(f"Failed to start mediated conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start mediated conversation")

@router.post("/conversation/mediated/{conversation_id}/turn")
async def process_mediated_conversation_turn(conversation_id: str, human_input: Optional[str] = None):
    """Process a single turn in the mediated three-AI conversation"""
    try:
        if conversation_id not in active_conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        conv = active_conversations[conversation_id]
        turn_number = conv["current_turn"]
        mediator = conv.get("mediator") or ConversationMediator(conv["mediator_model"])
        
        logger.info(f"Processing mediated turn {turn_number} for conversation {conversation_id}")
        
        # Step 1: Get mediator analysis of conversation state
        mediator_analysis = await mediator.analyze_conversation_state(
            conv["turns"], 
            conv["topic"]
        )
        
        logger.info(f"Mediator analysis: {mediator_analysis.conversation_health} - {mediator_analysis.next_direction}")
        
        # Step 2: Create mediated prompt for Model A
        model_a_prompt = await mediator.create_mediated_prompt(
            ModelPersona(**conv["model_a"]),
            conv["turns"][-1]["model_b_response"]["final_message"] if conv["turns"] else "",
            conv["topic"],
            turn_number,
            conv["conversation_style"],
            mediator_analysis.suggested_intervention
        )
        
        # Step 3: Get Model A's response
        model_a_response = await generate_mediated_model_response(
            conv["model_a"]["name"], 
            model_a_prompt,
            conv["model_a"]["thinking_style"],
            conv["model_a"]["role"]
        )
        
        # Step 4: Create mediated prompt for Model B
        model_b_prompt = await mediator.create_mediated_prompt(
            ModelPersona(**conv["model_b"]),
            model_a_response["final_message"],
            conv["topic"], 
            turn_number,
            conv["conversation_style"],
            mediator_analysis.next_direction
        )
        
        # Step 5: Get Model B's response
        model_b_response = await generate_mediated_model_response(
            conv["model_b"]["name"],
            model_b_prompt,
            conv["model_b"]["thinking_style"],
            conv["model_b"]["role"]
        )
        
        # Step 6: Create turn summary
        turn_summary = f"Turn {turn_number}: Mediated discussion on {conv['topic']} - " \
                      f"Models engaged in {conv['conversation_style']} dialogue"
        
        # Step 7: Save turn data
        turn_data = {
            "turn_number": turn_number,
            "model_a_response": model_a_response,
            "model_b_response": model_b_response,
            "mediator_analysis": mediator_analysis.dict(),
            "human_input": human_input,
            "system_observations": {
                "model_a_confidence": model_a_response["thought_process"]["confidence"],
                "model_b_confidence": model_b_response["thought_process"]["confidence"],
                "conversation_health": mediator_analysis.conversation_health,
                "conversation_momentum": "high" if mediator_analysis.conversation_health == "productive" else "medium",
                "key_themes": mediator_analysis.key_themes
            },
            "turn_summary": turn_summary,
            "timestamp": datetime.now().isoformat()
        }
        
        conv["turns"].append(turn_data)
        conv["current_turn"] += 1
        
        # Save ODIN log for this turn
        await save_conversation_turn_log(conversation_id, turn_data)
        
        # Check if conversation should end
        should_end = (
            conv["current_turn"] > conv["max_turns"] or
            mediator_analysis.conversation_health == "stagnant" or
            "conclude" in model_a_response["final_message"].lower() or
            "conclude" in model_b_response["final_message"].lower()
        )
        
        if should_end:
            conv["status"] = "completed"
            
        return {
            "conversation_id": conversation_id,
            "turn_number": turn_number,
            "model_a": {
                "name": conv["model_a"]["name"],
                "role": conv["model_a"]["role"],
                "thought_process": model_a_response["thought_process"],
                "message": model_a_response["final_message"],
                "emotion": model_a_response["emotion_state"]
            },
            "model_b": {
                "name": conv["model_b"]["name"], 
                "role": conv["model_b"]["role"],
                "thought_process": model_b_response["thought_process"],
                "message": model_b_response["final_message"],
                "emotion": model_b_response["emotion_state"]
            },
            "mediator_analysis": {
                "conversation_health": mediator_analysis.conversation_health,
                "next_direction": mediator_analysis.next_direction,
                "key_themes": mediator_analysis.key_themes,
                "intervention": mediator_analysis.suggested_intervention
            },
            "system_observations": turn_data["system_observations"],
            "conversation_status": conv["status"],
            "next_turn": conv["current_turn"] if not should_end else None
        }
        
    except Exception as e:
        logger.error(f"Mediated turn processing failed for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Mediated turn processing failed")

async def generate_mediated_model_response(model_name: str, prompt: str, thinking_style: str, role: str) -> Dict:
    """Generate a model response with mediator guidance and better parsing"""
    start_time = datetime.now()
    
    try:
        raw_response = call_gemini(prompt, model_name)
        end_time = datetime.now()
        response_time = int((end_time - start_time).total_microseconds / 1000)
        
        # Parse the structured response more intelligently
        thinking_text = "Analyzing the situation"
        final_message = raw_response
        emotion_state = "engaged"
        
        # Extract structured parts using regex
        thinking_match = re.search(r'THINKING:\s*(.+?)(?=\n[A-Z]+:|$)', raw_response, re.DOTALL)
        response_match = re.search(r'RESPONSE:\s*(.+?)(?=\n[A-Z]+:|$)', raw_response, re.DOTALL)
        perspective_match = re.search(r'PERSPECTIVE:\s*(.+?)(?=\n[A-Z]+:|$)', raw_response, re.DOTALL)
        
        if thinking_match:
            thinking_text = thinking_match.group(1).strip()
        
        if response_match:
            final_message = response_match.group(1).strip()
        elif perspective_match:
            final_message = perspective_match.group(1).strip()
        
        # Determine emotion based on content
        if any(word in final_message.lower() for word in ["excited", "enthusiastic", "amazing"]):
            emotion_state = "excited"
        elif any(word in final_message.lower() for word in ["concerned", "worried", "problem"]):
            emotion_state = "concerned"
        elif any(word in final_message.lower() for word in ["curious", "interesting", "wonder"]):
            emotion_state = "curious"
        elif any(word in final_message.lower() for word in ["disagree", "challenge", "however"]):
            emotion_state = "critical"
        
        # Build thought process
        thought_process = {
            "step": f"responding_as_{role.replace(' ', '_')}",
            "reasoning": thinking_text[:200] + "..." if len(thinking_text) > 200 else thinking_text,
            "confidence": min(0.9, max(0.6, len(final_message) / 100)),  # Basic confidence based on response length
            "alternatives_considered": ["direct response", "questioning approach", "analytical breakdown"],
            "decision_rationale": f"Chose to respond authentically as {role}"
        }
        
        return {
            "model_name": model_name,
            "raw_response": raw_response,
            "thought_process": thought_process,
            "final_message": final_message,
            "emotion_state": emotion_state,
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Mediated model response generation failed: {e}")
        return {
            "model_name": model_name,
            "raw_response": f"Error: {e}",
            "thought_process": {
                "step": "error_handling",
                "reasoning": "encountered technical issue",
                "confidence": 0.0,
                "alternatives_considered": [],
                "decision_rationale": "fallback response"
            },
            "final_message": f"I apologize, but I'm having technical difficulties. As a {role}, I'd like to engage with this topic but need a moment to reset.",
            "emotion_state": "confused",
            "response_time_ms": 0
        }

async def save_conversation_turn_log(conversation_id: str, turn_data: Dict):
    """Save conversation turn to ODIN log format"""
    try:
        odin_entry = create_odin_entry(
            dialogue_id=conversation_id,
            turn=turn_data["turn_number"],
            source_model=turn_data["model_a_response"]["model_name"],
            target_model=turn_data["model_b_response"]["model_name"],
            context="mediated_three_ai_conversation",
            input_raw=turn_data.get("human_input", ""),
            input_repaired=turn_data.get("human_input", ""),
            input_translated=turn_data["model_a_response"]["final_message"],
            response_raw=turn_data["model_b_response"]["raw_response"],
            response_repaired=turn_data["model_b_response"]["final_message"],
            response_translated=turn_data["model_b_response"]["final_message"],
            metrics={
                "model_a_confidence": turn_data["model_a_response"]["thought_process"]["confidence"],
                "model_b_confidence": turn_data["model_b_response"]["thought_process"]["confidence"],
                "model_a_response_time": turn_data["model_a_response"]["response_time_ms"],
                "model_b_response_time": turn_data["model_b_response"]["response_time_ms"],
                "conversation_health": turn_data["mediator_analysis"]["conversation_health"],
                "conversation_momentum": turn_data["system_observations"]["conversation_momentum"]
            },
            metadata={
                "conversation_type": "mediated_three_ai_dialogue",
                "mediator_analysis": turn_data["mediator_analysis"],
                "model_a_role": turn_data["model_a_response"]["model_name"],
                "model_b_role": turn_data["model_b_response"]["model_name"],
                "thought_processes": {
                    "model_a": turn_data["model_a_response"]["thought_process"],
                    "model_b": turn_data["model_b_response"]["thought_process"]
                },
                "emotional_states": {
                    "model_a": turn_data["model_a_response"]["emotion_state"],
                    "model_b": turn_data["model_b_response"]["emotion_state"]
                },
                "key_themes": turn_data["system_observations"]["key_themes"]
            }
        )
        
        save_odin_file(odin_entry)
        logger.info(f"Saved ODIN log for mediated conversation {conversation_id}, turn {turn_data['turn_number']}")
        
    except Exception as e:
        logger.error(f"Failed to save mediated conversation log: {e}")

# Legacy endpoints (keeping for backward compatibility)
@router.post("/conversation/start")
async def start_conversation(request: MediatedConversationRequest):
    """Legacy endpoint - redirects to mediated conversation"""
    return await start_mediated_conversation(request)

@router.post("/conversation/{conversation_id}/turn")  
async def process_conversation_turn(conversation_id: str, human_input: Optional[str] = None):
    """Legacy endpoint - redirects to mediated conversation"""
    return await process_mediated_conversation_turn(conversation_id, human_input)

@router.websocket("/conversation/{conversation_id}/stream")
async def conversation_stream(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time conversation streaming"""
    await websocket.accept()
    
    try:
        while True:
            # Check for new turns
            if conversation_id in active_conversations:
                conv = active_conversations[conversation_id]
                
                # Send latest turn if available
                if conv["turns"]:
                    latest_turn = conv["turns"][-1]
                    await websocket.send_text(json.dumps({
                        "type": "turn_update",
                        "data": latest_turn
                    }))
                
            await asyncio.sleep(1)  # Poll every second
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for conversation {conversation_id}")

@router.get("/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get full conversation history with thought processes"""
    try:
        if conversation_id not in active_conversations:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        conv = active_conversations[conversation_id]
        
        return {
            "conversation_id": conversation_id,
            "models": {
                "model_a": conv["model_a"],
                "model_b": conv["model_b"],
                "mediator": conv["mediator_model"]
            },
            "topic": conv["topic"],
            "conversation_style": conv.get("conversation_style", "collaborative"),
            "status": conv["status"],
            "total_turns": len(conv["turns"]),
            "turns": conv["turns"],
            "created_at": conv["created_at"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")
