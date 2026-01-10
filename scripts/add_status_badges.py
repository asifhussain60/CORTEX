"""
Add Implementation Status Badges to CORTEX 6.0 Documentation
Reads current phase status and adds visual badges to all HTML docs
"""

from pathlib import Path
import json
import re

def get_phase_status():
    """Read progress tracker to get current phase status"""
    tracker_path = Path("d:/PROJECTS/CORTEX/cortex-brain/tier1/tracking/progress-tracker.json")
    with open(tracker_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {
        "phase_1": {
            "status": data["current_phase"]["status"],
            "name": data["current_phase"]["name"],
            "completed": data["current_phase"]["completed_count"]
        },
        "phase_2": {
            "status": "blocked_by_phase_1",
            "name": "Orchestration Core",
            "completed": 0
        },
        "phase_3": {
            "status": "blocked_by_phase_2",
            "name": "Feature Orchestrators",
            "completed": 0
        },
        "phase_4": {
            "status": "blocked_by_phase_3",
            "name": "Intelligence Layer",
            "completed": 0
        }
    }

def generate_status_badge_html():
    """Generate HTML for status badge banner"""
    phases = get_phase_status()
    
    badge_html = '''
    <!-- Implementation Status Banner -->
    <div style="background: linear-gradient(135deg, rgba(255, 190, 11, 0.1), rgba(255, 0, 110, 0.1)); 
                border: 2px solid rgba(255, 190, 11, 0.3); 
                border-radius: 12px; 
                padding: 25px; 
                margin: 30px 0 40px; 
                position: relative;">
        <div style="font-family: 'Space Grotesk', sans-serif; 
                    font-size: 1.3em; 
                    font-weight: 600; 
                    margin-bottom: 20px; 
                    color: var(--warning);">
            📋 Implementation Status (Design Phase)
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
            <div style="background: rgba(0, 0, 0, 0.3); padding: 15px; border-radius: 8px; border-left: 4px solid #ffbe0b;">
                <div style="font-size: 1.5em; margin-bottom: 5px;">🟡</div>
                <div style="font-weight: 600;">Phase 1: ''' + phases["phase_1"]["name"] + '''</div>
                <div style="color: var(--warning); font-size: 0.9em; margin-top: 5px;">Ready to Implement</div>
                <div style="color: var(--text-muted); font-size: 0.85em; margin-top: 3px;">0/43 AC-IDs Complete</div>
            </div>
            <div style="background: rgba(0, 0, 0, 0.3); padding: 15px; border-radius: 8px; border-left: 4px solid #ff006e;">
                <div style="font-size: 1.5em; margin-bottom: 5px;">🔴</div>
                <div style="font-weight: 600;">Phase 2: ''' + phases["phase_2"]["name"] + '''</div>
                <div style="color: var(--danger); font-size: 0.9em; margin-top: 5px;">Blocked by Phase 1</div>
                <div style="color: var(--text-muted); font-size: 0.85em; margin-top: 3px;">Not Started</div>
            </div>
            <div style="background: rgba(0, 0, 0, 0.3); padding: 15px; border-radius: 8px; border-left: 4px solid #ff006e;">
                <div style="font-size: 1.5em; margin-bottom: 5px;">🔴</div>
                <div style="font-weight: 600;">Phase 3: ''' + phases["phase_3"]["name"] + '''</div>
                <div style="color: var(--danger); font-size: 0.9em; margin-top: 5px;">Blocked by Phase 2</div>
                <div style="color: var(--text-muted); font-size: 0.85em; margin-top: 3px;">Not Started</div>
            </div>
            <div style="background: rgba(0, 0, 0, 0.3); padding: 15px; border-radius: 8px; border-left: 4px solid #ff006e;">
                <div style="font-size: 1.5em; margin-bottom: 5px;">🔴</div>
                <div style="font-weight: 600;">Phase 4: ''' + phases["phase_4"]["name"] + '''</div>
                <div style="color: var(--danger); font-size: 0.9em; margin-top: 5px;">Blocked by Phase 3</div>
                <div style="color: var(--text-muted); font-size: 0.85em; margin-top: 3px;">Not Started</div>
            </div>
        </div>
        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1); 
                    font-size: 0.95em; color: var(--text-secondary);">
            <strong>⚠️ Design Documentation:</strong> This documentation describes the <em>planned architecture</em>. 
            Implementation begins with Phase 1 foundation components. All content marked with 🟡 or 🔴 represents 
            future functionality, not current implementation.
        </div>
    </div>
'''
    return badge_html

def add_badge_to_html_file(filepath):
    """Add status badge to an HTML file if not already present"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if badge already exists
    if "Implementation Status Banner" in content:
        print(f"  ⏭️  Badge already exists: {filepath.name}")
        return False
    
    # Find insertion point (after <h1> and subtitle)
    badge_html = generate_status_badge_html()
    
    # Try multiple insertion points in order of preference
    insertion_patterns = [
        # Pattern 1: After </p> before glass-card
        (r'(</p>\s*\n\s*\n\s*<div class="glass-card">)', badge_html + r'\n\n\1'),
        # Pattern 2: After hero section
        (r'(<div class="hero-section"[^>]*>.*?</div>\s*\n)', r'\1' + badge_html + r'\n\n'),
        # Pattern 3: After first </p> tag
        (r'(</p>\s*\n\s*\n)', r'\1' + badge_html + r'\n\n'),
        # Pattern 4: After <main> tag
        (r'(<main[^>]*>\s*\n)', r'\1' + badge_html + r'\n\n'),
        # Pattern 5: After opening body tag
        (r'(<body[^>]*>\s*\n)', r'\1' + badge_html + r'\n\n'),
    ]
    
    for pattern, replacement in insertion_patterns:
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ Added badge: {filepath.name}")
            return True
    
    print(f"  ⚠️  Could not find insertion point: {filepath.name}")
    return False

def main():
    docs_dir = Path("d:/PROJECTS/CORTEX/docs/architecture")
    
    print("🚀 Adding Implementation Status Badges to Documentation\n")
    print(f"Phase Status:")
    phases = get_phase_status()
    for phase_key, phase_data in phases.items():
        print(f"  {phase_key}: {phase_data['status']} - {phase_data['name']}")
    print()
    
    html_files = list(docs_dir.glob("*.html"))
    print(f"Found {len(html_files)} HTML files\n")
    
    updated = 0
    skipped = 0
    errors = 0
    
    for html_file in html_files:
        # Skip index files
        if "index" in html_file.name.lower():
            print(f"  ⏭️  Skipping index file: {html_file.name}")
            skipped += 1
            continue
        
        try:
            if add_badge_to_html_file(html_file):
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error processing {html_file.name}: {e}")
            errors += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Updated: {updated}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Errors: {errors}")
    print(f"  📁 Total: {len(html_files)}")

if __name__ == "__main__":
    main()
