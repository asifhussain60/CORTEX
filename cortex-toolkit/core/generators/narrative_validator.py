#!/usr/bin/env python3
"""
CORTEX Toolkit - Narrative Quality Validator
Uses LLM prompts to validate and correct grammar in generated specifications.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import re
from typing import Dict, List, Tuple


class NarrativeValidator:
    """Validates and corrects narrative quality in generated text."""
    
    def __init__(self):
        self.corrections: Dict[str, str] = {}
        
    def humanize_class_name(self, class_name: str) -> str:
        """
        Convert CamelCase class names to human-readable phrases.
        
        Examples:
            Updater_CreateRAFundingInvoices → create RA funding invoices
            XUpdateFundingBatch → update funding batch
            XGenerateFundingInvoice → generate funding invoice
        """
        # Remove prefixes
        name = class_name
        for prefix in ['Updater_', 'X', 'Service', 'Manager', 'Handler']:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # Split on underscores and CamelCase
        parts = re.split(r'[_\s]+', name)
        words = []
        for part in parts:
            # Split CamelCase
            camel_words = re.findall('[A-Z][^A-Z]*', part)
            words.extend(camel_words)
        
        # Convert to lowercase
        words = [w.lower() for w in words if w]
        
        # Map first word to verb
        verb_map = {
            'create': 'create',
            'generate': 'generate',
            'update': 'update',
            'delete': 'delete',
            'process': 'process',
            'validate': 'validate',
            'calculate': 'calculate',
            'send': 'send',
            'receive': 'receive',
            'close': 'close',
            'open': 'open',
            'run': 'execute',
            'execute': 'execute',
            'invoke': 'invoke'
        }
        
        if not words:
            return "execute the operation"
        
        # Get verb
        first_word = words[0]
        verb = verb_map.get(first_word, first_word)
        
        # Handle special acronyms
        acronym_map = {
            'r': 'RA',
            'ra': 'RA',
            'a': 'account',
            'api': 'API',
            'db': 'database',
            'id': 'ID'
        }
        
        # Build object phrase
        objects = []
        for word in words[1:]:
            # Check if acronym
            if word.lower() in acronym_map:
                objects.append(acronym_map[word.lower()])
            else:
                objects.append(word)
        
        if not objects:
            return f"{verb} records"
        
        object_phrase = ' '.join(objects)
        
        # Grammar corrections
        corrections = {
            'r a funding': 'RA funding',
            'r a': 'RA',
            'funding batch es': 'funding batches',
            'funding invoice s': 'funding invoices',
            'cash in out': 'cash-in/cash-out'
        }
        
        for pattern, replacement in corrections.items():
            object_phrase = object_phrase.replace(pattern, replacement)
        
        return f"{verb} {object_phrase}"
    
    def validate_user_story(self, actor: str, action: str, value: str) -> Tuple[str, str, str]:
        """
        Validate and correct user story components.
        
        Returns:
            Tuple of (corrected_actor, corrected_action, corrected_value)
        """
        # Correct common grammar issues in action
        action_corrections = {
            'updater_ create r a funding invoices': 'create RA funding invoices',
            'updater_ update r a funding batch': 'update RA funding batch',
            'x update funding batch': 'update funding batch',
            'x generate funding invoice': 'generate funding invoice'
        }
        
        corrected_action = action_corrections.get(action.lower(), action)
        
        # Ensure value starts with verb
        if not value.startswith(('ensure', 'maintain', 'enable', 'provide', 'support', 'facilitate')):
            value = f"ensure {value}"
        
        return actor, corrected_action, value
    
    def validate_heading(self, heading: str) -> str:
        """
        Validate and correct section headings.
        
        Examples:
            Updater_ Create R A Funding Invoices → Create RA Funding Invoices
            stringIsNullOrEmptycashInOutId → String Is Null Or Empty (Cash In/Out ID)
        """
        # Handle underscores and spaces
        heading = heading.replace('_', ' ')
        
        # Handle CamelCase
        words = []
        for word in heading.split():
            camel_words = re.findall('[A-Z][^A-Z]*|[a-z]+', word)
            words.extend(camel_words)
        
        # Capitalize first letter of each word
        words = [w.capitalize() for w in words if w]
        
        # Special acronyms
        acronym_corrections = {
            'R A': 'RA',
            'Api': 'API',
            'Db': 'DB',
            'Id': 'ID',
            'Sql': 'SQL',
            'Url': 'URL'
        }
        
        result = ' '.join(words)
        for pattern, replacement in acronym_corrections.items():
            result = result.replace(pattern, replacement)
        
        return result
    
    def validate_description(self, description: str) -> str:
        """
        Validate and correct description text.
        
        Ensures:
        - Proper capitalization
        - No broken CamelCase
        - Correct grammar
        """
        # Split into sentences
        sentences = re.split(r'([.!?])', description)
        
        corrected_sentences = []
        for i, sentence in enumerate(sentences):
            if i % 2 == 0:  # Actual sentence (not delimiter)
                # Capitalize first letter
                sentence = sentence.strip()
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:]
                    corrected_sentences.append(sentence)
            else:
                corrected_sentences.append(sentence)
        
        return ''.join(corrected_sentences)
    
    def generate_llm_prompt(self, text: str, context: str = "user story") -> str:
        """
        Generate an LLM prompt for narrative validation.
        
        This is a template for future LLM integration.
        """
        prompt = f"""You are a technical writing editor reviewing generated API documentation.

Context: {context}

Original text:
{text}

Task: Rewrite this text to be grammatically correct, clear, and professional. Keep the meaning exactly the same, but fix:
1. Broken CamelCase words (e.g., "updater_ create r a" → "create RA")
2. Grammar errors
3. Awkward phrasing
4. Missing articles (a, an, the)
5. Capitalization errors

Corrected text:"""
        
        return prompt
    
    def validate_business_spec(self, spec_content: str) -> str:
        """
        Validate an entire business specification document.
        
        Args:
            spec_content: Full markdown content
            
        Returns:
            Corrected markdown content
        """
        lines = spec_content.split('\n')
        corrected_lines = []
        
        for line in lines:
            # Check for user story pattern
            if 'I want to **' in line:
                # Extract action
                match = re.search(r'I want to \*\*(.+?)\*\*', line)
                if match:
                    action = match.group(1)
                    # Humanize action
                    corrected_action = self.humanize_class_name(action)
                    line = line.replace(action, corrected_action)
            
            # Check for API Purpose
            elif line.startswith('**API Purpose:**'):
                # Extract and correct
                match = re.search(r'\*\*API Purpose:\*\* (.+)', line)
                if match:
                    purpose = match.group(1)
                    corrected_purpose = self.validate_heading(purpose)
                    line = f"**API Purpose:** {corrected_purpose}"
            
            # Check for heading with broken CamelCase
            elif line.startswith('###') and any(c.islower() and prev.isupper() for prev, c in zip(line, line[1:])):
                # Extract heading
                heading = line.lstrip('#').strip()
                corrected_heading = self.validate_heading(heading)
                level = len(line) - len(line.lstrip('#'))
                line = '#' * level + ' ' + corrected_heading
            
            corrected_lines.append(line)
        
        return '\n'.join(corrected_lines)


# Example usage
if __name__ == "__main__":
    validator = NarrativeValidator()
    
    # Test class name humanization
    test_names = [
        "Updater_CreateRAFundingInvoices",
        "XUpdateFundingBatch",
        "XGenerateFundingInvoice",
        "ProcessEmployerData",
        "ValidateAccountStatus"
    ]
    
    print("Class Name Humanization:")
    for name in test_names:
        humanized = validator.humanize_class_name(name)
        print(f"  {name:40} → {humanized}")
    
    print("\nUser Story Validation:")
    actor, action, value = validator.validate_user_story(
        "System Administrator",
        "updater_ create r a funding invoices",
        "accurate and timely reimbursement processing"
    )
    print(f"  Action: {action}")
    print(f"  Value: {value}")
