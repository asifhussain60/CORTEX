#!/usr/bin/env python3
"""
Dialogue Analysis Script for CORTEX Story
Extracts all quoted dialogues from markdown files and analyzes attribution patterns.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Dialogue:
    """Represents a single dialogue instance"""
    text: str
    chapter: str
    line_number: int
    context_before: str  # 200 chars before
    context_after: str   # 100 chars after
    detected_speaker: str | None
    confidence: str  # high, medium, low, none


class DialogueAnalyzer:
    """Analyzes story markdown files for dialogue attribution"""
    
    # Character detection patterns (matching story-viewer.js logic)
    CHARACTERS = {
        'Asif': '#00d4ff',
        'Miss G': '#ba55d3',
        'Copilot': '#7b61ff',
        'CORTEX': '#ff6b6b',
        'client': '#ffb347',
        'Mom': '#ff69b4'
    }
    
    # Pronoun mappings
    PRONOUNS = {
        'he': 'Asif',
        'He': 'Asif',
        'his': 'Asif',
        'His': 'Asif',
        'she': 'Miss G',
        'She': 'Miss G',
        'her': 'Miss G',
        'Her': 'Miss G'
    }
    
    def __init__(self, story_dir: Path):
        self.story_dir = story_dir
        self.dialogues: List[Dialogue] = []
        
    def extract_dialogues_from_file(self, file_path: Path) -> List[Dialogue]:
        """Extract all dialogues from a markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        dialogues = []
        
        # Find all quoted text
        for line_num, line in enumerate(lines, start=1):
            # Skip HTML/CSS/meta content
            if self._is_meta_content(line):
                continue
            
            # Find all quoted dialogues in this line
            for match in re.finditer(r'"([^"]+)"', line):
                dialogue_text = match.group(1)
                
                # Skip technical content
                if self._is_technical_content(dialogue_text):
                    continue
                
                # Get context
                context_before = self._get_context_before(lines, line_num, match.start())
                context_after = self._get_context_after(lines, line_num, match.end())
                
                # Detect speaker
                speaker, confidence = self._detect_speaker(
                    dialogue_text, context_before, context_after
                )
                
                dialogue = Dialogue(
                    text=dialogue_text,
                    chapter=file_path.parent.name,
                    line_number=line_num,
                    context_before=context_before,
                    context_after=context_after,
                    detected_speaker=speaker,
                    confidence=confidence
                )
                
                dialogues.append(dialogue)
        
        return dialogues
    
    def _is_meta_content(self, line: str) -> bool:
        """Check if line contains HTML/CSS/meta content"""
        meta_patterns = [
            r'<.*?>',  # HTML tags
            r'href=',  # Links
            r'src=',   # Images
            r'style=', # Inline styles
            r'class=', # CSS classes
            r'---',    # YAML frontmatter
            r'^\|',    # Markdown tables
        ]
        return any(re.search(pattern, line) for pattern in meta_patterns)
    
    def _is_technical_content(self, text: str) -> bool:
        """Check if quoted text is technical/meta content"""
        technical_indicators = [
            '://',      # URLs
            '.css',     # CSS files
            '.jpeg',    # Image files
            '.png',     # Image files
            'float:',   # CSS properties
            'margin:',  # CSS properties
            'max-width', # CSS properties
            'story-',   # CSS classes
            'Chapter',  # Navigation
        ]
        return any(indicator in text for indicator in technical_indicators)
    
    def _get_context_before(self, lines: List[str], line_num: int, char_pos: int) -> str:
        """Get 200 characters of context before the dialogue"""
        current_line = lines[line_num - 1][:char_pos]
        context = current_line
        
        # Go backwards through lines until we have 200 chars
        i = line_num - 2
        while i >= 0 and len(context) < 200:
            context = lines[i] + ' ' + context
            i -= 1
        
        # Return last 200 chars
        return context[-200:].strip()
    
    def _get_context_after(self, lines: List[str], line_num: int, char_pos: int) -> str:
        """Get 100 characters of context after the dialogue"""
        current_line = lines[line_num - 1][char_pos:]
        context = current_line
        
        # Go forwards through lines until we have 100 chars
        i = line_num
        while i < len(lines) and len(context) < 100:
            context = context + ' ' + lines[i]
            i += 1
        
        # Return first 100 chars
        return context[:100].strip()
    
    def _detect_speaker(self, dialogue: str, context_before: str, 
                       context_after: str) -> Tuple[str | None, str]:
        """
        Detect the speaker of a dialogue using context patterns.
        Returns (speaker, confidence_level)
        """
        
        # First-person narrator (Asif)
        first_person_patterns = [
            r'\bI\s+(?:said|asked|responded|replied|muttered|whispered|thought|wondered)',
            r'\bI\s+(?:froze|looked|turned|spun|gestured|pointed)',
            r'\bMy\s+(?:voice|thoughts|mind)',
        ]
        for pattern in first_person_patterns:
            if re.search(pattern, context_before):
                return ('Asif', 'high')
        
        # Check each character's patterns
        for character in self.CHARACTERS.keys():
            if self._check_character_patterns(character, context_before, context_after):
                confidence = self._calculate_confidence(character, context_before, context_after)
                return (character, confidence)
        
        # Check pronouns with context
        for pronoun, character in self.PRONOUNS.items():
            if self._check_pronoun_patterns(pronoun, context_before, context_after):
                return (character, 'medium')
        
        return (None, 'none')
    
    def _check_character_patterns(self, character: str, 
                                  context_before: str, context_after: str) -> bool:
        """Check if character patterns match in context"""
        
        # Direct attribution patterns
        patterns = [
            # Direct speech verbs
            rf'{character}\s+(?:asked|said|responded|replied|explained|observed|suggested|confirmed|muttered|whispered|shouted|called|announced|added|continued)',
            
            # Possessive forms
            rf'{character}\'s\s+(?:voice|thoughts|mind|presence)',
            
            # Physical actions
            rf'{character}\s+(?:gestured|pointed|looked up|turned|stopped|ran|squinted|spun)',
            
            # Emotional actions
            rf'{character}\s+(?:blinked|sighed|groaned|laughed|smiled|frowned|winced)',
            
            # Temporal markers
            rf'{character}\s+(?:finally|eventually|suddenly|immediately|quickly|slowly|carefully)',
        ]
        
        combined_context = context_before + ' ' + context_after
        return any(re.search(pattern, combined_context, re.IGNORECASE) for pattern in patterns)
    
    def _check_pronoun_patterns(self, pronoun: str, 
                               context_before: str, context_after: str) -> bool:
        """Check if pronoun with action verb appears in context"""
        action_verbs = [
            'asked', 'said', 'responded', 'replied', 'muttered', 'whispered',
            'gestured', 'pointed', 'looked', 'turned', 'blinked', 'sighed',
            'finally', 'suddenly', 'carefully'
        ]
        
        pattern = rf'{pronoun}\s+(?:{"|".join(action_verbs)})'
        combined_context = context_before + ' ' + context_after
        return bool(re.search(pattern, combined_context, re.IGNORECASE))
    
    def _calculate_confidence(self, character: str, 
                             context_before: str, context_after: str) -> str:
        """Calculate confidence level of speaker detection"""
        combined_context = context_before + ' ' + context_after
        
        # High confidence: Character name + speech verb
        if re.search(rf'{character}\s+(?:asked|said|replied)', combined_context, re.IGNORECASE):
            return 'high'
        
        # High confidence: Character's voice/thoughts
        if re.search(rf'{character}\'s\s+(?:voice|thoughts)', combined_context, re.IGNORECASE):
            return 'high'
        
        # Medium confidence: Character + action verb
        if re.search(rf'{character}\s+\w+', combined_context, re.IGNORECASE):
            return 'medium'
        
        return 'low'
    
    def analyze_all_chapters(self) -> Dict:
        """Analyze all chapter files in the story directory"""
        chapter_dirs = [
            'Prologue',
            *[f'Chapter-{i:02d}' for i in range(1, 14)]
        ]
        
        all_dialogues = []
        
        for chapter_dir in chapter_dirs:
            chapter_path = self.story_dir / chapter_dir / 'index.md'
            if chapter_path.exists():
                print(f"Analyzing {chapter_dir}...")
                dialogues = self.extract_dialogues_from_file(chapter_path)
                all_dialogues.extend(dialogues)
                print(f"  Found {len(dialogues)} dialogues")
        
        self.dialogues = all_dialogues
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate analysis report"""
        total = len(self.dialogues)
        
        # Count by speaker
        speaker_counts = {}
        for dialogue in self.dialogues:
            speaker = dialogue.detected_speaker or 'Unattributed'
            speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
        
        # Count by confidence
        confidence_counts = {
            'high': 0,
            'medium': 0,
            'low': 0,
            'none': 0
        }
        for dialogue in self.dialogues:
            confidence_counts[dialogue.confidence] += 1
        
        # Get unattributed dialogues
        unattributed = [
            d for d in self.dialogues 
            if d.detected_speaker is None or d.confidence in ['low', 'none']
        ]
        
        report = {
            'total_dialogues': total,
            'speaker_distribution': speaker_counts,
            'confidence_distribution': confidence_counts,
            'attribution_rate': f"{((total - confidence_counts['none']) / total * 100):.1f}%",
            'unattributed_count': len(unattributed),
            'unattributed_dialogues': [
                {
                    'text': d.text[:50] + '...' if len(d.text) > 50 else d.text,
                    'chapter': d.chapter,
                    'line': d.line_number,
                    'context_before': d.context_before[-50:],
                    'context_after': d.context_after[:50],
                    'confidence': d.confidence
                }
                for d in unattributed[:50]  # First 50 for readability
            ]
        }
        
        return report


def main():
    """Main execution"""
    # Hardcode the correct path
    story_dir = Path('D:/PROJECTS/CORTEX/docs/story')
    
    if not story_dir.exists():
        print(f"❌ Story directory not found: {story_dir}")
        return
    
    print("🔍 CORTEX Story Dialogue Analysis")
    print("=" * 50)
    
    analyzer = DialogueAnalyzer(story_dir)
    report = analyzer.analyze_all_chapters()
    
    # Save report
    output_dir = Path(__file__).parent / 'reports'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'uncolored-dialogues-analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n📊 Analysis Summary")
    print("=" * 50)
    print(f"Total Dialogues: {report['total_dialogues']}")
    print(f"Attribution Rate: {report['attribution_rate']}")
    print(f"Unattributed: {report['unattributed_count']}")
    print("\n📈 Speaker Distribution:")
    for speaker, count in sorted(report['speaker_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / report['total_dialogues'] * 100)
        print(f"  {speaker}: {count} ({percentage:.1f}%)")
    
    print("\n📉 Confidence Distribution:")
    for level, count in report['confidence_distribution'].items():
        percentage = (count / report['total_dialogues'] * 100)
        print(f"  {level}: {count} ({percentage:.1f}%)")
    
    print(f"\n✅ Report saved to: {output_file}")
    print(f"\n🔍 First 10 Unattributed Dialogues:")
    for i, d in enumerate(report['unattributed_dialogues'][:10], 1):
        print(f"\n{i}. [{d['chapter']}:{d['line']}] \"{d['text']}\"")
        print(f"   Before: ...{d['context_before']}")
        print(f"   After: {d['context_after']}...")
        print(f"   Confidence: {d['confidence']}")


if __name__ == '__main__':
    main()
