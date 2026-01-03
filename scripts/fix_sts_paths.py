#!/usr/bin/env python3
"""
Fix STS CSS paths after flattening directory structure
"""

import os
import re
from pathlib import Path

sts_files = [
    "docs/sts/testing-strategies.html",
    "docs/sts/security-best-practices.html",
    "docs/sts/documentation-guidelines.html",
    "docs/sts/solid-principles.html",
    "docs/sts/performance-optimization.html",
    "docs/sts/code-quality.html"
]

for file_path in sts_files:
    if not Path(file_path).exists():
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix CSS paths from ../../ to ../
    content = content.replace('href="../../assets/css/', 'href="../assets/css/')
    content = content.replace('src="../../assets/js/', 'src="../assets/js/')
    content = content.replace('src="../../assets/images/', 'src="../assets/images/')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {file_path}")

print("\n✅ All STS files corrected!")
