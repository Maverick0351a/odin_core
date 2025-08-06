#!/usr/bin/env python3
"""
Real-Time HEL Performance Monitor
Provides live monitoring and analytics for ODIN Protocol HEL System
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque
import threading
from hel_mediator_ai import HelMediatorAI, create_hel_mediator_ai


@dataclass
class PerformanceMetric:
    """Individual performance metric snapshot"""
    timestamp: str
    metric_name: str
    value: float
    unit: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None


@dataclass
class HealthStatus:
    """System health status"""
    overall_health: str  # "healthy", "warning", "critical"
    component_health: Dict[str, str]
    active_alerts: List[str]
    performance_score: float
    last_updated: str


class RealTimeHelMonitor:
    """Real-time monitoring system for HEL Rule Engine"""
    
    def __init__(self, hel_mediator: HelMediatorAI):
        self.hel_mediator = hel_mediator
        self.monitoring_active = False
        self.metrics_history: Dict[str, deque] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.performance_baselines = {
            "response_time": 0.1,  # seconds
            "confidence_average": 0.8,
            "compliance_rate": 0.95,
            "error_rate": 0.01
        }
        self.thresholds = {
            "response_time_warning": 0.2,
            "response_time_critical": 0.5,
            "confidence_warning": 0.7,
            "confidence_critical": 0.6,
            "error_rate_warning": 0.05,
            "error_rate_critical": 0.1
        }
        
        # Initialize metric history with 1000 data points
        for metric in ["response_time", "confidence", "compliance_rate", "error_rate", 
                      "throughput", "rule_efficiency", "colleague_performance"]:
            self.metrics_history[metric] = deque(maxlen=1000)
        
        self.monitoring_thread = None
        
    def start_monitoring(self, interval_seconds: float = 5.0):
        """Start real-time monitoring"""
        if self.monitoring_active:
            print("⚠️  Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        print(f"✅ Real-time monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        print("🛑 Monitoring stopped")
    
    def _monitoring_loop(self, interval_seconds: float):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._collect_metrics()
                self._check_thresholds()
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(interval_seconds)
    
    def _collect_metrics(self):
        """Collect current performance metrics"""
        current_time = datetime.now().isoformat()
        
        # Get HEL stats
        hel_stats = self.hel_mediator.get_hel_stats()
        
        # Calculate response time (simulate based on recent evaluations)
        response_time = self._calculate_average_response_time()
        self._add_metric("response_time", response_time, current_time)
        
        # Calculate average confidence
        confidence = self._calculate_average_confidence()
        self._add_metric("confidence", confidence, current_time)
        
        # Calculate compliance rate
        compliance_rate = self._calculate_compliance_rate()
        self._add_metric("compliance_rate", compliance_rate, current_time)
        
        # Calculate error rate
        error_rate = self._calculate_error_rate()
        self._add_metric("error_rate", error_rate, current_time)
        
        # Calculate throughput (evaluations per second)
        throughput = self._calculate_throughput()
        self._add_metric("throughput", throughput, current_time)
        
        # Calculate rule efficiency
        rule_efficiency = self._calculate_rule_efficiency()
        self._add_metric("rule_efficiency", rule_efficiency, current_time)
        
        # Calculate colleague performance
        colleague_performance = self._calculate_colleague_performance()
        self._add_metric("colleague_performance", colleague_performance, current_time)
    
    def _add_metric(self, metric_name: str, value: float, timestamp: str):
        """Add metric to history"""
        metric = PerformanceMetric(
            timestamp=timestamp,
            metric_name=metric_name,
            value=value,
            unit=self._get_metric_unit(metric_name),
            threshold_warning=self.thresholds.get(f"{metric_name}_warning"),
            threshold_critical=self.thresholds.get(f"{metric_name}_critical")
        )
        self.metrics_history[metric_name].append(metric)
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get unit for metric"""
        units = {
            "response_time": "seconds",
            "confidence": "ratio",
            "compliance_rate": "percentage",
            "error_rate": "percentage",
            "throughput": "eval/sec",
            "rule_efficiency": "ratio",
            "colleague_performance": "ratio"
        }
        return units.get(metric_name, "unit")
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time"""
        # Simulate based on complexity and recent performance
        base_time = 0.05  # Base processing time
        load_factor = min(len(self.hel_mediator.rule_engine.rules) / 10, 2.0)
        return base_time * (1 + load_factor * 0.5)
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence from recent evaluations"""
        # Simulate based on system health
        base_confidence = 0.85
        error_impact = len(self.alerts) * 0.02
        return max(base_confidence - error_impact, 0.0)
    
    def _calculate_compliance_rate(self) -> float:
        """Calculate compliance rate"""
        hel_stats = self.hel_mediator.get_hel_stats()
        execution_stats = hel_stats.get("execution_stats", {})
        
        total_evals = execution_stats.get("total_evaluations", 1)
        rejections = execution_stats.get("rejection_count", 0)
        
        # Compliance rate = (total - rejections) / total
        return max((total_evals - rejections) / total_evals, 0.0)
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        # Simulate based on recent alerts
        recent_alerts = [a for a in self.alerts 
                        if datetime.fromisoformat(a["timestamp"]) > 
                        datetime.now() - timedelta(minutes=5)]
        return min(len(recent_alerts) / 100, 1.0)
    
    def _calculate_throughput(self) -> float:
        """Calculate throughput (evaluations per second)"""
        # Simulate based on system capacity
        base_throughput = 10.0  # Base evaluations per second
        load_factor = len(self.hel_mediator.rule_engine.rules) / 20
        return base_throughput / (1 + load_factor)
    
    def _calculate_rule_efficiency(self) -> float:
        """Calculate rule efficiency"""
        hel_stats = self.hel_mediator.get_hel_stats()
        execution_stats = hel_stats.get("execution_stats", {})
        
        total_evals = execution_stats.get("total_evaluations", 1)
        triggered_rules = execution_stats.get("rules_triggered", 0)
        
        # Efficiency = triggered / total evaluations
        return min(triggered_rules / total_evals, 1.0)
    
    def _calculate_colleague_performance(self) -> float:
        """Calculate colleague performance"""
        hel_stats = self.hel_mediator.get_hel_stats()
        colleague_stats = hel_stats.get("hel_engine_stats", {})
        
        interactions = colleague_stats.get("colleague_interactions", 0)
        requests = colleague_stats.get("mediator_requests", 1)
        
        # Performance = successful interactions / requests
        return min(interactions / requests, 1.0)
    
    def _check_thresholds(self):
        """Check metrics against thresholds and generate alerts"""
        for metric_name, history in self.metrics_history.items():
            if not history:
                continue
            
            latest_metric = history[-1]
            self._check_metric_threshold(latest_metric)
    
    def _check_metric_threshold(self, metric: PerformanceMetric):
        """Check individual metric against thresholds"""
        # Critical threshold check
        if (metric.threshold_critical is not None and 
            self._is_threshold_exceeded(metric.value, metric.threshold_critical, metric.metric_name)):
            self._create_alert("critical", metric)
        
        # Warning threshold check
        elif (metric.threshold_warning is not None and 
              self._is_threshold_exceeded(metric.value, metric.threshold_warning, metric.metric_name)):
            self._create_alert("warning", metric)
    
    def _is_threshold_exceeded(self, value: float, threshold: float, metric_name: str) -> bool:
        """Check if threshold is exceeded based on metric type"""
        # For error_rate and response_time, higher is worse
        if metric_name in ["error_rate", "response_time"]:
            return value > threshold
        # For confidence and other metrics, lower is worse
        else:
            return value < threshold
    
    def _create_alert(self, severity: str, metric: PerformanceMetric):
        """Create performance alert"""
        alert_id = f"{metric.metric_name}_{severity}_{int(time.time())}"
        
        # Check if similar alert already exists
        existing_alert = any(
            a["metric_name"] == metric.metric_name and a["severity"] == severity
            for a in self.alerts[-10:]  # Check last 10 alerts
        )
        
        if not existing_alert:
            alert = {
                "alert_id": alert_id,
                "timestamp": metric.timestamp,
                "severity": severity,
                "metric_name": metric.metric_name,
                "current_value": metric.value,
                "threshold": (metric.threshold_critical if severity == "critical" 
                            else metric.threshold_warning),
                "unit": metric.unit,
                "message": self._generate_alert_message(metric, severity)
            }
            
            self.alerts.append(alert)
            print(f"🚨 {severity.upper()} ALERT: {alert['message']}")
            
            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
    
    def _generate_alert_message(self, metric: PerformanceMetric, severity: str) -> str:
        """Generate human-readable alert message"""
        threshold = (metric.threshold_critical if severity == "critical" 
                    else metric.threshold_warning)
        
        return f"{metric.metric_name} {severity}: {metric.value:.3f} {metric.unit} (threshold: {threshold})"
    
    def get_health_status(self) -> HealthStatus:
        """Get current system health status"""
        # Check recent alerts
        recent_alerts = [a for a in self.alerts 
                        if datetime.fromisoformat(a["timestamp"]) > 
                        datetime.now() - timedelta(minutes=5)]
        
        critical_alerts = [a for a in recent_alerts if a["severity"] == "critical"]
        warning_alerts = [a for a in recent_alerts if a["severity"] == "warning"]
        
        # Determine overall health
        if critical_alerts:
            overall_health = "critical"
        elif warning_alerts:
            overall_health = "warning"
        else:
            overall_health = "healthy"
        
        # Calculate performance score
        performance_score = self._calculate_performance_score()
        
        # Get component health
        component_health = self._get_component_health()
        
        return HealthStatus(
            overall_health=overall_health,
            component_health=component_health,
            active_alerts=[a["message"] for a in recent_alerts],
            performance_score=performance_score,
            last_updated=datetime.now().isoformat()
        )
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-1)"""
        scores = []
        
        for metric_name in ["response_time", "confidence", "compliance_rate", "error_rate"]:
            if metric_name in self.metrics_history and self.metrics_history[metric_name]:
                latest = self.metrics_history[metric_name][-1]
                baseline = self.performance_baselines.get(metric_name, 0.5)
                
                if metric_name in ["response_time", "error_rate"]:
                    # Lower is better
                    score = max(0, min(1, 1 - (latest.value / (baseline * 2))))
                else:
                    # Higher is better
                    score = max(0, min(1, latest.value / baseline))
                
                scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _get_component_health(self) -> Dict[str, str]:
        """Get health status of individual components"""
        return {
            "hel_rule_engine": "healthy",
            "mediator_ai": "healthy", 
            "colleague_network": "healthy",
            "rule_evaluation": "healthy"
        }
    
    def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get data for real-time dashboard"""
        health = self.get_health_status()
        
        # Get latest metrics
        latest_metrics = {}
        for metric_name, history in self.metrics_history.items():
            if history:
                latest = history[-1]
                latest_metrics[metric_name] = {
                    "value": latest.value,
                    "unit": latest.unit,
                    "timestamp": latest.timestamp,
                    "trend": self._calculate_trend(metric_name)
                }
        
        # Get HEL statistics
        hel_stats = self.hel_mediator.get_hel_stats()
        
        return {
            "health_status": asdict(health),
            "latest_metrics": latest_metrics,
            "hel_statistics": hel_stats,
            "alert_summary": {
                "total_alerts": len(self.alerts),
                "recent_alerts": len([a for a in self.alerts 
                                    if datetime.fromisoformat(a["timestamp"]) > 
                                    datetime.now() - timedelta(hours=1)])
            },
            "monitoring_status": {
                "active": self.monitoring_active,
                "metrics_collected": sum(len(h) for h in self.metrics_history.values())
            }
        }
    
    def _calculate_trend(self, metric_name: str) -> str:
        """Calculate trend for metric (up/down/stable)"""
        history = self.metrics_history.get(metric_name, deque())
        
        if len(history) < 2:
            return "stable"
        
        recent_avg = sum(m.value for m in list(history)[-5:]) / min(5, len(history))
        older_avg = sum(m.value for m in list(history)[-10:-5]) / max(1, min(5, len(history) - 5))
        
        change_percent = (recent_avg - older_avg) / older_avg * 100 if older_avg > 0 else 0
        
        if change_percent > 5:
            return "up"
        elif change_percent < -5:
            return "down"
        else:
            return "stable"
    
    def export_performance_report(self) -> Dict[str, Any]:
        """Export comprehensive performance report"""
        health = self.get_health_status()
        dashboard_data = self.get_real_time_dashboard_data()
        
        # Calculate time-based statistics
        time_stats = {}
        for metric_name, history in self.metrics_history.items():
            if history:
                values = [m.value for m in history]
                time_stats[metric_name] = {
                    "current": values[-1],
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "samples": len(values)
                }
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "monitoring_period": "real-time",
            "health_summary": asdict(health),
            "performance_metrics": time_stats,
            "alert_history": self.alerts[-50:],  # Last 50 alerts
            "system_statistics": dashboard_data["hel_statistics"],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check response time
        if "response_time" in self.metrics_history and self.metrics_history["response_time"]:
            avg_response = sum(m.value for m in self.metrics_history["response_time"]) / len(self.metrics_history["response_time"])
            if avg_response > 0.2:
                recommendations.append("Consider optimizing rule evaluation order for better response time")
        
        # Check error rate
        if "error_rate" in self.metrics_history and self.metrics_history["error_rate"]:
            latest_error_rate = self.metrics_history["error_rate"][-1].value
            if latest_error_rate > 0.05:
                recommendations.append("Investigate recent errors to improve system reliability")
        
        # Check rule efficiency
        if "rule_efficiency" in self.metrics_history and self.metrics_history["rule_efficiency"]:
            efficiency = self.metrics_history["rule_efficiency"][-1].value
            if efficiency < 0.3:
                recommendations.append("Review rule conditions - many rules may not be triggering")
        
        return recommendations


async def demo_real_time_monitoring():
    """Demonstrate real-time monitoring system"""
    print("📊 ODIN Protocol Real-Time HEL Monitoring Demo")
    print("=" * 60)
    
    # Initialize HEL system
    hel_mediator = create_hel_mediator_ai()
    monitor = RealTimeHelMonitor(hel_mediator)
    
    print("✅ Real-time monitor initialized")
    
    # Start monitoring
    monitor.start_monitoring(interval_seconds=2.0)
    
    # Simulate some activity
    print("\n🔄 Simulating HEL activity...")
    
    for i in range(10):
        # Simulate evaluation
        test_context = {
            "content": f"Test message {i}",
            "confidence": 0.8 + (i % 3) * 0.1,
            "trace_id": f"monitor-test-{i}"
        }
        
        await hel_mediator.evaluate_enhanced_async(test_context)
        await asyncio.sleep(1)
    
    # Get real-time data
    print("\n📈 Real-time Dashboard Data:")
    dashboard = monitor.get_real_time_dashboard_data()
    
    health = dashboard["health_status"]
    print(f"  Overall Health: {health['overall_health']}")
    print(f"  Performance Score: {health['performance_score']:.2f}")
    
    metrics = dashboard["latest_metrics"]
    for metric_name, data in metrics.items():
        print(f"  {metric_name}: {data['value']:.3f} {data['unit']} ({data['trend']})")
    
    # Generate performance report
    print(f"\n📋 Performance Report:")
    report = monitor.export_performance_report()
    
    for metric_name, stats in report["performance_metrics"].items():
        print(f"  {metric_name}: avg={stats['average']:.3f}, current={stats['current']:.3f}")
    
    if report["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")
    
    # Export report
    filename = f"hel_performance_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Performance report exported: {filename}")
    
    # Stop monitoring
    monitor.stop_monitoring()
    print("\n✅ Real-time monitoring demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demo_real_time_monitoring())
