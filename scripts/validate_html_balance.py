"""
Validate HTML structure balance for orchestrator-ecosystem.html
"""

def validate_html_balance(filepath):
    """Check for balanced HTML tags"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tags to check
    tags = [
        'html', 'head', 'body', 'header', 'main', 'footer', 
        'nav', 'section', 'div', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
        'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'p', 'a', 'span', 'strong'
    ]
    
    results = {}
    
    for tag in tags:
        open_count = content.count(f'<{tag}') - content.count(f'</{tag}')
        # Subtract self-closing tags
        self_closing = content.count(f'<{tag}/>')
        open_count -= self_closing
        
        # Count opening tags more precisely (exclude attributes)
        import re
        open_pattern = rf'<{tag}(?:\s|>)'
        close_pattern = rf'</{tag}>'
        
        opens = len(re.findall(open_pattern, content))
        closes = len(re.findall(close_pattern, content))
        
        difference = opens - closes
        
        if difference != 0:
            results[tag] = {
                'opens': opens,
                'closes': closes,
                'difference': difference
            }
    
    return results

if __name__ == "__main__":
    filepath = "docs/architecture/orchestrator-ecosystem.html"
    results = validate_html_balance(filepath)
    
    print("HTML Tag Balance Check")
    print("=" * 60)
    
    if not results:
        print("✅ All tags are balanced!")
    else:
        print("⚠️ Unbalanced tags found:\n")
        for tag, info in results.items():
            print(f"{tag}:")
            print(f"  Opens:  {info['opens']}")
            print(f"  Closes: {info['closes']}")
            print(f"  Diff:   {info['difference']:+d}")
            print()
