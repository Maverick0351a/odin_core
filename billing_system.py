"""
ODIN Protocol - Stripe Billing Integration
Johnson Technologies (USA) - Revenue Management System
"""

import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # Set this in your environment

class OdinBillingSystem:
    """Complete billing system for ODIN Protocol with international support"""
    
    def __init__(self):
        self.pricing_tiers = {
            'free': {
                'name': 'Community Edition',
                'price_usd': 0,
                'calls_per_month': 1000,
                'features': ['Basic AI coordination', 'Community support']
            },
            'startup': {
                'name': 'Startup Package',
                'price_usd': 9,
                'calls_per_month': 50000,
                'features': ['All basic features', 'Email support', 'API access']
            },
            'professional': {
                'name': 'Professional',
                'price_usd': 39,
                'calls_per_month': 500000,
                'features': ['All startup features', 'Priority support', 'Analytics dashboard']
            },
            'enterprise': {
                'name': 'Enterprise',
                'price_usd': 79,
                'calls_per_month': -1,  # Unlimited
                'features': ['All professional features', 'Dedicated support', 'Custom integrations']
            }
        }
        
        # International pricing (conversion rates)
        self.regional_pricing = {
            'US': {'currency': 'usd', 'multiplier': 1.0},
            'BR': {'currency': 'brl', 'multiplier': 5.5},  # R$49 for $9 startup
            'DE': {'currency': 'eur', 'multiplier': 0.92}, # €10 for $9 startup  
            'IN': {'currency': 'inr', 'multiplier': 83.0}, # ₹999 for $12 startup
            'JP': {'currency': 'jpy', 'multiplier': 150.0} # ¥1500 for $10 startup
        }
    
    def create_stripe_products(self):
        """Create ODIN Protocol products in Stripe for all regions"""
        
        products_created = []
        
        for tier_id, tier_info in self.pricing_tiers.items():
            if tier_id == 'free':
                continue  # Skip free tier for Stripe
                
            # Create product for each region
            for region, regional_info in self.regional_pricing.items():
                try:
                    # Create product
                    product = stripe.Product.create(
                        name=f"ODIN Protocol {tier_info['name']} - {region}",
                        description=f"AI-to-AI Communication Infrastructure - {', '.join(tier_info['features'])}",
                        metadata={
                            'tier': tier_id,
                            'region': region,
                            'calls_per_month': str(tier_info['calls_per_month']),
                            'company': 'Johnson Technologies (USA)'
                        }
                    )
                    
                    # Calculate regional price
                    base_price = tier_info['price_usd']
                    regional_price = int(base_price * regional_info['multiplier'] * 100)  # Stripe uses cents
                    
                    # Create price
                    price = stripe.Price.create(
                        product=product.id,
                        unit_amount=regional_price,
                        currency=regional_info['currency'],
                        recurring={'interval': 'month'},
                        metadata={
                            'tier': tier_id,
                            'region': region,
                            'base_price_usd': str(base_price)
                        }
                    )
                    
                    products_created.append({
                        'product_id': product.id,
                        'price_id': price.id,
                        'tier': tier_id,
                        'region': region,
                        'amount': regional_price,
                        'currency': regional_info['currency']
                    })
                    
                    print(f"✅ Created {tier_info['name']} for {region}: {regional_price/100} {regional_info['currency'].upper()}")
                    
                except stripe.error.StripeError as e:
                    print(f"❌ Error creating {tier_id} for {region}: {e}")
        
        return products_created
    
    def create_customer(self, email: str, name: str, region: str = 'US', 
                       company: Optional[str] = None, university: bool = False) -> str:
        """Create a new customer in Stripe"""
        
        metadata = {
            'region': region,
            'university': str(university),
            'created_via': 'odin_protocol_sdk'
        }
        
        if company:
            metadata['company'] = company
            
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata,
                description=f"ODIN Protocol customer from {region}"
            )
            
            print(f"✅ Created customer: {name} ({email}) in {region}")
            return customer.id
            
        except stripe.error.StripeError as e:
            print(f"❌ Error creating customer: {e}")
            return None
    
    def create_subscription(self, customer_id: str, tier: str, region: str = 'US') -> Dict:
        """Create a subscription for a customer"""
        
        # Get the price ID for this tier and region
        price_id = self.get_price_id(tier, region)
        if not price_id:
            return {'error': f'Price not found for {tier} in {region}'}
        
        try:
            # Special handling for university customers (free)
            metadata = {
                'tier': tier,
                'region': region,
                'billing_contact': 'travjohnson831@gmail.com'
            }
            
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata,
                collection_method='charge_automatically'
            )
            
            return {
                'subscription_id': subscription.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end
            }
            
        except stripe.error.StripeError as e:
            return {'error': str(e)}
    
    def get_price_id(self, tier: str, region: str) -> Optional[str]:
        """Get Stripe price ID for a specific tier and region"""
        # This would normally query your database or Stripe directly
        # For now, return a placeholder - you'll need to store these after creation
        price_mapping = {
            ('startup', 'US'): 'price_startup_us',
            ('startup', 'BR'): 'price_startup_br',
            ('professional', 'US'): 'price_professional_us',
            ('enterprise', 'US'): 'price_enterprise_us'
        }
        return price_mapping.get((tier, region))
    
    def handle_webhook(self, event_data: Dict) -> Dict:
        """Handle Stripe webhook events"""
        
        event_type = event_data.get('type')
        
        if event_type == 'invoice.payment_succeeded':
            return self.handle_payment_succeeded(event_data['data']['object'])
        elif event_type == 'invoice.payment_failed':
            return self.handle_payment_failed(event_data['data']['object'])
        elif event_type == 'customer.subscription.deleted':
            return self.handle_subscription_cancelled(event_data['data']['object'])
        
        return {'status': 'ignored', 'event_type': event_type}
    
    def handle_payment_succeeded(self, invoice: Dict) -> Dict:
        """Handle successful payment"""
        customer_id = invoice['customer']
        amount_paid = invoice['amount_paid'] / 100  # Convert from cents
        
        # Reset customer's API usage for the new billing period
        self.reset_customer_usage(customer_id)
        
        print(f"✅ Payment succeeded: Customer {customer_id} paid {amount_paid}")
        return {'status': 'processed', 'action': 'usage_reset'}
    
    def handle_payment_failed(self, invoice: Dict) -> Dict:
        """Handle failed payment"""
        customer_id = invoice['customer']
        
        # Downgrade customer to free tier or suspend service
        self.suspend_customer_service(customer_id)
        
        print(f"❌ Payment failed: Customer {customer_id} service suspended")
        return {'status': 'processed', 'action': 'service_suspended'}
    
    def reset_customer_usage(self, customer_id: str):
        """Reset API call count for new billing period"""
        # This would update your usage tracking database
        print(f"🔄 Reset usage for customer: {customer_id}")
    
    def suspend_customer_service(self, customer_id: str):
        """Suspend service for non-payment"""
        # This would update customer status in your database
        print(f"⏸️ Suspended service for customer: {customer_id}")
    
    def generate_usage_report(self, customer_id: str) -> Dict:
        """Generate usage report for a customer"""
        # This would query your usage tracking system
        return {
            'customer_id': customer_id,
            'current_period_calls': 15420,
            'limit': 50000,
            'overage': False,
            'cost_this_period': 9.00
        }

def setup_billing_system():
    """Initialize the complete ODIN Protocol billing system"""
    
    print("🏦 SETTING UP ODIN PROTOCOL BILLING SYSTEM")
    print("=" * 50)
    
    billing = OdinBillingSystem()
    
    print("📊 Pricing Tiers:")
    for tier_id, tier_info in billing.pricing_tiers.items():
        print(f"  {tier_info['name']}: ${tier_info['price_usd']}/month ({tier_info['calls_per_month']} calls)")
    
    print("\n🌍 Regional Pricing:")
    for region, info in billing.regional_pricing.items():
        startup_price = 9 * info['multiplier']
        symbol = {'usd': '$', 'brl': 'R$', 'eur': '€', 'inr': '₹', 'jpy': '¥'}.get(info['currency'], '')
        print(f"  {region}: {symbol}{startup_price:.0f} {info['currency'].upper()}")
    
    print("\n🔧 Next Steps:")
    print("1. Set STRIPE_SECRET_KEY environment variable")
    print("2. Run billing.create_stripe_products() to set up products")
    print("3. Configure webhook endpoint: /webhook/stripe")
    print("4. Test with stripe.api_key = 'sk_test_...'")
    
    return billing

if __name__ == "__main__":
    # Demo the billing system
    billing_system = setup_billing_system()
    
    print(f"\n💳 BILLING CONTACT: travjohnson831@gmail.com")
    print(f"🏢 COMPANY: Johnson Technologies (USA)")
    print(f"🎯 REVENUE TARGET: $5M+ through international expansion")
