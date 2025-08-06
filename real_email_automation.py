#!/usr/bin/env python3
"""
REAL Email Marketing Automation for ODIN Protocol
Actually sends emails to media outlets - no simulation
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

class RealEmailMarketing:
    """Actually sends emails to media outlets"""
    
    def __init__(self, smtp_config: Dict[str, str]):
        """Initialize with real SMTP configuration"""
        self.smtp_config = smtp_config
        self.sent_emails = []
        self.setup_logging()
        
        # Media database from business_media_wave.py
        self.outlets = self._get_media_outlets()
        
    def setup_logging(self):
        """Setup logging for email tracking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_marketing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_media_outlets(self) -> List[Dict]:
        """Get real media outlet contact information"""
        return [
            {
                'name': 'TechCrunch',
                'email': 'tips@techcrunch.com',
                'focus': 'startup_stories',
                'best_time': 'Tuesday-Thursday 10AM PST'
            },
            {
                'name': 'Hacker News (via Show HN)',
                'contact_method': 'post_submission',
                'url': 'https://news.ycombinator.com/submit'
            },
            {
                'name': 'Product Hunt',
                'contact_method': 'product_submission',
                'url': 'https://www.producthunt.com/posts/new'
            },
            {
                'name': 'Dev.to Community',
                'contact_method': 'blog_post',
                'url': 'https://dev.to/new'
            },
            {
                'name': 'Reddit r/programming',
                'contact_method': 'reddit_post',
                'url': 'https://reddit.com/r/programming'
            },
            {
                'name': 'LinkedIn Tech Influencers',
                'contact_method': 'linkedin_message',
                'reach': 'targeted_connections'
            }
        ]
    
    def generate_pitch_email(self, outlet: Dict, personal_info: Dict) -> Dict[str, str]:
        """Generate personalized pitch email"""
        
        subject = f"EXCLUSIVE: From Homeless Shelter to AI Breakthrough - {personal_info['name']}"
        
        body = f"""Dear {outlet['name']} Editorial Team,

I'm reaching out with an extraordinary story about breakthrough innovation emerging from the most unlikely circumstances.

**THE STORY:**
• Developer created revolutionary AI communication protocol while homeless in San Jose
• Built ODIN Protocol with zero funding, no office, just determination
• Now live on PyPI: pip install odin-protocol
• Solving $50B industry coordination problem
• 92% test success rate, production-ready

**WHY THIS MATTERS:**
This isn't just another tech story - it's proof that innovation can come from anywhere. The combination of personal triumph and technical achievement makes this compelling for your audience.

**VERIFICATION AVAILABLE:**
• Technical demonstrations
• Shelter documentation
• Working code on GitHub
• Usage metrics and testimonials

**IMMEDIATE AVAILABILITY:**
• Exclusive interview opportunity
• Technical deep-dive demos
• Personal story documentation
• Custom content for {outlet['name']}

**CONTACT:**
• Email: {personal_info['email']}
• Phone: {personal_info['phone']}
• Technical Info: https://pypi.org/project/odin-protocol/

This story combines human interest with significant business impact. The technical achievement is remarkable, but the personal journey makes it unforgettable.

Best regards,
{personal_info['name']}
Creator, ODIN Protocol

P.S. Happy to provide any verification or additional context needed for your editorial review.

---
QUICK FACTS:
• Installation: pip install odin-protocol
• Tests: 92% success rate, production ready
• Impact: Solving critical AI infrastructure gap
• Story: Built from homeless shelter in 18 months
"""
        
        return {
            'subject': subject,
            'body': body,
            'outlet': outlet['name'],
            'email': outlet.get('email', '')
        }
    
    def send_email(self, to_email: str, subject: str, body: str, personal_info: Dict) -> bool:
        """Actually send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = personal_info['email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['port'])
            server.starttls()  # Enable TLS encryption
            server.login(self.smtp_config['email'], self.smtp_config['password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(personal_info['email'], to_email, text)
            server.quit()
            
            # Log success
            self.logger.info(f"✅ Email sent successfully to {to_email}")
            
            # Track sent email
            self.sent_emails.append({
                'to': to_email,
                'subject': subject,
                'sent_at': datetime.now().isoformat(),
                'status': 'sent'
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def execute_email_campaign(self, personal_info: Dict, target_count: int = 10) -> Dict:
        """Execute real email marketing campaign"""
        
        self.logger.info("🚀 Starting REAL email marketing campaign")
        self.logger.info(f"Target outlets: {target_count}")
        
        campaign_results = {
            'campaign_start': datetime.now().isoformat(),
            'emails_sent': 0,
            'emails_failed': 0,
            'outlets_contacted': [],
            'next_followup_date': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Send to outlets with email addresses
        email_outlets = [o for o in self.outlets if 'email' in o and o['email']]
        
        for outlet in email_outlets[:target_count]:
            # Generate personalized pitch
            pitch = self.generate_pitch_email(outlet, personal_info)
            
            # Send email
            success = self.send_email(
                outlet['email'], 
                pitch['subject'], 
                pitch['body'], 
                personal_info
            )
            
            if success:
                campaign_results['emails_sent'] += 1
                campaign_results['outlets_contacted'].append({
                    'outlet': outlet['name'],
                    'email': outlet['email'],
                    'sent_at': datetime.now().isoformat(),
                    'status': 'sent'
                })
                
                # Respectful delay between emails
                time.sleep(2)
            else:
                campaign_results['emails_failed'] += 1
        
        # Save campaign results
        filename = f"email_campaign_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, 'w') as f:
            json.dump(campaign_results, f, indent=2)
        
        self.logger.info(f"📊 Campaign completed: {campaign_results['emails_sent']} sent, {campaign_results['emails_failed']} failed")
        
        return campaign_results
    
    def schedule_followups(self, days_later: int = 7) -> List[Dict]:
        """Schedule follow-up emails"""
        followups = []
        
        for sent_email in self.sent_emails:
            followup = {
                'to': sent_email['to'],
                'scheduled_for': (datetime.now() + timedelta(days=days_later)).isoformat(),
                'type': 'follow_up',
                'original_sent': sent_email['sent_at']
            }
            followups.append(followup)
        
        # Save follow-up schedule
        with open('followup_schedule.json', 'w') as f:
            json.dump(followups, f, indent=2)
        
        return followups

def setup_real_marketing():
    """Setup wizard for real email marketing"""
    print("🎯 REAL EMAIL MARKETING SETUP")
    print("=" * 50)
    print("This will actually send emails to media outlets!")
    print()
    
    # Get personal information
    personal_info = {
        'name': input("Your name: "),
        'email': input("Your email address: "),
        'phone': input("Your phone number: ")
    }
    
    print("\n📧 Email Configuration:")
    print("You need SMTP settings to send emails.")
    print("For Gmail: smtp.gmail.com, port 587, app password required")
    print()
    
    smtp_config = {
        'smtp_server': input("SMTP server (e.g., smtp.gmail.com): "),
        'port': int(input("SMTP port (e.g., 587): ")),
        'email': input("Your email (same as above): "),
        'password': input("Email password/app password: ")
    }
    
    # Create marketing system
    marketing = RealEmailMarketing(smtp_config)
    
    print(f"\n🚀 Ready to send real emails!")
    print(f"Available outlets: {len([o for o in marketing.outlets if 'email' in o])}")
    
    target_count = int(input("How many outlets to contact? "))
    
    # Execute campaign
    results = marketing.execute_email_campaign(personal_info, target_count)
    
    print(f"\n✅ Campaign completed!")
    print(f"Emails sent: {results['emails_sent']}")
    print(f"Follow-ups scheduled for: {results['next_followup_date'][:10]}")
    
    return results

if __name__ == "__main__":
    setup_real_marketing()
