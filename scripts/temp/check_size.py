from pathlib import Path

content = Path('.github/prompts/CORTEX.prompt.md').read_text(encoding='utf-8')
lines = content.count('\n') + 1
words = len(content.split())
chars = len(content)
# Rough token estimate: ~4 chars per token
tokens_estimate = chars // 4

print('Entry Point Metrics:')
print(f'  Lines: {lines} (target: <500)')
print(f'  Words: {words}')
print(f'  Chars: {chars}')
print(f'  Tokens (est): {tokens_estimate} (target: <5000)')
print()

status = "PASS" if lines <= 500 and tokens_estimate <= 5000 else "FAIL"
print(f'  Status: {status}')

if status == "FAIL":
    if lines > 500:
        print(f'    Need to reduce by {lines - 500} lines')
    if tokens_estimate > 5000:
        print(f'    Need to reduce by {tokens_estimate - 5000} tokens')
