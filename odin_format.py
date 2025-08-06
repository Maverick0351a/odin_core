"""
ODIN Protocol Format - Protocol Buffer Implementation
Enhanced logging format for AI-to-AI communication with binary serialization
"""

import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

# Import the new Protocol Buffer SDK
try:
    from odin_sdk import OdinSDK, OdinMessage, OdinMessageBuilder
except ImportError:
    print("❌ ODIN SDK not found. Please run 'python odin_cli.py compile' first.")
    raise

def create_odin_entry(
    dialogue_id: str,
    turn: int,
    source_model: str,
    target_model: str,
    context: str,
    input_raw: str,
    input_repaired: str,
    input_translated: str,
    response_raw: str,
    response_repaired: str,
    response_translated: str,
    metrics: Dict[str, Any],
    trace_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> OdinMessage:
    """
    Create an ODIN Protocol Buffer message with all required fields
    
    Args:
        dialogue_id: Unique identifier for the conversation
        turn: Turn number in the conversation
        source_model: ID of the sending AI model
        target_model: ID of the receiving AI model
        context: Context/topic of the conversation
        input_raw: Original unprocessed input
        input_repaired: Processed/corrected input
        input_translated: Translated input for the target model
        response_raw: Original model response
        response_repaired: Processed/corrected response
        response_translated: Final translated response
        metrics: Performance and quality metrics
        trace_id: Optional trace identifier (defaults to dialogue_id)
        metadata: Additional metadata
    
    Returns:
        OdinMessage: Protocol Buffer message object
    """
    
    # Create message builder
    builder = OdinSDK.create_message()
    
    # Set core identifiers
    session_id = metadata.get("session_id", dialogue_id) if metadata else dialogue_id
    builder.set_ids(
        trace_id=trace_id or dialogue_id,
        session_id=session_id,
        sender_id=source_model,
        receiver_id=target_model
    )
    
    # Determine role from metadata or default to assistant
    role = "assistant"
    if metadata:
        role = metadata.get("role", "assistant")
        if "mediator" in context.lower():
            role = "mediator"
        elif "tool" in source_model.lower():
            role = "tool"
        elif "user" in source_model.lower():
            role = "user"
    
    builder.set_role(role)
    
    # Set content (use translated versions as primary content)
    builder.set_content(
        raw_output=response_raw,
        healed_output=response_translated
    )
    
    # Calculate semantic drift score
    semantic_drift = calculate_semantic_drift(response_raw, response_translated)
    builder.set_semantic_drift(semantic_drift)
    
    # Set healing metadata
    healing_method = metadata.get("healing_method", "auto_process") if metadata else "auto_process"
    healing_confidence = metrics.get("confidence", 0.8)
    healing_notes = f"Input: {input_raw[:100]}..." if len(input_raw) > 100 else input_raw
    
    builder.set_healing_metadata(
        method=healing_method,
        confidence=healing_confidence,
        source_doc_id=metadata.get("source_document_id", "") if metadata else "",
        notes=healing_notes,
        applied_rules=metadata.get("applied_rules", []) if metadata else [],
        iteration_count=metadata.get("iteration_count", 1) if metadata else 1
    )
    
    # Set conversation context
    conversation_type = metadata.get("conversation_type", "dialogue") if metadata else "dialogue"
    key_themes = metadata.get("key_themes", []) if metadata else []
    emotional_state = metadata.get("emotional_state", "neutral") if metadata else "neutral"
    
    builder.set_conversation_context(
        conversation_id=dialogue_id,
        turn_number=turn,
        conversation_type=conversation_type,
        topic=context,
        key_themes=key_themes,
        emotional_state=emotional_state
    )
    
    # Set performance metrics
    response_time = metrics.get("response_time_ms", 0)
    model_version = metadata.get("model_version", source_model) if metadata else source_model
    
    builder.set_performance_metrics(
        response_time_ms=response_time,
        coherence_score=metrics.get("coherence_score", 0.0),
        relevance_score=metrics.get("relevance_score", 0.0),
        token_count=metrics.get("token_count", len(response_raw.split())),
        complexity_score=metrics.get("complexity_score", 0.0),
        model_version=model_version
    )
    
    return builder.build()

def calculate_semantic_drift(original: str, processed: str) -> float:
    """
    Calculate semantic drift between original and processed text
    Simple implementation based on text similarity
    
    Returns:
        float: Drift score between 0.0 (identical) and 1.0 (completely different)
    """
    if not original or not processed:
        return 1.0
    
    if original == processed:
        return 0.0
    
    # Simple character-based similarity
    original_words = set(original.lower().split())
    processed_words = set(processed.lower().split())
    
    if not original_words:
        return 1.0
    
    intersection = original_words.intersection(processed_words)
    union = original_words.union(processed_words)
    
    if not union:
        return 1.0
    
    similarity = len(intersection) / len(union)
    drift = 1.0 - similarity
    
    return min(1.0, max(0.0, drift))

def save_odin_file(message: OdinMessage, directory: str = "logs") -> str:
    """
    Save ODIN Protocol Buffer message to binary file
    
    Args:
        message: OdinMessage Protocol Buffer object
        directory: Directory to save the file
    
    Returns:
        str: Path to the saved file
    """
    os.makedirs(directory, exist_ok=True)
    filename = f"{message.context.conversation_id}_turn{message.context.turn_number}.odin"
    filepath = os.path.join(directory, filename)
    
    if OdinSDK.save_message(message, filepath):
        return filepath
    else:
        raise IOError(f"Failed to save ODIN message to {filepath}")

def load_odin_file(filepath: str) -> Optional[OdinMessage]:
    """
    Load ODIN Protocol Buffer message from binary file
    
    Args:
        filepath: Path to the .odin file
    
    Returns:
        OdinMessage: Loaded Protocol Buffer message or None if failed
    """
    return OdinSDK.load_message(filepath)

def validate_odin_format(message: OdinMessage) -> bool:
    """
    Validate ODIN Protocol Buffer message has required fields
    
    Args:
        message: OdinMessage to validate
    
    Returns:
        bool: True if valid, raises ValueError if invalid
    """
    required_fields = [
        ("trace_id", message.trace_id),
        ("session_id", message.session_id),
        ("sender_id", message.sender_id),
        ("receiver_id", message.receiver_id),
        ("role", message.role),
        ("raw_output", message.raw_output)
    ]
    
    missing = [field for field, value in required_fields if not value]
    
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    
    if message.timestamp <= 0:
        raise ValueError("Invalid timestamp")
    
    if not (0.0 <= message.semantic_drift_score <= 1.0):
        raise ValueError("semantic_drift_score must be between 0.0 and 1.0")
    
    return True

# Legacy compatibility functions
def create_odin_entry_legacy(
    dialogue_id: str,
    turn: int,
    source_model: str,
    target_model: str,
    context: str,
    input_raw: str,
    input_repaired: str,
    input_translated: str,
    response_raw: str,
    response_repaired: str,
    response_translated: str,
    metrics: dict,
    trace_id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> dict:
    """
    Legacy function that returns a dict instead of Protocol Buffer
    Maintained for backward compatibility
    """
    return {
        "type": "odin-message",
        "protocol_version": "2.0-protobuf",
        "dialogue_id": dialogue_id,
        "trace_id": trace_id or dialogue_id,
        "turn": turn,
        "source_model": source_model,
        "target_model": target_model,
        "context": context,
        "input": {
            "raw": input_raw,
            "repaired": input_repaired,
            "translated": input_translated
        },
        "response": {
            "raw": response_raw,
            "repaired": response_repaired,
            "translated": response_translated
        },
        "metrics": metrics,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
