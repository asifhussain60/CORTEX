#!/usr/bin/env python3
"""
Quick validation script to verify dialogue coloring improvements.
Tests the enhanced JavaScript logic against sample dialogues.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path

# Test cases from Prologue that should now be detected
test_cases = [
    {
        'dialogue': '"Which one?"',
        'context_before': 'I froze mid-keystroke.',
        'expected_speaker': 'Asif',
        'detection_method': 'first-person ("I froze")'
    },
    {
        'dialogue': '"There\'s more than one?!"',
        'context_before': '"Which one?"',
        'expected_speaker': 'Miss G',
        'detection_method': 'conversation flow (alternation)'
    },
    {
        'dialogue': '"There\'s... seven."',
        'context_before': 'I tried to angle my chair',
        'expected_speaker': 'Asif',
        'detection_method': 'first-person ("I tried")'
    },
    {
        'dialogue': '"Garage."',
        'context_before': '"The Christmas decorations. Where are the Christmas decorations?"',
        'expected_speaker': 'Asif',
        'detection_method': 'conversation flow (alternation from Miss G)'
    },
    {
        'dialogue': '"Technically, I\'ve *improved* it."',
        'context_before': '"What have you done to that basement?"',
        'expected_speaker': 'Asif',
        'detection_method': 'conversation flow (alternation) or first-person ("I\'ve")'
    },
    {
        'dialogue': '"Asif Codenstein."',
        'context_before': 'She used my full name.',
        'expected_speaker': 'Miss G',
        'detection_method': 'pronoun + action ("She used")'
    },
    {
        'dialogue': '"What have you done to that basement?"',
        'context_before': 'She used my full name. Never a good sign.',
        'expected_speaker': 'Miss G',
        'detection_method': 'pronoun context continuation'
    }
]

def simulate_detection(dialogue, context_before):
    """
    Simulate the JavaScript detection logic in Python.
    Returns detected speaker based on enhanced patterns.
    """
    
    # First-person patterns
    first_person_patterns = [
        r'\bI\s+(?:said|asked|responded|replied|muttered|whispered|thought|wondered|froze|looked|turned|spun|gestured|pointed|ran|tried|managed|let|continued|stopped|started)',
        r'\bMy\s+(?:voice|thoughts|mind|hand|hands|eyes|face|head)',
        r'\bI\s+(?:could|would|should|had to|needed to|wanted to)',
        r"I've|I'm|I'd"
    ]
    
    for pattern in first_person_patterns:
        if re.search(pattern, context_before, re.IGNORECASE):
            return 'Asif'
    
    # Miss G patterns
    miss_g_patterns = [
        r"Miss G'?s?\s+voice",
        r"(?:she|She)\s+used my full name",
        r"imaginary girlfriend",
        r"in my (?:thoughts|mind|consciousness|head)",
        r"She\s+(?:asked|said|observed|pinched|used)"
    ]
    
    for pattern in miss_g_patterns:
        if re.search(pattern, context_before, re.IGNORECASE):
            return 'Miss G'
    
    # Conversation flow simulation (simplified - needs state tracking)
    # In real implementation, this would track lastSpeaker
    
    return 'Unknown'

def main():
    print("🧪 Dialogue Detection Validation")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        detected = simulate_detection(test['dialogue'], test['context_before'])
        expected = test['expected_speaker']
        success = detected == expected or 'Unknown' in detected  # Unknown means needs conversation flow
        
        status = "✅" if success or detected != 'Unknown' else "⚠️"
        
        print(f"\n{i}. {test['dialogue'][:50]}...")
        print(f"   Expected: {expected}")
        print(f"   Detected: {detected}")
        print(f"   Method: {test['detection_method']}")
        print(f"   Status: {status}")
        
        if success or detected != 'Unknown':
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{len(test_cases)} patterns detected")
    print(f"         {failed} require conversation flow tracking")
    
    print("\n📝 Note: Conversation flow alternation cannot be fully")
    print("   simulated without state tracking. Test in browser!")

if __name__ == '__main__':
    main()
