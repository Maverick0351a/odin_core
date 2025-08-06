"""
ODIN Protocol - India Market Examples
Demonstrating AI coordination for major Indian industries
"""

# Example 1: UPI Payment System Coordination
def upi_payment_coordination():
    """Coordinate multiple AI agents for UPI fraud detection"""
    from odin_sdk import OdinClient
    from hel_mediator_ai import create_hel_mediator_ai
    
    # Initialize for Indian financial sector
    mediator = create_hel_mediator_ai(
        region='india',
        compliance=['rbi_guidelines', 'digital_india'],
        language='hindi'
    )
    client = OdinClient()
    
    # UPI transaction analysis
    transaction_data = {
        'amount': 50000,  # INR
        'source_bank': 'SBI',
        'dest_bank': 'HDFC',
        'merchant_category': 'e-commerce',
        'user_location': 'Mumbai'
    }
    
    # Create AI coordination message
    message = client.create_message()\
        .set_ids("upi-fraud-check", "payment-session", "fraud-ai", "approval-ai")\
        .set_content(f"Analyze UPI transaction: {transaction_data}")\
        .add_metadata("industry", "fintech")\
        .add_metadata("regulation", "RBI_compliant")\
        .add_metadata("language", "hindi")\
        .build()
    
    # Coordinate fraud detection + approval AIs
    result = mediator.evaluate_message(message)
    
    return {
        'approval_status': result.action_taken,
        'risk_score': result.confidence,
        'processing_time_ms': result.processing_time_ms,
        'compliance_check': 'RBI_approved'
    }

# Example 2: Telemedicine Rural Healthcare
def rural_healthcare_coordination():
    """Coordinate AI agents for rural telemedicine in India"""
    from odin_sdk import OdinClient
    
    client = OdinClient(region='india')
    
    # Rural patient data
    patient_data = {
        'location': 'Village in Rajasthan',
        'symptoms': ['बुखार', 'खांसी', 'सिरदर्द'],  # Fever, cough, headache in Hindi
        'language': 'hindi',
        'nearest_hospital_km': 50,
        'connectivity': 'low_bandwidth'
    }
    
    # Coordinate diagnostic AI + prescription AI + local pharmacy AI
    message = client.create_message()\
        .set_ids("rural-health", "telemedicine", "diagnostic-ai", "prescription-ai")\
        .set_content(f"Rural patient consultation: {patient_data}")\
        .add_metadata("healthcare_type", "telemedicine")\
        .add_metadata("region", "rural_india")\
        .add_metadata("language", "hindi")\
        .build()
    
    return message

# Example 3: EdTech Regional Language Learning
def edtech_multilingual_coordination():
    """Coordinate AI for Indian EdTech with regional languages"""
    from odin_sdk import OdinClient
    
    client = OdinClient()
    
    # Student learning data
    student_profile = {
        'grade': 8,
        'primary_language': 'tamil',
        'subject': 'mathematics',
        'learning_style': 'visual',
        'location': 'Chennai',
        'device': 'smartphone'
    }
    
    # Coordinate content AI + translation AI + assessment AI
    message = client.create_message()\
        .set_ids("edtech-coord", "learning-session", "content-ai", "assessment-ai")\
        .set_content(f"Personalized learning for: {student_profile}")\
        .add_metadata("education_board", "tamil_nadu")\
        .add_metadata("primary_language", "tamil")\
        .add_metadata("secondary_language", "english")\
        .build()
    
    return message

# Example 4: E-commerce Recommendation Engine (Flipkart-style)
def ecommerce_recommendation_coordination():
    """Coordinate AI agents for Indian e-commerce recommendations"""
    from odin_sdk import OdinClient
    
    client = OdinClient()
    
    # Indian customer data
    customer_data = {
        'location': 'Pune',
        'festival_season': 'diwali',
        'price_sensitivity': 'high',
        'categories': ['electronics', 'clothing', 'home_decor'],
        'payment_preference': 'upi',
        'language': 'marathi'
    }
    
    # Coordinate recommendation AI + inventory AI + pricing AI
    message = client.create_message()\
        .set_ids("ecom-recom", "shopping-session", "recommend-ai", "inventory-ai")\
        .set_content(f"Festival shopping recommendations: {customer_data}")\
        .add_metadata("festival", "diwali")\
        .add_metadata("region", "maharashtra")\
        .add_metadata("market_segment", "value_conscious")\
        .build()
    
    return message

# Example 5: Manufacturing Quality Control (Tata Steel style)
def manufacturing_quality_coordination():
    """Coordinate AI for Indian manufacturing quality control"""
    from odin_sdk import OdinClient
    
    client = OdinClient()
    
    # Manufacturing data
    production_data = {
        'plant_location': 'Jamshedpur',
        'product_type': 'steel_grade_50',
        'batch_size': 1000,
        'temperature': 1650,  # Celsius
        'quality_parameters': ['tensile_strength', 'carbon_content', 'surface_finish'],
        'shift': 'night',
        'operator_experience': 'experienced'
    }
    
    # Coordinate quality AI + predictive maintenance AI + compliance AI
    message = client.create_message()\
        .set_ids("quality-check", "production-batch", "quality-ai", "maintenance-ai")\
        .set_content(f"Quality control analysis: {production_data}")\
        .add_metadata("industry", "steel_manufacturing")\
        .add_metadata("compliance", "bis_standards")\
        .add_metadata("location", "jharkhand")\
        .build()
    
    return message

# Example 6: Startup MVP Rapid Development
def startup_mvp_coordination():
    """Coordinate AI for Indian startup MVP development"""
    from odin_sdk import OdinClient
    
    client = OdinClient()
    
    # Startup requirements
    startup_data = {
        'industry': 'food_delivery',
        'target_market': 'tier_2_cities',
        'budget': 'limited',
        'timeline': '3_months',
        'team_size': 5,
        'tech_stack': ['python', 'react', 'postgresql'],
        'funding_stage': 'pre_seed'
    }
    
    # Coordinate development AI + testing AI + deployment AI
    message = client.create_message()\
        .set_ids("startup-mvp", "dev-sprint", "code-ai", "test-ai")\
        .set_content(f"MVP development coordination: {startup_data}")\
        .add_metadata("startup_ecosystem", "indian")\
        .add_metadata("cost_optimization", "aggressive")\
        .add_metadata("speed_priority", "high")\
        .build()
    
    return message

# India-specific configuration
INDIA_CONFIG = {
    'regions': {
        'north': ['delhi', 'gurugram', 'noida', 'chandigarh'],
        'south': ['bangalore', 'hyderabad', 'chennai', 'kochi'],
        'west': ['mumbai', 'pune', 'ahmedabad', 'surat'],
        'east': ['kolkata', 'bhubaneswar', 'guwahati']
    },
    'languages': {
        'primary': ['hindi', 'english'],
        'regional': ['tamil', 'telugu', 'marathi', 'gujarati', 'bengali', 'kannada', 'malayalam']
    },
    'compliance': {
        'financial': ['rbi_guidelines', 'sebi_regulations'],
        'healthcare': ['clinical_research_guidelines', 'ayush_compliance'],
        'technology': ['digital_india_guidelines', 'cert_in_standards'],
        'data': ['personal_data_protection_bill', 'aadhaar_regulations']
    },
    'pricing': {
        'currency': 'INR',
        'tax': 'gst_18_percent',
        'payment_methods': ['upi', 'net_banking', 'credit_card', 'debit_card'],
        'billing_cycle': ['monthly', 'quarterly', 'annual'],
        'startup_discount': 50,  # 50% discount for registered startups
        'global_university_program': {
            'discount': 100,  # FREE for universities worldwide
            'requirements': [
                'research_data_opt_in',
                'mandatory_travis_johnson_citation', 
                'academic_publication_sharing',
                'anonymous_use_case_contribution'
            ],
            'citation_format': 'Johnson, T.J. (2025). ODIN Protocol: Heuristic-Empowered Logic System for AI-to-AI Communication. DOI: 10.1000/odin-protocol',
            'shared_data': [
                'anonymous_performance_metrics',
                'aggregated_usage_patterns',
                'anonymized_success_cases', 
                'comparative_benchmarks'
            ]
        }
    }
}

# Demo function showcasing Indian use cases
def demo_indian_ai_coordination():
    """Demonstrate ODIN Protocol for various Indian industries"""
    
    print("🇮🇳 ODIN Protocol - India Market Demonstration")
    print("=" * 60)
    
    # Test all Indian industry examples
    examples = [
        ("UPI Payment Fraud Detection", upi_payment_coordination),
        ("Rural Healthcare Telemedicine", rural_healthcare_coordination),
        ("EdTech Multilingual Learning", edtech_multilingual_coordination),
        ("E-commerce Recommendations", ecommerce_recommendation_coordination),
        ("Manufacturing Quality Control", manufacturing_quality_coordination),
        ("Startup MVP Development", startup_mvp_coordination)
    ]
    
    for name, example_func in examples:
        print(f"\n🔍 Testing: {name}")
        try:
            result = example_func()
            if isinstance(result, dict):
                print(f"✅ Success: {result}")
            else:
                print(f"✅ Message created: {result.trace_id}")
        except Exception as e:
            print(f"⚠️ Demo mode: {e}")
        print("-" * 40)
    
    print(f"\n💰 India Pricing Tiers:")
    print(f"🆓 Community: Free (1K API calls/month)")
    print(f"🚀 Startup: ₹999/month ($12) - 50K calls")
    print(f"🏢 Professional: ₹4,149/month ($50) - 500K calls")
    print(f"🏭 Enterprise: ₹8,299/month ($99) - Unlimited")
    print(f"\n🎓 Global University Program:")
    print(f"🌍 FREE for all universities worldwide")
    print(f"📊 Requirements: Research data opt-in + Mandatory citation")
    print(f"� Citation: 'Johnson, T.J. (2025). ODIN Protocol: HEL System for AI Communication'")
    print(f"🔬 Benefits: Full access + Research data + Publications")
    print(f"🚀 Registered Startups: 50% off for first year")
    print(f"🏛️ Government/PSU: Custom pricing available")

if __name__ == "__main__":
    demo_indian_ai_coordination()
