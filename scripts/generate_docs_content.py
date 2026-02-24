import yaml
import json
import os
from pathlib import Path
from datetime import datetime

# Configuration
KNOWLEDGE_ROOT = Path("cortex-registry/knowledge")
KNOWLEDGE_BASE_ROOT = Path("cortex-registry/knowledge-base")
OUTPUT_FILE = Path("cortex-docs/data/content.json")

def load_yaml(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def generate_html_from_yaml(data):
    html = ""
    
    # Handle "best_practices" structure
    if "best_practices" in data:
        if isinstance(data["best_practices"], dict):
            for section, items in data["best_practices"].items():
                if isinstance(items, dict):
                    html += f"<h2>{section.replace('_', ' ').title()}</h2>"
                    html += "<ul>"
                    for key, value in items.items():
                        desc = value.get("description", "") if isinstance(value, dict) else str(value)
                        if desc:
                            html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {desc}</li>"
                    html += "</ul>"
                elif isinstance(items, list):
                     html += f"<h2>{section.replace('_', ' ').title()}</h2>"
                     html += "<ul>"
                     for item in items:
                         html += f"<li>{item}</li>"
                     html += "</ul>"
                else:
                    html += f"<h2>{section.replace('_', ' ').title()}</h2>"
                    html += f"<p>{items}</p>"
        elif isinstance(data["best_practices"], list):
            html += "<h2>Best Practices</h2>"
            html += "<ul>"
            for item in data["best_practices"]:
                html += f"<li>{item}</li>"
            html += "</ul>"
            
    # Handle simple "practices" list
    elif "practices" in data:
        html += "<ul>"
        for item in data["practices"]:
            html += f"<li>{item}</li>"
        html += "</ul>"
            
    # Handle generic key-value pairs if specific structure not found
    else:
        for key, value in data.items():
            if key in ["title", "category", "version", "authority"]:
                continue
            if isinstance(value, dict):
                html += f"<h2>{key.replace('_', ' ').title()}</h2>"
                html += "<ul>"
                for k, v in value.items():
                     html += f"<li><strong>{k}:</strong> {v}</li>"
                html += "</ul>"
            elif isinstance(value, list):
                html += f"<h2>{key.replace('_', ' ').title()}</h2>"
                html += "<ul>"
                for item in value:
                    html += f"<li>{item}</li>"
                html += "</ul>"
            else:
                 html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"

    return html

def main():
    print("Generating documentation content...")
    
    # Initialize structure
    content_data = {
        "categories": [],
        "roles": {
            "curious-learner": {
                "label": "Curious Learner",
                "icon": "🎓",
                "focus": "Explore best practices and learn from CORTEX's knowledge base."
            },
            "software-engineer": {
                "label": "Software Engineer",
                "icon": "💻",
                "focus": "Best practices, patterns, and code examples."
            },
            "product-owner": {
                "label": "Product Owner",
                "icon": "📋",
                "focus": "Requirements, user stories, and acceptance criteria."
            },
             "business-leader": {
                "label": "Business Leader",
                "icon": "👔",
                "focus": "ROI, governance, and compliance."
            }
        }
    }

    # Load INDEX.yaml
    index = load_yaml(KNOWLEDGE_ROOT / "INDEX.yaml")
    if not index:
        return

    # Process each domain in INDEX
    for domain, data in index.items():
        if domain in ["version", "created", "updated"]:
             continue
             
        category = {
            "id": domain,
            "title": domain.replace("-", " ").title(),
            "files": []
        }
        
        # Process guides
        guides = data.get("guides", [])
        for guide in guides:
            path_str = guide.get("path")
            if not path_str:
                continue

            # Determine actual file path
            if path_str.startswith("../knowledge-base/"):
                file_path = KNOWLEDGE_BASE_ROOT / path_str.replace("../knowledge-base/", "")
            else:
                file_path = KNOWLEDGE_ROOT / path_str
            
            # Load file content
            file_data = load_yaml(file_path)
            if not file_data:
                continue
                
            # Generate HTML content
            content_html = generate_html_from_yaml(file_data)
            
            # Create file entry
            file_entry = {
                "slug": file_path.stem,
                "title": guide.get("title", file_data.get("title", file_path.stem)),
                "category": domain,
                "roles": ["curious-learner", "software-engineer"], # Default roles
                "excerpt": f"Learn about {guide.get('title')} in {domain}.", # Simple excerpt
                "content_html": content_html,
                "word_count": len(content_html.split()),
                "last_verified": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add to category
            category["files"].append(file_entry)
            
        # Add category if it has files
        if category["files"]:
            content_data["categories"].append(category)

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(content_data, f, indent=2)
        
    print(f"Generated {len(content_data['categories'])} categories with {sum(len(c['files']) for c in content_data['categories'])} files.")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
