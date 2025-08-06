#!/usr/bin/env python3
"""
ODIN Protocol Revenue Tracker
Integrates with Stripe to track revenue, conversions, and business metrics
"""

import os
import stripe
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class OdinRevenueTracker:
    """Revenue tracking and analytics for ODIN Protocol"""
    
    def __init__(self, stripe_secret_key: str = None):
        """Initialize revenue tracker with Stripe integration"""
        self.stripe_key = stripe_secret_key or os.getenv('STRIPE_SECRET_KEY')
        if self.stripe_key:
            stripe.api_key = self.stripe_key
        
        self.logger = logging.getLogger(__name__)
        
        # Revenue targets
        self.targets = {
            'month_1_mrr': 1990,      # 10 Professional customers
            'month_3_mrr': 9950,      # 50 Professional customers  
            'month_6_mrr': 29900,     # 100 Pro + 10 Enterprise
            'month_12_mrr': 64750,    # 200 Pro + 25 Enterprise
            'year_1_arr': 777000      # Annual recurring revenue
        }
    
    def get_current_metrics(self) -> Dict:
        """Get current revenue and subscription metrics"""
        try:
            # Get current month revenue
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            timestamp = int(start_of_month.timestamp())
            
            # Fetch charges from Stripe
            charges = stripe.Charge.list(
                created={'gte': timestamp},
                limit=100
            )
            
            current_revenue = sum(charge.amount for charge in charges.data) / 100
            
            # Get active subscriptions
            subscriptions = stripe.Subscription.list(
                status='active',
                limit=100
            )
            
            # Calculate MRR
            mrr = 0
            subscription_breakdown = {'professional': 0, 'enterprise': 0}
            
            for sub in subscriptions.data:
                amount = sub.items.data[0].price.unit_amount / 100
                mrr += amount
                
                # Categorize by amount
                if amount >= 999:
                    subscription_breakdown['enterprise'] += 1
                elif amount >= 199:
                    subscription_breakdown['professional'] += 1
            
            # Calculate projected ARR
            projected_arr = mrr * 12
            
            return {
                'timestamp': datetime.now().isoformat(),
                'current_month_revenue': current_revenue,
                'monthly_recurring_revenue': mrr,
                'projected_arr': projected_arr,
                'active_subscriptions': len(subscriptions.data),
                'subscription_breakdown': subscription_breakdown,
                'target_progress': self._calculate_target_progress(mrr),
                'growth_metrics': self._calculate_growth_metrics()
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching metrics: {e}")
            return {'error': str(e)}
    
    def _calculate_target_progress(self, current_mrr: float) -> Dict:
        """Calculate progress towards revenue targets"""
        progress = {}
        
        for target_name, target_value in self.targets.items():
            if 'mrr' in target_name:
                progress[target_name] = {
                    'target': target_value,
                    'current': current_mrr,
                    'percentage': min(100, (current_mrr / target_value) * 100),
                    'remaining': max(0, target_value - current_mrr)
                }
            elif 'arr' in target_name:
                current_arr = current_mrr * 12
                progress[target_name] = {
                    'target': target_value,
                    'current': current_arr,
                    'percentage': min(100, (current_arr / target_value) * 100),
                    'remaining': max(0, target_value - current_arr)
                }
        
        return progress
    
    def _calculate_growth_metrics(self) -> Dict:
        """Calculate growth and conversion metrics"""
        try:
            # Get last 30 days of data
            thirty_days_ago = datetime.now() - timedelta(days=30)
            timestamp = int(thirty_days_ago.timestamp())
            
            # Recent charges
            recent_charges = stripe.Charge.list(
                created={'gte': timestamp},
                limit=100
            )
            
            # Recent customers
            recent_customers = stripe.Customer.list(
                created={'gte': timestamp},
                limit=100
            )
            
            return {
                'new_revenue_30d': sum(c.amount for c in recent_charges.data) / 100,
                'new_customers_30d': len(recent_customers.data),
                'avg_revenue_per_customer': self._calculate_arpc(),
                'conversion_rate': self._estimate_conversion_rate()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating growth metrics: {e}")
            return {}
    
    def _calculate_arpc(self) -> float:
        """Calculate Average Revenue Per Customer"""
        try:
            subs = stripe.Subscription.list(status='active', limit=100)
            if len(subs.data) == 0:
                return 0
            
            total_revenue = sum(sub.items.data[0].price.unit_amount for sub in subs.data) / 100
            return total_revenue / len(subs.data)
            
        except Exception:
            return 0
    
    def _estimate_conversion_rate(self) -> float:
        """Estimate conversion rate from PyPI downloads to paid"""
        # This would integrate with PyPI stats API
        # For now, return estimated rate
        return 2.5  # 2.5% conversion rate estimate
    
    def generate_revenue_report(self) -> str:
        """Generate a comprehensive revenue report"""
        metrics = self.get_current_metrics()
        
        if 'error' in metrics:
            return f"❌ Error generating report: {metrics['error']}"
        
        report = f"""
🚀 ODIN Protocol Revenue Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 CURRENT REVENUE
Monthly Recurring Revenue (MRR): ${metrics['monthly_recurring_revenue']:,.2f}
Current Month Revenue: ${metrics['current_month_revenue']:,.2f}
Projected Annual Revenue (ARR): ${metrics['projected_arr']:,.2f}

📊 SUBSCRIPTIONS
Total Active Subscriptions: {metrics['active_subscriptions']}
Professional ($199/mo): {metrics['subscription_breakdown']['professional']}
Enterprise ($999/mo): {metrics['subscription_breakdown']['enterprise']}

🎯 TARGET PROGRESS
Month 1 Target (${self.targets['month_1_mrr']:,}): {metrics['target_progress']['month_1_mrr']['percentage']:.1f}%
Month 3 Target (${self.targets['month_3_mrr']:,}): {metrics['target_progress']['month_3_mrr']['percentage']:.1f}%
Year 1 ARR Target (${self.targets['year_1_arr']:,}): {metrics['target_progress']['year_1_arr']['percentage']:.1f}%

📈 GROWTH METRICS
New Revenue (30d): ${metrics['growth_metrics'].get('new_revenue_30d', 0):,.2f}
New Customers (30d): {metrics['growth_metrics'].get('new_customers_30d', 0)}
Avg Revenue Per Customer: ${metrics['growth_metrics'].get('avg_revenue_per_customer', 0):,.2f}
Estimated Conversion Rate: {metrics['growth_metrics'].get('conversion_rate', 0)}%

🎉 NEXT MILESTONES
To reach Month 1 target: {max(0, metrics['target_progress']['month_1_mrr']['remaining'] / 199)} more Professional customers
To reach Month 3 target: {max(0, metrics['target_progress']['month_3_mrr']['remaining'] / 199)} more Professional customers

🔗 UPGRADE LINK
Professional Tier: https://dashboard.stripe.com/payment-links/plink_1RsjbNG3Q24y5lVvscfhtzSX
"""
        
        return report
    
    def track_conversion_event(self, event_type: str, user_id: str = None, metadata: Dict = None):
        """Track conversion events for analytics"""
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,  # 'signup', 'upgrade_prompt', 'payment_complete'
            'user_id': user_id,
            'metadata': metadata or {}
        }
        
        # Log to file for analysis
        with open('conversion_events.jsonl', 'a') as f:
            f.write(json.dumps(event_data) + '\n')
    
    def get_pypi_stats(self) -> Dict:
        """Get PyPI download statistics (placeholder for integration)"""
        # This would integrate with PyPI stats API
        # For now, return placeholder data
        return {
            'total_downloads': 1500,  # Estimated
            'downloads_last_30d': 800,
            'downloads_last_7d': 250
        }

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ODIN Protocol Revenue Tracker')
    parser.add_argument('--report', action='store_true', help='Generate revenue report')
    parser.add_argument('--json', action='store_true', help='Output metrics as JSON')
    parser.add_argument('--track-event', help='Track conversion event')
    
    args = parser.parse_args()
    
    tracker = OdinRevenueTracker()
    
    if args.report:
        print(tracker.generate_revenue_report())
    elif args.json:
        metrics = tracker.get_current_metrics()
        print(json.dumps(metrics, indent=2))
    elif args.track_event:
        tracker.track_conversion_event(args.track_event)
        print(f"✅ Tracked event: {args.track_event}")
    else:
        # Default: show current metrics
        print(tracker.generate_revenue_report())

if __name__ == "__main__":
    main()
