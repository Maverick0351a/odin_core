#!/usr/bin/env python3
"""
Additional Colleagues for Hel Rule Engine Mediator Pattern.
Implements PolicyColleague and ActionTriggerColleague for enhanced rule processing.
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from hel_rule_engine import BaseColleague


class PolicyType(Enum):
    """Types of policies that can be enforced."""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    BUSINESS_RULE = "business_rule"
    DATA_GOVERNANCE = "data_governance"
    OPERATIONAL = "operational"


class ActionType(Enum):
    """Types of actions that can be triggered."""
    NOTIFICATION = "notification"
    ESCALATION = "escalation"
    AUTOMATION = "automation"
    AUDIT_LOG = "audit_log"
    WORKFLOW = "workflow"
    ALERT = "alert"


@dataclass
class Policy:
    """Represents a policy that can be enforced."""
    policy_id: str
    policy_type: PolicyType
    name: str
    description: str
    rules: List[str]  # Rule conditions in text format
    enforcement_level: str = "warn"  # warn, block, audit
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ActionTrigger:
    """Represents an action that can be triggered."""
    trigger_id: str
    action_type: ActionType
    name: str
    description: str
    conditions: List[str]  # Trigger conditions
    parameters: Dict[str, Any] = field(default_factory=dict)
    cooldown_minutes: int = 0  # Minimum time between triggers
    last_triggered: Optional[datetime] = None
    active: bool = True


class PolicyColleague(BaseColleague):
    """Colleague responsible for policy enforcement and compliance checks."""
    
    def __init__(self):
        super().__init__("policy")
        self.policies: Dict[str, Policy] = {}
        self.policy_violations: List[Dict[str, Any]] = []
        self.enforcement_stats = {
            "policies_evaluated": 0,
            "violations_detected": 0,
            "warnings_issued": 0,
            "blocks_enforced": 0
        }
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default policies for ODIN Protocol."""
        
        # Security Policy: PII Detection
        pii_policy = Policy(
            policy_id="pii_detection_001",
            policy_type=PolicyType.SECURITY,
            name="PII Detection Policy",
            description="Detect and flag personally identifiable information",
            rules=[
                "contains_email_pattern",
                "contains_phone_pattern", 
                "contains_ssn_pattern",
                "contains_credit_card_pattern"
            ],
            enforcement_level="block"
        )
        self.policies[pii_policy.policy_id] = pii_policy
        
        # Compliance Policy: Content Standards
        content_policy = Policy(
            policy_id="content_standards_001", 
            policy_type=PolicyType.COMPLIANCE,
            name="Content Standards Policy",
            description="Ensure content meets quality and appropriateness standards",
            rules=[
                "minimum_content_length",
                "inappropriate_content_check",
                "language_appropriateness"
            ],
            enforcement_level="warn"
        )
        self.policies[content_policy.policy_id] = content_policy
        
        # Business Rule: Confidence Thresholds
        confidence_policy = Policy(
            policy_id="confidence_threshold_001",
            policy_type=PolicyType.BUSINESS_RULE,
            name="Confidence Threshold Policy", 
            description="Enforce minimum confidence levels for different operations",
            rules=[
                "minimum_confidence_for_approval",
                "escalation_on_low_confidence"
            ],
            enforcement_level="block"
        )
        self.policies[confidence_policy.policy_id] = confidence_policy
        
        self.logger.info(f"Initialized {len(self.policies)} default policies")
    
    async def handle_request(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle policy-related requests."""
        if request_type == "evaluate_policies":
            return await self._evaluate_policies(context)
        elif request_type == "check_compliance":
            return await self._check_compliance(context)
        elif request_type == "enforce_policy":
            return await self._enforce_policy(context)
        elif request_type == "get_policy_recommendations":
            return await self._get_policy_recommendations(context)
        elif request_type == "audit_policy_violations":
            return await self._audit_policy_violations(context)
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this colleague provides."""
        return [
            "evaluate_policies",
            "check_compliance",
            "enforce_policy", 
            "get_policy_recommendations",
            "audit_policy_violations",
            "policy_management"
        ]
    
    async def _evaluate_policies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all applicable policies against the context."""
        self.enforcement_stats["policies_evaluated"] += 1
        
        violations = []
        warnings = []
        policy_results = {}
        
        for policy_id, policy in self.policies.items():
            if not policy.active:
                continue
            
            policy_result = await self._evaluate_single_policy(policy, context)
            policy_results[policy_id] = policy_result
            
            if policy_result["violation_detected"]:
                self.enforcement_stats["violations_detected"] += 1
                
                violation_info = {
                    "policy_id": policy_id,
                    "policy_name": policy.name,
                    "policy_type": policy.policy_type.value,
                    "enforcement_level": policy.enforcement_level,
                    "violation_details": policy_result["violation_details"],
                    "timestamp": datetime.now().isoformat()
                }
                
                if policy.enforcement_level == "block":
                    violations.append(violation_info)
                    self.enforcement_stats["blocks_enforced"] += 1
                elif policy.enforcement_level == "warn":
                    warnings.append(violation_info)
                    self.enforcement_stats["warnings_issued"] += 1
                
                # Store for audit trail
                self.policy_violations.append(violation_info)
        
        return {
            "evaluation_completed": True,
            "policies_evaluated": len([p for p in self.policies.values() if p.active]),
            "violations": violations,
            "warnings": warnings,
            "policy_results": policy_results,
            "enforcement_required": len(violations) > 0,
            "recommendation": "block" if violations else "warn" if warnings else "allow"
        }
    
    async def _evaluate_single_policy(self, policy: Policy, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single policy against the context."""
        violation_detected = False
        violation_details = []
        
        # Simple rule evaluation (in real implementation, this would be more sophisticated)
        content = context.get("content", "")
        confidence = context.get("confidence", 1.0)
        
        if policy.policy_type == PolicyType.SECURITY:
            # Check for PII patterns
            if "contains_email_pattern" in policy.rules:
                if "@" in content and "." in content:
                    violation_detected = True
                    violation_details.append("Email pattern detected")
            
            if "contains_phone_pattern" in policy.rules:
                import re
                phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
                if re.search(phone_pattern, content):
                    violation_detected = True
                    violation_details.append("Phone number pattern detected")
        
        elif policy.policy_type == PolicyType.COMPLIANCE:
            # Check content standards
            if "minimum_content_length" in policy.rules:
                if len(content) < 10:
                    violation_detected = True
                    violation_details.append("Content below minimum length")
            
            if "inappropriate_content_check" in policy.rules:
                inappropriate_keywords = ["spam", "malicious", "harmful"]
                if any(keyword in content.lower() for keyword in inappropriate_keywords):
                    violation_detected = True
                    violation_details.append("Inappropriate content detected")
        
        elif policy.policy_type == PolicyType.BUSINESS_RULE:
            # Check confidence thresholds
            if "minimum_confidence_for_approval" in policy.rules:
                if confidence < 0.7:
                    violation_detected = True
                    violation_details.append(f"Confidence {confidence} below threshold 0.7")
        
        return {
            "policy_id": policy.policy_id,
            "violation_detected": violation_detected,
            "violation_details": violation_details,
            "evaluation_timestamp": datetime.now().isoformat()
        }
    
    async def _check_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance status for the given context."""
        compliance_policies = [p for p in self.policies.values() 
                             if p.policy_type == PolicyType.COMPLIANCE and p.active]
        
        compliance_results = []
        overall_compliant = True
        
        for policy in compliance_policies:
            result = await self._evaluate_single_policy(policy, context)
            compliance_results.append(result)
            if result["violation_detected"]:
                overall_compliant = False
        
        return {
            "compliant": overall_compliant,
            "compliance_policies_checked": len(compliance_policies),
            "compliance_results": compliance_results,
            "compliance_score": sum(1 for r in compliance_results if not r["violation_detected"]) / len(compliance_results) if compliance_results else 1.0
        }
    
    async def _enforce_policy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce a specific policy."""
        policy_id = context.get("policy_id")
        if not policy_id or policy_id not in self.policies:
            return {"error": "Invalid or missing policy_id"}
        
        policy = self.policies[policy_id]
        result = await self._evaluate_single_policy(policy, context)
        
        enforcement_action = "none"
        if result["violation_detected"]:
            if policy.enforcement_level == "block":
                enforcement_action = "blocked"
            elif policy.enforcement_level == "warn":
                enforcement_action = "warning_issued"
            elif policy.enforcement_level == "audit":
                enforcement_action = "audit_logged"
        
        return {
            "policy_id": policy_id,
            "enforcement_action": enforcement_action,
            "policy_result": result,
            "enforcement_timestamp": datetime.now().isoformat()
        }
    
    async def _get_policy_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get policy recommendations based on context."""
        recommendations = []
        
        # Analyze context and suggest relevant policies
        content = context.get("content", "")
        confidence = context.get("confidence", 1.0)
        data_source = context.get("data_source", "unknown")
        
        if confidence < 0.5:
            recommendations.append({
                "type": "policy_suggestion",
                "policy_type": "business_rule",
                "recommendation": "Consider implementing stricter confidence thresholds",
                "rationale": f"Low confidence detected: {confidence}"
            })
        
        if data_source == "external_api":
            recommendations.append({
                "type": "security_review",
                "policy_type": "security", 
                "recommendation": "Enhanced security validation for external data",
                "rationale": "External data source requires additional validation"
            })
        
        if len(content) > 1000:
            recommendations.append({
                "type": "performance_optimization",
                "policy_type": "operational",
                "recommendation": "Consider content size limits for performance",
                "rationale": f"Large content detected: {len(content)} characters"
            })
        
        return {
            "recommendations": recommendations,
            "recommendation_count": len(recommendations),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def _audit_policy_violations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Audit policy violations and generate report."""
        time_range = context.get("time_range_hours", 24)
        cutoff_time = datetime.now() - timedelta(hours=time_range)
        
        recent_violations = [
            v for v in self.policy_violations
            if datetime.fromisoformat(v["timestamp"]) >= cutoff_time
        ]
        
        # Group violations by policy type
        violations_by_type = {}
        for violation in recent_violations:
            policy_type = violation["policy_type"]
            if policy_type not in violations_by_type:
                violations_by_type[policy_type] = []
            violations_by_type[policy_type].append(violation)
        
        return {
            "audit_period_hours": time_range,
            "total_violations": len(recent_violations),
            "violations_by_type": violations_by_type,
            "enforcement_stats": self.enforcement_stats.copy(),
            "audit_timestamp": datetime.now().isoformat()
        }
    
    def add_policy(self, policy: Policy) -> None:
        """Add a new policy to the system."""
        self.policies[policy.policy_id] = policy
        self.logger.info(f"Added policy: {policy.name} ({policy.policy_id})")
    
    def get_policy_stats(self) -> Dict[str, Any]:
        """Get policy management statistics."""
        active_policies = sum(1 for p in self.policies.values() if p.active)
        
        return {
            "total_policies": len(self.policies),
            "active_policies": active_policies,
            "policies_by_type": {
                policy_type.value: sum(1 for p in self.policies.values() 
                                     if p.policy_type == policy_type and p.active)
                for policy_type in PolicyType
            },
            "enforcement_stats": self.enforcement_stats.copy(),
            "total_violations": len(self.policy_violations)
        }


class ActionTriggerColleague(BaseColleague):
    """Colleague responsible for triggering actions based on rule results."""
    
    def __init__(self):
        super().__init__("action_trigger")
        self.triggers: Dict[str, ActionTrigger] = {}
        self.action_history: List[Dict[str, Any]] = []
        self.trigger_stats = {
            "triggers_evaluated": 0,
            "actions_triggered": 0,
            "notifications_sent": 0,
            "escalations_created": 0,
            "workflows_started": 0
        }
        
        # Initialize default triggers
        self._initialize_default_triggers()
    
    def _initialize_default_triggers(self):
        """Initialize default action triggers."""
        
        # High-priority escalation trigger
        escalation_trigger = ActionTrigger(
            trigger_id="high_priority_escalation",
            action_type=ActionType.ESCALATION,
            name="High Priority Escalation",
            description="Escalate high-priority issues to human review",
            conditions=["action == 'escalate'", "priority == 'high'"],
            parameters={
                "escalation_level": "L2",
                "notify_channels": ["email", "slack"],
                "urgency": "high"
            },
            cooldown_minutes=5
        )
        self.triggers[escalation_trigger.trigger_id] = escalation_trigger
        
        # Security alert trigger
        security_alert_trigger = ActionTrigger(
            trigger_id="security_alert",
            action_type=ActionType.ALERT,
            name="Security Alert",
            description="Send alerts for security violations",
            conditions=["policy_type == 'security'", "violation_detected == true"],
            parameters={
                "alert_severity": "critical",
                "notify_security_team": True,
                "create_incident": True
            },
            cooldown_minutes=1
        )
        self.triggers[security_alert_trigger.trigger_id] = security_alert_trigger
        
        # Audit logging trigger
        audit_trigger = ActionTrigger(
            trigger_id="audit_logging",
            action_type=ActionType.AUDIT_LOG,
            name="Audit Logging",
            description="Log all rule evaluations for audit purposes",
            conditions=["always_true"],
            parameters={
                "log_level": "info",
                "include_context": True,
                "retention_days": 90
            }
        )
        self.triggers[audit_trigger.trigger_id] = audit_trigger
        
        # Low confidence notification
        confidence_notification = ActionTrigger(
            trigger_id="low_confidence_notification",
            action_type=ActionType.NOTIFICATION,
            name="Low Confidence Notification",
            description="Notify when confidence scores are low",
            conditions=["confidence < 0.3"],
            parameters={
                "notification_type": "warning",
                "recipients": ["data_team", "qa_team"],
                "include_improvement_suggestions": True
            },
            cooldown_minutes=15
        )
        self.triggers[confidence_notification.trigger_id] = confidence_notification
        
        self.logger.info(f"Initialized {len(self.triggers)} default action triggers")
    
    async def handle_request(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle action trigger related requests."""
        if request_type == "evaluate_triggers":
            return await self._evaluate_triggers(context)
        elif request_type == "execute_action":
            return await self._execute_action(context)
        elif request_type == "get_trigger_recommendations":
            return await self._get_trigger_recommendations(context)
        elif request_type == "audit_actions":
            return await self._audit_actions(context)
        elif request_type == "manage_cooldowns":
            return await self._manage_cooldowns(context)
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this colleague provides."""
        return [
            "evaluate_triggers",
            "execute_action",
            "get_trigger_recommendations",
            "audit_actions",
            "manage_cooldowns",
            "action_management"
        ]
    
    async def _evaluate_triggers(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all triggers against the context and execute matching actions."""
        self.trigger_stats["triggers_evaluated"] += 1
        
        triggered_actions = []
        skipped_triggers = []
        
        for trigger_id, trigger in self.triggers.items():
            if not trigger.active:
                continue
            
            # Check cooldown
            if self._is_in_cooldown(trigger):
                skipped_triggers.append({
                    "trigger_id": trigger_id,
                    "reason": "cooldown_active",
                    "cooldown_remaining_minutes": self._get_cooldown_remaining(trigger)
                })
                continue
            
            # Evaluate trigger conditions
            if await self._evaluate_trigger_conditions(trigger, context):
                action_result = await self._execute_trigger_action(trigger, context)
                triggered_actions.append({
                    "trigger_id": trigger_id,
                    "action_type": trigger.action_type.value,
                    "action_result": action_result,
                    "triggered_at": datetime.now().isoformat()
                })
                
                # Update last triggered time
                trigger.last_triggered = datetime.now()
                self.trigger_stats["actions_triggered"] += 1
        
        return {
            "evaluation_completed": True,
            "triggers_evaluated": len([t for t in self.triggers.values() if t.active]),
            "triggered_actions": triggered_actions,
            "skipped_triggers": skipped_triggers,
            "total_actions_triggered": len(triggered_actions)
        }
    
    async def _evaluate_trigger_conditions(self, trigger: ActionTrigger, context: Dict[str, Any]) -> bool:
        """Evaluate if trigger conditions are met."""
        try:
            for condition in trigger.conditions:
                if condition == "always_true":
                    continue
                
                # Simple condition evaluation (in real implementation, use proper parser)
                if "action == 'escalate'" in condition:
                    if context.get("action") != "escalate":
                        return False
                
                elif "priority == 'high'" in condition:
                    if context.get("priority") != "high":
                        return False
                
                elif "policy_type == 'security'" in condition:
                    if context.get("policy_type") != "security":
                        return False
                
                elif "violation_detected == true" in condition:
                    if not context.get("violation_detected", False):
                        return False
                
                elif "confidence <" in condition:
                    import re
                    match = re.search(r'confidence < ([\d.]+)', condition)
                    if match:
                        threshold = float(match.group(1))
                        if context.get("confidence", 1.0) >= threshold:
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating trigger conditions: {e}")
            return False
    
    async def _execute_trigger_action(self, trigger: ActionTrigger, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action for a triggered trigger."""
        action_result = {
            "trigger_id": trigger.trigger_id,
            "action_type": trigger.action_type.value,
            "executed_at": datetime.now().isoformat(),
            "success": True,
            "details": {}
        }
        
        try:
            if trigger.action_type == ActionType.NOTIFICATION:
                result = await self._send_notification(trigger, context)
                action_result["details"] = result
                self.trigger_stats["notifications_sent"] += 1
            
            elif trigger.action_type == ActionType.ESCALATION:
                result = await self._create_escalation(trigger, context)
                action_result["details"] = result
                self.trigger_stats["escalations_created"] += 1
            
            elif trigger.action_type == ActionType.ALERT:
                result = await self._send_alert(trigger, context)
                action_result["details"] = result
            
            elif trigger.action_type == ActionType.AUDIT_LOG:
                result = await self._create_audit_log(trigger, context)
                action_result["details"] = result
            
            elif trigger.action_type == ActionType.WORKFLOW:
                result = await self._start_workflow(trigger, context)
                action_result["details"] = result
                self.trigger_stats["workflows_started"] += 1
            
            elif trigger.action_type == ActionType.AUTOMATION:
                result = await self._execute_automation(trigger, context)
                action_result["details"] = result
            
            # Store in action history
            self.action_history.append(action_result.copy())
            
        except Exception as e:
            action_result["success"] = False
            action_result["error"] = str(e)
            self.logger.error(f"Error executing action for trigger {trigger.trigger_id}: {e}")
        
        return action_result
    
    async def _send_notification(self, trigger: ActionTrigger, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send a notification."""
        recipients = trigger.parameters.get("recipients", ["admin"])
        notification_type = trigger.parameters.get("notification_type", "info")
        
        # Simulate notification sending
        notification_data = {
            "recipients": recipients,
            "type": notification_type,
            "subject": f"Hel Rule Engine: {trigger.name}",
            "message": f"Trigger '{trigger.name}' activated",
            "context_summary": {
                "confidence": context.get("confidence"),
                "action": context.get("action"),
                "trace_id": context.get("trace_id")
            },
            "sent_at": datetime.now().isoformat()
        }
        
        self.logger.info(f"Notification sent: {notification_data['subject']}")
        return notification_data
    
    async def _create_escalation(self, trigger: ActionTrigger, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create an escalation."""
        escalation_level = trigger.parameters.get("escalation_level", "L1")
        urgency = trigger.parameters.get("urgency", "medium")
        
        escalation_data = {
            "escalation_id": f"ESC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "level": escalation_level,
            "urgency": urgency,
            "trigger": trigger.name,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "status": "open"
        }
        
        self.logger.info(f"Escalation created: {escalation_data['escalation_id']}")
        return escalation_data
    
    async def _send_alert(self, trigger: ActionTrigger, context: Dict[str, Any]) -> Dict[str, Any]:
        """Send an alert."""
        severity = trigger.parameters.get("alert_severity", "medium")
        
        alert_data = {
            "alert_id": f"ALERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "severity": severity,
            "trigger": trigger.name,
            "message": f"Security alert triggered: {context.get('violation_details', [])}",
            "context": context,
            "created_at": datetime.now().isoformat()
        }
        
        self.logger.warning(f"Security alert: {alert_data['alert_id']}")
        return alert_data
    
    async def _create_audit_log(self, trigger: ActionTrigger, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create an audit log entry."""
        log_level = trigger.parameters.get("log_level", "info")
        include_context = trigger.parameters.get("include_context", True)
        
        audit_entry = {
            "audit_id": f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "log_level": log_level,
            "event": "rule_evaluation",
            "trigger": trigger.name,
            "timestamp": datetime.now().isoformat()
        }
        
        if include_context:
            audit_entry["context"] = context
        
        self.logger.info(f"Audit log created: {audit_entry['audit_id']}")
        return audit_entry
    
    async def _start_workflow(self, trigger: ActionTrigger, context: Dict[str, Any]) -> Dict[str, Any]:
        """Start a workflow."""
        workflow_data = {
            "workflow_id": f"WF-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "trigger": trigger.name,
            "context": context,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        
        self.logger.info(f"Workflow started: {workflow_data['workflow_id']}")
        return workflow_data
    
    async def _execute_automation(self, trigger: ActionTrigger, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automation."""
        automation_data = {
            "automation_id": f"AUTO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "trigger": trigger.name,
            "actions_performed": ["log_event", "update_metrics"],
            "context": context,
            "executed_at": datetime.now().isoformat()
        }
        
        self.logger.info(f"Automation executed: {automation_data['automation_id']}")
        return automation_data
    
    def _is_in_cooldown(self, trigger: ActionTrigger) -> bool:
        """Check if trigger is in cooldown period."""
        if not trigger.last_triggered or trigger.cooldown_minutes == 0:
            return False
        
        cooldown_duration = timedelta(minutes=trigger.cooldown_minutes)
        return datetime.now() - trigger.last_triggered < cooldown_duration
    
    def _get_cooldown_remaining(self, trigger: ActionTrigger) -> float:
        """Get remaining cooldown time in minutes."""
        if not trigger.last_triggered:
            return 0.0
        
        elapsed = datetime.now() - trigger.last_triggered
        cooldown_duration = timedelta(minutes=trigger.cooldown_minutes)
        
        if elapsed >= cooldown_duration:
            return 0.0
        
        remaining = cooldown_duration - elapsed
        return remaining.total_seconds() / 60.0
    
    async def _execute_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action by ID."""
        trigger_id = context.get("trigger_id")
        if not trigger_id or trigger_id not in self.triggers:
            return {"error": "Invalid or missing trigger_id"}
        
        trigger = self.triggers[trigger_id]
        return await self._execute_trigger_action(trigger, context)
    
    async def _get_trigger_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get action trigger recommendations."""
        recommendations = []
        
        # Analyze context for trigger recommendations
        confidence = context.get("confidence", 1.0)
        action = context.get("action", "continue")
        
        if confidence < 0.5:
            recommendations.append({
                "trigger_type": "notification",
                "recommendation": "Add low confidence monitoring",
                "rationale": f"Confidence {confidence} suggests monitoring needed"
            })
        
        if action == "escalate":
            recommendations.append({
                "trigger_type": "escalation",
                "recommendation": "Implement escalation workflow",
                "rationale": "Escalation action detected"
            })
        
        return {
            "recommendations": recommendations,
            "recommendation_count": len(recommendations)
        }
    
    async def _audit_actions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Audit action trigger history."""
        time_range = context.get("time_range_hours", 24)
        cutoff_time = datetime.now() - timedelta(hours=time_range)
        
        recent_actions = [
            action for action in self.action_history
            if datetime.fromisoformat(action["executed_at"]) >= cutoff_time
        ]
        
        # Group by action type
        actions_by_type = {}
        for action in recent_actions:
            action_type = action["action_type"]
            if action_type not in actions_by_type:
                actions_by_type[action_type] = []
            actions_by_type[action_type].append(action)
        
        return {
            "audit_period_hours": time_range,
            "total_actions": len(recent_actions),
            "actions_by_type": actions_by_type,
            "trigger_stats": self.trigger_stats.copy(),
            "audit_timestamp": datetime.now().isoformat()
        }
    
    async def _manage_cooldowns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Manage trigger cooldowns."""
        action = context.get("cooldown_action", "status")
        
        if action == "reset":
            trigger_id = context.get("trigger_id")
            if trigger_id and trigger_id in self.triggers:
                self.triggers[trigger_id].last_triggered = None
                return {"message": f"Cooldown reset for trigger {trigger_id}"}
        
        # Return cooldown status for all triggers
        cooldown_status = {}
        for trigger_id, trigger in self.triggers.items():
            cooldown_status[trigger_id] = {
                "in_cooldown": self._is_in_cooldown(trigger),
                "cooldown_remaining_minutes": self._get_cooldown_remaining(trigger),
                "last_triggered": trigger.last_triggered.isoformat() if trigger.last_triggered else None
            }
        
        return {
            "cooldown_status": cooldown_status,
            "checked_at": datetime.now().isoformat()
        }
    
    def add_trigger(self, trigger: ActionTrigger) -> None:
        """Add a new action trigger."""
        self.triggers[trigger.trigger_id] = trigger
        self.logger.info(f"Added action trigger: {trigger.name} ({trigger.trigger_id})")
    
    def get_trigger_stats(self) -> Dict[str, Any]:
        """Get action trigger statistics."""
        active_triggers = sum(1 for t in self.triggers.values() if t.active)
        
        return {
            "total_triggers": len(self.triggers),
            "active_triggers": active_triggers,
            "triggers_by_type": {
                action_type.value: sum(1 for t in self.triggers.values()
                                     if t.action_type == action_type and t.active)
                for action_type in ActionType
            },
            "trigger_stats": self.trigger_stats.copy(),
            "total_actions_in_history": len(self.action_history)
        }
