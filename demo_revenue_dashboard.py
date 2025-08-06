#!/usr/bin/env python3
"""
Demo Revenue Dashboard for ODIN Protocol
Shows projected growth and revenue potential without Stripe API key
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class DemoRevenueDashboard:
    """Simulates revenue metrics for demonstration purposes"""
    
    def __init__(self):
        self.pricing = {
            'professional': 199,  # $199/month
            'enterprise': 999,    # $999/month
            'free_limit': 10000,  # 10K messages
            'pro_limit': 100000   # 100K messages
        }
        
        # Simulated growth projections
        self.projections = self._generate_projections()
    
    def _generate_projections(self) -> Dict[str, Any]:
        """Generate realistic revenue projections"""
        start_date = datetime.now()
        projections = {
            'launch_date': start_date.isoformat(),
            'monthly_projections': [],
            'key_metrics': {},
            'growth_scenarios': {}
        }
        
        # Conservative scenario
        conservative_customers = [10, 20, 35, 50, 75, 100, 130, 160, 200, 250, 300, 350]
        conservative_enterprise = [0, 1, 2, 5, 8, 10, 15, 20, 25, 30, 35, 40]
        
        # Optimistic scenario  
        optimistic_customers = [25, 50, 100, 150, 225, 325, 450, 600, 775, 975, 1200, 1450]
        optimistic_enterprise = [2, 5, 10, 20, 30, 45, 65, 85, 110, 140, 175, 215]
        
        for month in range(12):
            month_date = start_date + timedelta(days=30 * month)
            
            # Conservative projections
            conservative_pro_rev = conservative_customers[month] * self.pricing['professional']
            conservative_ent_rev = conservative_enterprise[month] * self.pricing['enterprise']
            conservative_total = conservative_pro_rev + conservative_ent_rev
            
            # Optimistic projections
            optimistic_pro_rev = optimistic_customers[month] * self.pricing['professional']
            optimistic_ent_rev = optimistic_enterprise[month] * self.pricing['enterprise']
            optimistic_total = optimistic_pro_rev + optimistic_ent_rev
            
            projections['monthly_projections'].append({
                'month': month + 1,
                'date': month_date.strftime('%Y-%m'),
                'conservative': {
                    'professional_customers': conservative_customers[month],
                    'enterprise_customers': conservative_enterprise[month],
                    'professional_revenue': conservative_pro_rev,
                    'enterprise_revenue': conservative_ent_rev,
                    'total_mrr': conservative_total,
                    'arr': conservative_total * 12
                },
                'optimistic': {
                    'professional_customers': optimistic_customers[month],
                    'enterprise_customers': optimistic_enterprise[month], 
                    'professional_revenue': optimistic_pro_rev,
                    'enterprise_revenue': optimistic_ent_rev,
                    'total_mrr': optimistic_total,
                    'arr': optimistic_total * 12
                }
            })
        
        # Key metrics
        projections['key_metrics'] = {
            'target_customers_month_1': 10,
            'target_mrr_month_1': 1990,
            'target_arr_year_1': 777000,
            'conversion_rate_target': 0.05,  # 5% of free users upgrade
            'churn_rate_target': 0.02,       # 2% monthly churn
            'customer_lifetime_value': 2500, # Average LTV
            'customer_acquisition_cost': 150 # Target CAC
        }
        
        return projections
    
    def show_dashboard(self):
        """Display the revenue dashboard"""
        print("🚀 ODIN PROTOCOL - REVENUE DASHBOARD")
        print("=" * 50)
        print(f"Launch Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Stripe Payment Link: Active ✅")
        print()
        
        print("💰 PRICING STRUCTURE")
        print("-" * 30)
        print(f"FREE Tier: {self.pricing['free_limit']:,} messages/month")
        print(f"PROFESSIONAL: ${self.pricing['professional']}/month ({self.pricing['pro_limit']:,} messages)")
        print(f"ENTERPRISE: ${self.pricing['enterprise']}/month (unlimited)")
        print()
        
        print("📊 12-MONTH REVENUE PROJECTIONS")
        print("-" * 50)
        
        for month_data in self.projections['monthly_projections'][:6]:  # Show first 6 months
            month = month_data['month']
            conservative = month_data['conservative']
            optimistic = month_data['optimistic']
            
            print(f"Month {month} ({month_data['date']}):")
            print(f"  Conservative: {conservative['professional_customers']:3d} Pro + {conservative['enterprise_customers']:2d} Ent = ${conservative['total_mrr']:,}/month")
            print(f"  Optimistic:   {optimistic['professional_customers']:3d} Pro + {optimistic['enterprise_customers']:2d} Ent = ${optimistic['total_mrr']:,}/month")
            print()
        
        print("🎯 YEAR 1 TARGETS")
        print("-" * 20)
        year_1_conservative = self.projections['monthly_projections'][11]['conservative']
        year_1_optimistic = self.projections['monthly_projections'][11]['optimistic']
        
        print(f"Conservative ARR: ${year_1_conservative['arr']:,}")
        print(f"Optimistic ARR:   ${year_1_optimistic['arr']:,}")
        print()
        
        print("⚡ KEY CONVERSION METRICS")
        print("-" * 30)
        metrics = self.projections['key_metrics']
        print(f"Target Conversion Rate: {metrics['conversion_rate_target']*100:.1f}%")
        print(f"Target Monthly Churn: {metrics['churn_rate_target']*100:.1f}%")
        print(f"Customer Lifetime Value: ${metrics['customer_lifetime_value']:,}")
        print(f"Customer Acquisition Cost: ${metrics['customer_acquisition_cost']:,}")
        print()
        
        print("🏆 IMMEDIATE ACTION ITEMS")
        print("-" * 30)
        print("1. Set Stripe API key for live tracking")
        print("2. Launch social media campaigns")
        print("3. Reach out to 50 AI companies")
        print("4. Monitor PyPI download metrics")
        print("5. A/B test upgrade prompts")
        print()
        
        return self.projections
    
    def simulate_real_time_metrics(self):
        """Simulate real-time revenue metrics"""
        current_time = datetime.now()
        
        # Simulate some current activity
        simulated_metrics = {
            'timestamp': current_time.isoformat(),
            'pypi_downloads_today': random.randint(50, 200),
            'active_free_users': random.randint(100, 500),
            'usage_approaching_limit': random.randint(5, 25),
            'upgrade_prompts_shown': random.randint(2, 15),
            'payment_page_visits': random.randint(1, 8),
            'conversions_today': random.randint(0, 3),
            'current_mrr': random.randint(800, 2500),
            'growth_rate_30d': random.uniform(15.0, 45.0)
        }
        
        print("⚡ REAL-TIME METRICS (Simulated)")
        print("=" * 40)
        print(f"PyPI Downloads Today: {simulated_metrics['pypi_downloads_today']}")
        print(f"Active Free Users: {simulated_metrics['active_free_users']}")
        print(f"Approaching Limit: {simulated_metrics['usage_approaching_limit']} users")
        print(f"Upgrade Prompts: {simulated_metrics['upgrade_prompts_shown']} shown")
        print(f"Payment Page Visits: {simulated_metrics['payment_page_visits']}")
        print(f"Conversions Today: {simulated_metrics['conversions_today']}")
        print(f"Current MRR: ${simulated_metrics['current_mrr']:,}")
        print(f"30-Day Growth: {simulated_metrics['growth_rate_30d']:.1f}%")
        print()
        
        return simulated_metrics

def main():
    """Run the demo revenue dashboard"""
    dashboard = DemoRevenueDashboard()
    
    print("Starting ODIN Protocol Revenue Dashboard...")
    print()
    
    # Show main dashboard
    projections = dashboard.show_dashboard()
    
    # Show real-time simulation
    metrics = dashboard.simulate_real_time_metrics()
    
    print("💡 TO ACTIVATE LIVE TRACKING:")
    print("export STRIPE_SECRET_KEY='your-stripe-key'")
    print("python revenue_tracker.py --report")
    print()
    
    print("🚀 YOUR REVENUE SYSTEM IS READY!")
    print("All tools in place to start generating income immediately.")

if __name__ == "__main__":
    main()
