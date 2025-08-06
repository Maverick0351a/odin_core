#!/usr/bin/env python3
"""
Configuration management for ODIN Protocol.
Centralized settings with environment variable support.
"""

import os
from typing import Optional, List


class OdinSettings:
    """Main configuration class for ODIN Protocol."""
    
    def __init__(self):
        """Initialize settings with defaults and environment overrides."""
        
        # AI Service Configuration
        self.gemini_project_id = os.getenv("ODIN_GEMINI_PROJECT_ID", "clarifyai-466505")
        self.gemini_location = os.getenv("ODIN_GEMINI_LOCATION", "us-central1")
        self.openai_api_key = os.getenv("ODIN_OPENAI_API_KEY")
        
        # Conversation Settings
        self.max_conversation_turns = int(os.getenv("ODIN_MAX_CONVERSATION_TURNS", "50"))
        self.default_temperature = float(os.getenv("ODIN_DEFAULT_TEMPERATURE", "0.7"))
        
        # Self-Reflection Settings
        self.mediator_confidence_threshold = float(os.getenv("ODIN_MEDIATOR_CONFIDENCE_THRESHOLD", "0.7"))
        self.semantic_drift_threshold = float(os.getenv("ODIN_SEMANTIC_DRIFT_THRESHOLD", "0.3"))
        self.max_reflection_iterations = int(os.getenv("ODIN_MAX_REFLECTION_ITERATIONS", "3"))
        
        # File Storage Settings
        self.logs_directory = os.getenv("ODIN_LOGS_DIRECTORY", "logs")
        self.reflection_log_file = os.getenv("ODIN_REFLECTION_LOG_FILE", "logs/reflections.jsonl")
        
        # API Settings
        self.api_host = os.getenv("ODIN_API_HOST", "127.0.0.1")
        self.api_port = int(os.getenv("ODIN_API_PORT", "8000"))
        self.api_reload = os.getenv("ODIN_API_RELOAD", "false").lower() == "true"
        
        # Rate Limiting
        self.rate_limit_requests = int(os.getenv("ODIN_RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("ODIN_RATE_LIMIT_WINDOW", "60"))
        
        # Security Settings
        self.enable_cors = os.getenv("ODIN_ENABLE_CORS", "true").lower() == "true"
        cors_origins_str = os.getenv("ODIN_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:8000")
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        self.max_message_size = int(os.getenv("ODIN_MAX_MESSAGE_SIZE", str(1024 * 1024)))
        
        # Monitoring Settings
        self.enable_metrics = os.getenv("ODIN_ENABLE_METRICS", "false").lower() == "true"
        self.log_level = os.getenv("ODIN_LOG_LEVEL", "INFO").upper()
        
        # Development Settings
        self.debug_mode = os.getenv("ODIN_DEBUG_MODE", "false").lower() == "true"
        self.mock_ai_responses = os.getenv("ODIN_MOCK_AI_RESPONSES", "false").lower() == "true"


# Global settings instance
settings = OdinSettings()


def get_settings() -> OdinSettings:
    """Get the global settings instance."""
    return settings


def update_settings(**kwargs) -> None:
    """Update settings at runtime."""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
        else:
            raise ValueError(f"Unknown setting: {key}")


def validate_settings() -> List[str]:
    """Validate current settings and return any issues."""
    issues = []
    
    # Check AI service configuration
    if not settings.gemini_project_id:
        issues.append("Gemini project ID not configured")
    
    # Check file paths
    import os
    if not os.path.exists(os.path.dirname(settings.reflection_log_file)):
        try:
            os.makedirs(os.path.dirname(settings.reflection_log_file), exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create logs directory: {e}")
    
    # Check thresholds
    if not 0.0 <= settings.mediator_confidence_threshold <= 1.0:
        issues.append("Mediator confidence threshold must be between 0.0 and 1.0")
    
    if not 0.0 <= settings.semantic_drift_threshold <= 1.0:
        issues.append("Semantic drift threshold must be between 0.0 and 1.0")
    
    if settings.max_reflection_iterations < 1:
        issues.append("Max reflection iterations must be at least 1")
    
    # Check port availability
    if not 1024 <= settings.api_port <= 65535:
        issues.append("API port must be between 1024 and 65535")
    
    return issues


def print_settings_summary():
    """Print a summary of current settings."""
    print("🔧 ODIN Protocol Configuration")
    print("=" * 40)
    print(f"Gemini Project: {settings.gemini_project_id}")
    print(f"Gemini Location: {settings.gemini_location}")
    print(f"API Server: {settings.api_host}:{settings.api_port}")
    print(f"Max Turns: {settings.max_conversation_turns}")
    print(f"Confidence Threshold: {settings.mediator_confidence_threshold}")
    print(f"Logs Directory: {settings.logs_directory}")
    print(f"Debug Mode: {settings.debug_mode}")
    print(f"CORS Enabled: {settings.enable_cors}")
    
    # Check for issues
    issues = validate_settings()
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("\n✅ Configuration valid")


if __name__ == "__main__":
    print_settings_summary()
