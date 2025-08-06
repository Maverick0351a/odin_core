#!/usr/bin/env python3
"""
Enterprise HEL Integration Layer
Provides enterprise-grade features for ODIN Protocol adoption
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from hel_mediator_ai import HelMediatorAI, create_hel_mediator_ai
from rules_engine import Rule, RuleCondition, RuleOperator, RuleAction


@dataclass
class EnterprisePolicy:
    """Enterprise policy configuration for HEL Rule System"""
    policy_id: str
    name: str
    description: str
    compliance_level: str  # "strict", "moderate", "flexible"
    auto_escalation: bool
    custom_rules: List[Dict[str, Any]]
    audit_requirements: Dict[str, Any]


class EnterpriseHelIntegration:
    """Enterprise integration layer for HEL Rule System"""
    
    def __init__(self, organization_id: str):
        self.organization_id = organization_id
        self.hel_mediator = create_hel_mediator_ai()
        self.enterprise_policies: Dict[str, EnterprisePolicy] = {}
        self.compliance_logs: List[Dict[str, Any]] = []
        self.performance_metrics = {
            "total_evaluations": 0,
            "compliance_violations": 0,
            "auto_corrections": 0,
            "escalations": 0,
            "average_response_time": 0.0
        }
    
    def register_enterprise_policy(self, policy: EnterprisePolicy) -> None:
        """Register enterprise-specific policy"""
        self.enterprise_policies[policy.policy_id] = policy
        
        # Convert policy to HEL rules
        for rule_config in policy.custom_rules:
            rule = self._create_enterprise_rule(rule_config, policy)
            self.hel_mediator.rule_engine.register_rule(rule)
        
        print(f"✅ Registered enterprise policy: {policy.name}")
    
    def _create_enterprise_rule(self, rule_config: Dict[str, Any], policy: EnterprisePolicy) -> Rule:
        """Create enterprise rule from policy configuration"""
        conditions = []
        for cond in rule_config.get("conditions", []):
            condition = RuleCondition(
                field=cond["field"],
                operator=RuleOperator(cond["operator"]),
                value=cond["value"],
                description=f"Enterprise policy: {policy.name}"
            )
            conditions.append(condition)
        
        return Rule(
            name=f"enterprise_{policy.policy_id}_{rule_config['name']}",
            description=f"Enterprise rule for {policy.name}: {rule_config.get('description', '')}",
            conditions=conditions,
            action=RuleAction(rule_config["action"]),
            priority=rule_config.get("priority", 50),
            metadata={
                "enterprise_policy": policy.policy_id,
                "compliance_level": policy.compliance_level,
                "organization_id": self.organization_id
            }
        )
    
    async def evaluate_with_enterprise_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate message with enterprise compliance requirements"""
        start_time = datetime.now()
        
        # Add enterprise context
        enterprise_context = {
            **context,
            "organization_id": self.organization_id,
            "enterprise_policies": list(self.enterprise_policies.keys()),
            "compliance_mode": "enterprise"
        }
        
        # Create OdinMessage from context for evaluation
        from odin_sdk.enhanced import OdinMessageBuilder
        
        trace_id = enterprise_context.get("trace_id", f"enterprise_{int(time.time())}")
        builder = OdinMessageBuilder()
        message = (builder
                  .set_ids(trace_id, f"session_{int(time.time())}", "enterprise_user", "enterprise_system")
                  .set_role("user")
                  .set_content(enterprise_context.get("content", ""))
                  .build())
        
        # Use HEL enhanced evaluation
        reflection = await self.hel_mediator.evaluate_async(message)
        
        # Convert reflection to dict for compatibility
        reflection_dict = {
            "confidence": reflection.confidence_score,
            "action_taken": reflection.action_taken,
            "explanation": reflection.explanation,
            "correction_tags": list(reflection.correction_tags),
            "trace_id": reflection.trace_id,
            "rule_results": []  # Will be populated from rule engine
        }
        
        # Check compliance
        compliance_result = self._check_compliance(reflection_dict, enterprise_context)
        
        # Update metrics
        self._update_performance_metrics(start_time, compliance_result)
        
        # Log for audit
        self._log_compliance_evaluation(enterprise_context, reflection_dict, compliance_result)
        
        # Enhanced reflection with enterprise metadata
        enhanced_reflection = {
            **reflection_dict,
            "enterprise_compliance": compliance_result,
            "organization_id": self.organization_id,
            "evaluation_timestamp": datetime.now().isoformat()
        }
        
        return enhanced_reflection
    
    def _check_compliance(self, reflection: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Check enterprise compliance requirements"""
        violations = []
        warnings = []
        
        # Check confidence thresholds
        confidence = reflection.get("confidence", 0.0)
        if confidence < 0.8:
            warnings.append("Below enterprise confidence threshold")
        
        # Check for policy violations in rule results
        rule_results = reflection.get("rule_results", [])
        for result in rule_results:
            if result.get("action") == "reject":
                metadata = result.get("metadata", {})
                if metadata.get("enterprise_policy"):
                    violations.append({
                        "policy": metadata["enterprise_policy"],
                        "rule": result.get("rule_name"),
                        "reason": result.get("reason")
                    })
        
        # Determine compliance status
        if violations:
            status = "violation"
            self.performance_metrics["compliance_violations"] += 1
        elif warnings:
            status = "warning"
        else:
            status = "compliant"
        
        return {
            "status": status,
            "violations": violations,
            "warnings": warnings,
            "compliance_score": 1.0 - (len(violations) * 0.3 + len(warnings) * 0.1),
            "requires_escalation": len(violations) > 0
        }
    
    def _update_performance_metrics(self, start_time: datetime, compliance_result: Dict[str, Any]) -> None:
        """Update enterprise performance metrics"""
        response_time = (datetime.now() - start_time).total_seconds()
        
        self.performance_metrics["total_evaluations"] += 1
        
        # Update average response time
        prev_avg = self.performance_metrics["average_response_time"]
        total_evals = self.performance_metrics["total_evaluations"]
        self.performance_metrics["average_response_time"] = (prev_avg * (total_evals - 1) + response_time) / total_evals
        
        if compliance_result["requires_escalation"]:
            self.performance_metrics["escalations"] += 1
    
    def _log_compliance_evaluation(self, context: Dict[str, Any], reflection: Dict[str, Any], 
                                 compliance_result: Dict[str, Any]) -> None:
        """Log compliance evaluation for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "organization_id": self.organization_id,
            "trace_id": context.get("trace_id"),
            "compliance_status": compliance_result["status"],
            "compliance_score": compliance_result["compliance_score"],
            "confidence": reflection.get("confidence"),
            "violations": compliance_result["violations"],
            "warnings": compliance_result["warnings"]
        }
        
        self.compliance_logs.append(log_entry)
        
        # Keep only last 1000 logs in memory
        if len(self.compliance_logs) > 1000:
            self.compliance_logs = self.compliance_logs[-1000:]
    
    def get_compliance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate compliance report for specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_logs = [
            log for log in self.compliance_logs
            if datetime.fromisoformat(log["timestamp"]) >= cutoff_date
        ]
        
        if not recent_logs:
            return {"error": "No data available for specified period"}
        
        # Calculate statistics
        total_evaluations = len(recent_logs)
        violations = sum(1 for log in recent_logs if log["compliance_status"] == "violation")
        warnings = sum(1 for log in recent_logs if log["compliance_status"] == "warning")
        compliant = total_evaluations - violations - warnings
        
        avg_compliance_score = sum(log["compliance_score"] for log in recent_logs) / total_evaluations
        avg_confidence = sum(log["confidence"] for log in recent_logs) / total_evaluations
        
        return {
            "report_period_days": days,
            "total_evaluations": total_evaluations,
            "compliance_summary": {
                "compliant": compliant,
                "warnings": warnings,
                "violations": violations,
                "compliance_rate": compliant / total_evaluations * 100
            },
            "average_compliance_score": avg_compliance_score,
            "average_confidence": avg_confidence,
            "performance_metrics": self.performance_metrics.copy(),
            "policy_violations_by_type": self._analyze_violation_patterns(recent_logs)
        }
    
    def _analyze_violation_patterns(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze patterns in policy violations"""
        violation_patterns = {}
        
        for log in logs:
            for violation in log.get("violations", []):
                policy = violation.get("policy", "unknown")
                violation_patterns[policy] = violation_patterns.get(policy, 0) + 1
        
        return violation_patterns
    
    def export_enterprise_configuration(self) -> Dict[str, Any]:
        """Export enterprise configuration for backup/sharing"""
        return {
            "organization_id": self.organization_id,
            "policies": {
                policy_id: {
                    "name": policy.name,
                    "description": policy.description,
                    "compliance_level": policy.compliance_level,
                    "auto_escalation": policy.auto_escalation,
                    "custom_rules": policy.custom_rules,
                    "audit_requirements": policy.audit_requirements
                }
                for policy_id, policy in self.enterprise_policies.items()
            },
            "hel_configuration": self.hel_mediator.export_hel_configuration(),
            "performance_baseline": self.performance_metrics.copy()
        }


# Predefined enterprise policy templates
ENTERPRISE_POLICY_TEMPLATES = {
    "financial_services": EnterprisePolicy(
        policy_id="finserv_compliance",
        name="Financial Services Compliance",
        description="Strict compliance for financial services industry",
        compliance_level="strict",
        auto_escalation=True,
        custom_rules=[
            {
                "name": "pii_detection",
                "description": "Reject messages containing PII",
                "conditions": [
                    {"field": "contains_pii", "operator": "==", "value": True}
                ],
                "action": "reject",
                "priority": 5
            },
            {
                "name": "high_confidence_only",
                "description": "Require very high confidence for approval",
                "conditions": [
                    {"field": "confidence", "operator": ">=", "value": 0.95}
                ],
                "action": "approve",
                "priority": 10
            }
        ],
        audit_requirements={
            "log_retention_days": 2555,  # 7 years
            "audit_trail": True,
            "compliance_reporting": "monthly"
        }
    ),
    
    "healthcare": EnterprisePolicy(
        policy_id="hipaa_compliance",
        name="HIPAA Healthcare Compliance",
        description="HIPAA-compliant AI communication",
        compliance_level="strict",
        auto_escalation=True,
        custom_rules=[
            {
                "name": "phi_protection",
                "description": "Protect PHI information",
                "conditions": [
                    {"field": "contains_phi", "operator": "==", "value": True}
                ],
                "action": "escalate",
                "priority": 1
            }
        ],
        audit_requirements={
            "log_retention_days": 2190,  # 6 years
            "encryption_required": True,
            "audit_trail": True
        }
    ),
    
    "general_enterprise": EnterprisePolicy(
        policy_id="general_enterprise",
        name="General Enterprise Policy",
        description="Standard enterprise AI governance",
        compliance_level="moderate",
        auto_escalation=False,
        custom_rules=[
            {
                "name": "confidence_threshold",
                "description": "Standard confidence requirements",
                "conditions": [
                    {"field": "confidence", "operator": ">=", "value": 0.8}
                ],
                "action": "approve",
                "priority": 20
            },
            {
                "name": "content_safety",
                "description": "Basic content safety check",
                "conditions": [
                    {"field": "inappropriate_content", "operator": "==", "value": True}
                ],
                "action": "reject",
                "priority": 15
            }
        ],
        audit_requirements={
            "log_retention_days": 365,
            "audit_trail": True,
            "compliance_reporting": "quarterly"
        }
    )
}


async def demo_enterprise_integration():
    """Demonstrate enterprise HEL integration"""
    print("🏢 ODIN Protocol Enterprise HEL Integration Demo")
    print("=" * 60)
    
    # Initialize enterprise integration
    enterprise = EnterpriseHelIntegration("acme-corp-001")
    
    # Register financial services policy
    enterprise.register_enterprise_policy(ENTERPRISE_POLICY_TEMPLATES["financial_services"])
    
    print(f"✅ Enterprise integration initialized for {enterprise.organization_id}")
    
    # Test messages
    test_messages = [
        {
            "name": "Compliant Message",
            "context": {
                "content": "Process this legitimate business request",
                "confidence": 0.96,
                "contains_pii": False,
                "trace_id": "msg-001"
            }
        },
        {
            "name": "PII Violation",
            "context": {
                "content": "John Smith SSN: 123-45-6789",
                "confidence": 0.85,
                "contains_pii": True,
                "trace_id": "msg-002"
            }
        },
        {
            "name": "Low Confidence",
            "context": {
                "content": "Unclear request with ambiguous intent",
                "confidence": 0.45,
                "contains_pii": False,
                "trace_id": "msg-003"
            }
        }
    ]
    
    print("\n🧪 Testing Enterprise Compliance:")
    
    for test in test_messages:
        print(f"\n  Testing: {test['name']}")
        result = await enterprise.evaluate_with_enterprise_compliance(test["context"])
        
        compliance = result["enterprise_compliance"]
        print(f"    Status: {compliance['status']}")
        print(f"    Score: {compliance['compliance_score']:.2f}")
        
        if compliance["violations"]:
            print(f"    Violations: {len(compliance['violations'])}")
        if compliance["warnings"]:
            print(f"    Warnings: {len(compliance['warnings'])}")
    
    # Generate compliance report
    print(f"\n📊 Compliance Report:")
    report = enterprise.get_compliance_report(days=1)
    summary = report["compliance_summary"]
    print(f"  Total evaluations: {report['total_evaluations']}")
    print(f"  Compliance rate: {summary['compliance_rate']:.1f}%")
    print(f"  Average confidence: {report['average_confidence']:.2f}")
    print(f"  Performance: {enterprise.performance_metrics['average_response_time']:.3f}s avg")
    
    # Export configuration
    config = enterprise.export_enterprise_configuration()
    filename = f"enterprise_config_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Enterprise configuration exported: {filename}")
    print("\n🎯 Enterprise HEL Integration Ready for Production!")


if __name__ == "__main__":
    asyncio.run(demo_enterprise_integration())
