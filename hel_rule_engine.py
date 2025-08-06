#!/usr/bin/env python3
"""
Hel Rule Engine - Enhanced Rule Engine with Mediator Pattern Support.
Extends the ODIN Protocol Rule Engine with advanced architectural patterns.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Protocol, Union
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

# Import base ODIN Rule Engine components
from rules_engine import RuleEngine, Rule, RuleCondition, RuleAction, RuleOperator


class ColleagueProtocol(Protocol):
    """Protocol defining the interface for Mediator Pattern Colleagues."""
    
    def set_mediator(self, mediator: 'HelRuleMediator') -> None:
        """Set the mediator reference for this colleague."""
        ...
    
    async def handle_request(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a specific request type with given context."""
        ...
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this colleague provides."""
        ...


class BaseColleague(ABC):
    """Abstract base class for Mediator Pattern Colleagues."""
    
    def __init__(self, colleague_id: str):
        self.colleague_id = colleague_id
        self.mediator: Optional['HelRuleMediator'] = None
        self.logger = logging.getLogger(f"{__name__}.{colleague_id}")
    
    def set_mediator(self, mediator: 'HelRuleMediator') -> None:
        """Set the mediator reference for this colleague."""
        self.mediator = mediator
        self.logger.info(f"Colleague {self.colleague_id} connected to mediator")
    
    @abstractmethod
    async def handle_request(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a specific request type with given context."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this colleague provides."""
        pass
    
    async def notify_mediator(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify the mediator of an event."""
        if self.mediator:
            await self.mediator.handle_colleague_notification(self.colleague_id, event_type, data)


class DataSourceColleague(BaseColleague):
    """Colleague responsible for data source evaluation and validation."""
    
    def __init__(self):
        super().__init__("data_source")
        self.data_quality_threshold = 0.8
        self.supported_sources = ["user_input", "api_response", "database", "file_upload"]
    
    async def handle_request(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data source related requests."""
        if request_type == "validate_data_quality":
            return await self._validate_data_quality(context)
        elif request_type == "assess_source_reliability":
            return await self._assess_source_reliability(context)
        elif request_type == "extract_metadata":
            return await self._extract_metadata(context)
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this colleague provides."""
        return [
            "validate_data_quality",
            "assess_source_reliability", 
            "extract_metadata",
            "data_source_validation"
        ]
    
    async def _validate_data_quality(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of data in the context."""
        data_source = context.get("data_source", "unknown")
        content = context.get("content", "")
        
        # Simulate data quality assessment
        quality_score = 0.9 if len(content) > 10 and data_source in self.supported_sources else 0.3
        
        result = {
            "quality_score": quality_score,
            "meets_threshold": quality_score >= self.data_quality_threshold,
            "source_type": data_source,
            "assessment_timestamp": datetime.now().isoformat(),
            "issues": []
        }
        
        if quality_score < self.data_quality_threshold:
            result["issues"].append("Below quality threshold")
        
        if data_source not in self.supported_sources:
            result["issues"].append(f"Unsupported data source: {data_source}")
        
        self.logger.debug(f"Data quality assessment: {quality_score} for source {data_source}")
        return result
    
    async def _assess_source_reliability(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the reliability of the data source."""
        source_id = context.get("source_id", "unknown")
        historical_accuracy = context.get("historical_accuracy", 0.7)
        
        reliability_score = min(historical_accuracy + 0.1, 1.0)
        
        return {
            "reliability_score": reliability_score,
            "source_id": source_id,
            "is_reliable": reliability_score >= 0.8,
            "historical_accuracy": historical_accuracy
        }
    
    async def _extract_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from the context."""
        return {
            "extracted_metadata": {
                "content_length": len(str(context.get("content", ""))),
                "has_structured_data": isinstance(context.get("data"), dict),
                "context_keys": list(context.keys()),
                "extraction_timestamp": datetime.now().isoformat()
            }
        }


class RuleEvaluatorColleague(BaseColleague):
    """Colleague responsible for advanced rule evaluation strategies."""
    
    def __init__(self):
        super().__init__("rule_evaluator")
        self.evaluation_strategies = ["standard", "weighted", "prioritized", "consensus"]
        self.confidence_weights = {"high": 1.0, "medium": 0.7, "low": 0.3}
    
    async def handle_request(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rule evaluation related requests."""
        if request_type == "evaluate_with_strategy":
            return await self._evaluate_with_strategy(context)
        elif request_type == "calculate_rule_confidence":
            return await self._calculate_rule_confidence(context)
        elif request_type == "optimize_rule_order":
            return await self._optimize_rule_order(context)
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this colleague provides."""
        return [
            "evaluate_with_strategy",
            "calculate_rule_confidence",
            "optimize_rule_order",
            "rule_performance_analysis"
        ]
    
    async def _evaluate_with_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate rules using specified strategy."""
        strategy = context.get("strategy", "standard")
        rules_results = context.get("rule_results", [])
        
        if strategy == "weighted":
            return await self._weighted_evaluation(rules_results)
        elif strategy == "consensus":
            return await self._consensus_evaluation(rules_results)
        else:
            return {"strategy": strategy, "results": rules_results}
    
    async def _weighted_evaluation(self, rule_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform weighted evaluation of rule results."""
        if not rule_results:
            return {"weighted_score": 0.0, "recommendation": "continue"}
        
        total_weight = 0
        weighted_sum = 0
        
        for result in rule_results:
            action = result.get("action", "continue")
            weight = self.confidence_weights.get(
                result.get("confidence_level", "medium"), 0.7
            )
            
            action_score = {"approve": 1.0, "continue": 0.5, "retry": 0.3, "reject": 0.0, "escalate": 0.2}.get(action, 0.5)
            
            weighted_sum += action_score * weight
            total_weight += weight
        
        weighted_score = weighted_sum / total_weight if total_weight > 0 else 0.5
        
        if weighted_score >= 0.8:
            recommendation = "approve"
        elif weighted_score >= 0.6:
            recommendation = "continue"
        elif weighted_score >= 0.3:
            recommendation = "retry"
        else:
            recommendation = "reject"
        
        return {
            "weighted_score": weighted_score,
            "recommendation": recommendation,
            "total_weight": total_weight,
            "evaluation_method": "weighted"
        }
    
    async def _consensus_evaluation(self, rule_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform consensus-based evaluation."""
        if not rule_results:
            return {"consensus": "continue", "agreement_level": 0.0}
        
        action_counts = {}
        for result in rule_results:
            action = result.get("action", "continue")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        total_results = len(rule_results)
        consensus_action = max(action_counts, key=action_counts.get)
        agreement_level = action_counts[consensus_action] / total_results
        
        return {
            "consensus": consensus_action,
            "agreement_level": agreement_level,
            "action_distribution": action_counts,
            "requires_review": agreement_level < 0.6
        }
    
    async def _calculate_rule_confidence(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence in rule evaluation."""
        rule_name = context.get("rule_name", "unknown")
        execution_history = context.get("execution_history", [])
        
        if not execution_history:
            confidence = 0.5
        else:
            success_rate = sum(1 for h in execution_history if h.get("success", False)) / len(execution_history)
            confidence = min(success_rate + 0.1, 1.0)
        
        return {
            "rule_name": rule_name,
            "confidence_score": confidence,
            "historical_executions": len(execution_history),
            "confidence_level": "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low"
        }
    
    async def _optimize_rule_order(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize rule execution order based on performance."""
        rules = context.get("rules", [])
        
        # Simple optimization: sort by priority and success rate
        optimized_rules = sorted(rules, key=lambda r: (
            r.get("priority", 100),
            -r.get("success_rate", 0.5)
        ))
        
        return {
            "optimized_order": [r.get("name", "unknown") for r in optimized_rules],
            "optimization_applied": True,
            "optimization_timestamp": datetime.now().isoformat()
        }


class HelRuleMediator:
    """Mediator that coordinates between different rule engine colleagues."""
    
    def __init__(self):
        self.mediator_id = f"hel-mediator-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.colleagues: Dict[str, BaseColleague] = {}
        self.logger = logging.getLogger(__name__)
        self.event_history: List[Dict[str, Any]] = []
        
        # Initialize default colleagues
        self._initialize_default_colleagues()
    
    def _initialize_default_colleagues(self):
        """Initialize default colleagues for the mediator."""
        self.register_colleague(DataSourceColleague())
        self.register_colleague(RuleEvaluatorColleague())
        
        # Import and register additional colleagues
        try:
            from hel_colleagues import PolicyColleague, ActionTriggerColleague
            self.register_colleague(PolicyColleague())
            self.register_colleague(ActionTriggerColleague())
        except ImportError:
            self.logger.warning("Additional colleagues not available, continuing with basic setup")
    
    def register_colleague(self, colleague: BaseColleague) -> None:
        """Register a colleague with the mediator."""
        colleague.set_mediator(self)
        self.colleagues[colleague.colleague_id] = colleague
        self.logger.info(f"Registered colleague: {colleague.colleague_id}")
    
    async def coordinate_request(self, request_type: str, context: Dict[str, Any], 
                               target_colleague: Optional[str] = None) -> Dict[str, Any]:
        """Coordinate a request between colleagues."""
        if target_colleague and target_colleague in self.colleagues:
            colleague = self.colleagues[target_colleague]
            if request_type in colleague.get_capabilities():
                return await colleague.handle_request(request_type, context)
            else:
                return {"error": f"Colleague {target_colleague} cannot handle {request_type}"}
        
        # Find capable colleagues
        capable_colleagues = []
        for colleague_id, colleague in self.colleagues.items():
            if request_type in colleague.get_capabilities():
                capable_colleagues.append(colleague)
        
        if not capable_colleagues:
            return {"error": f"No colleague capable of handling {request_type}"}
        
        # Use first capable colleague (could be enhanced with load balancing)
        return await capable_colleagues[0].handle_request(request_type, context)
    
    async def handle_colleague_notification(self, colleague_id: str, event_type: str, 
                                          data: Dict[str, Any]) -> None:
        """Handle notifications from colleagues."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "colleague_id": colleague_id,
            "event_type": event_type,
            "data": data
        }
        self.event_history.append(event)
        self.logger.debug(f"Received notification from {colleague_id}: {event_type}")
    
    def get_colleague_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all registered colleagues."""
        return {
            colleague_id: colleague.get_capabilities()
            for colleague_id, colleague in self.colleagues.items()
        }
    
    def get_mediator_stats(self) -> Dict[str, Any]:
        """Get mediator statistics."""
        return {
            "mediator_id": self.mediator_id,
            "colleagues_count": len(self.colleagues),
            "colleagues": list(self.colleagues.keys()),
            "event_history_count": len(self.event_history),
            "capabilities": self.get_colleague_capabilities()
        }


class HelRuleEngine(RuleEngine):
    """Hel Rule Engine with Mediator Pattern Support."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Hel Rule Engine."""
        super().__init__(config_path)
        
        # Initialize mediator
        self.mediator = HelRuleMediator()
        self.hel_handlers: Dict[str, Callable] = {}
        
        # Enhanced statistics
        self.hel_stats = {
            "mediator_requests": 0,
            "colleague_interactions": 0,
            "enhanced_evaluations": 0
        }
        
        # Register Hel-specific handlers
        self._register_hel_handlers()
        
        self.logger.info(f"Initialized Hel Rule Engine with mediator: {self.mediator.mediator_id}")
    
    def _register_hel_handlers(self):
        """Register Hel-specific custom handlers."""
        
        def hel_data_quality_handler(context: Dict[str, Any], rule: Rule) -> Dict[str, Any]:
            """Hel handler for data quality assessment."""
            # This will be called through the mediator pattern
            return {
                "action": "custom",
                "reason": "Hel data quality assessment required",
                "requires_mediator": True,
                "mediator_request": "validate_data_quality"
            }
        
        def hel_consensus_handler(context: Dict[str, Any], rule: Rule) -> Dict[str, Any]:
            """Hel handler for consensus-based decisions."""
            return {
                "action": "custom", 
                "reason": "Hel consensus evaluation required",
                "requires_mediator": True,
                "mediator_request": "evaluate_with_strategy",
                "strategy": "consensus"
            }
        
        # Register with the base rule engine
        self.register_custom_handler("hel_data_quality", hel_data_quality_handler)
        self.register_custom_handler("hel_consensus", hel_consensus_handler)
        
        # Store in Hel-specific registry
        self.hel_handlers["hel_data_quality"] = hel_data_quality_handler
        self.hel_handlers["hel_consensus"] = hel_consensus_handler
    
    async def evaluate_rules_with_mediator(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate rules using the mediator pattern for enhanced decisions."""
        self.hel_stats["enhanced_evaluations"] += 1
        
        # First, run standard rule evaluation
        standard_results = await self.evaluate_rules_async(context)
        
        # Check if any results require mediator intervention
        mediator_enhanced_results = []
        
        for result in standard_results:
            if result.get("requires_mediator", False):
                self.hel_stats["mediator_requests"] += 1
                
                # Get mediator request details
                request_type = result.get("mediator_request", "validate_data_quality")
                
                # Coordinate request through mediator
                mediator_result = await self.mediator.coordinate_request(request_type, context)
                self.hel_stats["colleague_interactions"] += 1
                
                # Enhance the result with mediator data
                enhanced_result = result.copy()
                enhanced_result["mediator_enhancement"] = mediator_result
                enhanced_result["enhanced_by"] = "hel_mediator"
                
                # Update action based on mediator feedback
                if request_type == "validate_data_quality":
                    quality_assessment = mediator_result.get("meets_threshold", True)
                    if not quality_assessment:
                        enhanced_result["action"] = "reject"
                        enhanced_result["reason"] += " | Data quality below threshold"
                
                mediator_enhanced_results.append(enhanced_result)
            else:
                mediator_enhanced_results.append(result)
        
        return mediator_enhanced_results
    
    def get_hel_stats(self) -> Dict[str, Any]:
        """Get Hel Rule Engine specific statistics."""
        base_stats = self.get_stats()
        
        hel_specific_stats = {
            "hel_engine_stats": self.hel_stats.copy(),
            "mediator_stats": self.mediator.get_mediator_stats(),
            "hel_handlers": list(self.hel_handlers.keys()),
            "colleague_capabilities": self.mediator.get_colleague_capabilities()
        }
        
        # Merge with base stats
        base_stats.update(hel_specific_stats)
        return base_stats
    
    def register_colleague(self, colleague: BaseColleague) -> None:
        """Register a new colleague with the mediator."""
        self.mediator.register_colleague(colleague)
        self.logger.info(f"Registered colleague {colleague.colleague_id} with Hel Rule Engine")


# Factory function for easy initialization
def create_hel_rule_engine(config_path: Optional[str] = None) -> HelRuleEngine:
    """Create and initialize a Hel Rule Engine instance."""
    return HelRuleEngine(config_path)


# Global Hel Rule Engine instance
_hel_rule_engine: Optional[HelRuleEngine] = None


def get_hel_rule_engine(config_path: Optional[str] = None) -> HelRuleEngine:
    """Get the global Hel Rule Engine instance."""
    global _hel_rule_engine
    if _hel_rule_engine is None:
        _hel_rule_engine = HelRuleEngine(config_path)
    return _hel_rule_engine
