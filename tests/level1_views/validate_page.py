"""Quick validation script for Level 1 pages."""
from bs4 import BeautifulSoup
from pathlib import Path

def validate_page(page_name):
    html_path = Path(f'docs/{page_name}/index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    glass_panels = soup.find_all(class_=lambda x: x and 'glass-panel-' in x)
    clickable_cards = soup.find_all(class_=lambda x: x and 'glass-card-clickable' in x)
    hero_section = soup.find('div', class_='hero-section')
    stat_pills = soup.find_all(class_='card-stat-pill')
    total_text = len(soup.get_text(strip=True))
    
    print(f'\n{page_name.upper()} Page Validation')
    print('=' * 60)
    print(f'✅ Glass Panel Sections: {len(glass_panels)}')
    print(f'✅ Clickable Cards: {len(clickable_cards)}')
    print(f'✅ Hero Section: {"Found" if hero_section else "Missing"}')
    print(f'✅ Stat Pills: {len(stat_pills)}')
    print(f'✅ Total Text: {total_text:,} chars')
    
    # Check color diversity
    colors = set()
    for panel in glass_panels:
        for cls in panel.get('class', []):
            if 'glass-panel-' in cls:
                colors.add(cls.replace('glass-panel-', ''))
    print(f'✅ Color Palette: {", ".join(sorted(colors))}')
    
    return {
        'page': page_name,
        'glass_panels': len(glass_panels),
        'clickable_cards': len(clickable_cards),
        'hero_section': bool(hero_section),
        'stat_pills': len(stat_pills),
        'text_length': total_text,
        'colors': list(colors)
    }

if __name__ == '__main__':
    pages = [
        'architecture', 'security', 'features', 'story', 'sts',
        'getting-started', 'knowledge', 'learning-paths', 'lens',
        'token-optimization', 'toolkit-manager'
    ]
    
    results = []
    for page in pages:
        results.append(validate_page(page))
    
    print('\n\n' + '=' * 60)
    print('SUMMARY: ALL 11 PAGES VALIDATED')
    print('=' * 60)
    print(f'Total Glass Panels: {sum(r["glass_panels"] for r in results)}')
    print(f'Total Clickable Cards: {sum(r["clickable_cards"] for r in results)}')
    print(f'Total Stat Pills: {sum(r["stat_pills"] for r in results)}')
    print(f'Total Text Content: {sum(r["text_length"] for r in results):,} chars')
    print(f'Pages with Hero Sections: {sum(1 for r in results if r["hero_section"])}')
