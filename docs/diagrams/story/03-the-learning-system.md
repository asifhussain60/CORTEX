# Chapter 3: The Learning System

## Tier 2: Knowledge Graph

Here's a fun fact about memory: it's not just about *remembering* things. It's about *connecting* them.

Your brain doesn't store "bike" separately from "riding" and "falling" and "childhood trauma." It weaves them together into a beautiful tapestry of regret.

That's what Tier 2 does. The Knowledge Graph. CORTEX's way of saying "Hey, I've seen this before. Last time you built authentication, you used JWT tokens and bcrypt. Want me to do that again, or are we feeling adventurous today?"

It learns patterns. It remembers what worked. It suggests reuse. It's basically a really good sous chef who remembers that you hate cilantro and never puts it in your food, ever, no matter how much the recipe insists.

The Roomba watched in silence as I built this layer. I think it was learning too. Possibly plotting. Hard to tell with Roombas.

### When Memory Becomes Intelligence

Tier 1 remembers. Tier 2 *learns*.

Your brain doesn't just remember that you burned yourself on the stove. It learns "hot stove = bad" and applies that knowledge to all future stoves. That's pattern recognition. That's intelligence.

CORTEX Tier 2 is a knowledge graph. It stores:

**Intent Patterns:** "When user says 'add authentication', they usually mean JWT + bcrypt + login/logout endpoints"

**File Relationships:** "HostControlPanel.razor imports HostService.cs, which depends on ApiClient.cs"

**Workflow Templates:** "Last 3 features followed RED-GREEN-REFACTOR. User prefers TDD."

**Success Patterns:** "Factory pattern worked great for service initialization. Suggest reuse."

**Anti-Patterns:** "Singleton caused issues in testing. Avoid."

#### Real-World Learning Example

```
Project 1: You build user authentication
- JWT tokens
- bcrypt password hashing  
- Login/Logout/Register endpoints
- Token refresh logic
- CORS configuration

CORTEX stores this pattern in Tier 2.

Project 2: You say "add authentication"
CORTEX: "I've built authentication before. Here's what worked:
         - JWT tokens (configured, tested, secure)
         - bcrypt for password hashing
         - Login/logout/register endpoints
         - Token refresh with sliding expiration
         - CORS config for your API
         
         Want the same setup, or something different?"
```

You just saved 2-4 hours. And avoided re-implementing from scratch. That's pattern reuse. That's Tier 2.

#### What Gets Learned

**Feature Patterns** (50+ types captured):
- Authentication flows (JWT, OAuth, SAML, API keys)
- CRUD operations (create, read, update, delete patterns)
- API integrations (REST, GraphQL, WebSockets)
- Testing strategies (unit, integration, e2e)
- Error handling approaches
- Logging patterns
- Caching strategies
- Database migrations
- File upload handling
- Email notification setups

**Relationship Patterns:**
- Component dependencies
- Service layer architecture
- Data flow patterns
- Event communication
- State management approaches

**Quality Patterns:**
- Code review feedback that was accepted
- Refactoring improvements that worked
- Security fixes that prevented issues
- Performance optimizations that mattered

The knowledge graph grows with every project. The more you build with CORTEX, the smarter it gets.

#### Pattern Decay (The Forgetting Curve)

Not all patterns age well. That authentication approach from 2019? Maybe not best practice anymore.

CORTEX implements pattern decay:
- **High confidence** (used recently, worked great): 90-100%
- **Medium confidence** (used months ago): 60-80%  
- **Low confidence** (old pattern, rarely used): 30-50%
- **Deprecated** (known to cause issues): 0-20%

Old patterns fade. Recent successes shine. Like human memory, but with better version control.


**Key Takeaway:** Tier 2 transforms memory into intelligence. Pattern learning means never rebuilding from scratch. The brain gets smarter with every project.

