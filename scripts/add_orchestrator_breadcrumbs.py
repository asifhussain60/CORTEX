#!/usr/bin/env python3
"""
Add breadcrumb navigation to all orchestrator HTML files
Author: Asif Hussain
"""

import os
import re
from pathlib import Path

# Define orchestrators and their display names
ORCHESTRATORS = {
    "ado-planning.html": "ADO Planning",
    "maintenance-orchestrator.html": "System Maintenance",
    "code-sanitization.html": "Code Sanitization",
    "system-integrity.html": "System Integrity",
    "refinement-orchestrator.html": "Refinement",
    "cleanup-orchestrator.html": "Cleanup",
    "git-checkpoint.html": "Git Checkpoint",
    "architectural-review.html": "Architectural Review",
    "cortex-lens.html": "CORTEX Lens v3",
    "intelligent-dashboard.html": "Intelligent Dashboard",
    "debug-orchestrator.html": "Debug",
    "rollback-orchestrator.html": "Rollback",
    "autonomous-execution.html": "Autonomous Execution",
    "pre-flight-orchestrator.html": "Pre-Flight",
}

BREADCRUMB_CSS = """        
        /* Breadcrumb Navigation */
        .breadcrumb {
            background: rgba(30, 41, 59, 0.8);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(124, 58, 237, 0.3);
            margin-bottom: 2rem;
        }
        
        .breadcrumb a {
            color: var(--primary, #2196F3);
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .breadcrumb a:hover {
            color: var(--secondary, #1976D2);
            text-decoration: underline;
        }
        
        .breadcrumb-separator {
            color: #64748b;
            margin: 0 0.5rem;
        }
        
        .breadcrumb-current {
            color: #e2e8f0;
        }
"""

def get_breadcrumb_html(display_name):
    """Generate breadcrumb HTML"""
    return f"""    <!-- Breadcrumb -->
    <nav class="breadcrumb">
        <a href="../../index.html">Home</a>
        <span class="breadcrumb-separator">›</span>
        <a href="../../features/orchestrators.html">Orchestrators</a>
        <span class="breadcrumb-separator">›</span>
        <a href="index.html">Technical Documentation</a>
        <span class="breadcrumb-separator">›</span>
        <span class="breadcrumb-current">{display_name}</span>
    </nav>
    
"""

def add_breadcrumbs(filepath, display_name):
    """Add breadcrumbs to an orchestrator HTML file"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if breadcrumb already exists
    if 'class="breadcrumb"' in content:
        return "skip", "Breadcrumb already exists"
    
    # Add CSS before closing </style> tag
    # Find the last @media query or the </style> tag
    style_pattern = r'(@media[^}]+\{[^}]+\}[\s\n]+)(</style>)'
    
    if re.search(style_pattern, content):
        # Add breadcrumb mobile styles within existing media query
        def add_breadcrumb_mobile(match):
            media_block = match.group(1)
            # Add breadcrumb mobile style before closing }
            mobile_breadcrumb = """            
            .breadcrumb {
                padding: 0.75rem 1rem;
                font-size: 0.9rem;
            }
"""
            # Insert before the last closing brace
            media_block = media_block.rstrip() + mobile_breadcrumb + "        }\n"
            return media_block + match.group(2)
        
        content = re.sub(style_pattern, add_breadcrumb_mobile, content)
        # Now add main breadcrumb CSS before the media query
        content = re.sub(r'(\n\s+)(@media)', BREADCRUMB_CSS + r'\1\2', content)
    else:
        # No media query, just add before </style>
        content = content.replace('</style>', BREADCRUMB_CSS + '\n    </style>')
    
    # Add breadcrumb HTML after <body> tag
    breadcrumb_html = get_breadcrumb_html(display_name)
    content = re.sub(
        r'(<body>\s*\n)',
        r'\1' + breadcrumb_html,
        content
    )
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return "success", "Breadcrumb added successfully"

def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    orchestrators_dir = script_dir.parent / "docs" / "technical" / "orchestrators"
    
    print("🧠 CORTEX Breadcrumb Navigation Installer")
    print("=" * 50)
    print()
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for filename, display_name in ORCHESTRATORS.items():
        filepath = orchestrators_dir / filename
        
        if not filepath.exists():
            print(f"❌ {filename} - File not found")
            fail_count += 1
            continue
        
        try:
            status, message = add_breadcrumbs(filepath, display_name)
            
            if status == "success":
                print(f"✅ {filename} - {message}")
                success_count += 1
            elif status == "skip":
                print(f"⏭️  {filename} - {message}")
                skip_count += 1
            else:
                print(f"❌ {filename} - {message}")
                fail_count += 1
        except Exception as e:
            print(f"❌ {filename} - Error: {str(e)}")
            fail_count += 1
    
    print()
    print("=" * 50)
    print("📊 Summary:")
    print(f"  ✅ Successfully added: {success_count}")
    print(f"  ⏭️  Already existed: {skip_count}")
    print(f"  ❌ Failed: {fail_count}")
    print()
    print("✅ Breadcrumb installation complete!")

if __name__ == "__main__":
    main()
