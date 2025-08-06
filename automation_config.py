#!/usr/bin/env python3
"""
ODIN Protocol Automation Configuration
Central configuration for all automation systems
"""

import os
from typing import Dict, List, Any

class AutomationConfig:
    """Central configuration for ODIN Protocol automation"""
    
    def __init__(self):
        self.load_environment_variables()
        
    def load_environment_variables(self):
        """Load configuration from environment variables"""
        # Stripe configuration
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        
        # Social media API keys (when ready to connect)
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        self.twitter_api_secret = os.getenv('TWITTER_API_SECRET')
        self.twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.linkedin_api_key = os.getenv('LINKEDIN_API_KEY')
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        # Email configuration
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'team@odinprotocol.com')
        
        # Discord webhook for notifications
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK')
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'your-username/odin-protocol')
    
    def get_social_media_config(self) -> Dict[str, Dict]:
        """Get social media platform configurations"""
        return {
            'twitter': {
                'enabled': bool(self.twitter_api_key),
                'character_limit': 280,
                'hashtag_limit': 5,
                'optimal_times': ['09:00', '14:00', '18:00'],
                'daily_limit': 3,
                'api_config': {
                    'api_key': self.twitter_api_key,
                    'api_secret': self.twitter_api_secret,
                    'access_token': self.twitter_access_token,
                    'access_token_secret': self.twitter_access_token_secret
                }
            },
            'linkedin': {
                'enabled': bool(self.linkedin_api_key),
                'character_limit': 3000,
                'hashtag_limit': 10,
                'optimal_times': ['08:00', '12:00', '17:00'],
                'daily_limit': 2,
                'api_config': {
                    'api_key': self.linkedin_api_key
                }
            },
            'reddit': {
                'enabled': bool(self.reddit_client_id),
                'subreddits': ['MachineLearning', 'artificial', 'programming', 'startups'],
                'optimal_times': ['10:00', '15:00', '20:00'],
                'daily_limit': 1,
                'api_config': {
                    'client_id': self.reddit_client_id,
                    'client_secret': self.reddit_client_secret
                }
            },
            'hackernews': {
                'enabled': True,  # No API key needed for basic posting
                'post_types': ['Show HN', 'Ask HN', 'discussion'],
                'optimal_times': ['09:00'],  # PST
                'daily_limit': 1
            }
        }
    
    def get_enterprise_targets(self) -> List[Dict]:
        """Get enterprise outreach target companies"""
        return [
            {
                'company': 'OpenAI',
                'contact': 'partnerships@openai.com',
                'focus': 'Multi-agent coordination at scale',
                'pain_point': 'Managing GPT-4 agent communication',
                'value_prop': 'Reduce coordination overhead by 80%',
                'priority': 'high',
                'contacted': False
            },
            {
                'company': 'Anthropic',
                'contact': 'business@anthropic.com', 
                'focus': 'Claude model integration',
                'pain_point': 'Standardizing AI-to-AI protocols',
                'value_prop': 'First standardized protocol for AI communication',
                'priority': 'high',
                'contacted': False
            },
            {
                'company': 'Mistral AI',
                'contact': 'contact@mistral.ai',
                'focus': 'European AI infrastructure',
                'pain_point': 'Self-healing communication systems',
                'value_prop': '99.9% uptime with automatic recovery',
                'priority': 'medium',
                'contacted': False
            },
            {
                'company': 'Cohere',
                'contact': 'partnerships@cohere.ai',
                'focus': 'Enterprise AI deployments',
                'pain_point': 'Custom business logic in AI systems',
                'value_prop': '100+ rule operators for business logic',
                'priority': 'medium',
                'contacted': False
            },
            {
                'company': 'Hugging Face',
                'contact': 'partnerships@huggingface.co',
                'focus': 'Open source AI ecosystem',
                'pain_point': 'Model interoperability',
                'value_prop': 'Plugin system for unlimited customization',
                'priority': 'high',
                'contacted': False
            }
        ]
    
    def get_automation_schedule(self) -> Dict[str, List[str]]:
        """Get automation scheduling configuration"""
        return {
            'social_media_posting': [
                '09:00',  # Morning engagement
                '14:00',  # Lunch break browsing
                '18:00'   # Evening commute
            ],
            'enterprise_outreach': [
                'monday:10:00',
                'wednesday:10:00', 
                'friday:10:00'
            ],
            'revenue_tracking': [
                'hourly'  # Check revenue every hour
            ],
            'github_management': [
                '08:00'  # Daily morning update
            ],
            'content_generation': [
                '06:00'  # Generate fresh content early
            ]
        }
    
    def get_content_templates(self) -> Dict[str, List[Dict]]:
        """Get content templates for automation"""
        return {
            'launch_posts': [
                {
                    'platform': 'twitter',
                    'template': """🚀 {announcement}

✅ FREE: 10K AI messages/month  
💼 PRO: $199/mo - 100K messages + analytics
🏢 ENTERPRISE: $999/mo - unlimited + support

{call_to_action}

pip install odin-protocol
{payment_link}

{hashtags}""",
                    'variables': {
                        'announcement': 'ODIN Protocol is LIVE with pricing!',
                        'call_to_action': 'Perfect for AI startups scaling communication.',
                        'payment_link': 'https://dashboard.stripe.com/payment-links/plink_1RsjbNG3Q24y5lVvscfhtzSX',
                        'hashtags': '#AI #Startup #Revenue #SaaS #TechLaunch'
                    }
                }
            ],
            'technical_posts': [
                {
                    'platform': 'twitter',
                    'template': """🧵 Thread: {topic}

{problem_statement}

{solution_preview}

{call_to_action}

{hashtags}""",
                    'variables': {
                        'topic': 'Why AI systems need standardized communication protocols',
                        'problem_statement': 'Most AI agents use ad-hoc communication methods, leading to 40% more development time...',
                        'solution_preview': 'ODIN Protocol solves this with TCP/IP-like standardization...',
                        'call_to_action': 'Try free: pip install odin-protocol',
                        'hashtags': '#AI #TechSolutions #Innovation'
                    }
                }
            ],
            'value_props': [
                {
                    'platform': 'linkedin',
                    'template': """💡 {pain_point}

{solution_benefits}

{customer_proof}

{call_to_action}

{hashtags}""",
                    'variables': {
                        'pain_point': 'AI coordination problems costing your team time?',
                        'solution_benefits': 'ODIN Protocol reduces AI development overhead by 80%',
                        'customer_proof': 'Early customers report 99.9% uptime and 50% faster deployment',
                        'call_to_action': 'Ready to scale? Professional tier: $199/month',
                        'hashtags': '#AIInfrastructure #Enterprise #TechSolutions'
                    }
                }
            ]
        }
    
    def get_email_templates(self) -> Dict[str, str]:
        """Get email templates for enterprise outreach"""
        return {
            'initial_outreach': """Subject: 🚀 {focus} - ODIN Protocol Partnership Opportunity

Hi {company} Team,

I noticed {company}'s excellent work in {focus} and thought you'd be interested in ODIN Protocol - the first standardized AI-to-AI communication protocol.

**Specific value for {company}:**
• {value_prop}
• Solves your {pain_point} challenges
• Enterprise-ready with SOC2 compliance
• 30-day free trial for evaluation

**Real results from early customers:**
• 80% reduction in AI coordination overhead
• 99.9% uptime with automatic error recovery
• 50% faster multi-agent deployment

Would you be interested in a 15-minute technical demo this week?

Best regards,
ODIN Protocol Team

P.S. We're offering early enterprise customers custom deployment assistance and direct engineering support.

Try free: pip install odin-protocol
Enterprise demo: https://calendly.com/odin-protocol/enterprise-demo""",
            
            'followup_technical': """Subject: Technical Deep Dive: {focus} with ODIN Protocol

Hi {company} Team,

Following up on my previous email about ODIN Protocol's potential for {focus}.

I wanted to share some technical details that might be relevant:

**Architecture Benefits:**
• Protocol Buffers for efficient serialization
• Async/sync Python SDK for flexibility
• Plugin system for {company}-specific customizations
• Built-in security and compliance features

**Integration Approach:**
• Drop-in replacement for existing communication layers
• Gradual migration path with backward compatibility
• Custom rule engine for {company}'s business logic
• White-glove technical support during implementation

Would you like to schedule a technical deep-dive call? I can show you exactly how ODIN Protocol would integrate with your existing AI infrastructure.

Best regards,
ODIN Protocol Team""",
            
            'followup_roi': """Subject: ROI Analysis: {company} + ODIN Protocol

Hi {company} Team,

I've put together a quick ROI analysis for {company} implementing ODIN Protocol:

**Current Estimated Costs (based on industry averages):**
• 40% developer time on communication infrastructure
• 15% downtime from coordination failures
• Security and compliance overhead
• Custom protocol maintenance

**With ODIN Protocol:**
• 80% reduction in infrastructure development time
• 99.9% uptime with automatic error recovery
• Built-in enterprise security and compliance
• Zero maintenance overhead

**Estimated Annual Savings:** $200K - $500K
**Implementation Time:** 2-4 weeks
**ROI Timeline:** 30-60 days

Ready to discuss specifics for {company}?

Best regards,
ODIN Protocol Team"""
        }

# Global configuration instance
automation_config = AutomationConfig()
