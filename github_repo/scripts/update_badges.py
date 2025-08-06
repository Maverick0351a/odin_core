#!/usr/bin/env python3
"""
Update GitHub README badges with live revenue data
"""

import json
import re
from datetime import datetime

def update_readme_badges():
    """Update README with live revenue badges"""
    
    # Load current metrics
    try:
        with open('revenue_metrics.json', 'r') as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print("No revenue metrics found, using defaults")
        metrics = {
            'total_mrr': 0,
            'active_subscriptions': 0,
            'professional_customers': 0,
            'enterprise_customers': 0
        }
    
    # Read current README
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Generate new badges
    mrr_badge = f"![Current MRR](https://img.shields.io/badge/MRR-${metrics['total_mrr']:,}-brightgreen)"
    customers_badge = f"![Active Customers](https://img.shields.io/badge/customers-{metrics['active_subscriptions']}-blue)"
    pro_badge = f"![Professional](https://img.shields.io/badge/professional-{metrics['professional_customers']}-orange)"
    enterprise_badge = f"![Enterprise](https://img.shields.io/badge/enterprise-{metrics['enterprise_customers']}-red)"
    
    # Define badge section
    live_stats_section = f"""## 🔥 Live Stats

{mrr_badge}
{customers_badge}
{pro_badge}
{enterprise_badge}
![PyPI Downloads](https://img.shields.io/pypi/dm/odin-protocol)
![GitHub Stars](https://img.shields.io/github/stars/your-username/odin-protocol)"""
    
    # Replace or add live stats section
    live_stats_pattern = r'## 🔥 Live Stats.*?(?=##|\Z)'
    
    if re.search(live_stats_pattern, readme_content, re.DOTALL):
        # Replace existing section
        readme_content = re.sub(
            live_stats_pattern, 
            live_stats_section + '\n\n',
            readme_content, 
            flags=re.DOTALL
        )
    else:
        # Add new section before "Contributing"
        contributing_pattern = r'(## 🤝 Contributing)'
        readme_content = re.sub(
            contributing_pattern,
            live_stats_section + '\n\n\\1',
            readme_content
        )
    
    # Update timestamp comment
    timestamp_comment = f"<!-- Last updated: {datetime.now().isoformat()} -->"
    readme_content = re.sub(
        r'<!-- Last updated:.*? -->',
        timestamp_comment,
        readme_content
    )
    
    if '<!-- Last updated:' not in readme_content:
        readme_content = timestamp_comment + '\n' + readme_content
    
    # Write updated README
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"README updated with live stats: ${metrics['total_mrr']:,} MRR, {metrics['active_subscriptions']} customers")

def main():
    """Update README badges"""
    update_readme_badges()

if __name__ == "__main__":
    main()
