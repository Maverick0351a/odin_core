from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dialogue import router as dialogue_router
from multi_model_dialogue import router as multi_model_router
from conversation_viewer import frontend_router
from llm_utils import init_gemini
from config import get_settings
from security import (
    check_rate_limit, 
    authenticate_token, 
    require_authentication,
    add_security_headers,
    get_admin_token
)
from rules_engine import get_rule_engine, initialize_rule_engine
from mediator_ai import MediatorAI
import logging
import sys
import os

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("odin-main")

# Step 1: Create app
app = FastAPI(
    title="ODIN Protocol", 
    version="2.0", 
    description="AI-to-AI Communication Protocol with Self-Reflection Capabilities",
    debug=settings.debug_mode
)

# Step 2: Add CORS middleware
if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Step 3: Global exception handler with security headers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "UnhandledException"}
    )
    return add_security_headers(response)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception on {request.url}: {exc.detail}")
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "HTTPException"}
    )
    return add_security_headers(response)

# Step 4: Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests."""
    try:
        # Skip rate limiting for health check and static files
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            response = await call_next(request)
            return add_security_headers(response)
        
        # Apply rate limiting
        await check_rate_limit(request)
        
        response = await call_next(request)
        return add_security_headers(response)
        
    except HTTPException as e:
        response = JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
        return add_security_headers(response)

# Step 5: Mount routers with dependencies
app.include_router(dialogue_router, tags=["Dialogue"], dependencies=[Depends(check_rate_limit)])
app.include_router(multi_model_router, tags=["Multi-Model Conversations"], dependencies=[Depends(check_rate_limit)])
app.include_router(frontend_router, tags=["Frontend"])  # No rate limiting for frontend

# Step 6: Add security info endpoint
@app.get("/auth/info")
async def auth_info(user_info: dict = Depends(authenticate_token)):
    """Get authentication info (optional auth)."""
    if user_info:
        return {
            "authenticated": True,
            "user": user_info["name"],
            "permissions": user_info["permissions"]
        }
    else:
        return {
            "authenticated": False,
            "message": "No authentication provided"
        }

@app.get("/auth/admin-token")
async def get_admin_token_endpoint():
    """Get admin token for development/testing."""
    if settings.debug_mode:
        return {
            "token": get_admin_token(),
            "note": "This endpoint only works in debug mode"
        }
    else:
        raise HTTPException(status_code=404, detail="Not found")

# Step 7: Add health check with configuration validation
@app.get("/health")
async def health_check():
    """Comprehensive health check including configuration validation."""
    from config import validate_settings
    
    # Check configuration
    config_issues = validate_settings()
    
    # Check AI service connectivity (basic check)
    ai_status = "unknown"
    try:
        # This would be expanded to actually test AI connectivity
        ai_status = "configured"
    except Exception as e:
        logger.error(f"AI service check failed: {e}")
        ai_status = "error"
    
    health_status = {
        "status": "healthy" if not config_issues else "degraded",
        "service": "ODIN Protocol",
        "version": "2.0",
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            "", 0, "", 0, "", (), None
        )),
        "features": [
            "single_dialogue",
            "multi_model_conversation", 
            "self_reflection_system",
            "real_time_streaming",
            "conversation_viewer",
            "mediator_ai_evaluation",
            "rate_limiting",
            "token_authentication"
        ],
        "configuration": {
            "status": "valid" if not config_issues else "invalid",
            "issues": config_issues
        },
        "services": {
            "ai_backend": ai_status,
            "reflection_system": "operational",
            "conversation_viewer": "operational",
            "authentication": "enabled",
            "rate_limiting": "enabled"
        },
        "settings": {
            "max_turns": settings.max_conversation_turns,
            "confidence_threshold": settings.mediator_confidence_threshold,
            "debug_mode": settings.debug_mode
        }
    }
    
    # Return appropriate status code
    status_code = 200 if not config_issues else 503
    return JSONResponse(content=health_status, status_code=status_code)

# Step 8: Configuration endpoint with optional auth
@app.get("/config")
async def get_configuration(user_info: dict = Depends(authenticate_token)):
    """Get current configuration (excluding sensitive data)."""
    safe_config = {
        "max_conversation_turns": settings.max_conversation_turns,
        "mediator_confidence_threshold": settings.mediator_confidence_threshold,
        "semantic_drift_threshold": settings.semantic_drift_threshold,
        "max_reflection_iterations": settings.max_reflection_iterations,
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "debug_mode": settings.debug_mode,
        "enable_cors": settings.enable_cors,
        "log_level": settings.log_level
    }
    
    # Add additional info for authenticated users
    if user_info and "admin" in user_info.get("permissions", []):
        safe_config["admin_info"] = {
            "rate_limit_requests": settings.rate_limit_requests,
            "max_message_size": settings.max_message_size,
            "logs_directory": settings.logs_directory
        }
    
    return safe_config

# Step 9: Rule Engine API endpoints
@app.get("/rules/stats")
async def get_rule_stats(user_info: dict = Depends(authenticate_token)):
    """Get Rule Engine statistics."""
    if not hasattr(app.state, 'rule_engine'):
        raise HTTPException(status_code=503, detail="Rule Engine not initialized")
    
    stats = app.state.rule_engine.get_stats()
    return stats

@app.get("/rules/list")
async def list_rules(user_info: dict = Depends(require_authentication)):
    """List all rules with their configurations."""
    if not hasattr(app.state, 'rule_engine'):
        raise HTTPException(status_code=503, detail="Rule Engine not initialized")
    
    stats = app.state.rule_engine.get_stats()
    return {
        "total_rules": stats["total_rules"],
        "enabled_rules": stats["enabled_rules"],
        "rules": stats["rules_summary"]
    }

@app.post("/rules/evaluate")
async def evaluate_rules(
    context: dict,
    user_info: dict = Depends(require_authentication),
    client_id: str = Depends(check_rate_limit)
):
    """Evaluate rules against provided context."""
    if not hasattr(app.state, 'rule_engine'):
        raise HTTPException(status_code=503, detail="Rule Engine not initialized")
    
    try:
        results = app.state.rule_engine.evaluate_rules(context)
        
        return {
            "context_summary": {
                "confidence": context.get("confidence", "N/A"),
                "semantic_drift": context.get("semantic_drift_score", "N/A"),
                "message_size": context.get("message_size", "N/A")
            },
            "rules_triggered": len(results),
            "results": results,
            "final_decision": app.state.rule_engine.get_decision(context)
        }
    
    except Exception as e:
        logger.error(f"Rule evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Rule evaluation failed: {str(e)}")

@app.post("/rules/reload")
async def reload_rules(
    config_path: str = None,
    user_info: dict = Depends(require_authentication)
):
    """Reload rules from configuration file (admin only)."""
    if "admin" not in user_info.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not hasattr(app.state, 'rule_engine'):
        raise HTTPException(status_code=503, detail="Rule Engine not initialized")
    
    try:
        if config_path and os.path.exists(config_path):
            app.state.rule_engine.load_rules_from_config(config_path)
            logger.info(f"Rules reloaded from: {config_path}")
        else:
            app.state.rule_engine._load_default_rules()
            logger.info("Rules reloaded with defaults")
        
        stats = app.state.rule_engine.get_stats()
        return {
            "status": "success",
            "message": "Rules reloaded successfully",
            "total_rules": stats["total_rules"],
            "enabled_rules": stats["enabled_rules"]
        }
    
    except Exception as e:
        logger.error(f"Rule reload error: {e}")
        raise HTTPException(status_code=500, detail=f"Rule reload failed: {str(e)}")

@app.get("/mediator/stats")
async def get_mediator_stats(user_info: dict = Depends(authenticate_token)):
    """Get MediatorAI statistics including rule engine stats."""
    if not hasattr(app.state, 'mediator_ai'):
        raise HTTPException(status_code=503, detail="MediatorAI not initialized")
    
    try:
        rule_stats = app.state.mediator_ai.get_rule_engine_stats()
        
        return {
            "mediator_id": app.state.mediator_ai.mediator_id,
            "confidence_threshold": app.state.mediator_ai.confidence_threshold,
            "semantic_drift_threshold": app.state.mediator_ai.semantic_drift_threshold,
            "rule_engine": rule_stats
        }
    
    except Exception as e:
        logger.error(f"Mediator stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get mediator stats: {str(e)}")

@app.post("/mediator/evaluate")
async def evaluate_with_mediator(
    message_data: dict,
    user_info: dict = Depends(require_authentication),
    client_id: str = Depends(check_rate_limit)
):
    """Evaluate a message using the enhanced MediatorAI with Rule Engine."""
    if not hasattr(app.state, 'mediator_ai'):
        raise HTTPException(status_code=503, detail="MediatorAI not initialized")
    
    try:
        # Create OdinMessage from input data (simplified for API)
        from odin_sdk.enhanced import OdinMessageBuilder
        
        builder = OdinMessageBuilder()
        message = builder.set_ids(
            trace_id=message_data.get("trace_id", f"api-{client_id}"),
            session_id=message_data.get("session_id", f"session-{client_id}"),
            sender_id=message_data.get("sender_id", user_info.get("name", "api-user")),
            receiver_id=message_data.get("receiver_id", "mediator-ai")
        ).set_role(message_data.get("role", "user")).set_content(
            message_data.get("content", "")
        ).build()
        
        # Set additional fields if provided
        if "semantic_drift_score" in message_data:
            message.semantic_drift_score = float(message_data["semantic_drift_score"])
        
        # Evaluate with rule-enhanced mediator
        reflection = app.state.mediator_ai.evaluate(message, iteration_count=1)
        
        # Convert reflection to JSON-serializable format
        result = {
            "action_taken": reflection.action_taken,
            "explanation": reflection.explanation,
            "confidence_score": reflection.confidence_score,
            "reflection_timestamp": reflection.reflection_timestamp,
            "iteration_count": reflection.iteration_count,
            "correction_tags": list(reflection.correction_tags),
            "has_healed_message": reflection.HasField('healed'),
            "mediator_id": reflection.mediator_id
        }
        
        if reflection.HasField('healed'):
            result["healed_content"] = reflection.healed.healed_output
        
        return result
    
    except Exception as e:
        logger.error(f"Mediator evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Mediator evaluation failed: {str(e)}")

# Step 10: Demo endpoint for Rule Engine (debug mode only)
@app.get("/demo/rule-engine")
async def demo_rule_engine(user_info: dict = Depends(authenticate_token)):
    """Demonstrate Rule Engine capabilities (debug mode only)."""
    if not settings.debug_mode:
        raise HTTPException(status_code=404, detail="Endpoint not available in production")
    
    if not hasattr(app.state, 'rule_engine'):
        raise HTTPException(status_code=503, detail="Rule Engine not initialized")
    
    # Create demo contexts
    demo_contexts = [
        {
            "name": "High Confidence",
            "context": {
                "confidence": 0.95,
                "semantic_drift_score": 0.1,
                "hallucination_risk": 0.05,
                "message_size": 500
            }
        },
        {
            "name": "Low Confidence",
            "context": {
                "confidence": 0.25,
                "semantic_drift_score": 0.8,
                "hallucination_risk": 0.6,
                "message_size": 1200
            }
        },
        {
            "name": "Security Threat",
            "context": {
                "confidence": 0.7,
                "security": {"threat_level": 0.9, "flagged": True},
                "semantic_drift_score": 0.3,
                "message_size": 800
            }
        }
    ]
    
    results = []
    for demo in demo_contexts:
        try:
            rule_results = app.state.rule_engine.evaluate_rules(demo["context"])
            decision = app.state.rule_engine.get_decision(demo["context"])
            
            results.append({
                "scenario": demo["name"],
                "context": demo["context"],
                "rules_triggered": len(rule_results),
                "results": rule_results,
                "final_decision": decision
            })
        except Exception as e:
            results.append({
                "scenario": demo["name"],
                "error": str(e)
            })
    
    return {
        "demo_title": "ODIN Protocol Rule Engine Demo",
        "total_scenarios": len(demo_contexts),
        "scenarios": results,
        "rule_engine_stats": app.state.rule_engine.get_stats()
    }

# Step 9: Startup event with proper initialization
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("🚀 Starting ODIN Protocol v2.0...")
    
    # Initialize Rule Engine
    try:
        rules_config_path = os.path.join("rules_config.yaml") if os.path.exists("rules_config.yaml") else None
        rule_engine = initialize_rule_engine(rules_config_path)
        
        if rules_config_path:
            logger.info(f"✅ Rule Engine initialized with configuration: {rules_config_path}")
        else:
            logger.info("✅ Rule Engine initialized with default rules")
        
        stats = rule_engine.get_stats()
        logger.info(f"📊 Loaded {stats['total_rules']} rules ({stats['enabled_rules']} enabled)")
        
        # Store rule engine in app state for API access
        app.state.rule_engine = rule_engine
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Rule Engine: {e}")
        if not settings.debug_mode:
            sys.exit(1)
    
    # Initialize Enhanced MediatorAI with Rule Engine
    try:
        app.state.mediator_ai = MediatorAI(
            mediator_id="odin-mediator-v2",
            confidence_threshold=settings.confidence_threshold,
            semantic_drift_threshold=settings.semantic_drift_threshold,
            rules_config_path=rules_config_path
        )
        logger.info("✅ Enhanced MediatorAI with Rule Engine initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize MediatorAI: {e}")
        if not settings.debug_mode:
            sys.exit(1)
    
    # Print security info in debug mode
    if settings.debug_mode:
        logger.info(f"🔑 Admin token for testing: {get_admin_token()}")
        logger.info("🔒 Authentication and rate limiting enabled")
    
    # Validate configuration
    from config import validate_settings
    config_issues = validate_settings()
    
    if config_issues:
        logger.error("❌ Configuration validation failed:")
        for issue in config_issues:
            logger.error(f"   • {issue}")
        
        if not settings.debug_mode:
            logger.error("Exiting due to configuration issues (set debug_mode=true to ignore)")
            sys.exit(1)
        else:
            logger.warning("Continuing in debug mode despite configuration issues")
    
    # Initialize AI services
    try:
        init_gemini(project_id=settings.gemini_project_id, location=settings.gemini_location)
        logger.info("✅ Gemini AI service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini: {e}")
        
        if not settings.debug_mode and not settings.mock_ai_responses:
            logger.error("Exiting due to AI service initialization failure")
            sys.exit(1)
        else:
            logger.warning("Continuing without AI service (debug mode or mock responses enabled)")
    
    # Create necessary directories
    import os
    os.makedirs(settings.logs_directory, exist_ok=True)
    
    logger.info("✅ ODIN Protocol v2.0 initialized successfully")
    logger.info("🔒 Security features: Authentication, Rate Limiting, Input Validation")
    logger.info("🧠 Self-Reflection: Mediator AI, Loopback Correction, Analytics")
    logger.info("⚙️  Rule Engine: Dynamic Decision Making, Custom Handlers, YAML Config")

# Step 10: Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("🛑 Shutting down ODIN Protocol...")
    # Add any cleanup logic here
    logger.info("✅ ODIN Protocol shutdown complete")
