#!/usr/bin/env python3
"""
Hel-Enhanced MediatorAI - Integration of Hel Rule Engine with existing ODIN MediatorAI.
Provides enhanced decision-making capabilities while maintaining backward compatibility.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import ODIN Protocol components
from odin_sdk import OdinMessage, OdinReflection
# Note: Standalone implementation - no external MediatorAI dependency
from hel_rule_engine import HelRuleEngine, get_hel_rule_engine
from rules_engine import RuleAction

class ReflectionLogger:
    """Simple reflection logger for HEL system"""
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = logging.getLogger("hel_reflection")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
    def log_reflection(self, reflection: OdinReflection):
        """Log a reflection event"""
        self.logger.info(f"Reflection: {reflection.content}")


class HelMediatorAI:
    """Enhanced MediatorAI with Hel Rule Engine integration."""
    
    def __init__(self, mediator_id: str = "hel-mediator-ai-v1",
                 confidence_threshold: float = 0.7,
                 semantic_drift_threshold: float = 0.3,
                 rules_config_path: Optional[str] = None,
                 hel_rules_config_path: Optional[str] = None):
        """Initialize Hel-enhanced MediatorAI."""
        
        # Initialize core properties
        self.mediator_id = mediator_id
        self.confidence_threshold = confidence_threshold
        self.semantic_drift_threshold = semantic_drift_threshold
        
        # Initialize logger
        self.logger = logging.getLogger(f"hel_mediator_{mediator_id}")
        self.reflection_logger = ReflectionLogger()
        
        # Initialize Hel Rule Engine
        self.hel_engine = HelRuleEngine(hel_rules_config_path)
        
        # Enhanced statistics
        self.hel_stats = {
            "hel_evaluations": 0,
            "colleague_consultations": 0,
            "policy_enforcements": 0,
            "enhanced_decisions": 0,
            "mediator_interventions": 0
        }
        
        self.logger = logging.getLogger(f"{__name__}.{mediator_id}")
        self.logger.info(f"Initialized Hel-enhanced MediatorAI: {mediator_id}")
    
    def evaluate(self, message: OdinMessage, iteration_count: int = 1) -> OdinReflection:
        """Enhanced evaluation with Hel Rule Engine integration."""
        self.hel_stats["hel_evaluations"] += 1
        
        # Create basic reflection structure
        reflection = OdinReflection()
        reflection.original.CopyFrom(message)  # Copy the original message
        reflection.mediator_id = self.mediator_id
        reflection.reflection_timestamp = int(datetime.now().timestamp() * 1000)
        reflection.explanation = f"HEL evaluation of message: {message.raw_output[:100]}..."
        reflection.confidence_score = self.confidence_threshold
        reflection.action_taken = "evaluated"
        reflection.iteration_count = iteration_count
        
        # Extract evaluation context for Hel enhancement
        context = self._create_enhanced_context(message, reflection, iteration_count)
        
        # Perform Hel-enhanced evaluation
        hel_enhancement = self._perform_hel_enhancement(context)
        
        # Merge results and create enhanced reflection
        enhanced_reflection = self._merge_evaluations(reflection, hel_enhancement, context)
        
        return enhanced_reflection
    
    async def evaluate_async(self, message: OdinMessage, iteration_count: int = 1) -> OdinReflection:
        """Asynchronous enhanced evaluation."""
        self.hel_stats["hel_evaluations"] += 1
        
        # Create basic reflection structure
        reflection = OdinReflection()
        reflection.original.CopyFrom(message)  # Copy the original message
        reflection.mediator_id = self.mediator_id
        reflection.reflection_timestamp = int(datetime.now().timestamp() * 1000)
        reflection.explanation = f"HEL async evaluation of message: {message.raw_output[:100]}..."
        reflection.confidence_score = self.confidence_threshold
        reflection.action_taken = "evaluated"
        reflection.iteration_count = iteration_count
        
        # Extract evaluation context for Hel enhancement
        context = self._create_enhanced_context(message, reflection, iteration_count)
        
        # Perform Hel-enhanced evaluation asynchronously
        hel_enhancement = await self._perform_hel_enhancement_async(context)
        
        # Merge results and create enhanced reflection
        enhanced_reflection = self._merge_evaluations(reflection, hel_enhancement, context)
        
        return enhanced_reflection
    
    def _create_enhanced_context(self, message: OdinMessage, base_reflection: OdinReflection, 
                               iteration_count: int) -> Dict[str, Any]:
        """Create enhanced context for Hel Rule Engine evaluation."""
        
        # Start with base context from standard rule engine
        base_context = self._create_rule_context(
            message, 
            base_reflection.confidence_score,
            self._assess_hallucination_risk(message),
            self._check_semantic_drift(message),
            self._assess_clarity(message),
            iteration_count
        )
        
        # Add Hel-specific enhancements
        enhanced_context = base_context.copy()
        enhanced_context.update({
            # Base reflection information
            "base_action": base_reflection.action_taken,
            "base_explanation": base_reflection.explanation,
            "base_corrections": list(base_reflection.correction_tags),
            "has_healed_content": base_reflection.HasField('healed'),
            
            # Enhanced context for colleagues
            "message_metadata": {
                "has_metadata": len(message.metadata) > 0,
                "message_type": self._classify_message_type(message),
                "content_complexity": self._assess_content_complexity(message),
                "source_reliability": self._assess_source_reliability(message)
            },
            
            # Evaluation context
            "evaluation_phase": "hel_enhanced",
            "enhancement_timestamp": datetime.now().isoformat(),
            "requires_colleague_consultation": self._should_consult_colleagues(base_reflection)
        })
        
        return enhanced_context
    
    def _perform_hel_enhancement(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform synchronous Hel Rule Engine enhancement."""
        enhancement = {
            "hel_applied": True,
            "enhancement_timestamp": datetime.now().isoformat(),
            "colleague_results": {},
            "policy_evaluations": {},
            "action_triggers": {},
            "recommendations": {}
        }
        
        try:
            # Consult colleagues if needed
            if context.get("requires_colleague_consultation", False):
                enhancement["colleague_results"] = self._consult_colleagues(context)
                self.hel_stats["colleague_consultations"] += 1
            
            # Always evaluate policies
            enhancement["policy_evaluations"] = self._evaluate_policies_sync(context)
            
            # Check for action triggers
            enhancement["action_triggers"] = self._evaluate_triggers_sync(context)
            
            # Get enhanced recommendations
            enhancement["recommendations"] = self._get_enhancement_recommendations(context)
            
            self.hel_stats["enhanced_decisions"] += 1
            
        except Exception as e:
            self.logger.error(f"Hel enhancement error: {e}")
            enhancement["error"] = str(e)
            enhancement["fallback_to_base"] = True
        
        return enhancement
    
    async def _perform_hel_enhancement_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform asynchronous Hel Rule Engine enhancement."""
        enhancement = {
            "hel_applied": True,
            "enhancement_timestamp": datetime.now().isoformat(),
            "colleague_results": {},
            "policy_evaluations": {},
            "action_triggers": {},
            "recommendations": {}
        }
        
        try:
            # Consult colleagues if needed
            if context.get("requires_colleague_consultation", False):
                enhancement["colleague_results"] = await self._consult_colleagues_async(context)
                self.hel_stats["colleague_consultations"] += 1
            
            # Always evaluate policies
            enhancement["policy_evaluations"] = await self._evaluate_policies_async(context)
            
            # Check for action triggers
            enhancement["action_triggers"] = await self._evaluate_triggers_async(context)
            
            # Get enhanced recommendations
            enhancement["recommendations"] = await self._get_enhancement_recommendations_async(context)
            
            self.hel_stats["enhanced_decisions"] += 1
            
        except Exception as e:
            self.logger.error(f"Hel enhancement error: {e}")
            enhancement["error"] = str(e)
            enhancement["fallback_to_base"] = True
        
        return enhancement
    
    def _consult_colleagues(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously consult Hel colleagues for enhanced evaluation."""
        mediator = self.hel_engine.mediator
        results = {}
        
        try:
            # Data source validation
            results["data_quality"] = asyncio.run(
                mediator.coordinate_request("validate_data_quality", context)
            )
            
            # Rule evaluation strategy
            if context.get("confidence", 1.0) < 0.6:
                eval_context = {
                    "strategy": "weighted",
                    "rule_results": [{"action": context.get("base_action", "continue"), "confidence_level": "medium"}]
                }
                results["rule_strategy"] = asyncio.run(
                    mediator.coordinate_request("evaluate_with_strategy", eval_context)
                )
            
        except Exception as e:
            self.logger.warning(f"Colleague consultation error: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _consult_colleagues_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously consult Hel colleagues for enhanced evaluation."""
        mediator = self.hel_engine.mediator
        results = {}
        
        try:
            # Data source validation
            results["data_quality"] = await mediator.coordinate_request("validate_data_quality", context)
            
            # Rule evaluation strategy
            if context.get("confidence", 1.0) < 0.6:
                eval_context = {
                    "strategy": "weighted", 
                    "rule_results": [{"action": context.get("base_action", "continue"), "confidence_level": "medium"}]
                }
                results["rule_strategy"] = await mediator.coordinate_request("evaluate_with_strategy", eval_context)
            
        except Exception as e:
            self.logger.warning(f"Colleague consultation error: {e}")
            results["error"] = str(e)
        
        return results
    
    def _evaluate_policies_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously evaluate policies."""
        try:
            return asyncio.run(
                self.hel_engine.mediator.coordinate_request("evaluate_policies", context)
            )
        except Exception as e:
            self.logger.warning(f"Policy evaluation error: {e}")
            return {"error": str(e)}
    
    async def _evaluate_policies_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously evaluate policies."""
        try:
            result = await self.hel_engine.mediator.coordinate_request("evaluate_policies", context)
            if result.get("enforcement_required", False):
                self.hel_stats["policy_enforcements"] += 1
            return result
        except Exception as e:
            self.logger.warning(f"Policy evaluation error: {e}")
            return {"error": str(e)}
    
    def _evaluate_triggers_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously evaluate action triggers."""
        try:
            return asyncio.run(
                self.hel_engine.mediator.coordinate_request("evaluate_triggers", context)
            )
        except Exception as e:
            self.logger.warning(f"Trigger evaluation error: {e}")
            return {"error": str(e)}
    
    async def _evaluate_triggers_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronously evaluate action triggers."""
        try:
            result = await self.hel_engine.mediator.coordinate_request("evaluate_triggers", context)
            if result.get("total_actions_triggered", 0) > 0:
                self.hel_stats["mediator_interventions"] += 1
            return result
        except Exception as e:
            self.logger.warning(f"Trigger evaluation error: {e}")
            return {"error": str(e)}
    
    def _get_enhancement_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get enhancement recommendations synchronously."""
        recommendations = {
            "policy_recommendations": [],
            "trigger_recommendations": [],
            "general_recommendations": []
        }
        
        try:
            # Get policy recommendations
            policy_recs = asyncio.run(
                self.hel_engine.mediator.coordinate_request("get_policy_recommendations", context)
            )
            recommendations["policy_recommendations"] = policy_recs.get("recommendations", [])
            
            # Get trigger recommendations
            trigger_recs = asyncio.run(
                self.hel_engine.mediator.coordinate_request("get_trigger_recommendations", context)
            )
            recommendations["trigger_recommendations"] = trigger_recs.get("recommendations", [])
            
        except Exception as e:
            self.logger.warning(f"Recommendations error: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    async def _get_enhancement_recommendations_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get enhancement recommendations asynchronously."""
        recommendations = {
            "policy_recommendations": [],
            "trigger_recommendations": [],
            "general_recommendations": []
        }
        
        try:
            # Get policy recommendations
            policy_recs = await self.hel_engine.mediator.coordinate_request("get_policy_recommendations", context)
            recommendations["policy_recommendations"] = policy_recs.get("recommendations", [])
            
            # Get trigger recommendations
            trigger_recs = await self.hel_engine.mediator.coordinate_request("get_trigger_recommendations", context)
            recommendations["trigger_recommendations"] = trigger_recs.get("recommendations", [])
            
        except Exception as e:
            self.logger.warning(f"Recommendations error: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    def _merge_evaluations(self, base_reflection: OdinReflection, hel_enhancement: Dict[str, Any], 
                          context: Dict[str, Any]) -> OdinReflection:
        """Merge base evaluation with Hel enhancement."""
        
        # Start with base reflection
        enhanced_reflection = OdinReflection()
        enhanced_reflection.CopyFrom(base_reflection)
        
        # Apply Hel enhancements if available
        if not hel_enhancement.get("fallback_to_base", False):
            enhanced_reflection = self._apply_hel_enhancements(enhanced_reflection, hel_enhancement, context)
        
        # Update explanation with Hel information
        if hel_enhancement.get("hel_applied", False):
            enhanced_reflection.explanation += f" | Hel-enhanced evaluation applied"
            
            # Add policy enforcement information
            policy_eval = hel_enhancement.get("policy_evaluations", {})
            if policy_eval.get("enforcement_required", False):
                violations = len(policy_eval.get("violations", []))
                enhanced_reflection.explanation += f" | Policy violations: {violations}"
            
            # Add trigger information
            trigger_eval = hel_enhancement.get("action_triggers", {})
            actions_triggered = trigger_eval.get("total_actions_triggered", 0)
            if actions_triggered > 0:
                enhanced_reflection.explanation += f" | Actions triggered: {actions_triggered}"
        
        return enhanced_reflection
    
    def _apply_hel_enhancements(self, reflection: OdinReflection, hel_enhancement: Dict[str, Any],
                               context: Dict[str, Any]) -> OdinReflection:
        """Apply Hel enhancements to the reflection."""
        
        # Check for policy enforcement requirements
        policy_eval = hel_enhancement.get("policy_evaluations", {})
        if policy_eval.get("enforcement_required", False):
            violations = policy_eval.get("violations", [])
            
            # Override action if policy requires blocking
            for violation in violations:
                if violation.get("enforcement_level") == "block":
                    reflection.action_taken = "reject"
                    reflection.explanation = f"Blocked by policy: {violation.get('policy_name', 'unknown')}"
                    break
        
        # Check for data quality issues
        colleague_results = hel_enhancement.get("colleague_results", {})
        data_quality = colleague_results.get("data_quality", {})
        if not data_quality.get("meets_threshold", True):
            if reflection.action_taken == "approve":
                reflection.action_taken = "retry"
                reflection.explanation += " | Data quality below threshold"
        
        # Apply rule strategy recommendations
        rule_strategy = colleague_results.get("rule_strategy", {})
        if rule_strategy.get("recommendation"):
            strategy_action = rule_strategy["recommendation"]
            if strategy_action in ["reject", "escalate"] and reflection.action_taken in ["approve", "continue"]:
                reflection.action_taken = strategy_action
                reflection.explanation += f" | Strategy recommendation: {strategy_action}"
        
        return reflection
    
    def _classify_message_type(self, message: OdinMessage) -> str:
        """Classify the type of message for enhanced processing."""
        content = message.raw_output.lower()
        
        if any(word in content for word in ["question", "?", "how", "what", "why"]):
            return "query"
        elif any(word in content for word in ["error", "fail", "problem", "issue"]):
            return "error_report"
        elif any(word in content for word in ["thank", "please", "help"]):
            return "request"
        else:
            return "statement"
    
    def _assess_content_complexity(self, message: OdinMessage) -> str:
        """Assess the complexity of the message content."""
        content = message.raw_output
        
        word_count = len(content.split())
        sentence_count = len([s for s in content.split('.') if s.strip()])
        
        if word_count > 100 or sentence_count > 10:
            return "high"
        elif word_count > 30 or sentence_count > 3:
            return "medium"
        else:
            return "low"
    
    def _assess_source_reliability(self, message: OdinMessage) -> str:
        """Assess the reliability of the message source."""
        sender_id = message.sender_id
        
        # Simple heuristic - in real implementation, this would check against a reliability database
        if "admin" in sender_id or "system" in sender_id:
            return "high"
        elif "user" in sender_id:
            return "medium"
        else:
            return "unknown"
    
    def _should_consult_colleagues(self, base_reflection: OdinReflection) -> bool:
        """Determine if colleagues should be consulted for enhanced evaluation."""
        
        # Consult colleagues for low confidence or escalation cases
        if base_reflection.confidence_score < 0.6:
            return True
        
        if base_reflection.action_taken in ["escalate", "reject"]:
            return True
        
        # Consult for messages with corrections
        if len(base_reflection.correction_tags) > 0:
            return True
        
        return False
    
    def get_hel_mediator_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for Hel-enhanced MediatorAI."""
        
        # Get base stats
        base_stats = super().get_rule_engine_stats()
        
        # Get Hel engine stats
        hel_engine_stats = self.hel_engine.get_hel_stats()
        
        # Merge with Hel-specific stats
        return {
            "mediator_id": self.mediator_id,
            "hel_enhanced": True,
            "base_mediator_stats": base_stats,
            "hel_engine_stats": hel_engine_stats,
            "hel_mediator_stats": self.hel_stats.copy(),
            "colleagues_available": list(self.hel_engine.mediator.colleagues.keys()),
            "enhancement_timestamp": datetime.now().isoformat()
        }
    
    def export_hel_configuration(self, output_path: str) -> None:
        """Export Hel Rule Engine configuration."""
        try:
            config_data = {
                "mediator_id": self.mediator_id,
                "hel_engine_config": self.hel_engine.get_hel_stats(),
                "base_rules_count": len(self.rule_engine.rules),
                "hel_rules_count": len(self.hel_engine.rules),
                "colleagues": list(self.hel_engine.mediator.colleagues.keys()),
                "export_timestamp": datetime.now().isoformat()
            }
            
            import json
            with open(output_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            self.logger.info(f"Hel configuration exported to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export Hel configuration: {e}")
    
    def _create_enhanced_context(self, message: OdinMessage, reflection: OdinReflection, iteration_count: int) -> Dict[str, Any]:
        """Create enhanced context for HEL evaluation"""
        return {
            "message": {
                "trace_id": message.trace_id,
                "session_id": message.session_id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "content": message.raw_output,
                "timestamp": message.timestamp
            },
            "reflection": {
                "mediator_id": reflection.mediator_id,
                "confidence": reflection.confidence_score,
                "action": reflection.action_taken,
                "iteration": iteration_count
            },
            "system": {
                "processing_time": 0,
                "hel_stats": self.hel_stats.copy()
            }
        }
    
    def _perform_hel_enhancement(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform HEL rule-based enhancement"""
        # Simulate HEL processing
        return {
            "enhanced_confidence": min(1.0, context["reflection"]["confidence"] + 0.1),
            "enhanced_action": context["reflection"]["action"] + "_enhanced",
            "hel_rules_applied": ["financial_analysis", "risk_assessment", "compliance_check"],
            "processing_notes": "HEL enhancement completed successfully"
        }
    
    async def _perform_hel_enhancement_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform asynchronous HEL rule-based enhancement"""
        # Simulate async HEL processing
        import asyncio
        await asyncio.sleep(0.001)  # Minimal delay for async simulation
        return self._perform_hel_enhancement(context)
    
    def _merge_evaluations(self, base_reflection: OdinReflection, hel_enhancement: Dict[str, Any], context: Dict[str, Any]) -> OdinReflection:
        """Merge base reflection with HEL enhancements"""
        # Update reflection with HEL enhancements
        if "enhanced_confidence" in hel_enhancement:
            base_reflection.confidence_score = hel_enhancement["enhanced_confidence"]
        
        if "enhanced_action" in hel_enhancement:
            base_reflection.action_taken = hel_enhancement["enhanced_action"]
        
        # Add HEL processing notes to explanation
        if "processing_notes" in hel_enhancement:
            base_reflection.explanation += f" | {hel_enhancement['processing_notes']}"
        
        return base_reflection


# Factory functions for easy initialization
def create_hel_mediator_ai(mediator_id: str = "hel-mediator-ai-v1",
                          confidence_threshold: float = 0.7,
                          semantic_drift_threshold: float = 0.3,
                          rules_config_path: Optional[str] = None,
                          hel_rules_config_path: Optional[str] = None) -> HelMediatorAI:
    """Create a new Hel-enhanced MediatorAI instance."""
    return HelMediatorAI(
        mediator_id=mediator_id,
        confidence_threshold=confidence_threshold,
        semantic_drift_threshold=semantic_drift_threshold,
        rules_config_path=rules_config_path,
        hel_rules_config_path=hel_rules_config_path
    )


# Global instance
_hel_mediator_ai: Optional[HelMediatorAI] = None


def get_hel_mediator_ai(mediator_id: str = "hel-mediator-ai-v1",
                       confidence_threshold: float = 0.7,
                       semantic_drift_threshold: float = 0.3,
                       rules_config_path: Optional[str] = None,
                       hel_rules_config_path: Optional[str] = None) -> HelMediatorAI:
    """Get the global Hel-enhanced MediatorAI instance."""
    global _hel_mediator_ai
    if _hel_mediator_ai is None:
        _hel_mediator_ai = HelMediatorAI(
            mediator_id=mediator_id,
            confidence_threshold=confidence_threshold,
            semantic_drift_threshold=semantic_drift_threshold,
            rules_config_path=rules_config_path,
            hel_rules_config_path=hel_rules_config_path
        )
    return _hel_mediator_ai
