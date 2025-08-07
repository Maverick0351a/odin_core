"""
ODIN Protocol - Billing API Server
Flask application for handling Stripe payments and usage tracking
"""

from flask import Flask, request, jsonify, render_template_string
import stripe
import os
import json
import logging
from datetime import datetime
from billing_system import OdinBillingSystem

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'odin-protocol-dev-key')

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # You need to set this
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')  # You need to set this

# Initialize billing system
billing = OdinBillingSystem()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def billing_dashboard():
    """Simple billing dashboard"""
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ODIN Protocol - Billing Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }
            .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
            .pricing-card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; text-align: center; }
            .pricing-card.popular { border-color: #007acc; background: #f0f8ff; }
            .price { font-size: 2em; color: #007acc; font-weight: bold; }
            .features { list-style: none; padding: 0; }
            .features li { padding: 5px 0; }
            .btn { background: #007acc; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #005a9c; }
            .contact-info { background: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🚀 ODIN Protocol - Johnson Technologies</h1>
            <p><strong>AI-to-AI Communication Infrastructure</strong> | Trusted by enterprises worldwide</p>
            
            <h2>💰 Pricing Plans</h2>
            <div class="pricing-grid">
                <div class="pricing-card">
                    <h3>🆓 Community</h3>
                    <div class="price">$0<small>/month</small></div>
                    <ul class="features">
                        <li>✅ 1,000 API calls/month</li>
                        <li>✅ Basic AI coordination</li>
                        <li>✅ Community support</li>
                        <li>✅ Perfect for testing</li>
                    </ul>
                    <button class="btn" onclick="alert('Sign up at PyPI: pip install odin_protocol')">Get Started</button>
                </div>
                
                <div class="pricing-card popular">
                    <h3>🚀 Startup</h3>
                    <div class="price">$9<small>/month</small></div>
                    <ul class="features">
                        <li>✅ 50,000 API calls/month</li>
                        <li>✅ All basic features</li>
                        <li>✅ Email support</li>
                        <li>✅ API access</li>
                        <li>✅ Brazil: R$49/month</li>
                    </ul>
                    <button class="btn" onclick="subscribeTo('startup')">Subscribe Now</button>
                </div>
                
                <div class="pricing-card">
                    <h3>🏢 Professional</h3>
                    <div class="price">$39<small>/month</small></div>
                    <ul class="features">
                        <li>✅ 500,000 API calls/month</li>
                        <li>✅ All startup features</li>
                        <li>✅ Priority support</li>
                        <li>✅ Analytics dashboard</li>
                        <li>✅ Brazil: R$199/month</li>
                    </ul>
                    <button class="btn" onclick="subscribeTo('professional')">Subscribe Now</button>
                </div>
                
                <div class="pricing-card">
                    <h3>🏭 Enterprise</h3>
                    <div class="price">$79<small>/month</small></div>
                    <ul class="features">
                        <li>✅ Unlimited API calls</li>
                        <li>✅ All professional features</li>
                        <li>✅ Dedicated support</li>
                        <li>✅ Custom integrations</li>
                        <li>✅ Brazil: R$399/month</li>
                    </ul>
                    <button class="btn" onclick="subscribeTo('enterprise')">Subscribe Now</button>
                </div>
            </div>
            
            <h2>🎓 University Research Program</h2>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                <h3>100% FREE for Universities Worldwide!</h3>
                <p>✅ Unlimited API access for academic research</p>
                <p>✅ Required citation: "Johnson, T.J. (2025). ODIN Protocol: HEL System"</p>
                <p>✅ Research collaboration opportunities</p>
                <button class="btn" onclick="universitySignup()">Apply for University Access</button>
            </div>
            
            <div class="contact-info">
                <h3>📞 Contact Information</h3>
                <p><strong>Billing Support:</strong> travjohnson831@gmail.com</p>
                <p><strong>Enterprise Sales:</strong> odinprotocol@outlook.com</p>
                <p><strong>Company:</strong> Johnson Technologies (USA)</p>
                <p><strong>CEO:</strong> Travis Jacob Johnson</p>
            </div>
        </div>
        
        <script>
            function subscribeTo(tier) {
                // This would integrate with Stripe Checkout
                alert(`Redirecting to Stripe Checkout for ${tier} plan...`);
                // window.location.href = `/checkout/${tier}`;
            }
            
            function universitySignup() {
                alert('University signup: Please email travjohnson831@gmail.com with your academic credentials');
            }
        </script>
    </body>
    </html>
    """
    return dashboard_html

@app.route('/checkout/<tier>')
def create_checkout_session(tier):
    """Create Stripe checkout session"""
    
    if tier not in billing.pricing_tiers:
        return jsonify({'error': 'Invalid pricing tier'}), 400
    
    try:
        # Get price info
        tier_info = billing.pricing_tiers[tier]
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"ODIN Protocol {tier_info['name']}",
                        'description': 'AI-to-AI Communication Infrastructure',
                    },
                    'unit_amount': tier_info['price_usd'] * 100,  # Stripe uses cents
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.url_root + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.url_root + 'cancel',
            metadata={
                'tier': tier,
                'billing_contact': 'travjohnson831@gmail.com'
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        result = billing.handle_webhook(event)
        
        logger.info(f"Webhook processed: {event['type']} -> {result}")
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

@app.route('/api/usage/<customer_id>')
def get_usage(customer_id):
    """Get usage statistics for a customer"""
    
    try:
        usage_data = billing.generate_usage_report(customer_id)
        return jsonify(usage_data)
    except Exception as e:
        logger.error(f"Usage lookup error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-customer', methods=['POST'])
def create_customer():
    """Create a new customer"""
    
    data = request.json
    
    try:
        customer_id = billing.create_customer(
            email=data['email'],
            name=data['name'],
            region=data.get('region', 'US'),
            company=data.get('company'),
            university=data.get('university', False)
        )
        
        return jsonify({'customer_id': customer_id})
        
    except Exception as e:
        logger.error(f"Customer creation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/success')
def payment_success():
    """Payment success page"""
    return """
    <h1>🎉 Payment Successful!</h1>
    <p>Welcome to ODIN Protocol!</p>
    <p>You can now use your API key to access our services.</p>
    <p>Questions? Contact: travjohnson831@gmail.com</p>
    """

@app.route('/cancel')
def payment_cancel():
    """Payment cancelled page"""
    return """
    <h1>Payment Cancelled</h1>
    <p>No worries! You can always subscribe later.</p>
    <p>Try our free tier: pip install odin_protocol</p>
    """

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'odin-protocol-billing',
        'company': 'Johnson Technologies (USA)',
        'contact': 'travjohnson831@gmail.com'
    })

if __name__ == '__main__':
    print("🏦 ODIN Protocol Billing Server Starting...")
    print("=" * 50)
    print("🌍 Dashboard: http://localhost:5000")
    print("💳 Billing Contact: travjohnson831@gmail.com")
    print("🏢 Johnson Technologies (USA)")
    print("")
    print("⚠️ REQUIRED ENVIRONMENT VARIABLES:")
    print("   STRIPE_SECRET_KEY=sk_live_... (or sk_test_... for testing)")
    print("   STRIPE_WEBHOOK_SECRET=whsec_...")
    print("   FLASK_SECRET_KEY=your-secret-key")
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
