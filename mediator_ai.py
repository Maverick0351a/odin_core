#!/usr/bin/env python3
"""
MediatorAI - Agent self-dialogue and reflection system for ODIN Protocol.

This module provides a Mediator AI that can evaluate OdinMessages and provide
feedback through an OdinReflection message. The mediator can pass, modify, or
reject messages based on confidence, hallucination risk, and semantic drift.
"""

import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import json
import asyncio

from odin_sdk import OdinMessage, OdinReflection
from odin_sdk.enhanced import OdinMessageBuilder, OdinSDK
from rules_engine import RuleEngine, RuleAction, get_rule_engine


class MediatorAI:
    """
    Mediator AI for agent self-dialogue and message reflection.
    
    The MediatorAI evaluates OdinMessages and provides feedback through
    OdinReflection objects. It can identify issues and suggest corrections
    to improve message quality and reduce hallucination risk.
    """
    
    def __init__(self, mediator_id: str = "mediator-ai-v1", 
                 confidence_threshold: float = 0.7,
                 semantic_drift_threshold: float = 0.3,
                 rules_config_path: Optional[str] = None):
        """
        Initialize the MediatorAI.
        
        Args:
            mediator_id: Unique identifier for this mediator instance
            confidence_threshold: Minimum confidence score to pass a message
            semantic_drift_threshold: Maximum semantic drift to allow
            rules_config_path: Path to YAML rules configuration file
        """
        self.mediator_id = mediator_id
        self.confidence_threshold = confidence_threshold
        self.semantic_drift_threshold = semantic_drift_threshold
        
        # Initialize Rule Engine
        self.rule_engine = get_rule_engine(rules_config_path)
        
        # Register custom handlers for ODIN-specific rules
        self._register_custom_handlers()
        
        # Patterns that indicate potential issues
        self.hallucination_patterns = [
            r'\b(?:I think|I believe|I assume|probably|maybe|might be)\b',
            r'\b(?:not sure|uncertain|unclear|confusing)\b',
            r'\b(?:seems like|appears to|could be)\b'
        ]
        
        self.low_confidence_patterns = [
            r'\b(?:I don\'t know|I\'m not certain|I can\'t say)\b',
            r'\b(?:it\'s possible|it might|perhaps)\b'
        ]
        
        # Tags for common correction types
        self.correction_tags = {
            'confidence': 'low-confidence-language',
            'hallucination': 'potential-hallucination',
            'semantic_drift': 'high-semantic-drift',
            'clarity': 'unclear-language',
            'factual': 'factual-correction',
            'tone': 'tone-adjustment'
        }
    
    def _register_custom_handlers(self):
        """Register custom rule handlers for ODIN Protocol."""
        
        def odin_confidence_handler(context: Dict[str, Any], rule) -> Dict[str, Any]:
            """Custom handler for ODIN confidence-based decisions."""
            confidence = context.get("confidence", 0.0)
            
            if confidence >= 0.9:
                return {
                    "action": "approve",
                    "reason": f"High confidence score: {confidence}",
                    "bypass_further_checks": True
                }
            elif confidence <= 0.3:
                return {
                    "action": "reject",
                    "reason": f"Very low confidence: {confidence}",
                    "suggest_retry": True
                }
            else:
                return {
                    "action": "continue",
                    "reason": f"Moderate confidence: {confidence}"
                }
        
        def odin_semantic_drift_handler(context: Dict[str, Any], rule) -> Dict[str, Any]:
            """Custom handler for semantic drift detection."""
            drift_score = context.get("semantic_drift_score", 0.0)
            threshold = self.semantic_drift_threshold
            
            if drift_score > threshold * 2:  # High drift
                return {
                    "action": "escalate",
                    "reason": f"High semantic drift: {drift_score} (threshold: {threshold})",
                    "requires_human_review": True
                }
            elif drift_score > threshold:  # Medium drift
                return {
                    "action": "retry",
                    "reason": f"Semantic drift detected: {drift_score}",
                    "healing_recommended": True
                }
            else:
                return {
                    "action": "continue",
                    "reason": f"Acceptable semantic drift: {drift_score}"
                }
        
        def odin_hallucination_handler(context: Dict[str, Any], rule) -> Dict[str, Any]:
            """Custom handler for hallucination risk assessment."""
            risk_score = context.get("hallucination_risk", 0.0)
            
            if risk_score > 0.7:
                return {
                    "action": "reject",
                    "reason": f"High hallucination risk: {risk_score}",
                    "requires_regeneration": True
                }
            elif risk_score > 0.4:
                return {
                    "action": "retry",
                    "reason": f"Moderate hallucination risk: {risk_score}",
                    "apply_healing": True
                }
            else:
                return {
                    "action": "continue",
                    "reason": f"Low hallucination risk: {risk_score}"
                }
        
        # Register the custom handlers
        self.rule_engine.register_custom_handler("odin_confidence_handler", odin_confidence_handler)
        self.rule_engine.register_custom_handler("odin_semantic_drift_handler", odin_semantic_drift_handler)
        self.rule_engine.register_custom_handler("odin_hallucination_handler", odin_hallucination_handler)
    
    def evaluate(self, message: OdinMessage, iteration_count: int = 1) -> OdinReflection:
        """
        Evaluate an OdinMessage and return an OdinReflection with feedback.
        
        Args:
            message: The OdinMessage to evaluate
            iteration_count: Current iteration count for this message
            
        Returns:
            OdinReflection: Contains evaluation results and any corrections
            
        Raises:
            ValueError: If message is invalid or too large
        """
        # Validate input
        if not self._validate_message(message):
            raise ValueError("Invalid OdinMessage provided")
        
        if iteration_count < 1:
            raise ValueError("Iteration count must be at least 1")
        
        # Perform various evaluation checks
        confidence_score = self._calculate_confidence(message)
        hallucination_risk = self._assess_hallucination_risk(message)
        semantic_issues = self._check_semantic_drift(message)
        clarity_issues = self._assess_clarity(message)
        
        # Create context for rule engine evaluation
        rule_context = self._create_rule_context(
            message, confidence_score, hallucination_risk, semantic_issues, clarity_issues, iteration_count
        )
        
        # Evaluate rules using the rule engine
        rule_results = self.rule_engine.evaluate_rules(rule_context)
        
        # Determine final action based on rule results and traditional evaluation
        action_taken, healed_message, explanation, corrections = self._determine_action_with_rules(
            message, confidence_score, hallucination_risk, semantic_issues, clarity_issues, rule_results
        )
        
        # Build the reflection message
        reflection = OdinReflection()
        reflection.original.CopyFrom(message)
        reflection.mediator_id = self.mediator_id
        reflection.action_taken = action_taken
        reflection.explanation = explanation
        reflection.confidence_score = confidence_score
        reflection.reflection_timestamp = int(time.time() * 1000)
        reflection.iteration_count = iteration_count
        reflection.correction_tags.extend(corrections)
        
        # Add rule evaluation metadata
        if rule_results:
            rule_summary = "; ".join([f"{r['rule_name']}: {r['action']}" for r in rule_results])
            reflection.explanation += f" | Rules applied: {rule_summary}"
        
        if healed_message:
            reflection.healed.CopyFrom(healed_message)
        
        return reflection
    
    def _create_rule_context(self, message: OdinMessage, confidence: float, 
                           hallucination_risk: float, semantic_issues: bool,
                           clarity_issues: List[str], iteration_count: int) -> Dict[str, Any]:
        """Create context dictionary for rule engine evaluation."""
        return {
            # Core message data
            "trace_id": message.trace_id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "role": message.role,
            "timestamp": message.timestamp,
            "message_type": getattr(message, 'message_type', 'standard'),
            
            # Evaluation metrics
            "confidence": confidence,
            "hallucination_risk": hallucination_risk,
            "semantic_drift_score": message.semantic_drift_score,
            "has_semantic_issues": semantic_issues,
            "clarity_issues": clarity_issues,
            "clarity_issues_count": len(clarity_issues),
            
            # Message content analysis
            "message_length": len(message.raw_output),
            "message_size": len(message.SerializeToString()),
            "has_healed_output": bool(message.healed_output),
            "word_count": len(message.raw_output.split()),
            
            # Processing metadata
            "iteration_count": iteration_count,
            "mediator_id": self.mediator_id,
            "evaluation_timestamp": int(time.time() * 1000),
            
            # Security and compliance context
            "source": getattr(message, 'source', 'unknown'),
            "user_id": getattr(message, 'user_id', None),
            
            # Pattern detection results
            "has_uncertainty_patterns": self._has_uncertainty_patterns(message.raw_output),
            "has_hallucination_patterns": self._has_hallucination_indicators(message.raw_output),
            
            # Thresholds for reference
            "confidence_threshold": self.confidence_threshold,
            "semantic_drift_threshold": self.semantic_drift_threshold,
            
            # Metadata from healing if present
            "healing_metadata": {
                "has_healing": message.HasField('healing_metadata'),
                "healing_confidence": message.healing_metadata.confidence if message.HasField('healing_metadata') else 0.0,
                "healing_iteration": message.healing_metadata.iteration_count if message.HasField('healing_metadata') else 0
            },
            
            # ODIN message context fields for rule evaluation
            "context": {
                "conversation_id": message.context.conversation_id if message.HasField('context') else "",
                "turn_number": message.context.turn_number if message.HasField('context') else 0,
                "conversation_type": message.context.conversation_type if message.HasField('context') else "",
                "topic": message.context.topic if message.HasField('context') else "",
                "key_themes": list(message.context.key_themes) if message.HasField('context') else [],
                "emotional_state": message.context.emotional_state if message.HasField('context') else ""
            },
            
            # ODIN message metrics for rule evaluation
            "metrics": {
                "response_time_ms": message.metrics.response_time_ms if message.HasField('metrics') else 0,
                "coherence_score": message.metrics.coherence_score if message.HasField('metrics') else 0.0,
                "relevance_score": message.metrics.relevance_score if message.HasField('metrics') else 0.0,
                "token_count": message.metrics.token_count if message.HasField('metrics') else 0,
                "complexity_score": message.metrics.complexity_score if message.HasField('metrics') else 0.0,
                "model_version": message.metrics.model_version if message.HasField('metrics') else ""
            },
            
            # ODIN message metadata for rule evaluation
            "metadata": dict(message.metadata) if len(message.metadata) > 0 else {}
        }
    
    def _has_uncertainty_patterns(self, text: str) -> bool:
        """Check if text contains uncertainty patterns."""
        for pattern in self.low_confidence_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _has_hallucination_indicators(self, text: str) -> bool:
        """Check if text contains hallucination indicator patterns."""
        for pattern in self.hallucination_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _determine_action_with_rules(self, message: OdinMessage, confidence: float, 
                                   hallucination_risk: float, semantic_issues: bool,
                                   clarity_issues: List[str], rule_results: List[Dict[str, Any]]) -> tuple:
        """
        Determine action considering both rule engine results and traditional evaluation.
        
        Returns:
            tuple: (action_taken, healed_message, explanation, correction_tags)
        """
        # Check if rules provided a decisive action
        decisive_actions = ["approve", "reject", "escalate"]
        for result in rule_results:
            if result["action"] in decisive_actions:
                action = result["action"]
                explanation = f"Rule-based decision: {result.get('reason', 'Rule triggered')}"
                
                # Create healed message if action is modify or retry
                healed_message = None
                if action in ["retry", "modify"] or any(r["action"] == "retry" for r in rule_results):
                    corrections = [result["rule_name"]] + [r["rule_name"] for r in rule_results if r["action"] == "retry"]
                    healed_message = self._create_healed_message(message, corrections)
                
                return (action, healed_message, explanation, [result["rule_name"]])
        
        # If no decisive rule action, fall back to traditional evaluation
        return self._determine_action(message, confidence, hallucination_risk, semantic_issues, clarity_issues)
    
    async def evaluate_async(self, message: OdinMessage, iteration_count: int = 1) -> OdinReflection:
        """
        Asynchronous version of evaluate method with rule engine integration.
        
        Args:
            message: The OdinMessage to evaluate
            iteration_count: Current iteration count for this message
            
        Returns:
            OdinReflection: Contains evaluation results and any corrections
        """
        # Validate input
        if not self._validate_message(message):
            raise ValueError("Invalid OdinMessage provided")
        
        if iteration_count < 1:
            raise ValueError("Iteration count must be at least 1")
        
        # Perform various evaluation checks
        confidence_score = self._calculate_confidence(message)
        hallucination_risk = self._assess_hallucination_risk(message)
        semantic_issues = self._check_semantic_drift(message)
        clarity_issues = self._assess_clarity(message)
        
        # Create context for rule engine evaluation
        rule_context = self._create_rule_context(
            message, confidence_score, hallucination_risk, semantic_issues, clarity_issues, iteration_count
        )
        
        # Evaluate rules asynchronously
        rule_results = await self.rule_engine.evaluate_rules_async(rule_context)
        
        # Determine final action based on rule results
        action_taken, healed_message, explanation, corrections = self._determine_action_with_rules(
            message, confidence_score, hallucination_risk, semantic_issues, clarity_issues, rule_results
        )
        
        # Build the reflection message
        reflection = OdinReflection()
        reflection.original.CopyFrom(message)
        reflection.mediator_id = self.mediator_id
        reflection.action_taken = action_taken
        reflection.explanation = explanation
        reflection.confidence_score = confidence_score
        reflection.reflection_timestamp = int(time.time() * 1000)
        reflection.iteration_count = iteration_count
        reflection.correction_tags.extend(corrections)
        
        # Add rule evaluation metadata
        if rule_results:
            rule_summary = "; ".join([f"{r['rule_name']}: {r['action']}" for r in rule_results])
            reflection.explanation += f" | Rules applied: {rule_summary}"
        
        if healed_message:
            reflection.healed.CopyFrom(healed_message)
        
        return reflection
    
    def get_rule_engine_stats(self) -> Dict[str, Any]:
        """Get statistics from the integrated rule engine."""
        return self.rule_engine.get_stats()
    
    def reload_rules(self, config_path: Optional[str] = None) -> None:
        """Reload rules from configuration file."""
        if config_path:
            self.rule_engine.load_rules_from_config(config_path)
        else:
            self.rule_engine._load_default_rules()
    
    def export_rules_config(self, output_path: str) -> None:
        """Export current rules to YAML configuration."""
        self.rule_engine.export_rules_to_config(output_path)
    
    def _validate_message(self, message: OdinMessage) -> bool:
        """
        Validate that the OdinMessage meets basic requirements.
        
        Args:
            message: OdinMessage to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check required fields
        if not message.trace_id:
            return False
        if not message.sender_id:
            return False
        if not message.receiver_id:
            return False
        if not message.raw_output:
            return False
        
        # Check message size (Protocol Buffer serialized size)
        try:
            serialized_size = len(message.SerializeToString())
            max_size = 1024 * 1024  # 1MB limit
            if serialized_size > max_size:
                return False
        except Exception:
            # If serialization fails, message is invalid
            return False
        
        # Check semantic drift score range
        if not 0.0 <= message.semantic_drift_score <= 1.0:
            return False
        
        # Check text content length (raw text limit)
        if len(message.raw_output) > 50000:  # 50k character limit
            return False
        
        # Check healed output if present
        if message.healed_output and len(message.healed_output) > 50000:
            return False
        
        # Validate timestamp (should be positive)
        if message.timestamp < 0:
            return False
        
        # Validate role field
        valid_roles = ["assistant", "tool", "user", "mediator"]
        if message.role and message.role not in valid_roles:
            return False
        
        return True
    
    def validate_message_size(self, message: OdinMessage) -> None:
        """
        Validate message size and raise HTTP exception if too large.
        
        Args:
            message: OdinMessage to validate
            
        Raises:
            ValueError: If message exceeds size limits
        """
        from config import get_settings
        settings = get_settings()
        
        serialized_size = len(message.SerializeToString())
        
        if serialized_size > settings.max_message_size:
            raise ValueError(
                f"Message size ({serialized_size} bytes) exceeds limit "
                f"({settings.max_message_size} bytes)"
            )
        
        # Also check raw text size
        text_size = len(message.raw_output.encode('utf-8'))
        max_text_size = 100 * 1024  # 100KB text limit
        
        if text_size > max_text_size:
            raise ValueError(
                f"Message text size ({text_size} bytes) exceeds limit "
                f"({max_text_size} bytes)"
            )
    
    def _calculate_confidence(self, message: OdinMessage) -> float:
        """Calculate confidence score based on message content and metadata."""
        base_confidence = 0.8
        
        # Check for low confidence language patterns
        text = message.raw_output.lower()
        confidence_penalty = 0.0
        
        for pattern in self.low_confidence_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            confidence_penalty += matches * 0.1
        
        # Factor in semantic drift if available
        if message.semantic_drift_score > 0:
            confidence_penalty += message.semantic_drift_score * 0.2
        
        # Consider healing metadata confidence if available
        if message.HasField('healing_metadata') and message.healing_metadata.confidence > 0:
            base_confidence = (base_confidence + message.healing_metadata.confidence) / 2
        
        final_confidence = max(0.0, min(1.0, base_confidence - confidence_penalty))
        return final_confidence
    
    def _assess_hallucination_risk(self, message: OdinMessage) -> float:
        """Assess the risk of hallucination in the message."""
        text = message.raw_output.lower()
        risk_score = 0.0
        
        for pattern in self.hallucination_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            risk_score += matches * 0.15
        
        # Check for contradictions or inconsistencies
        if self._has_contradictions(text):
            risk_score += 0.2
        
        return min(1.0, risk_score)
    
    def _check_semantic_drift(self, message: OdinMessage) -> bool:
        """Check if semantic drift exceeds threshold."""
        return message.semantic_drift_score > self.semantic_drift_threshold
    
    def _assess_clarity(self, message: OdinMessage) -> List[str]:
        """Assess clarity issues in the message."""
        issues = []
        text = message.raw_output
        
        # Check for very long sentences
        sentences = text.split('.')
        for sentence in sentences:
            if len(sentence.split()) > 30:
                issues.append("overly-long-sentences")
                break
        
        # Check for unclear pronouns
        if re.search(r'\b(?:it|this|that|they)\b.*\b(?:it|this|that|they)\b', text, re.IGNORECASE):
            issues.append("unclear-pronouns")
        
        # Check for jargon or complex terminology without explanation
        complex_words = re.findall(r'\b\w{12,}\b', text)
        if len(complex_words) > 3:
            issues.append("complex-terminology")
        
        return issues
    
    def _has_contradictions(self, text: str) -> bool:
        """Simple check for potential contradictions in text."""
        contradiction_indicators = [
            (r'\bbut\b', r'\bhowever\b'),
            (r'\byes\b.*\bno\b', r'\bno\b.*\byes\b'),
            (r'\btrue\b.*\bfalse\b', r'\bfalse\b.*\btrue\b'),
            (r'\balways\b.*\bnever\b', r'\bnever\b.*\balways\b')
        ]
        
        for indicator_group in contradiction_indicators:
            for indicator in indicator_group:
                if re.search(indicator, text, re.IGNORECASE):
                    return True
        
        return False
    
    def _determine_action(self, message: OdinMessage, confidence: float, 
                         hallucination_risk: float, semantic_issues: bool,
                         clarity_issues: List[str]) -> tuple:
        """
        Determine the action to take based on evaluation results.
        
        Returns:
            tuple: (action_taken, healed_message, explanation, correction_tags)
        """
        corrections = []
        explanations = []
        
        # Determine if message should be rejected
        if confidence < 0.4 or hallucination_risk > 0.6:
            return ("reject", None, 
                   f"Message rejected due to low confidence ({confidence:.2f}) or high hallucination risk ({hallucination_risk:.2f})",
                   ["critical-quality-issues"])
        
        # Determine if message needs modification
        needs_modification = False
        healed_message = None
        
        if confidence < self.confidence_threshold:
            needs_modification = True
            corrections.append(self.correction_tags['confidence'])
            explanations.append(f"confidence below threshold ({confidence:.2f})")
        
        if hallucination_risk > 0.3:
            needs_modification = True
            corrections.append(self.correction_tags['hallucination'])
            explanations.append(f"potential hallucination detected (risk: {hallucination_risk:.2f})")
        
        if semantic_issues:
            needs_modification = True
            corrections.append(self.correction_tags['semantic_drift'])
            explanations.append("semantic drift detected")
        
        if clarity_issues:
            needs_modification = True
            corrections.extend([f"clarity-{issue}" for issue in clarity_issues])
            explanations.append(f"clarity issues: {', '.join(clarity_issues)}")
        
        if needs_modification:
            healed_message = self._create_healed_message(message, corrections)
            explanation = f"Message modified: {'; '.join(explanations)}"
            return ("modify", healed_message, explanation, corrections)
        
        # Message passes evaluation
        return ("pass", None, 
               f"Message passed evaluation (confidence: {confidence:.2f}, hallucination risk: {hallucination_risk:.2f})",
               [])
    
    def _create_healed_message(self, original: OdinMessage, corrections: List[str]) -> OdinMessage:
        """Create a healed version of the message with corrections applied."""
        healed = OdinMessage()
        healed.CopyFrom(original)
        
        # Apply healing based on correction types
        healed_text = original.raw_output
        
        # Remove low confidence language
        if self.correction_tags['confidence'] in corrections:
            for pattern in self.low_confidence_patterns:
                healed_text = re.sub(pattern, '', healed_text, flags=re.IGNORECASE)
        
        # Add confidence qualifiers for potential hallucinations
        if self.correction_tags['hallucination'] in corrections:
            healed_text = "Based on available information: " + healed_text
        
        # Clean up extra spaces
        healed_text = re.sub(r'\s+', ' ', healed_text).strip()
        
        healed.healed_output = healed_text
        
        # Update healing metadata
        if not healed.HasField('healing_metadata'):
            healed.healing_metadata.method = "mediator_ai_healing"
            healed.healing_metadata.confidence = 0.8
            healed.healing_metadata.iteration_count = 1
        else:
            healed.healing_metadata.iteration_count += 1
        
        healed.healing_metadata.notes = f"Healed by {self.mediator_id}: {', '.join(corrections)}"
        healed.healing_metadata.applied_rules.extend(corrections)
        
        return healed


class ReflectionLogger:
    """Logger for tracking all reflections and exporting them for analytics."""
    
    def __init__(self, log_file: str = "logs/reflections.jsonl"):
        """
        Initialize the reflection logger.
        
        Args:
            log_file: Path to the JSONL log file
        """
        self.log_file = log_file
    
    def log_reflection(self, reflection: OdinReflection) -> None:
        """
        Log a reflection to JSONL format for analytics (synchronous).
        
        Args:
            reflection: The OdinReflection to log
        """
        # Convert reflection to JSON-serializable format
        reflection_data = {
            'mediator_id': reflection.mediator_id,
            'action_taken': reflection.action_taken,
            'explanation': reflection.explanation,
            'confidence_score': reflection.confidence_score,
            'reflection_timestamp': reflection.reflection_timestamp,
            'iteration_count': reflection.iteration_count,
            'correction_tags': list(reflection.correction_tags),
            'original_trace_id': reflection.original.trace_id,
            'original_sender_id': reflection.original.sender_id,
            'original_receiver_id': reflection.original.receiver_id,
            'has_healed_message': reflection.HasField('healed')
        }
        
        # Append to JSONL file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(reflection_data) + '\n')
    
    async def async_log_reflection(self, reflection: OdinReflection) -> None:
        """
        Log a reflection to JSONL format for analytics (asynchronous).
        
        Args:
            reflection: The OdinReflection to log
        """
        try:
            # Try to import aiofiles for async file operations
            try:
                import aiofiles
                async_available = True
            except ImportError:
                async_available = False
            
            # Convert reflection to JSON-serializable format
            reflection_data = {
                'mediator_id': reflection.mediator_id,
                'action_taken': reflection.action_taken,
                'explanation': reflection.explanation,
                'confidence_score': reflection.confidence_score,
                'reflection_timestamp': reflection.reflection_timestamp,
                'iteration_count': reflection.iteration_count,
                'correction_tags': list(reflection.correction_tags),
                'original_trace_id': reflection.original.trace_id,
                'original_sender_id': reflection.original.sender_id,
                'original_receiver_id': reflection.original.receiver_id,
                'has_healed_message': reflection.HasField('healed')
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            if async_available:
                # Async write to JSONL file
                async with aiofiles.open(self.log_file, 'a', encoding='utf-8') as f:
                    await f.write(json.dumps(reflection_data) + '\n')
            else:
                # Fallback to synchronous logging if aiofiles not available
                self.log_reflection(reflection)
                
        except Exception as e:
            # Final fallback to synchronous logging
            self.log_reflection(reflection)
    
    def get_reflection_stats(self) -> Dict[str, Any]:
        """
        Get analytics statistics from the reflection log.
        
        Returns:
            Dict with reflection statistics
        """
        if not os.path.exists(self.log_file):
            return {'error': 'No reflection log found'}
        
        stats = {
            'total_reflections': 0,
            'actions': {'pass': 0, 'modify': 0, 'reject': 0},
            'avg_confidence': 0.0,
            'common_corrections': {},
            'mediators': set()
        }
        
        total_confidence = 0.0
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            stats['total_reflections'] += 1
                            stats['actions'][data['action_taken']] += 1
                            total_confidence += data['confidence_score']
                            stats['mediators'].add(data['mediator_id'])
                            
                            for tag in data['correction_tags']:
                                stats['common_corrections'][tag] = stats['common_corrections'].get(tag, 0) + 1
                        except json.JSONDecodeError:
                            # Skip malformed lines
                            continue
        except Exception as e:
            return {'error': f'Failed to read log file: {e}'}
        
        if stats['total_reflections'] > 0:
            stats['avg_confidence'] = total_confidence / stats['total_reflections']
        
        stats['mediators'] = list(stats['mediators'])
        return stats


def save_reflection(reflection: OdinReflection, directory: str = "logs") -> str:
    """
    Save an OdinReflection to a binary file.
    
    Args:
        reflection: OdinReflection Protocol Buffer object
        directory: Directory to save the file
        
    Returns:
        str: Path to the saved file
        
    Raises:
        ValueError: If directory path is invalid
        Exception: If save operation fails
    """
    # Validate and sanitize directory path
    import os.path
    
    # Prevent path traversal attacks
    directory = os.path.normpath(directory)
    if ".." in directory or directory.startswith("/"):
        raise ValueError("Invalid directory path")
    
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Create safe filename
    safe_trace_id = "".join(c for c in reflection.original.trace_id if c.isalnum() or c in "-_")[:50]
    filename = f"reflection_{safe_trace_id}_{reflection.iteration_count}.odinr"
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, 'wb') as f:
            f.write(reflection.SerializeToString())
        return filepath
    except Exception as e:
        raise Exception(f"Failed to save reflection: {e}")


def load_reflection(filepath: str) -> Optional[OdinReflection]:
    """
    Load an OdinReflection from a binary file.
    
    Args:
        filepath: Path to the reflection file
        
    Returns:
        OdinReflection object or None if loading fails
        
    Raises:
        ValueError: If filepath is invalid
    """
    import os.path
    
    # Validate filepath
    if not filepath or ".." in filepath:
        raise ValueError("Invalid file path")
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'rb') as f:
            reflection = OdinReflection()
            reflection.ParseFromString(f.read())
            return reflection
    except Exception as e:
        print(f"Error loading reflection: {e}")
        return None
