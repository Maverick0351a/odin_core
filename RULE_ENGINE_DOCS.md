# ODIN Protocol Rule Engine Documentation

## Overview

The ODIN Protocol Rule Engine is an extensible, dynamic decision-making system integrated into the MediatorAI component. It provides configurable rules that can trigger different workflows (approve, retry, reject, escalate) based on custom conditions like confidence scores, semantic drift, and compliance checks.

## Key Features

- **🔧 Extensible Architecture**: Easy to add new rules and custom handlers
- **📄 YAML Configuration**: External rule management through configuration files
- **⚡ Async Support**: Asynchronous rule evaluation for better performance
- **📊 Analytics**: Comprehensive logging and statistics tracking
- **🛡️ Built-in Security**: Input validation and safe rule execution
- **🎯 Priority System**: Rule execution based on configurable priorities
- **🔄 Workflow Actions**: Support for approve, retry, reject, escalate, and custom actions

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MediatorAI    │───▶│   RuleEngine    │───▶│ Custom Handlers │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • evaluate()    │    │ • Rules         │    │ • Semantic      │
│ • async eval()  │    │ • Conditions    │    │ • Compliance    │
│ • validation    │    │ • Actions       │    │ • Custom Logic  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ OdinReflection  │    │ YAML Config     │    │ Action Results  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. RuleCondition

Represents a single condition that can be evaluated against a context.

```python
from rules_engine import RuleCondition, RuleOperator

# Simple condition
condition = RuleCondition(
    field="confidence",
    operator=RuleOperator.GTE,
    value=0.8,
    description="High confidence threshold"
)

# Nested field access
condition = RuleCondition(
    field="metadata.security.threat_level",
    operator=RuleOperator.LT,
    value=0.3,
    description="Low security threat"
)
```

**Supported Operators:**
- `GT`, `LT`, `GTE`, `LTE`: Numeric comparisons
- `EQ`, `NEQ`: Equality checks
- `CONTAINS`: String containment
- `REGEX`: Regular expression matching
- `IN`, `NOT_IN`: List membership
- `BETWEEN`: Range checks (inclusive)
- `IS_EMPTY`, `IS_NOT_EMPTY`: Empty value checks

### 2. Rule

Combines multiple conditions with an action to take when all conditions are met.

```python
from rules_engine import Rule, RuleAction

rule = Rule(
    name="high_confidence_approval",
    description="Auto-approve messages with high confidence",
    conditions=[
        RuleCondition("confidence", RuleOperator.GTE, 0.9),
        RuleCondition("source", RuleOperator.IN, ["trusted_api", "verified_user"])
    ],
    action=RuleAction.APPROVE,
    priority=10,
    enabled=True
)
```

**Available Actions:**
- `APPROVE`: Accept the message/request
- `REJECT`: Deny the message/request
- `RETRY`: Attempt processing again (possibly with healing)
- `ESCALATE`: Forward to human review
- `CONTINUE`: Proceed with normal processing
- `LOG_WARNING`: Log an issue but continue
- `CUSTOM`: Execute custom handler logic

### 3. RuleEngine

The main engine that evaluates rules and executes actions.

```python
from rules_engine import RuleEngine, get_rule_engine

# Initialize with default rules
engine = RuleEngine()

# Initialize with YAML configuration
engine = RuleEngine("rules_config.yaml")

# Get global instance
engine = get_rule_engine("rules_config.yaml")

# Register a new rule
engine.register_rule(my_rule)

# Register custom handler
engine.register_custom_handler("my_handler", my_handler_function)

# Evaluate rules
context = {"confidence": 0.95, "source": "api"}
results = engine.evaluate_rules(context)

# Async evaluation
results = await engine.evaluate_rules_async(context)
```

## YAML Configuration

Rules can be externalized into YAML configuration files for easy management:

```yaml
version: "1.0"
description: "ODIN Protocol Rules Configuration"

rules:
  - name: "high_confidence_approval"
    description: "Auto-approve high-confidence messages"
    priority: 10
    enabled: true
    action: "approve"
    conditions:
      - field: "confidence"
        operator: ">="
        value: 0.95
        description: "Very high confidence"
      - field: "source"
        operator: "in"
        value: ["trusted_api", "verified_user"]
        description: "Trusted source"

  - name: "security_escalation"
    description: "Escalate security threats"
    priority: 1
    enabled: true
    action: "escalate"
    conditions:
      - field: "security.threat_level"
        operator: ">"
        value: 0.8
        description: "High threat level"

  - name: "semantic_drift_retry"
    description: "Retry on semantic drift"
    priority: 30
    enabled: true
    action: "custom"
    custom_handler: "semantic_drift_handler"
    conditions:
      - field: "semantic_drift_score"
        operator: ">="
        value: 0.5
        description: "Significant semantic drift"

# Global settings
settings:
  max_rules_per_evaluation: 50
  detailed_logging: true
  evaluation_timeout_ms: 1000
  default_action: "continue"
```

## MediatorAI Integration

The Rule Engine is seamlessly integrated into the MediatorAI for enhanced decision-making:

```python
from mediator_ai import MediatorAI
from odin_sdk.enhanced import OdinMessageBuilder

# Initialize MediatorAI with rules
mediator = MediatorAI(
    mediator_id="my-mediator",
    confidence_threshold=0.7,
    rules_config_path="rules_config.yaml"
)

# Create a message
builder = OdinMessageBuilder()
message = builder.create_message(
    trace_id="test-001",
    sender_id="user-123",
    receiver_id="assistant",
    raw_output="Hello, world!",
    role="user"
)

# Evaluate with rule engine integration
reflection = mediator.evaluate(message)

# Async evaluation
reflection = await mediator.evaluate_async(message)

# Get rule engine statistics
stats = mediator.get_rule_engine_stats()
print(f"Total rules: {stats['total_rules']}")
```

## Custom Handlers

Create custom logic for complex decision-making scenarios:

```python
def my_custom_handler(context: Dict[str, Any], rule: Rule) -> Dict[str, Any]:
    """Custom handler for special business logic."""
    confidence = context.get("confidence", 0.0)
    user_tier = context.get("user_tier", "basic")
    
    if user_tier == "premium" and confidence > 0.7:
        return {
            "action": "approve",
            "reason": "Premium user with good confidence",
            "fast_track": True
        }
    elif confidence < 0.3:
        return {
            "action": "reject",
            "reason": f"Low confidence: {confidence}",
            "suggest_improvement": True
        }
    else:
        return {
            "action": "continue",
            "reason": "Standard processing"
        }

# Register the handler
mediator.rule_engine.register_custom_handler("my_custom_handler", my_custom_handler)

# Create a rule that uses the handler
custom_rule = Rule(
    name="business_logic_rule",
    description="Apply custom business logic",
    conditions=[
        RuleCondition("requires_special_handling", RuleOperator.EQ, True)
    ],
    action=RuleAction.CUSTOM,
    custom_handler=my_custom_handler,
    priority=15
)

mediator.rule_engine.register_rule(custom_rule)
```

## Built-in Handlers

The system includes several built-in handlers for common scenarios:

### Semantic Drift Handler
```python
# Automatically registered as "semantic_drift_handler"
context = {"semantic_drift": 0.8}
# Returns escalate/retry/continue based on drift level
```

### Compliance Check Handler
```python
# Automatically registered as "compliance_check_handler"
context = {
    "compliance": {
        "contains_pii": True,
        "inappropriate_content": False,
        "policy_violation": False
    }
}
# Returns reject if violations found, continue otherwise
```

### ODIN-Specific Handlers
- `odin_confidence_handler`: Confidence-based decisions
- `odin_semantic_drift_handler`: ODIN semantic drift handling
- `odin_hallucination_handler`: Hallucination risk assessment

## Context Structure

The rule evaluation context contains comprehensive information about the message and evaluation:

```python
context = {
    # Core message data
    "trace_id": "msg-123",
    "sender_id": "user-456",
    "receiver_id": "assistant",
    "role": "user",
    "timestamp": 1691234567890,
    
    # Evaluation metrics
    "confidence": 0.85,
    "hallucination_risk": 0.15,
    "semantic_drift_score": 0.3,
    "has_semantic_issues": False,
    "clarity_issues": [],
    
    # Message analysis
    "message_length": 150,
    "message_size": 1024,
    "word_count": 25,
    "has_healed_output": False,
    
    # Processing metadata
    "iteration_count": 1,
    "mediator_id": "mediator-v1",
    "evaluation_timestamp": 1691234567890,
    
    # Security context
    "source": "api",
    "user_id": "user-456",
    
    # Pattern detection
    "has_uncertainty_patterns": False,
    "has_hallucination_patterns": False,
    
    # Thresholds
    "confidence_threshold": 0.7,
    "semantic_drift_threshold": 0.3,
    
    # Healing metadata
    "healing_metadata": {
        "has_healing": False,
        "healing_confidence": 0.0,
        "healing_iteration": 0
    }
}
```

## Analytics and Monitoring

The Rule Engine provides comprehensive analytics:

```python
# Get execution statistics
stats = engine.get_stats()
print(f"""
Rule Engine Statistics:
- Total rules: {stats['total_rules']}
- Enabled rules: {stats['enabled_rules']}
- Total evaluations: {stats['execution_stats']['total_evaluations']}
- Rules triggered: {stats['execution_stats']['rules_triggered']}
- Approvals: {stats['execution_stats']['approval_count']}
- Rejections: {stats['execution_stats']['rejection_count']}
""")

# Get rule summaries
for rule_info in stats['rules_summary']:
    print(f"Rule: {rule_info['name']} (priority: {rule_info['priority']})")
```

### Reflection Logging

All rule evaluations are logged for audit and analytics:

```python
from mediator_ai import ReflectionLogger

logger = ReflectionLogger("logs/reflections.jsonl")

# Logging happens automatically during evaluation
reflection = mediator.evaluate(message)

# Get analytics from logs
reflection_stats = logger.get_reflection_stats()
print(f"Total reflections: {reflection_stats['total_reflections']}")
print(f"Actions taken: {reflection_stats['actions']}")
print(f"Average confidence: {reflection_stats['avg_confidence']}")
```

## Performance Considerations

### Async Evaluation
Use async evaluation for better performance with multiple messages:

```python
import asyncio

async def evaluate_batch(mediator, messages):
    tasks = [mediator.evaluate_async(msg) for msg in messages]
    reflections = await asyncio.gather(*tasks)
    return reflections

# Evaluate multiple messages concurrently
reflections = await evaluate_batch(mediator, message_list)
```

### Rule Optimization
- **Priority Ordering**: Higher priority rules (lower numbers) execute first
- **Decisive Actions**: Rules with decisive actions (approve, reject, escalate) stop further evaluation
- **Condition Optimization**: Place faster conditions first in rule definitions
- **Enable/Disable**: Use the `enabled` flag to temporarily disable rules

### Memory Management
- Rules are sorted once on registration for optimal evaluation order
- Context objects are created fresh for each evaluation
- Statistics are tracked in memory (consider periodic reset for long-running processes)

## Error Handling

The Rule Engine includes robust error handling:

```python
# Rule condition evaluation errors are logged but don't stop processing
try:
    results = engine.evaluate_rules(context)
except Exception as e:
    print(f"Rule evaluation error: {e}")

# Custom handler errors are caught and logged
def safe_custom_handler(context, rule):
    try:
        # Your custom logic here
        return {"action": "continue"}
    except Exception as e:
        # Error is logged automatically
        return {"action": "continue", "error": str(e)}
```

## Best Practices

### Rule Design
1. **Keep conditions simple**: Each condition should test one specific aspect
2. **Use descriptive names**: Make rule purposes clear from their names
3. **Set appropriate priorities**: Critical security rules should have priority 1-10
4. **Document conditions**: Use the description field to explain each condition

### Configuration Management
1. **Version control**: Keep YAML configurations in version control
2. **Environment-specific configs**: Use different configs for dev/staging/prod
3. **Validate configs**: Test rule loading in development environments
4. **Backup configs**: Keep backups of working configurations

### Testing
1. **Unit test rules**: Test individual rules with known contexts
2. **Integration test**: Test complete evaluation workflows
3. **Performance test**: Verify rule evaluation performance under load
4. **Edge case testing**: Test with invalid/missing context fields

### Monitoring
1. **Track statistics**: Monitor rule execution rates and patterns
2. **Alert on anomalies**: Set up alerts for unusual rule behavior
3. **Regular reviews**: Periodically review rule effectiveness
4. **A/B testing**: Test rule changes with controlled rollouts

## Troubleshooting

### Common Issues

#### Rules Not Triggering
- Check if rule is enabled: `rule.enabled == True`
- Verify conditions match context: Use debug logging
- Check rule priority: Higher priority rules might stop evaluation

#### Poor Performance
- Too many rules: Consider consolidating or disabling unused rules
- Complex conditions: Simplify or optimize condition logic
- Large context: Reduce context size or use field validation

#### Configuration Errors
- YAML syntax: Validate YAML format
- Operator names: Ensure operators match enum values
- Field references: Verify field paths exist in context

### Debug Tools

```python
# Enable detailed logging
import logging
logging.getLogger("rules_engine").setLevel(logging.DEBUG)

# Validate context against rules
missing_fields = engine.validate_context(context)
if missing_fields:
    print(f"Missing fields: {missing_fields}")

# Test individual rule
if rule.evaluate(context):
    print(f"Rule {rule.name} would trigger")
    result = rule.execute(context)
    print(f"Action: {result['action']}")

# Export current rules for inspection
engine.export_rules_to_config("debug_rules.yaml")
```

## API Reference

### RuleEngine

```python
class RuleEngine:
    def __init__(self, config_path: Optional[str] = None)
    def register_rule(self, rule: Rule) -> None
    def register_custom_handler(self, name: str, handler: Callable) -> None
    def evaluate_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
    async def evaluate_rules_async(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
    def get_decision(self, context: Dict[str, Any]) -> str
    def load_rules_from_config(self, config_path: str) -> None
    def export_rules_to_config(self, output_path: str) -> None
    def get_stats(self) -> Dict[str, Any]
    def validate_context(self, context: Dict[str, Any]) -> List[str]
```

### Rule

```python
class Rule:
    name: str
    description: str
    conditions: List[RuleCondition]
    action: RuleAction
    priority: int = 100
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom_handler: Optional[Callable] = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]
```

### RuleCondition

```python
class RuleCondition:
    field: str
    operator: RuleOperator
    value: Any
    description: str = ""
    
    def evaluate(self, context: Dict[str, Any]) -> bool
```

### Enhanced MediatorAI

```python
class MediatorAI:
    def __init__(self, ..., rules_config_path: Optional[str] = None)
    def evaluate(self, message: OdinMessage, iteration_count: int = 1) -> OdinReflection
    async def evaluate_async(self, message: OdinMessage, iteration_count: int = 1) -> OdinReflection
    def get_rule_engine_stats(self) -> Dict[str, Any]
    def reload_rules(self, config_path: Optional[str] = None) -> None
    def export_rules_config(self, output_path: str) -> None
```

## Examples

See `demo_rule_engine.py` for comprehensive examples including:
- Basic rule engine usage
- YAML configuration loading
- MediatorAI integration
- Custom handler creation
- Asynchronous evaluation
- Analytics and monitoring

Run the demonstration:
```bash
python demo_rule_engine.py
```

Run the test suite:
```bash
python test_rule_engine.py
```

## Contributing

To extend the Rule Engine:

1. Add new operators to `RuleOperator` enum
2. Implement operator logic in `RuleCondition._apply_operator()`
3. Add new actions to `RuleAction` enum
4. Create custom handlers for domain-specific logic
5. Update YAML schema documentation
6. Add comprehensive tests

The Rule Engine is designed to be highly extensible while maintaining simplicity and performance.
