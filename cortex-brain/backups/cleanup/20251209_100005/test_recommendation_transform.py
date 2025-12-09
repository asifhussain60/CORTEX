#!/usr/bin/env python3
"""Quick test of recommendation transformation logic"""

import json
from pathlib import Path

# Load actual recommendations.json
recommendations_file = Path("cortex-brain/dashboards/data/repos/cleansolidapp/recommendations.json")

with open(recommendations_file, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

print("="*70)
print("ORIGINAL BACKEND FORMAT")
print("="*70)
print(json.dumps(raw_data, indent=2))

# Simulate JavaScript transformation
def calculate_roi(impact, effort):
    impact_score = {'high': 3, 'medium': 2, 'low': 1}.get(impact.lower() if impact else '', 1)
    effort_score = {'low': 3, 'medium': 2, 'high': 1}.get(effort.lower() if effort else '', 1)
    return impact_score * effort_score

def generate_title(description):
    if not description:
        return 'Recommendation'
    import re
    cleaned = re.sub(r'^(Consider|Add|Remove|Update|Fix|Improve)\s+', '', description, flags=re.IGNORECASE)
    return cleaned[:57] + '...' if len(cleaned) > 60 else cleaned

# Flatten
flat_recommendations = []
for category, recs in raw_data['recommendations'].items():
    if isinstance(recs, list):
        for rec in recs:
            flat_recommendations.append({
                **rec,
                'title': generate_title(rec.get('description')),
                'roi_score': calculate_roi(rec.get('impact'), rec.get('effort')),
                'category': rec.get('category', category)
            })

# Sort by ROI
flat_recommendations.sort(key=lambda x: x.get('roi_score', 0), reverse=True)

transformed = {
    'recommendations': flat_recommendations,
    'top_recommendations': flat_recommendations[:10],
    'counts': {
        'total': raw_data['summary'].get('total_recommendations', len(flat_recommendations)),
        'by_priority': raw_data['summary'].get('by_priority', {}),
        'by_category': raw_data['summary'].get('by_category', {})
    }
}

print("\n" + "="*70)
print("TRANSFORMED UI FORMAT")
print("="*70)
print(json.dumps(transformed, indent=2))

print("\n" + "="*70)
print("VALIDATION")
print("="*70)
print(f"✅ recommendations is array: {isinstance(transformed['recommendations'], list)}")
print(f"✅ top_recommendations is array: {isinstance(transformed['top_recommendations'], list)}")
print(f"✅ Total count: {len(transformed['recommendations'])}")

if transformed['recommendations']:
    rec = transformed['recommendations'][0]
    print(f"✅ Has title field: {'title' in rec}")
    print(f"✅ Has roi_score field: {'roi_score' in rec}")
    print(f"   title: {rec.get('title')}")
    print(f"   roi_score: {rec.get('roi_score')}")
    print(f"   priority: {rec.get('priority')}")
    print(f"   category: {rec.get('category')}")
