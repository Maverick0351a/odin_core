#!/usr/bin/env python3
"""
Hugging Face Deployment Setup for ODIN Protocol HEL Rule System
"""

import os
import shutil
import subprocess
import sys

def setup_huggingface_deployment():
    """Setup files for Hugging Face Spaces deployment"""
    
    print("🧠 ODIN Protocol HEL Rule System - Hugging Face Setup")
    print("=" * 60)
    
    # Create deployment directory
    hf_dir = "huggingface_deployment"
    if os.path.exists(hf_dir):
        shutil.rmtree(hf_dir)
    os.makedirs(hf_dir)
    
    print(f"📁 Created deployment directory: {hf_dir}")
    
    # Copy essential files
    files_to_copy = [
        ("app.py", "app.py"),
        ("requirements.txt", "requirements.txt"),
        ("README_HUGGINGFACE.md", "README.md")
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(hf_dir, dst))
            print(f"✅ Copied: {src} -> {dst}")
        else:
            print(f"⚠️  File not found: {src}")
    
    # Create Hugging Face Space metadata
    space_config = """title: ODIN Protocol HEL Rule System Demo
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
short_description: Interactive demo of the world's first standardized AI-to-AI communication infrastructure
"""
    
    with open(os.path.join(hf_dir, "README.md"), "w", encoding='utf-8') as f:
        f.write("---\n")
        f.write(space_config)
        f.write("---\n\n")
        
        # Append the existing README content
        with open("README_HUGGINGFACE.md", "r", encoding='utf-8') as readme_file:
            f.write(readme_file.read())
    
    print("✅ Created Hugging Face Space metadata")
    
    # Create .gitignore for HF deployment
    gitignore_content = """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
*.log
.DS_Store
.idea/
.vscode/
"""
    
    with open(os.path.join(hf_dir, ".gitignore"), "w", encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ Created .gitignore")
    
    # Create deployment instructions
    instructions = f"""
🧠 ODIN Protocol HEL Rule System - Hugging Face Deployment
============================================================

Files prepared in: {hf_dir}/

📁 Deployment Structure:
├── app.py                 # Main Gradio application
├── requirements.txt       # Python dependencies
├── README.md             # Hugging Face Space documentation
└── .gitignore            # Git ignore file

🚀 Deployment Steps:

1. Create Hugging Face Account:
   - Visit: https://huggingface.co/join
   - Verify your email address

2. Create New Space:
   - Go to: https://huggingface.co/new-space
   - Name: odin-protocol-hel-demo
   - License: MIT
   - SDK: Gradio
   - Hardware: CPU (free tier)

3. Upload Files:
   - Upload all files from {hf_dir}/ directory
   - Or use git to push to the Space repository

4. Using Git (Recommended):
   ```bash
   cd {hf_dir}
   git init
   git lfs install
   git remote add origin https://huggingface.co/spaces/YOUR-USERNAME/odin-protocol-hel-demo
   git add .
   git commit -m "🧠 Initial deployment: ODIN Protocol HEL Rule System Demo"
   git push -u origin main
   ```

5. Access Your Demo:
   - URL: https://huggingface.co/spaces/YOUR-USERNAME/odin-protocol-hel-demo
   - Share with: AI community, potential users, enterprise contacts

📊 Demo Features:
✅ Interactive HEL Rule evaluation
✅ Real-time performance metrics
✅ 8 core capability demonstrations
✅ Cross-model interoperability testing
✅ Enterprise deployment information

🎯 Next Steps:
1. Deploy to Hugging Face Spaces
2. Share demo URL in technical communities
3. Include in business media pitches
4. Use for enterprise customer demonstrations
5. Collect user feedback for improvements

💡 Tips:
- Demo loads automatically on Hugging Face
- No local setup required for users
- Professional presentation for business contacts
- Technical validation for developers
- Perfect complement to PyPI package

Contact: travjohnson831@gmail.com
"""
    
    with open(os.path.join(hf_dir, "DEPLOYMENT_INSTRUCTIONS.txt"), "w", encoding='utf-8') as f:
        f.write(instructions)
    
    print("📋 Created deployment instructions")
    print()
    print("🎉 HUGGING FACE DEPLOYMENT READY!")
    print("=" * 40)
    print(f"📁 Files prepared in: {hf_dir}/")
    print("📋 Read DEPLOYMENT_INSTRUCTIONS.txt for next steps")
    print("🚀 Ready to deploy ODIN Protocol HEL demo to Hugging Face!")
    print()
    print("🔗 Deployment will showcase:")
    print("   • HEL Rule System 8 core capabilities")
    print("   • Real-time AI-to-AI coordination")
    print("   • Enterprise deployment options")
    print("   • Technical performance metrics")
    print("   • Cross-model interoperability")

if __name__ == "__main__":
    setup_huggingface_deployment()
