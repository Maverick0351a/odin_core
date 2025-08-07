"""
Performance Analytics Plugin - Integration Example
Shows how to use the plugin with your existing ODIN Protocol system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.performance_analytics import PerformanceAnalyticsPlugin
from odin_sdk.plugins import PluginManager
from odin_sdk import OdinClient
import time
import json

async def demo_plugin_integration():
    """Demonstrate how to integrate the Performance Analytics Plugin"""
    
    print("🔌 PERFORMANCE ANALYTICS PLUGIN - INTEGRATION DEMO")
    print("=" * 70)
    
    # 1. Initialize Plugin Manager
    manager = PluginManager()
    
    # 2. Load Performance Analytics Plugin
    analytics_plugin = PerformanceAnalyticsPlugin({
        'enable_brazil_tracking': True,
        'alert_threshold_ms': 100,
        'success_rate_threshold': 0.95
    })
    
    await analytics_plugin.initialize()
    
    # 3. Register plugin with manager
    manager.plugins['performance-analytics'] = analytics_plugin
    manager.enabled_plugins['performance-analytics'] = analytics_plugin
    
    print("✅ Performance Analytics Plugin loaded and active")
    
    # 4. Simulate ODIN Protocol messages with analytics
    print("\n📊 Simulating AI coordination with analytics...")
    
    # Simulate successful Brazil PIX transaction
    await simulate_brazil_pix_transaction(analytics_plugin)
    
    # Simulate agronegócio coordination
    await simulate_agronegocio_coordination(analytics_plugin)
    
    # Simulate AI model performance comparison
    await simulate_model_comparison(analytics_plugin)
    
    # Simulate performance bottleneck
    await simulate_performance_bottleneck(analytics_plugin)
    
    # 5. Get comprehensive analytics report
    print("\n📈 COMPREHENSIVE PERFORMANCE REPORT:")
    print("=" * 50)
    
    stats = analytics_plugin.get_performance_stats()
    print(f"📊 Total Requests: {stats['total_requests']}")
    print(f"✅ Success Rate: {stats['success_rate']:.2%}")
    print(f"⚡ Average Latency: {stats['avg_latency_ms']:.1f}ms")
    
    # Brazil-specific metrics
    brazil_stats = analytics_plugin.get_brazil_performance()
    print(f"\n🇧🇷 Brazil Performance:")
    print(f"💳 PIX Transactions: {brazil_stats['pix_transactions'].get('total_transactions', 0)}")
    print(f"🏆 Top Regions: {[region for region, _ in brazil_stats['top_regions']]}")
    
    # Model performance comparison
    print(f"\n🤖 AI Model Performance:")
    for model, perf in stats['model_performance'].items():
        if isinstance(perf, dict) and 'avg_confidence' in perf:
            print(f"  {model}: {perf['avg_confidence']:.2f} confidence, {perf['avg_processing_time']*1000:.1f}ms")
    
    # Optimization suggestions
    print(f"\n💡 Optimization Suggestions: {len(stats['optimization_suggestions'])}")
    for suggestion in stats['optimization_suggestions'][-3:]:  # Last 3
        print(f"  ⚠️ {suggestion['issue_type']}: {suggestion['suggestion'][:60]}...")
    
    print(f"\n🎉 Plugin Integration Complete!")
    print(f"📈 Ready for production monitoring")

async def simulate_brazil_pix_transaction(plugin):
    """Simulate a Brazil PIX transaction with analytics"""
    
    # Create mock message for PIX transaction
    class MockMessage:
        def __init__(self):
            self.trace_id = "pix-001"
            self.metadata = {
                'region': 'brazil',
                'sistema': 'pix',
                'metodo_pagamento': 'pix',
                'regiao': 'sudeste',
                'valor': 5000.00,
                'banco_origem': 'Nubank'
            }
    
    message = MockMessage()
    
    # Start tracking
    processed_message = await plugin.process_message(message, {})
    
    # Simulate processing time
    await asyncio.sleep(0.03)  # 30ms processing
    
    # Track completion
    await plugin.track_event("message_completed", {
        'request_id': message.trace_id
    })
    
    # Track Brazil transaction
    await plugin.track_event("brazil_transaction", {
        'type': 'pix',
        'amount': 5000.00,
        'processing_time': 0.03
    })
    
    print("💳 Simulated PIX transaction: ✅ Success (30ms)")

async def simulate_agronegocio_coordination(plugin):
    """Simulate agronegócio AI coordination"""
    
    class MockMessage:
        def __init__(self):
            self.trace_id = "agro-001"
            self.metadata = {
                'region': 'brazil',
                'setor': 'agronegocio',
                'cultura': 'soja',
                'regiao': 'centro_oeste',
                'area_hectares': 1000
            }
    
    message = MockMessage()
    
    # Process with analytics
    await plugin.process_message(message, {})
    
    # Simulate AI model coordination
    await asyncio.sleep(0.025)  # 25ms processing
    
    # Track model performance
    await plugin.track_event("model_response", {
        'model': 'agro-climate-ai',
        'confidence': 0.92,
        'processing_time': 0.025
    })
    
    await plugin.track_event("message_completed", {
        'request_id': message.trace_id
    })
    
    print("🌾 Simulated agronegócio coordination: ✅ Success (25ms)")

async def simulate_model_comparison(plugin):
    """Simulate AI model performance comparison"""
    
    models = [
        ('gpt-4', 0.89, 0.045),
        ('claude-3', 0.91, 0.038),
        ('gemini-pro', 0.86, 0.052)
    ]
    
    for model_name, confidence, processing_time in models:
        await plugin.track_event("model_response", {
            'model': model_name,
            'confidence': confidence,
            'processing_time': processing_time
        })
    
    print("🤖 Simulated AI model comparison: GPT-4, Claude-3, Gemini")

async def simulate_performance_bottleneck(plugin):
    """Simulate a performance issue for optimization suggestions"""
    
    class MockMessage:
        def __init__(self):
            self.trace_id = "slow-001"
            self.metadata = {'region': 'brazil'}
    
    message = MockMessage()
    
    # Process with analytics
    await plugin.process_message(message, {})
    
    # Simulate slow processing (triggers optimization suggestion)
    await asyncio.sleep(0.15)  # 150ms - triggers high latency alert
    
    await plugin.track_event("message_completed", {
        'request_id': message.trace_id
    })
    
    print("⚠️ Simulated performance bottleneck: 150ms latency (triggers optimization)")

async def production_usage_example():
    """Show how to use in production with real ODIN Protocol"""
    
    print("\n🏭 PRODUCTION USAGE EXAMPLE:")
    print("=" * 50)
    
    code_example = '''
# Production integration with ODIN Protocol
from odin_sdk import OdinClient
from odin_sdk.plugins import PluginManager
from plugins.performance_analytics import PerformanceAnalyticsPlugin

async def setup_production_monitoring():
    # Initialize ODIN client
    client = OdinClient()
    
    # Setup plugin manager with analytics
    manager = PluginManager()
    analytics = PerformanceAnalyticsPlugin({
        'enable_brazil_tracking': True,
        'alert_threshold_ms': 50,  # Alert if > 50ms
        'success_rate_threshold': 0.99  # Alert if < 99%
    })
    
    await analytics.initialize()
    manager.plugins['analytics'] = analytics
    manager.enabled_plugins['analytics'] = analytics
    
    return client, manager

async def monitored_ai_coordination(client, manager):
    # Create message with automatic analytics
    message = client.create_message()\\
        .set_ids("prod-task", "session-1", "ai-1", "ai-2")\\
        .set_content("Production AI coordination task")\\
        .add_metadata("priority", "high")\\
        .build()
    
    # Process through analytics
    monitored_message = await manager.process_message(message)
    
    # Your AI coordination logic here
    result = await your_ai_coordination_logic(monitored_message)
    
    # Analytics automatically tracks performance
    return result
'''
    
    print(code_example)
    
    print("\n📊 Enterprise Benefits:")
    print("  🎯 Real-time SLA monitoring")
    print("  💰 Cost optimization through performance insights")
    print("  🔧 Automatic bottleneck identification")
    print("  📈 AI model ROI analysis")
    print("  🇧🇷 Brazil market performance optimization")

if __name__ == "__main__":
    asyncio.run(demo_plugin_integration())
    asyncio.run(production_usage_example())
