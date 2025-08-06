#!/usr/bin/env python3
"""
Loopback Handler - Manages agent self-reflection and correction cycles.

This module provides a loopback system that handles rejected messages by
allowing agents to retry with revised prompts and corrections based on
mediator feedback.
"""

import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from odin_sdk import OdinMessage, OdinReflection
from mediator_ai import MediatorAI, ReflectionLogger, save_reflection


class LoopbackHandler:
    """
    Handles loopback logic for agent self-reflection and correction.
    
    When a mediator rejects or modifies a message, the LoopbackHandler
    manages the retry process, including prompt revision and correction
    metadata tracking.
    """
    
    def __init__(self, mediator: MediatorAI, max_iterations: int = 3,
                 reflection_logger: Optional[ReflectionLogger] = None):
        """
        Initialize the LoopbackHandler.
        
        Args:
            mediator: MediatorAI instance for message evaluation
            max_iterations: Maximum number of reflection iterations
            reflection_logger: Optional logger for analytics
        """
        self.mediator = mediator
        self.max_iterations = max_iterations
        self.reflection_logger = reflection_logger or ReflectionLogger()
        
        # Prompt templates for different correction types
        self.correction_prompts = {
            'low-confidence-language': "Please revise your response to be more definitive and confident. Avoid uncertain language.",
            'potential-hallucination': "Please revise your response to be more factual and evidence-based. Avoid speculation.",
            'high-semantic-drift': "Please revise your response to stay closer to the original topic and context.",
            'clarity-overly-long-sentences': "Please revise your response with shorter, clearer sentences.",
            'clarity-unclear-pronouns': "Please revise your response to clearly specify what pronouns refer to.",
            'clarity-complex-terminology': "Please revise your response using simpler, more accessible language."
        }
    
    def process_with_reflection(self, message: OdinMessage, 
                              agent_retry_function: Callable[[str, OdinMessage], OdinMessage]) -> tuple:
        """
        Process a message through the reflection loop.
        
        Args:
            message: Original OdinMessage to process
            agent_retry_function: Function to call for retrying message generation
                                 Signature: (correction_prompt, original_message) -> new_message
        
        Returns:
            tuple: (final_message, reflection_history, success)
        """
        reflection_history = []
        current_message = message
        iteration_count = 1
        
        while iteration_count <= self.max_iterations:
            # Get mediator evaluation
            reflection = self.mediator.evaluate(current_message, iteration_count)
            reflection_history.append(reflection)
            
            # Log the reflection
            self.reflection_logger.log_reflection(reflection)
            
            # Save reflection to file
            try:
                reflection_path = save_reflection(reflection)
                print(f"💾 Saved reflection to: {reflection_path}")
            except Exception as e:
                print(f"⚠️ Failed to save reflection: {e}")
            
            # Handle different actions
            if reflection.action_taken == "pass":
                print(f"✅ Message passed mediator evaluation on iteration {iteration_count}")
                return (current_message, reflection_history, True)
            
            elif reflection.action_taken == "modify":
                print(f"🔄 Message modified by mediator on iteration {iteration_count}")
                if reflection.HasField('healed'):
                    current_message = reflection.healed
                    iteration_count += 1
                    continue
                else:
                    # No healed message provided, treat as reject
                    reflection.action_taken = "reject"
            
            if reflection.action_taken == "reject":
                print(f"❌ Message rejected by mediator on iteration {iteration_count}: {reflection.explanation}")
                
                if iteration_count >= self.max_iterations:
                    print(f"🛑 Maximum iterations ({self.max_iterations}) reached. Giving up.")
                    return (current_message, reflection_history, False)
                
                # Generate correction prompt based on issues found
                correction_prompt = self._generate_correction_prompt(reflection)
                print(f"🔧 Requesting revision with prompt: {correction_prompt}")
                
                # Request agent to retry with correction prompt
                try:
                    revised_message = agent_retry_function(correction_prompt, current_message)
                    current_message = revised_message
                    iteration_count += 1
                except Exception as e:
                    print(f"⚠️ Agent retry failed: {e}")
                    return (current_message, reflection_history, False)
        
        print(f"🛑 Maximum iterations ({self.max_iterations}) reached without passing.")
        return (current_message, reflection_history, False)
    
    def _generate_correction_prompt(self, reflection: OdinReflection) -> str:
        """
        Generate a correction prompt based on the reflection feedback.
        
        Args:
            reflection: OdinReflection with correction tags and explanation
            
        Returns:
            str: Correction prompt for the agent
        """
        correction_parts = []
        
        # Add specific prompts based on correction tags
        for tag in reflection.correction_tags:
            if tag in self.correction_prompts:
                correction_parts.append(self.correction_prompts[tag])
        
        # Add general explanation
        if reflection.explanation:
            correction_parts.append(f"Reason: {reflection.explanation}")
        
        # Combine all correction guidance
        if correction_parts:
            prompt = " ".join(correction_parts)
            return f"Please revise your previous response. {prompt}"
        else:
            return "Please revise your previous response to address the identified issues."
    
    def get_iteration_metadata(self, reflection_history: List[OdinReflection]) -> Dict[str, Any]:
        """
        Extract metadata about the reflection iterations.
        
        Args:
            reflection_history: List of OdinReflection objects
            
        Returns:
            Dict with iteration metadata
        """
        if not reflection_history:
            return {}
        
        metadata = {
            'total_iterations': len(reflection_history),
            'final_action': reflection_history[-1].action_taken,
            'final_confidence': reflection_history[-1].confidence_score,
            'all_corrections': [],
            'confidence_trend': [],
            'iteration_explanations': []
        }
        
        for reflection in reflection_history:
            metadata['all_corrections'].extend(reflection.correction_tags)
            metadata['confidence_trend'].append(reflection.confidence_score)
            metadata['iteration_explanations'].append(reflection.explanation)
        
        # Remove duplicate corrections
        metadata['all_corrections'] = list(set(metadata['all_corrections']))
        
        return metadata


class AgentWithReflection:
    """
    Example agent wrapper that integrates with the loopback system.
    
    This demonstrates how to wrap an existing agent to support
    self-reflection and correction through the mediator system.
    """
    
    def __init__(self, agent_id: str, model_name: str, 
                 loopback_handler: LoopbackHandler):
        """
        Initialize the reflective agent.
        
        Args:
            agent_id: Unique identifier for this agent
            model_name: Name of the underlying AI model
            loopback_handler: LoopbackHandler for reflection management
        """
        self.agent_id = agent_id
        self.model_name = model_name
        self.loopback_handler = loopback_handler
    
    def generate_message(self, prompt: str, trace_id: str, 
                        receiver_id: str, context: str) -> tuple:
        """
        Generate a message with automatic reflection and correction.
        
        Args:
            prompt: Input prompt for message generation
            trace_id: Unique trace identifier
            receiver_id: ID of the receiving agent
            context: Conversation context
            
        Returns:
            tuple: (final_message, reflection_history, success)
        """
        # Create initial message (this would typically call your AI model)
        initial_message = self._create_odin_message(
            prompt, trace_id, receiver_id, context, 
            raw_output=self._simulate_agent_response(prompt)
        )
        
        # Process through reflection loop
        return self.loopback_handler.process_with_reflection(
            initial_message, self._retry_with_correction
        )
    
    def _create_odin_message(self, prompt: str, trace_id: str, 
                           receiver_id: str, context: str, 
                           raw_output: str) -> OdinMessage:
        """Create an OdinMessage from agent response."""
        from odin_format import create_odin_entry
        
        # This is a simplified version - adapt to your actual message creation
        return create_odin_entry(
            dialogue_id=trace_id,
            trace_id=trace_id,
            turn=1,
            source_model=self.agent_id,
            target_model=receiver_id,
            context=context,
            input_raw=prompt,
            input_repaired=prompt,
            input_translated=prompt,
            response_raw=raw_output,
            response_repaired=raw_output,
            response_translated=raw_output,
            metrics={'semantic_drift': 0.0, 'hallucination_score': 0.0, 'efficiency_gain': 0.0},
            metadata={'model': self.model_name}
        )
    
    def _retry_with_correction(self, correction_prompt: str, 
                             original_message: OdinMessage) -> OdinMessage:
        """
        Retry message generation with correction guidance.
        
        Args:
            correction_prompt: Guidance for correction
            original_message: Original message that was rejected
            
        Returns:
            OdinMessage: New attempt at the message
        """
        # Combine original prompt with correction guidance
        original_prompt = original_message.healing_metadata.notes if original_message.HasField('healing_metadata') else "Generate response"
        revised_prompt = f"{original_prompt}\n\nCORRECTION GUIDANCE: {correction_prompt}"
        
        # Generate new response (this would call your AI model with the revised prompt)
        new_output = self._simulate_agent_response(revised_prompt)
        
        # Create new message with correction metadata
        new_message = OdinMessage()
        new_message.CopyFrom(original_message)
        new_message.raw_output = new_output
        new_message.healed_output = new_output
        
        # Update healing metadata
        new_message.healing_metadata.notes = revised_prompt
        new_message.healing_metadata.iteration_count += 1
        new_message.healing_metadata.applied_rules.append("correction_applied")
        
        return new_message
    
    def _simulate_agent_response(self, prompt: str) -> str:
        """
        Simulate agent response generation.
        
        In a real implementation, this would call your actual AI model.
        """
        # This is just a placeholder - replace with actual model calls
        responses = [
            "I think this might be a reasonable approach to consider.",
            "Based on the available information, this appears to be correct.",
            "This is definitely the right answer with high confidence.",
            "The data shows clear evidence supporting this conclusion."
        ]
        
        # Simple logic to simulate different response qualities
        if "confident" in prompt.lower() or "definitive" in prompt.lower():
            return responses[2] if len(responses) > 2 else responses[-1]
        elif "factual" in prompt.lower() or "evidence" in prompt.lower():
            return responses[3] if len(responses) > 3 else responses[-1]
        else:
            return responses[0]  # Default to uncertain response for initial attempt
