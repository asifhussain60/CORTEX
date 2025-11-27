"""Check entry point metrics."""
from pathlib import Path
import tiktoken

file_path = Path('.github/prompts/CORTEX.prompt.md')
content = file_path.read_text(encoding='utf-8')

# Count lines
lines = content.count('\n') + 1

# Count tokens (using cl100k_base which is GPT-4's tokenizer)
enc = tiktoken.get_encoding('cl100k_base')
tokens = len(enc.encode(content))

print(f'📊 Entry Point Metrics:')
print(f'   Lines: {lines} (target: <500)')
print(f'   Tokens: {tokens} (target: <5000)')
print()

if lines <= 500 and tokens <= 5000:
    print('✅ PASS - Entry point is within limits!')
else:
    print('❌ FAIL - Entry point exceeds limits')
    if lines > 500:
        print(f'   ⚠️  Need to reduce by {lines - 500} lines')
    if tokens > 5000:
        print(f'   ⚠️  Need to reduce by {tokens - 5000} tokens')
