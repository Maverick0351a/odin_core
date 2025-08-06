#!/usr/bin/env python3
"""
Extensible Rule Engine for ODIN Protocol.
Provides dynamic decision-making capabilities for the Mediator agent.
"""

import os
import yaml
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json


class RuleAction(Enum):
    """Available actions for rule evaluation results."""
    APPROVE = "approve"
    RETRY = "retry"
    REJECT = "reject"
    ESCALATE = "escalate"
    CONTINUE = "continue"
    LOG_WARNING = "log_warning"
    CUSTOM = "custom"


class RuleOperator(Enum):
    """Available operators for rule conditions."""
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    EQ = "=="
    NEQ = "!="
    CONTAINS = "contains"
    REGEX = "regex"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


@dataclass
class RuleCondition:
    """Represents a single condition in a rule."""
    field: str  # Field path (e.g., "confidence", "metadata.source")
    operator: RuleOperator
    value: Any
    description: str = ""
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate this condition against the provided context."""
        try:
            field_value = self._get_field_value(context, self.field)
            return self._apply_operator(field_value, self.operator, self.value)
        except Exception as e:
            logging.warning(f"Rule condition evaluation failed: {e}")
            return False
    
    def _get_field_value(self, context: Dict[str, Any], field_path: str) -> Any:
        """Extract field value from context using dot notation."""
        keys = field_path.split('.')
        value = context
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise ValueError(f"Field '{field_path}' not found in context")
        
        return value
    
    def _apply_operator(self, field_value: Any, operator: RuleOperator, expected_value: Any) -> bool:
        """Apply the specified operator to compare values."""
        if operator == RuleOperator.GT:
            return field_value > expected_value
        elif operator == RuleOperator.LT:
            return field_value < expected_value
        elif operator == RuleOperator.GTE:
            return field_value >= expected_value
        elif operator == RuleOperator.LTE:
            return field_value <= expected_value
        elif operator == RuleOperator.EQ:
            return field_value == expected_value
        elif operator == RuleOperator.NEQ:
            return field_value != expected_value
        elif operator == RuleOperator.CONTAINS:
            return str(expected_value) in str(field_value)
        elif operator == RuleOperator.REGEX:
            return bool(re.search(str(expected_value), str(field_value)))
        elif operator == RuleOperator.IN:
            return field_value in expected_value
        elif operator == RuleOperator.NOT_IN:
            return field_value not in expected_value
        elif operator == RuleOperator.BETWEEN:
            if isinstance(expected_value, (list, tuple)) and len(expected_value) == 2:
                return expected_value[0] <= field_value <= expected_value[1]
            return False
        elif operator == RuleOperator.IS_EMPTY:
            return not field_value or (isinstance(field_value, (list, dict, str)) and len(field_value) == 0)
        elif operator == RuleOperator.IS_NOT_EMPTY:
            return field_value and (not isinstance(field_value, (list, dict, str)) or len(field_value) > 0)
        else:
            raise ValueError(f"Unknown operator: {operator}")


@dataclass
class Rule:
    """Represents a complete rule with conditions and actions."""
    name: str
    description: str
    conditions: List[RuleCondition]
    action: RuleAction
    priority: int = 100  # Lower numbers = higher priority
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom_handler: Optional[Callable] = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate all conditions using AND logic."""
        if not self.enabled:
            return False
        
        return all(condition.evaluate(context) for condition in self.conditions)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the rule's action and return result."""
        result = {
            "rule_name": self.name,
            "action": self.action.value,
            "executed_at": datetime.now().isoformat(),
            "context_snapshot": self._create_context_snapshot(context)
        }
        
        if self.action == RuleAction.CUSTOM and self.custom_handler:
            try:
                custom_result = self.custom_handler(context, self)
                result["custom_result"] = custom_result
            except Exception as e:
                logging.error(f"Custom rule handler failed for '{self.name}': {e}")
                result["error"] = str(e)
        
        return result
    
    def _create_context_snapshot(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a safe snapshot of relevant context for logging."""
        snapshot = {}
        safe_keys = ["confidence", "message_type", "source", "timestamp", "user_id"]
        
        for key in safe_keys:
            if key in context:
                snapshot[key] = context[key]
        
        return snapshot


class RuleEngine:
    """Main rule engine for evaluating and executing decision rules."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the rule engine."""
        self.rules: List[Rule] = []
        self.custom_handlers: Dict[str, Callable] = {}
        self.execution_stats: Dict[str, int] = {
            "total_evaluations": 0,
            "rules_triggered": 0,
            "approval_count": 0,
            "rejection_count": 0,
            "escalation_count": 0,
            "retry_count": 0
        }
        self.logger = logging.getLogger(__name__)
        
        # Load rules from configuration if provided
        if config_path and os.path.exists(config_path):
            self.load_rules_from_config(config_path)
        else:
            self._load_default_rules()
    
    def register_rule(self, rule: Rule) -> None:
        """Register a new rule with the engine."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)  # Sort by priority
        self.logger.info(f"Registered rule: {rule.name} (priority: {rule.priority})")
    
    def register_custom_handler(self, name: str, handler: Callable) -> None:
        """Register a custom action handler."""
        self.custom_handlers[name] = handler
        self.logger.info(f"Registered custom handler: {name}")
    
    def evaluate_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate all rules against the provided context."""
        self.execution_stats["total_evaluations"] += 1
        results = []
        
        for rule in self.rules:
            try:
                if rule.evaluate(context):
                    self.execution_stats["rules_triggered"] += 1
                    result = rule.execute(context)
                    results.append(result)
                    
                    # Update action-specific stats
                    action = rule.action.value
                    if action in ["approve"]:
                        self.execution_stats["approval_count"] += 1
                    elif action in ["reject"]:
                        self.execution_stats["rejection_count"] += 1
                    elif action in ["escalate"]:
                        self.execution_stats["escalation_count"] += 1
                    elif action in ["retry"]:
                        self.execution_stats["retry_count"] += 1
                    
                    self.logger.info(f"Rule triggered: {rule.name} -> {action}")
                    
                    # If this is a decisive action, stop processing other rules
                    if rule.action in [RuleAction.APPROVE, RuleAction.REJECT, RuleAction.ESCALATE]:
                        break
            
            except Exception as e:
                self.logger.error(f"Error evaluating rule '{rule.name}': {e}")
        
        return results
    
    async def evaluate_rules_async(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Asynchronous version of rule evaluation."""
        return await asyncio.to_thread(self.evaluate_rules, context)
    
    def get_decision(self, context: Dict[str, Any]) -> str:
        """Get the final decision based on rule evaluation."""
        results = self.evaluate_rules(context)
        
        if not results:
            return RuleAction.CONTINUE.value
        
        # Return the action from the highest priority rule that triggered
        return results[0]["action"]
    
    def load_rules_from_config(self, config_path: str) -> None:
        """Load rules from a YAML configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            if "rules" not in config:
                self.logger.warning(f"No 'rules' section found in {config_path}")
                return
            
            for rule_config in config["rules"]:
                rule = self._create_rule_from_config(rule_config)
                if rule:
                    self.register_rule(rule)
            
            self.logger.info(f"Loaded {len(config['rules'])} rules from {config_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to load rules from {config_path}: {e}")
            self._load_default_rules()
    
    def _create_rule_from_config(self, rule_config: Dict[str, Any]) -> Optional[Rule]:
        """Create a Rule object from configuration dictionary."""
        try:
            conditions = []
            for cond_config in rule_config.get("conditions", []):
                condition = RuleCondition(
                    field=cond_config["field"],
                    operator=RuleOperator(cond_config["operator"]),
                    value=cond_config["value"],
                    description=cond_config.get("description", "")
                )
                conditions.append(condition)
            
            rule = Rule(
                name=rule_config["name"],
                description=rule_config.get("description", ""),
                conditions=conditions,
                action=RuleAction(rule_config["action"]),
                priority=rule_config.get("priority", 100),
                enabled=rule_config.get("enabled", True),
                metadata=rule_config.get("metadata", {})
            )
            
            # Register custom handler if specified
            if "custom_handler" in rule_config:
                handler_name = rule_config["custom_handler"]
                if handler_name in self.custom_handlers:
                    rule.custom_handler = self.custom_handlers[handler_name]
            
            return rule
        
        except Exception as e:
            self.logger.error(f"Failed to create rule from config: {e}")
            return None
    
    def _load_default_rules(self) -> None:
        """Load default rules for the ODIN Protocol."""
        # High confidence approval rule
        self.register_rule(Rule(
            name="high_confidence_approval",
            description="Approve messages with high confidence scores",
            conditions=[
                RuleCondition("confidence", RuleOperator.GTE, 0.9, "Confidence >= 90%")
            ],
            action=RuleAction.APPROVE,
            priority=10
        ))
        
        # Low confidence rejection rule
        self.register_rule(Rule(
            name="low_confidence_rejection",
            description="Reject messages with very low confidence",
            conditions=[
                RuleCondition("confidence", RuleOperator.LT, 0.3, "Confidence < 30%")
            ],
            action=RuleAction.REJECT,
            priority=20
        ))
        
        # Medium confidence retry rule
        self.register_rule(Rule(
            name="medium_confidence_retry",
            description="Retry messages with medium confidence",
            conditions=[
                RuleCondition("confidence", RuleOperator.BETWEEN, [0.3, 0.7], "30% <= Confidence < 70%")
            ],
            action=RuleAction.RETRY,
            priority=30
        ))
        
        # Compliance escalation rule
        self.register_rule(Rule(
            name="compliance_escalation",
            description="Escalate messages flagged for compliance review",
            conditions=[
                RuleCondition("context.topic", RuleOperator.EQ, "compliance", "Compliance topic detected")
            ],
            action=RuleAction.ESCALATE,
            priority=5
        ))
        
        # Message size warning rule
        self.register_rule(Rule(
            name="large_message_warning",
            description="Log warning for large messages",
            conditions=[
                RuleCondition("message_size", RuleOperator.GT, 10000, "Message size > 10KB")
            ],
            action=RuleAction.LOG_WARNING,
            priority=50
        ))
        
        self.logger.info("Loaded default rules for ODIN Protocol")
    
    def export_rules_to_config(self, output_path: str) -> None:
        """Export current rules to a YAML configuration file."""
        try:
            rules_config = {
                "version": "1.0",
                "description": "ODIN Protocol Rule Engine Configuration",
                "created_at": datetime.now().isoformat(),
                "rules": []
            }
            
            for rule in self.rules:
                rule_config = {
                    "name": rule.name,
                    "description": rule.description,
                    "action": rule.action.value,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "metadata": rule.metadata,
                    "conditions": []
                }
                
                for condition in rule.conditions:
                    cond_config = {
                        "field": condition.field,
                        "operator": condition.operator.value,
                        "value": condition.value,
                        "description": condition.description
                    }
                    rule_config["conditions"].append(cond_config)
                
                rules_config["rules"].append(rule_config)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                yaml.dump(rules_config, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Exported {len(self.rules)} rules to {output_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to export rules to {output_path}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rule engine execution statistics."""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for rule in self.rules if rule.enabled),
            "execution_stats": self.execution_stats.copy(),
            "rules_summary": [
                {
                    "name": rule.name,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "action": rule.action.value
                }
                for rule in self.rules
            ]
        }
    
    def validate_context(self, context: Dict[str, Any]) -> List[str]:
        """Validate that context contains required fields for rule evaluation."""
        required_fields = set()
        for rule in self.rules:
            for condition in rule.conditions:
                required_fields.add(condition.field.split('.')[0])
        
        missing_fields = []
        for field in required_fields:
            if field not in context:
                missing_fields.append(field)
        
        return missing_fields


# Global rule engine instance
_rule_engine: Optional[RuleEngine] = None


def get_rule_engine(config_path: Optional[str] = None) -> RuleEngine:
    """Get the global rule engine instance."""
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = RuleEngine(config_path)
    return _rule_engine


def initialize_rule_engine(config_path: Optional[str] = None) -> RuleEngine:
    """Initialize the rule engine with optional configuration."""
    global _rule_engine
    _rule_engine = RuleEngine(config_path)
    return _rule_engine


# Example custom handlers
def semantic_drift_handler(context: Dict[str, Any], rule: Rule) -> Dict[str, Any]:
    """Custom handler for semantic drift detection."""
    drift_score = context.get("semantic_drift", 0.0)
    
    if drift_score > 0.8:
        return {
            "action": "escalate",
            "reason": f"High semantic drift detected: {drift_score}",
            "recommended_action": "human_review"
        }
    elif drift_score > 0.5:
        return {
            "action": "retry",
            "reason": f"Moderate semantic drift: {drift_score}",
            "recommended_action": "rephrase_request"
        }
    else:
        return {
            "action": "continue",
            "reason": f"Acceptable semantic drift: {drift_score}"
        }


def compliance_check_handler(context: Dict[str, Any], rule: Rule) -> Dict[str, Any]:
    """Custom handler for compliance checking."""
    compliance_data = context.get("compliance", {})
    
    violations = []
    if compliance_data.get("contains_pii", False):
        violations.append("PII_DETECTED")
    
    if compliance_data.get("inappropriate_content", False):
        violations.append("INAPPROPRIATE_CONTENT")
    
    if compliance_data.get("policy_violation", False):
        violations.append("POLICY_VIOLATION")
    
    if violations:
        return {
            "action": "reject",
            "reason": f"Compliance violations: {', '.join(violations)}",
            "violations": violations,
            "requires_audit": True
        }
    
    return {
        "action": "continue",
        "reason": "Compliance check passed"
    }
