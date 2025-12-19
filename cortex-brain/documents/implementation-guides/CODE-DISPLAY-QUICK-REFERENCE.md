# Code Display Quick Reference

**For Users:** How to get code from CORTEX

---

## 🎯 Default Behavior

By default, CORTEX explains implementations using **concise pseudo-code** instead of full code snippets:

### Example Question
**You:** "How would you implement caching?"

### CORTEX Response (Default)
```markdown
**Approach:**
1. Check cache for key
2. If miss → query data source
3. Transform data
4. Store in cache with TTL
5. Return result

**Logic:** Cache lookup → on miss (fetch + transform + store) → return
```

---

## 💬 How to Get Full Code

Use these phrases to request full code snippets:

### Trigger Phrases
- **"show me the code"**
- **"give me the implementation"**
- **"write the code for..."**
- **"provide code snippet"**
- **"example code"**
- **"what's the code for..."**

### Example
**You:** "Show me the code for implementing caching"

**CORTEX Response:**
```python
class CacheManager:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            if not self._is_expired(key):
                return self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
```

---

## 🔧 Implicit Triggers

CORTEX automatically shows code when:
- You paste code asking for a fix
- You're debugging a specific syntax error
- You request a code review

---

## ✅ Why Pseudo-Code by Default?

1. **Faster responses** - Less text to read
2. **Better conversations** - More natural flow
3. **Clear intent** - Focus on logic, not syntax
4. **Platform agnostic** - Works in any language
5. **Mobile friendly** - Less scrolling

---

## 📊 Comparison

### Question: "Implement user authentication"

#### Response WITHOUT Code Request
```markdown
**Approach:**
1. Validate credentials (username + password)
2. Check against user store (DB/LDAP)
3. Generate JWT token with claims
4. Set session/cookie
5. Return auth status

**Security:** Hash passwords → compare hashes → never store plaintext
```

#### Response WITH "show me the code"
```python
def authenticate_user(username: str, password: str) -> Optional[str]:
    """Authenticate user and return JWT token."""
    # Fetch user from database
    user = db.get_user(username)
    if not user:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    # Generate JWT
    token = create_jwt({
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.now() + timedelta(hours=24)
    })
    
    return token
```

---

## 🎯 Quick Tips

**Want pseudo-code (default):**
- "How does X work?"
- "Explain the approach for Y"
- "What's the best way to implement Z?"

**Want full code:**
- "Show me the code for X"
- "Give me the implementation of Y"
- "Write the code for Z"

---

**Updated:** December 19, 2025  
**Version:** 4.0.1  
**Author:** Asif Hussain
