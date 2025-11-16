---
title: Best Practices
description: Best practices for working with CORTEX
author: 
generated: true
version: ""
last_updated: 
---

# CORTEX Best Practices

**Purpose:** Best practices for effective CORTEX usage  
**Audience:** All users  
**Version:**   
**Last Updated:** 

---

## Development Workflow

### Test-Driven Development (TDD)

Always follow RED → GREEN → REFACTOR:

```python
# 1. RED: Write failing test
def test_login():
    result = auth.login("user", "pass")
    assert result.success == True  # FAILS

# 2. GREEN: Make it pass
def login(username, password):
    return LoginResult(success=True)  # PASSES

# 3. REFACTOR: Clean up
def login(username, password):
    if not username or not password:
        return LoginResult(success=False)
    # Proper implementation
```

**Why:** Prevents bugs, ensures coverage, maintains quality

### Incremental Development

Build features in small, testable increments:

```python
# ❌ Bad: Large monolithic feature
def create_complete_auth_system():
    # 500 lines of code
    pass

# ✅ Good: Incremental approach
def create_user_model():      # Step 1
    pass
def implement_login():        # Step 2
    pass
def add_session_management(): # Step 3
    pass
```

---

## Conversation Tracking

### Enable Ambient Tracking

**Best:** Automatic background capture

```json
"tracking": {
  "method": "ambient_daemon",
  "ambientDaemon": {
    "enabled": true,
    "autoStart": true
  }
}
```

### Manual Tracking Fallback

If automatic fails, track manually:

```bash
# After each coding session
cortex remember
```

### Verify Memory

Regularly check memory health:

```bash
# Check recent conversations
cortex stats

# Verify entity tracking
cortex entities --recent 5
```

---

## Memory Management

### FIFO Queue Tuning

Balance memory vs history:

```json
// Light usage (< 10 conversations/day)
"tier1": {
  "maxConversations": 10
}

// Standard usage (10-30 conversations/day)
"tier1": {
  "maxConversations": 20  // Default
}

// Heavy usage (> 30 conversations/day)
"tier1": {
  "maxConversations": 30
}
```

### Regular Archiving

Archive old conversations:

```bash
# Archive > 30 days
cortex archive --older-than 30

# Cleanup > 90 days (permanent)
cortex cleanup --older-than 90
```

---

## Agent Usage

### Clear Intent Communication

Be explicit in requests:

```
❌ "do something"
❌ "fix this"
❌ "make it work"

✅ "plan a user authentication feature"
✅ "fix the null reference error in AuthService.cs"
✅ "test the login functionality"
```

### Trust Agent Routing

Let Intent Router handle routing:

```
❌ "use the code executor to add a button"
✅ "add a button to the panel"
```

CORTEX routes automatically with 88% accuracy.

### Provide Context

Help agents with file references:

```
✅ "add authentication to LoginController.cs"
✅ "the button in HostControlPanel.razor"
✅ "fix the error in line 42 of AuthService.cs"
```

---

## Brain Protection

### Respect Challenges

When Brain Protector challenges:

```
❌ "ignore the warning and proceed"
✅ "what's the safer alternative?"
✅ "help me understand the risk"
```

### Application Separation

Keep application code separate:

```
❌ Add SignalR to cortex-brain/
✅ Add SignalR to your-app/

❌ Modify src/tier1/ for app logic
✅ Create app-specific services
```

---

## Performance Optimization

### Database Maintenance

Regular optimization:

```bash
# Weekly: Vacuum databases
sqlite3 cortex-brain/tier1/conversations.db "VACUUM;"

# Monthly: Rebuild indexes
python scripts/rebuild_indexes.py
```

### Cache Configuration

Tune for your machine:

```json
// Low RAM (< 8GB)
"performance": {
  "cacheSizeMB": 50,
  "maxWorkerThreads": 2
}

// High RAM (16GB+)
"performance": {
  "cacheSizeMB": 200,
  "maxWorkerThreads": 8
}
```

---

## Pattern Learning

### Consistent Terminology

Use consistent terms for better learning:

```
✅ Always "add button"
❌ Alternate "create button", "make button"

✅ Always "fix bug"
❌ Alternate "resolve issue", "correct error"
```

### Workflow Naming

Name workflows consistently:

```python
✅ "feature_development_workflow"
✅ "bug_fix_workflow"
❌ "my_workflow_1", "temp_workflow"
```

---

## Testing

### Comprehensive Coverage

Aim for 80%+ coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Test Categories

Write all test types:

```python
# Unit tests (isolated)
def test_calculate_total():
    assert calculate_total([1, 2]) == 3

# Integration tests (combined)
def test_auth_workflow():
    user = create_user()
    result = login(user)
    assert result.success

# Edge cases
def test_empty_input():
    assert calculate_total([]) == 0
```

---

## Documentation

### Keep Docs Current

Update when changing code:

```bash
# After feature addition
update docs/features/

# After API change
update docs/api/

# Generate docs
python src/epm/doc_generator.py
```

### Docstrings Everywhere

All public functions need docstrings:

```python
✅ Good
def calculate_total(items: List[Item]) -> float:
    """Calculate total price of items.
    
    Args:
        items: List of items to sum
        
    Returns:
        Total price as float
    """
    return sum(item.price for item in items)

❌ Bad (no docstring)
def calc(x):
    return sum([i.price for i in x])
```

---

## Configuration Management

### Version Control

```bash
# Track config template
git add cortex.config.template.json

# Ignore machine-specific config
echo "cortex.config.json" >> .gitignore
```

### Multi-Machine Setup

Use machine IDs:

```json
{
  "machines": {
    "WORK-PC": {
      "workspacePath": "D:\\PROJECTS\\CORTEX"
    },
    "LAPTOP": {
      "workspacePath": "/Users/me/CORTEX"
    }
  }
}
```

---

## Backup Strategy

### Regular Backups

```bash
# Weekly: Export brain state
cortex export --output backup-$(date +%Y%m%d).json

# Monthly: Full workspace backup
tar -czf cortex-backup.tar.gz cortex-brain/
```

### Disaster Recovery

Keep backups in multiple locations:

```bash
# Local backup
cp backup.json /backup/

# Cloud backup
aws s3 cp backup.json s3://my-bucket/cortex/
```

---

## Security

### Protect Secrets

Never commit secrets:

```bash
# Use .env file
echo "API_KEY=secret" >> .env
echo ".env" >> .gitignore

# Enable secret prevention
"security": {
  "preventCommitSecrets": true
}
```

### Encryption

For sensitive projects:

```bash
# Enable database encryption
cortex encrypt --enable
```

---

## Troubleshooting

### Regular Health Checks

```bash
# Weekly health check
cortex health-check

# Monthly diagnostics
cortex diagnose
```

### Log Monitoring

```bash
# Watch for errors
tail -f logs/cortex.log | grep ERROR

# Check specific component
tail -f logs/tier1.log
```

---

## Community

### Contribution Guidelines

Follow semantic commits:

```
feat(scope): Add feature
fix(scope): Fix bug
docs(scope): Update docs
```

### Code Reviews

- Write clear PR descriptions
- Include tests
- Update documentation
- Follow code standards

---

## Related Documentation

- **Developer Guide:** [Developer Guide](developer-guide.md)
- **Troubleshooting:** [Troubleshooting](troubleshooting.md)
- **API Reference:** [API](../reference/api-reference.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 