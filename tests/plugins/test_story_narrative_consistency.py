"""
Test Story Narrative Consistency
Validates that ALL chapters maintain Codenstein narrator voice with Copilot interactions

CRITICAL RULES:
1. Every chapter must have Codenstein/Copilot dialogue interactions
2. Each Copilot problem should lead to feature development (problem→solution pattern)
3. Hilarious tone maintained throughout (mustache, Roomba, cat, tea references)
4. No passive voice technical documentation style
5. First-person narrative perspective maintained

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
import re
from typing import Dict, List, Tuple

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.plugins.story_generator_plugin import StoryGeneratorPlugin


class NarrativeStyleValidator:
    """Validates narrative style consistency across chapters"""
    
    # Narrator voice markers (should appear in ALL chapters)
    NARRATOR_MARKERS = {
        'first_person': [r'\bI\b', r'\bme\b', r'\bmy\b', r'\bwe\b'],
        'codenstein_voice': [r'Codenstein', r'my mustache', r'my tea', r'my basement'],
        'copilot_dialogue': [r'\*\*Copilot:\*\*', r'Copilot:', r'"[^"]*"\s*-?\s*Copilot'],
        'character_reactions': [r'The Roomba', r'The cat', r'coffee mug', r'teacup'],
    }
    
    # Humor markers (maintain hilarious tone)
    HUMOR_MARKERS = {
        'physical_comedy': [r'mustache.*quiver', r'fling.*teacup', r'vanish.*ceiling'],
        'emotional_reactions': [r'betrayal', r'existential', r'suspicious', r'reasonable scientist'],
        'absurdist_elements': [r'Roomba', r'ceiling', r'mini fridge', r'coffee mug.*approved'],
        'meta_humor': [r'of course', r'naturally', r'obviously', r'clearly'],
    }
    
    # Problem→Solution pattern markers
    PROBLEM_SOLUTION_MARKERS = {
        'problem_indicators': [r'problem', r'issue', r'challenge', r'doesn\'t work', r'forgot'],
        'frustration': [r'"Wait', r'"What', r'"Which', r'"THE [A-Z]+', r'deeper breath'],
        'solution_indicators': [r'That\'s when', r'decided to', r'built', r'implemented', r'fixed'],
        'feature_outcomes': [r'worked', r'success', r'operational', r'remembered', r'Now it'],
    }
    
    # Anti-patterns (should NOT appear in narrative sections)
    ANTI_PATTERNS = {
        'passive_voice_docs': [r'^Your brain can', r'^CORTEX provides', r'^This system'],
        'encyclopedia_style': [r'^\*\*[A-Z][^:]*:\*\*\s*[A-Z]', r'^[A-Z][^.!?]*:$'],
        'bulleted_specs': [r'^\s*-\s*\*\*[A-Z][^:]*:\*\*', r'^\s*\*\s*\*\*Feature'],
        'technical_dumps': [r'^\s*```\n(?!.*Copilot|.*You:)', r'#### [A-Z][^(]*\([Tt]he [Tt]echnical'],
    }
    
    def __init__(self):
        self.violations: List[Dict] = []
    
    def validate_chapter(self, chapter_number: int, chapter_content: str) -> Dict:
        """
        Validate single chapter for narrative consistency
        
        Returns:
            Dict with validation results and violations
        """
        results = {
            'chapter_number': chapter_number,
            'passed': True,
            'violations': [],
            'scores': {},
        }
        
        # Skip prologue (chapter 0) - different style rules
        if chapter_number == 0:
            return results
        
        # Extract chapter body (exclude title, metadata)
        body = self._extract_chapter_body(chapter_content)
        
        # Test 1: Narrator voice presence
        narrator_score = self._check_narrator_voice(body, chapter_number)
        results['scores']['narrator_voice'] = narrator_score
        if narrator_score < 0.5:  # Less than 50% narrator markers found
            results['passed'] = False
            results['violations'].append({
                'type': 'MISSING_NARRATOR_VOICE',
                'severity': 'CRITICAL',
                'message': f'Chapter {chapter_number} lacks narrator voice (score: {narrator_score:.2%})',
                'expected': 'First-person narration with Codenstein voice',
            })
        
        # Test 2: Copilot dialogue interactions
        copilot_interactions = self._count_copilot_interactions(body)
        results['scores']['copilot_interactions'] = copilot_interactions
        if copilot_interactions < 2:  # Minimum 2 Copilot interactions per chapter
            results['passed'] = False
            results['violations'].append({
                'type': 'INSUFFICIENT_COPILOT_DIALOGUE',
                'severity': 'CRITICAL',
                'message': f'Chapter {chapter_number} has only {copilot_interactions} Copilot interaction(s)',
                'expected': 'Minimum 2 Copilot dialogue exchanges per chapter',
            })
        
        # Test 3: Problem→Solution pattern
        problem_solution_present = self._check_problem_solution_pattern(body)
        results['scores']['problem_solution_pattern'] = problem_solution_present
        if not problem_solution_present:
            results['passed'] = False
            results['violations'].append({
                'type': 'MISSING_PROBLEM_SOLUTION',
                'severity': 'HIGH',
                'message': f'Chapter {chapter_number} lacks clear problem→solution pattern',
                'expected': 'Copilot problem leads to CORTEX feature development',
            })
        
        # Test 4: Humor markers
        humor_score = self._check_humor_presence(body)
        results['scores']['humor_level'] = humor_score
        if humor_score < 0.3:  # Less than 30% humor markers
            results['passed'] = False
            results['violations'].append({
                'type': 'INSUFFICIENT_HUMOR',
                'severity': 'MEDIUM',
                'message': f'Chapter {chapter_number} lacks hilarious tone (score: {humor_score:.2%})',
                'expected': 'Maintain humor with Roomba, cat, mustache, tea references',
            })
        
        # Test 5: Anti-pattern detection (passive documentation style)
        anti_patterns_found = self._detect_anti_patterns(body)
        results['scores']['anti_patterns'] = len(anti_patterns_found)
        if anti_patterns_found:
            results['passed'] = False
            for pattern_type, matches in anti_patterns_found.items():
                results['violations'].append({
                    'type': 'ANTI_PATTERN_DETECTED',
                    'severity': 'HIGH',
                    'message': f'Chapter {chapter_number} contains {pattern_type}: {len(matches)} occurrences',
                    'expected': 'Narrative voice, not technical documentation',
                    'examples': matches[:3],  # First 3 examples
                })
        
        return results
    
    def _extract_chapter_body(self, chapter_content: str) -> str:
        """Extract chapter body, excluding metadata and title"""
        lines = chapter_content.split('\n')
        
        # Skip first few lines (title, metadata)
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith('##') and not line.startswith('###'):
                body_start = i + 1
                break
        
        return '\n'.join(lines[body_start:])
    
    def _check_narrator_voice(self, body: str, chapter_num: int) -> float:
        """
        Check for narrator voice presence
        Returns: Score 0.0-1.0 based on narrator marker density
        """
        total_markers = 0
        found_markers = 0
        
        for category, patterns in self.NARRATOR_MARKERS.items():
            for pattern in patterns:
                total_markers += 1
                if re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
                    found_markers += 1
        
        return found_markers / total_markers if total_markers > 0 else 0.0
    
    def _count_copilot_interactions(self, body: str) -> int:
        """Count Copilot dialogue exchanges"""
        copilot_dialogue = re.findall(
            r'\*\*Copilot:\*\*|Copilot:|"[^"]*"\s*-?\s*Copilot',
            body,
            re.IGNORECASE
        )
        return len(copilot_dialogue)
    
    def _check_problem_solution_pattern(self, body: str) -> bool:
        """
        Check for problem→solution narrative pattern
        Returns: True if both problem and solution indicators present
        """
        has_problem = False
        has_solution = False
        
        for pattern in self.PROBLEM_SOLUTION_MARKERS['problem_indicators']:
            if re.search(pattern, body, re.IGNORECASE):
                has_problem = True
                break
        
        for pattern in self.PROBLEM_SOLUTION_MARKERS['solution_indicators']:
            if re.search(pattern, body, re.IGNORECASE):
                has_solution = True
                break
        
        return has_problem and has_solution
    
    def _check_humor_presence(self, body: str) -> float:
        """
        Check humor marker density
        Returns: Score 0.0-1.0 based on humor elements found
        """
        total_categories = len(self.HUMOR_MARKERS)
        categories_found = 0
        
        for category, patterns in self.HUMOR_MARKERS.items():
            for pattern in patterns:
                if re.search(pattern, body, re.IGNORECASE):
                    categories_found += 1
                    break  # Count category once
        
        return categories_found / total_categories if total_categories > 0 else 0.0
    
    def _detect_anti_patterns(self, body: str) -> Dict[str, List[str]]:
        """
        Detect passive documentation style (anti-patterns)
        Returns: Dict of pattern_type -> list of matching lines
        """
        violations = {}
        lines = body.split('\n')
        
        for pattern_type, patterns in self.ANTI_PATTERNS.items():
            matches = []
            for line in lines:
                for pattern in patterns:
                    if re.search(pattern, line, re.MULTILINE):
                        matches.append(line.strip()[:100])  # First 100 chars
            
            if matches:
                violations[pattern_type] = matches
        
        return violations


def test_all_chapters_have_narrator_voice():
    """Test that ALL chapters maintain narrator voice (not just chapter 1)"""
    print("\n" + "="*80)
    print("Testing: Narrator Voice Consistency Across All Chapters")
    print("="*80)
    
    # Generate story
    plugin = StoryGeneratorPlugin({'root_path': Path.cwd()})
    plugin.initialize()
    
    result = plugin.execute({
        'dry_run': False,
        'chapters': 10,
        'max_words_per_chapter': 5000
    })
    
    assert result['success'], "Story generation failed"
    
    # Load generated chapters
    story_path = Path.cwd() / "docs" / "diagrams" / "story"
    chapter_files = sorted(story_path.glob("[0-9][0-9]-*.md"))
    
    validator = NarrativeStyleValidator()
    all_passed = True
    summary = []
    
    for i, chapter_file in enumerate(chapter_files, start=1):
        content = chapter_file.read_text(encoding='utf-8')
        validation = validator.validate_chapter(i, content)
        
        status = "✅ PASS" if validation['passed'] else "❌ FAIL"
        print(f"\nChapter {i}: {chapter_file.name} - {status}")
        print(f"  Narrator Voice: {validation['scores'].get('narrator_voice', 0):.2%}")
        print(f"  Copilot Interactions: {validation['scores'].get('copilot_interactions', 0)}")
        print(f"  Humor Level: {validation['scores'].get('humor_level', 0):.2%}")
        print(f"  Problem→Solution: {'Yes' if validation['scores'].get('problem_solution_pattern') else 'No'}")
        
        if validation['violations']:
            all_passed = False
            print(f"  Violations:")
            for violation in validation['violations']:
                print(f"    - [{violation['severity']}] {violation['message']}")
        
        summary.append(validation)
    
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    
    total_chapters = len(summary)
    passed_chapters = sum(1 for s in summary if s['passed'])
    
    print(f"Chapters Validated: {total_chapters}")
    print(f"Passed: {passed_chapters}/{total_chapters}")
    print(f"Failed: {total_chapters - passed_chapters}/{total_chapters}")
    
    # Calculate average scores
    avg_narrator = sum(s['scores'].get('narrator_voice', 0) for s in summary) / total_chapters
    avg_interactions = sum(s['scores'].get('copilot_interactions', 0) for s in summary) / total_chapters
    avg_humor = sum(s['scores'].get('humor_level', 0) for s in summary) / total_chapters
    
    print(f"\nAverage Scores:")
    print(f"  Narrator Voice: {avg_narrator:.2%}")
    print(f"  Copilot Interactions: {avg_interactions:.1f} per chapter")
    print(f"  Humor Level: {avg_humor:.2%}")
    
    assert all_passed, f"{total_chapters - passed_chapters} chapters failed narrative consistency checks"
    print("\n✅ All chapters maintain narrator voice consistency!")


def test_copilot_problems_lead_to_features():
    """Test that each Copilot problem leads to CORTEX feature development"""
    print("\n" + "="*80)
    print("Testing: Problem→Solution→Feature Pattern")
    print("="*80)
    
    story_path = Path.cwd() / "docs" / "diagrams" / "story"
    chapter_files = sorted(story_path.glob("[0-9][0-9]-*.md"))
    
    validator = NarrativeStyleValidator()
    failed_chapters = []
    
    for i, chapter_file in enumerate(chapter_files, start=1):
        content = chapter_file.read_text(encoding='utf-8')
        body = validator._extract_chapter_body(content)
        
        # Check for problem→solution pattern
        has_pattern = validator._check_problem_solution_pattern(body)
        
        status = "✅" if has_pattern else "❌"
        print(f"Chapter {i}: {status} Problem→Solution pattern")
        
        if not has_pattern:
            failed_chapters.append(i)
    
    if failed_chapters:
        print(f"\n❌ Chapters missing problem→solution pattern: {failed_chapters}")
        assert False, f"Chapters {failed_chapters} lack problem→solution narrative"
    else:
        print("\n✅ All chapters follow problem→solution→feature pattern!")


def test_hilarious_tone_maintained():
    """Test that hilarious tone is maintained throughout all chapters"""
    print("\n" + "="*80)
    print("Testing: Hilarious Tone Consistency")
    print("="*80)
    
    story_path = Path.cwd() / "docs" / "diagrams" / "story"
    chapter_files = sorted(story_path.glob("[0-9][0-9]-*.md"))
    
    validator = NarrativeStyleValidator()
    low_humor_chapters = []
    
    HUMOR_THRESHOLD = 0.3  # 30% minimum humor marker presence
    
    for i, chapter_file in enumerate(chapter_files, start=1):
        content = chapter_file.read_text(encoding='utf-8')
        body = validator._extract_chapter_body(content)
        
        humor_score = validator._check_humor_presence(body)
        status = "✅" if humor_score >= HUMOR_THRESHOLD else "❌"
        
        print(f"Chapter {i}: {status} Humor Score: {humor_score:.2%}")
        
        if humor_score < HUMOR_THRESHOLD:
            low_humor_chapters.append((i, humor_score))
    
    if low_humor_chapters:
        print(f"\n❌ Chapters with insufficient humor:")
        for chapter, score in low_humor_chapters:
            print(f"   Chapter {chapter}: {score:.2%} (expected ≥{HUMOR_THRESHOLD:.2%})")
        assert False, f"{len(low_humor_chapters)} chapters lack hilarious tone"
    else:
        print("\n✅ All chapters maintain hilarious tone!")


def test_no_passive_voice_documentation():
    """Test that chapters don't devolve into passive voice technical docs"""
    print("\n" + "="*80)
    print("Testing: No Passive Documentation Style")
    print("="*80)
    
    story_path = Path.cwd() / "docs" / "diagrams" / "story"
    chapter_files = sorted(story_path.glob("[0-9][0-9]-*.md"))
    
    validator = NarrativeStyleValidator()
    chapters_with_antipatterns = []
    
    for i, chapter_file in enumerate(chapter_files, start=1):
        content = chapter_file.read_text(encoding='utf-8')
        body = validator._extract_chapter_body(content)
        
        anti_patterns = validator._detect_anti_patterns(body)
        
        if anti_patterns:
            status = "❌"
            chapters_with_antipatterns.append((i, anti_patterns))
        else:
            status = "✅"
        
        print(f"Chapter {i}: {status} Anti-patterns: {len(anti_patterns)} types")
        
        if anti_patterns:
            for pattern_type, examples in anti_patterns.items():
                print(f"   - {pattern_type}: {len(examples)} occurrences")
    
    if chapters_with_antipatterns:
        print(f"\n❌ Chapters with passive documentation style:")
        for chapter, patterns in chapters_with_antipatterns:
            print(f"   Chapter {chapter}: {list(patterns.keys())}")
        assert False, f"{len(chapters_with_antipatterns)} chapters use passive documentation style"
    else:
        print("\n✅ All chapters maintain narrative voice (no passive docs)!")


def test_chapter_word_count_balance():
    """Test that chapters are balanced (not just technical dumps)"""
    print("\n" + "="*80)
    print("Testing: Chapter Word Count Balance")
    print("="*80)
    
    story_path = Path.cwd() / "docs" / "diagrams" / "story"
    chapter_files = sorted(story_path.glob("[0-9][0-9]-*.md"))
    
    MIN_WORDS = 1000  # Minimum words per chapter
    MAX_WORDS = 6000  # Maximum words per chapter
    
    unbalanced_chapters = []
    
    for i, chapter_file in enumerate(chapter_files, start=1):
        content = chapter_file.read_text(encoding='utf-8')
        word_count = len(re.findall(r'\b\w+\b', content))
        
        if word_count < MIN_WORDS:
            status = "❌ TOO SHORT"
            unbalanced_chapters.append((i, word_count, 'short'))
        elif word_count > MAX_WORDS:
            status = "❌ TOO LONG"
            unbalanced_chapters.append((i, word_count, 'long'))
        else:
            status = "✅"
        
        print(f"Chapter {i}: {status} {word_count:,} words")
    
    if unbalanced_chapters:
        print(f"\n❌ Unbalanced chapters:")
        for chapter, words, issue in unbalanced_chapters:
            print(f"   Chapter {chapter}: {words:,} words ({issue})")
        assert False, f"{len(unbalanced_chapters)} chapters are unbalanced"
    else:
        print(f"\n✅ All chapters balanced ({MIN_WORDS:,}-{MAX_WORDS:,} words)!")


if __name__ == "__main__":
    print("🧪 CORTEX Story Narrative Consistency Tests")
    print("Validating narrator voice, humor, and problem→solution patterns\n")
    
    try:
        test_all_chapters_have_narrator_voice()
        test_copilot_problems_lead_to_features()
        test_hilarious_tone_maintained()
        test_no_passive_voice_documentation()
        test_chapter_word_count_balance()
        
        print("\n" + "="*80)
        print("✅ ALL NARRATIVE CONSISTENCY TESTS PASSED")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
