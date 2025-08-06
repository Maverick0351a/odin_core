#!/usr/bin/env python3
"""
Advanced Revenue Tracking for ODIN Protocol
Automated GitHub Actions integration
"""

import os
import stripe
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class GitHubRevenueTracker:
    """Advanced revenue tracking with GitHub integration"""
    
    def __init__(self):
        self.stripe_key = os.getenv('STRIPE_SECRET_KEY')
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK')
        
        if self.stripe_key:
            stripe.api_key = self.stripe_key
    
    def get_revenue_metrics(self) -> Dict[str, Any]:
        """Get comprehensive revenue metrics"""
        try:
            # Get current subscriptions
            subscriptions = stripe.Subscription.list(limit=100)
            
            # Calculate metrics
            active_subs = [sub for sub in subscriptions.data if sub.status == 'active']
            
            professional_subs = [
                sub for sub in active_subs 
                if any(item.price.unit_amount == 19900 for item in sub.items.data)
            ]
            
            enterprise_subs = [
                sub for sub in active_subs
                if any(item.price.unit_amount == 99900 for item in sub.items.data)
            ]
            
            # Revenue calculations
            professional_mrr = len(professional_subs) * 199
            enterprise_mrr = len(enterprise_subs) * 999
            total_mrr = professional_mrr + enterprise_mrr
            projected_arr = total_mrr * 12
            
            # Get payment data for current month
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            charges = stripe.Charge.list(
                created={'gte': int(start_of_month.timestamp())},
                limit=100
            )
            
            current_month_revenue = sum(
                charge.amount / 100 
                for charge in charges.data 
                if charge.status == 'succeeded'
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_mrr': total_mrr,
                'projected_arr': projected_arr,
                'current_month_revenue': current_month_revenue,
                'active_subscriptions': len(active_subs),
                'professional_customers': len(professional_subs),
                'enterprise_customers': len(enterprise_subs),
                'professional_mrr': professional_mrr,
                'enterprise_mrr': enterprise_mrr,
                'growth_metrics': self._calculate_growth_metrics()
            }
            
        except Exception as e:
            print(f"Error getting revenue metrics: {e}")
            return self._get_demo_metrics()
    
    def _calculate_growth_metrics(self) -> Dict[str, float]:
        """Calculate growth rates and projections"""
        try:
            # Get last 30 days of data
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_subs = stripe.Subscription.list(
                created={'gte': int(thirty_days_ago.timestamp())},
                limit=100
            )
            
            new_customers_30d = len(recent_subs.data)
            
            # Estimate conversion rate (simplified)
            # In production, you'd track PyPI downloads and signups
            estimated_trial_users = new_customers_30d * 20  # Assume 5% conversion
            conversion_rate = (new_customers_30d / estimated_trial_users * 100) if estimated_trial_users > 0 else 2.5
            
            return {
                'new_customers_30d': new_customers_30d,
                'estimated_conversion_rate': round(conversion_rate, 2),
                'growth_rate_monthly': round(new_customers_30d * 2.5, 2)  # Simplified calculation
            }
            
        except Exception as e:
            print(f"Error calculating growth metrics: {e}")
            return {
                'new_customers_30d': 0,
                'estimated_conversion_rate': 2.5,
                'growth_rate_monthly': 0
            }
    
    def _get_demo_metrics(self) -> Dict[str, Any]:
        """Fallback demo metrics when Stripe unavailable"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_mrr': 0,
            'projected_arr': 0,
            'current_month_revenue': 0,
            'active_subscriptions': 0,
            'professional_customers': 0,
            'enterprise_customers': 0,
            'professional_mrr': 0,
            'enterprise_mrr': 0,
            'growth_metrics': {
                'new_customers_30d': 0,
                'estimated_conversion_rate': 2.5,
                'growth_rate_monthly': 0
            }
        }
    
    def notify_discord(self, metrics: Dict[str, Any]):
        """Send revenue update to Discord"""
        if not self.discord_webhook:
            return
            
        embed = {
            "title": "💰 ODIN Protocol Revenue Update",
            "color": 0x00ff00 if metrics['total_mrr'] > 0 else 0xffaa00,
            "fields": [
                {
                    "name": "📊 Current MRR",
                    "value": f"${metrics['total_mrr']:,}",
                    "inline": True
                },
                {
                    "name": "🎯 Projected ARR", 
                    "value": f"${metrics['projected_arr']:,}",
                    "inline": True
                },
                {
                    "name": "👥 Active Customers",
                    "value": f"{metrics['active_subscriptions']}",
                    "inline": True
                },
                {
                    "name": "💼 Professional",
                    "value": f"{metrics['professional_customers']} customers",
                    "inline": True
                },
                {
                    "name": "🏢 Enterprise", 
                    "value": f"{metrics['enterprise_customers']} customers",
                    "inline": True
                },
                {
                    "name": "📈 Growth Rate",
                    "value": f"{metrics['growth_metrics']['growth_rate_monthly']:.1f}%/month",
                    "inline": True
                }
            ],
            "footer": {
                "text": f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
            }
        }
        
        if metrics['total_mrr'] >= 1990:  # Month 1 target reached
            embed["title"] = "🎉 MILESTONE REACHED! Month 1 Target Hit!"
            embed["color"] = 0xffd700
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            response = requests.post(self.discord_webhook, json=payload)
            response.raise_for_status()
            print("Discord notification sent successfully")
        except Exception as e:
            print(f"Error sending Discord notification: {e}")
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to JSON file for processing"""
        with open('revenue_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"Revenue metrics saved: ${metrics['total_mrr']:,} MRR")
    
    def run_tracking(self):
        """Main tracking function"""
        print("🚀 Running ODIN Protocol Revenue Tracking...")
        
        metrics = self.get_revenue_metrics()
        self.save_metrics(metrics)
        self.notify_discord(metrics)
        
        # Print summary
        print(f"""
📊 REVENUE SUMMARY
==================
MRR: ${metrics['total_mrr']:,}
ARR: ${metrics['projected_arr']:,}  
Customers: {metrics['active_subscriptions']}
Professional: {metrics['professional_customers']}
Enterprise: {metrics['enterprise_customers']}
Growth: {metrics['growth_metrics']['growth_rate_monthly']:.1f}%/month
        """)
        
        return metrics

def main():
    """Run revenue tracking"""
    tracker = GitHubRevenueTracker()
    tracker.run_tracking()

if __name__ == "__main__":
    main()
