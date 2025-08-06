"""
Content Moderation Plugin for ODIN Protocol
Detects and flags inappropriate content.
"""

from odin_sdk.plugins import RulePlugin
from typing import Dict, Any
import re


class ContentModerationPlugin(RulePlugin):
    """Plugin that moderates message content for compliance."""
    
    @property
    def name(self) -> str:
        return "content-moderation"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Moderates content for inappropriate material and compliance"
    
    async def initialize(self) -> bool:
        """Initialize content moderation."""
        self.logger.info("Initializing content moderation plugin")
        
        # PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        # Inappropriate content keywords
        self.inappropriate_keywords = [
            'spam', 'scam', 'fraud', 'hack', 'malware', 'virus'
        ]
        
        # Compliance keywords that require escalation
        self.compliance_keywords = [
            'confidential', 'classified', 'proprietary', 'internal use only'
        ]
        
        return True
    
    async def process_message(self, message: Any, context: Dict[str, Any]) -> Any:
        """Moderate message content."""
        if not hasattr(message, 'raw_output'):
            return message
        
        content = message.raw_output
        moderation_flags = []
        
        # Check for PII
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                moderation_flags.append(f"pii_{pii_type}")
                self.logger.warning(f"PII detected: {pii_type}")
        
        # Check for inappropriate content
        content_lower = content.lower()
        for keyword in self.inappropriate_keywords:
            if keyword in content_lower:
                moderation_flags.append(f"inappropriate_{keyword}")
                self.logger.warning(f"Inappropriate content: {keyword}")
        
        # Check for compliance issues
        for keyword in self.compliance_keywords:
            if keyword in content_lower:
                moderation_flags.append(f"compliance_{keyword}")
                self.logger.warning(f"Compliance flag: {keyword}")
        
        # Add moderation results to metadata
        if moderation_flags and hasattr(message, 'metadata'):
            message.metadata["moderation_flags"] = ",".join(moderation_flags)
            message.metadata["moderation_status"] = "flagged" if moderation_flags else "clean"
            message.metadata["requires_review"] = "true" if moderation_flags else "false"
        
        return message
    
    async def evaluate_rule(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate content moderation rules."""
        message = context.get("message")
        if not message or not hasattr(message, 'raw_output'):
            return {"rule_name": "content_moderation", "passed": True, "score": 1.0}
        
        content = message.raw_output
        violations = 0
        total_checks = len(self.pii_patterns) + len(self.inappropriate_keywords) + len(self.compliance_keywords)
        
        # Count violations
        for pattern in self.pii_patterns.values():
            if re.search(pattern, content, re.IGNORECASE):
                violations += 1
        
        content_lower = content.lower()
        for keyword in self.inappropriate_keywords + self.compliance_keywords:
            if keyword in content_lower:
                violations += 1
        
        # Calculate score (lower is worse)
        score = max(0.0, 1.0 - (violations / max(total_checks, 1)))
        passed = violations == 0
        
        return {
            "rule_name": "content_moderation",
            "passed": passed,
            "score": score,
            "violations": violations,
            "details": f"Found {violations} content violations"
        }
