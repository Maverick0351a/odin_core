#!/usr/bin/env python3
"""
ODIN Protocol Automation Dashboard
Web-based dashboard for monitoring automation
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
import subprocess
from typing import Dict, List, Any

app = Flask(__name__)

class AutomationDashboard:
    """Web dashboard for monitoring automation"""
    
    def __init__(self):
        self.load_automation_data()
    
    def load_automation_data(self) -> Dict[str, Any]:
        """Load current automation status and metrics"""
        return {
            'revenue_metrics': self.get_revenue_metrics(),
            'social_media_stats': self.get_social_media_stats(),
            'enterprise_outreach_status': self.get_enterprise_status(),
            'automation_schedule': self.get_schedule_status(),
            'content_library_status': self.get_content_status()
        }
    
    def get_revenue_metrics(self) -> Dict[str, Any]:
        """Get current revenue metrics"""
        try:
            result = subprocess.run(['python', 'revenue_tracker.py', '--json'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"Error getting revenue metrics: {e}")
        
        return {
            'monthly_recurring_revenue': 0,
            'active_subscriptions': 0,
            'current_month_revenue': 0,
            'projected_arr': 0
        }
    
    def get_social_media_stats(self) -> Dict[str, Any]:
        """Get social media automation statistics"""
        try:
            if os.path.exists('social_media_automation.json'):
                with open('social_media_automation.json', 'r') as f:
                    logs = json.load(f)
                    
                today = datetime.now().date()
                today_posts = [log for log in logs 
                             if datetime.fromisoformat(log['timestamp']).date() == today]
                
                return {
                    'posts_today': len(today_posts),
                    'total_posts': len(logs),
                    'platforms_active': len(set(log['platform'] for log in logs)),
                    'last_post': logs[-1] if logs else None
                }
        except Exception:
            pass
        
        return {
            'posts_today': 0,
            'total_posts': 0,
            'platforms_active': 0,
            'last_post': None
        }
    
    def get_enterprise_status(self) -> Dict[str, Any]:
        """Get enterprise outreach status"""
        try:
            if os.path.exists('enterprise_outreach_automation.json'):
                with open('enterprise_outreach_automation.json', 'r') as f:
                    logs = json.load(f)
                    
                contacted = len(set(log['company'] for log in logs))
                pending_followups = len([log for log in logs 
                                       if log.get('followup_date') and 
                                       datetime.fromisoformat(log['followup_date']) <= datetime.now()])
                
                return {
                    'companies_contacted': contacted,
                    'emails_sent': len(logs),
                    'pending_followups': pending_followups,
                    'last_outreach': logs[-1] if logs else None
                }
        except Exception:
            pass
        
        return {
            'companies_contacted': 0,
            'emails_sent': 0,
            'pending_followups': 0,
            'last_outreach': None
        }
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """Get automation schedule status"""
        return {
            'automation_active': True,
            'next_social_post': self.get_next_scheduled_time('social'),
            'next_enterprise_email': self.get_next_scheduled_time('enterprise'),
            'next_revenue_check': self.get_next_scheduled_time('revenue'),
            'uptime_hours': 24  # Placeholder
        }
    
    def get_next_scheduled_time(self, automation_type: str) -> str:
        """Get next scheduled time for automation type"""
        now = datetime.now()
        
        schedules = {
            'social': ['09:00', '14:00', '18:00'],
            'enterprise': ['10:00'],  # Mon, Wed, Fri
            'revenue': ['hourly']
        }
        
        if automation_type == 'revenue':
            return (now + timedelta(hours=1)).strftime('%H:%M')
        
        times = schedules.get(automation_type, [])
        current_time = now.strftime('%H:%M')
        
        for time_str in times:
            if time_str > current_time:
                return time_str
        
        # Next day's first time
        return times[0] if times else 'N/A'
    
    def get_content_status(self) -> Dict[str, Any]:
        """Get content library status"""
        return {
            'total_templates': 15,
            'scheduled_posts': 8,
            'content_generated_today': 3,
            'platforms_covered': 4
        }

dashboard = AutomationDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for automation status"""
    data = dashboard.load_automation_data()
    return jsonify(data)

@app.route('/api/revenue')
def api_revenue():
    """API endpoint for revenue metrics"""
    return jsonify(dashboard.get_revenue_metrics())

@app.route('/api/social')
def api_social():
    """API endpoint for social media stats"""
    return jsonify(dashboard.get_social_media_stats())

@app.route('/api/enterprise')
def api_enterprise():
    """API endpoint for enterprise outreach"""
    return jsonify(dashboard.get_enterprise_status())

@app.route('/api/trigger/<automation_type>')
def trigger_automation(automation_type):
    """Manually trigger automation"""
    try:
        if automation_type == 'social':
            subprocess.run(['python', '-c', 
                          'from marketing_automation import OdinMarketingAutomation; '
                          'OdinMarketingAutomation().auto_post_social_media()'])
            return jsonify({'status': 'success', 'message': 'Social media posting triggered'})
        
        elif automation_type == 'enterprise':
            subprocess.run(['python', '-c',
                          'from marketing_automation import OdinMarketingAutomation; '
                          'OdinMarketingAutomation().auto_enterprise_outreach()'])
            return jsonify({'status': 'success', 'message': 'Enterprise outreach triggered'})
        
        elif automation_type == 'revenue':
            subprocess.run(['python', 'revenue_tracker.py', '--report'])
            return jsonify({'status': 'success', 'message': 'Revenue tracking triggered'})
        
        else:
            return jsonify({'status': 'error', 'message': 'Unknown automation type'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# HTML Template for Dashboard
dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>ODIN Protocol Automation Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                       gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; 
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .metric-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }
        .metric-value { font-size: 36px; font-weight: bold; color: #667eea; margin-bottom: 5px; }
        .metric-label { color: #666; font-size: 14px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; 
                           border-radius: 50%; margin-right: 8px; }
        .status-active { background: #4CAF50; }
        .status-inactive { background: #f44336; }
        .control-panel { background: white; padding: 20px; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #667eea; color: white; border: none; padding: 10px 20px; 
               border-radius: 5px; cursor: pointer; margin-right: 10px; margin-bottom: 10px; }
        .btn:hover { background: #5a6fd8; }
        .log-section { background: white; padding: 20px; border-radius: 10px; 
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-top: 20px; }
        .log-entry { padding: 10px; border-bottom: 1px solid #eee; font-family: monospace; }
        .refresh-indicator { color: #4CAF50; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 ODIN Protocol Marketing Automation Dashboard</h1>
            <p>Complete automation system running 24/7 - No marketing specialist needed!</p>
            <p><span class="status-indicator status-active"></span>Automation Status: ACTIVE</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">💰 Revenue Metrics</div>
                <div class="metric-value" id="mrr-value">$0</div>
                <div class="metric-label">Monthly Recurring Revenue</div>
                <div style="margin-top: 10px;">
                    <div>Customers: <span id="customer-count">0</span></div>
                    <div>ARR: $<span id="arr-value">0</span></div>
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">📱 Social Media</div>
                <div class="metric-value" id="posts-today">0</div>
                <div class="metric-label">Posts Today</div>
                <div style="margin-top: 10px;">
                    <div>Total Posts: <span id="total-posts">0</span></div>
                    <div>Platforms: <span id="platforms-active">0</span></div>
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🏢 Enterprise Outreach</div>
                <div class="metric-value" id="companies-contacted">0</div>
                <div class="metric-label">Companies Contacted</div>
                <div style="margin-top: 10px;">
                    <div>Emails Sent: <span id="emails-sent">0</span></div>
                    <div>Pending Followups: <span id="pending-followups">0</span></div>
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">⚡ Automation Status</div>
                <div class="metric-value">24/7</div>
                <div class="metric-label">Active Monitoring</div>
                <div style="margin-top: 10px;">
                    <div>Next Social Post: <span id="next-social">09:00</span></div>
                    <div>Next Enterprise Email: <span id="next-enterprise">10:00</span></div>
                </div>
            </div>
        </div>
        
        <div class="control-panel">
            <h3>🎮 Manual Controls</h3>
            <p>Trigger automation manually if needed:</p>
            <button class="btn" onclick="triggerAutomation('social')">📱 Trigger Social Media Post</button>
            <button class="btn" onclick="triggerAutomation('enterprise')">📧 Send Enterprise Email</button>
            <button class="btn" onclick="triggerAutomation('revenue')">💰 Check Revenue</button>
            <button class="btn" onclick="refreshDashboard()">🔄 Refresh Dashboard</button>
        </div>
        
        <div class="log-section">
            <h3>📋 Recent Activity Log</h3>
            <div id="activity-log">
                <div class="log-entry">🤖 Automation system initialized</div>
                <div class="log-entry">📊 Revenue tracking active</div>
                <div class="log-entry">📱 Social media scheduling enabled</div>
                <div class="log-entry">🏢 Enterprise outreach queue loaded</div>
            </div>
        </div>
    </div>

    <script>
        function refreshDashboard() {
            document.getElementById('activity-log').innerHTML += 
                '<div class="log-entry refresh-indicator">🔄 Dashboard refreshed at ' + 
                new Date().toLocaleTimeString() + '</div>';
            
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update revenue metrics
                    document.getElementById('mrr-value').textContent = 
                        '$' + (data.revenue_metrics.monthly_recurring_revenue || 0).toLocaleString();
                    document.getElementById('customer-count').textContent = 
                        data.revenue_metrics.active_subscriptions || 0;
                    document.getElementById('arr-value').textContent = 
                        (data.revenue_metrics.projected_arr || 0).toLocaleString();
                    
                    // Update social media metrics
                    document.getElementById('posts-today').textContent = 
                        data.social_media_stats.posts_today || 0;
                    document.getElementById('total-posts').textContent = 
                        data.social_media_stats.total_posts || 0;
                    document.getElementById('platforms-active').textContent = 
                        data.social_media_stats.platforms_active || 0;
                    
                    // Update enterprise metrics
                    document.getElementById('companies-contacted').textContent = 
                        data.enterprise_outreach_status.companies_contacted || 0;
                    document.getElementById('emails-sent').textContent = 
                        data.enterprise_outreach_status.emails_sent || 0;
                    document.getElementById('pending-followups').textContent = 
                        data.enterprise_outreach_status.pending_followups || 0;
                    
                    // Update schedule
                    document.getElementById('next-social').textContent = 
                        data.automation_schedule.next_social_post || 'N/A';
                    document.getElementById('next-enterprise').textContent = 
                        data.automation_schedule.next_enterprise_email || 'N/A';
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('activity-log').innerHTML += 
                        '<div class="log-entry">❌ Error fetching data: ' + error + '</div>';
                });
        }
        
        function triggerAutomation(type) {
            fetch('/api/trigger/' + type)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('activity-log').innerHTML += 
                        '<div class="log-entry">⚡ ' + data.message + ' at ' + 
                        new Date().toLocaleTimeString() + '</div>';
                    
                    if (data.status === 'success') {
                        setTimeout(refreshDashboard, 2000); // Refresh after 2 seconds
                    }
                })
                .catch(error => {
                    document.getElementById('activity-log').innerHTML += 
                        '<div class="log-entry">❌ Error triggering ' + type + ': ' + error + '</div>';
                });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshDashboard, 30000);
        
        // Initial load
        refreshDashboard();
    </script>
</body>
</html>
"""

# Create templates directory and file
import os
os.makedirs('templates', exist_ok=True)
with open('templates/dashboard.html', 'w') as f:
    f.write(dashboard_html)

if __name__ == '__main__':
    print("🚀 Starting ODIN Protocol Automation Dashboard...")
    print("Dashboard will be available at: http://localhost:5000")
    print("This provides real-time monitoring of all automation systems!")
    app.run(debug=True, host='0.0.0.0', port=5000)
