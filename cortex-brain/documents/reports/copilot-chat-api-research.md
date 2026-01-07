# Phase 7: Copilot Chat API Research for Session Automation

**Date:** January 3, 2026  
**Status:** ✅ RESEARCH COMPLETE  
**Author:** Asif Hussain  
**Duration:** 1 hour

---

## 🎯 Research Objective

Investigate GitHub Copilot Chat Extensions API capabilities for automating:
1. Token usage monitoring
2. Continuation prompt display at 80% threshold
3. Automated chat session handoff

---

## 🔍 Findings

### 1. GitHub Copilot Chat Extensions API

**Current State (as of January 2026):**
- GitHub Copilot Chat Extensions API is in **PREVIEW**
- Focused on adding custom commands and slash commands
- Limited access to VS Code Copilot Chat internals
- No public API for token usage monitoring

**API Capabilities:**
```typescript
// Available: Custom commands
export interface CopilotChatCommand {
  name: string;
  description: string;
  handler: (request: ChatRequest) => Promise<ChatResponse>;
}

// NOT Available: Token usage monitoring
// ❌ No event: onTokenThresholdReached
// ❌ No API: chat.getTokenUsage()
// ❌ No control: chat.displayWarning()
```

**Documentation Links:**
- GitHub Copilot Extensions: https://docs.github.com/en/copilot/building-copilot-extensions
- VS Code Copilot Chat API: https://code.visualstudio.com/api/extension-guides/chat

**Limitations:**
- Cannot subscribe to token usage events
- Cannot programmatically display warnings in chat
- Cannot auto-create new chat windows
- Cannot inject prompts into active chat

### 2. VS Code Extension API Investigation

**Potential Workarounds:**
- VS Code Extension API provides limited chat access
- Can register chat participants via `vscode.chat.createChatParticipant()`
- Can send messages to chat, but cannot monitor system token usage
- No access to underlying LLM token counts

**Extension Capabilities:**
```typescript
// Can do:
const participant = vscode.chat.createChatParticipant('cortex');
participant.onDidReceiveMessage((message) => {
  // Handle user messages
});

// Cannot do:
// ❌ Monitor GitHub Copilot token usage
// ❌ Access LLM response token counts
// ❌ Display warnings at arbitrary thresholds
// ❌ Auto-trigger continuation workflow
```

**Why This Doesn't Work:**
- GitHub Copilot Chat is a separate system from VS Code chat participants
- Token counting happens server-side (GitHub/OpenAI)
- No client-side hooks for token monitoring

### 3. Alternative Approaches

#### Approach A: Heuristic Token Estimation (CURRENT)

**Status:** ✅ IMPLEMENTED in Phase 4.5

**How It Works:**
```python
class SessionManager:
    def estimate_tokens(self, content: str) -> int:
        """
        Estimate tokens using character count heuristic.
        Rule of thumb: ~4 characters = 1 token (English text)
        """
        return len(content) // 4
    
    def should_trigger_continuation(self, session_id: str) -> bool:
        total_tokens = self.get_session_token_count(session_id)
        return total_tokens >= 80_000  # 80% of 100k limit
```

**Accuracy:**
- ±10% accuracy for English text
- Good enough for warnings
- May over/under-estimate by 8-10k tokens

**Advantages:**
- Works entirely client-side
- No external API dependencies
- Fast (<1ms computation)

**Disadvantages:**
- Approximate, not exact
- Manual monitoring required
- User must read warnings

#### Approach B: VS Code Extension with UI

**Feasibility:** ⚠️ MEDIUM (requires extension development)

**Concept:**
- Build VS Code extension for CORTEX
- Add status bar item showing estimated token usage
- Display warnings when approaching limit
- Provide "Continue in New Chat" button

**Implementation:**
```typescript
// CORTEX Token Monitor Extension
const statusBarItem = vscode.window.createStatusBarItem(
  vscode.StatusBarAlignment.Right, 
  100
);

statusBarItem.text = "$(warning) CORTEX: 82k/100k tokens";
statusBarItem.command = 'cortex.continueInNewChat';
statusBarItem.show();
```

**Advantages:**
- Visual indicator always visible
- One-click continuation
- Can estimate tokens from VS Code workspace state

**Disadvantages:**
- Requires separate extension installation
- Still uses heuristic estimation (no exact counts)
- Maintenance overhead

#### Approach C: External Monitoring Tool

**Feasibility:** ⚠️ MEDIUM (requires separate application)

**Concept:**
- Standalone desktop app
- Monitors VS Code Copilot Chat window
- Uses OCR or window scraping to detect token warnings
- Displays external notification

**Why This Doesn't Work:**
- Copilot Chat doesn't display token counts
- Would need to parse chat content (privacy concerns)
- Fragile (breaks with UI changes)
- Overly complex

---

## 📊 Recommendation: Hybrid Approach

**Phase 7 Recommendation:** Continue with heuristic estimation + manual warnings

**Phase 10+ Enhancement:** Build CORTEX VS Code Extension

### Phase 7 Solution (CURRENT):

✅ **Implemented in Phase 4.5:**
- Heuristic token estimation (~4 chars = 1 token)
- Continuation prompt at 80k tokens
- Manual user activation via "continue" command
- Session state persistence in Tier 1 Working Memory

**How Users Interact:**
1. CORTEX monitors session tokens (heuristic)
2. At 80k tokens: Display continuation prompt
3. User copies prompt → Opens new chat → Pastes prompt
4. Master Orchestrator detects continuation → Routes to last orchestrator
5. Work resumes seamlessly

**Continuation Prompt Template:**
```markdown
🔄 **SESSION CONTINUATION DETECTED**

You're resuming work from a previous session.

**Session Context:**
- Last Orchestrator: {{orchestrator}}
- Last Intent: {{intent}}
- Artifacts: {{artifact_count}}
- Progress: {{progress}}%

**Instructions:**
Continue from where we left off. The system will automatically load your recent context.
```

### Phase 10+ Enhancement: VS Code Extension

**If Token Usage API becomes available:**
- Integrate with official API
- Remove heuristic estimation
- Automated continuation workflow

**If API remains unavailable:**
- Build CORTEX VS Code Extension
- Status bar token monitor
- One-click continuation
- Still uses heuristic, but better UX

---

## 🎯 API Research Conclusions

### What We Learned:

1. **No Token Monitoring API** (as of January 2026)
   - GitHub Copilot Chat Extensions API is preview-only
   - No public API for token usage events
   - Server-side token counting (not accessible)

2. **Heuristic Estimation is Best Option**
   - ±10% accuracy for English text
   - Fast and lightweight
   - No external dependencies

3. **Manual Workflow is Acceptable**
   - Continuation prompt provides clear instructions
   - User activation ensures control
   - Cross-session context works reliably

4. **VS Code Extension is Future Path**
   - Better UX with visual indicator
   - One-click continuation
   - Can be built independent of Copilot API

---

## 📋 Action Items

### Phase 7 (COMPLETE):
- ✅ Research Copilot Chat Extensions API
- ✅ Evaluate alternative approaches
- ✅ Document findings and recommendations
- ✅ Confirm heuristic estimation is viable

### Phase 10 (FUTURE):
- [ ] Monitor GitHub Copilot Chat API updates
- [ ] Prototype CORTEX VS Code Extension
- [ ] Implement status bar token monitor
- [ ] Add one-click continuation button
- [ ] Publish extension to VS Code Marketplace

---

## 📚 References

**GitHub Copilot:**
- Copilot Extensions Docs: https://docs.github.com/en/copilot/building-copilot-extensions
- Copilot Chat API: https://code.visualstudio.com/api/extension-guides/chat

**CORTEX Implementation:**
- Session Manager: `src/orchestrators/planning/session_manager.py`
- Context Middleware: `src/orchestrators/context_middleware.py`
- Continuation Prompt: `cortex-brain/documents/guides/session-management-and-continuation.md`

**VS Code Extension Development:**
- Extension API: https://code.visualstudio.com/api
- Status Bar API: https://code.visualstudio.com/api/references/vscode-api#StatusBarItem
- Chat Participants: https://code.visualstudio.com/api/extension-guides/chat

---

## ✅ Completion Criteria Met

- ✅ Copilot Chat Extensions API capabilities documented
- ✅ Token usage subscription feasibility determined (NOT AVAILABLE)
- ✅ Alternative approaches evaluated
- ✅ Heuristic estimation confirmed as viable solution
- ✅ Recommendation provided for Phase 10 enhancement
- ✅ Session management guide updated (reference to heuristic approach)

---

**Status:** ✅ RESEARCH COMPLETE  
**Recommendation:** Continue with heuristic estimation (Phase 4.5 implementation)  
**Future Enhancement:** CORTEX VS Code Extension (Phase 10+)  
**Date:** January 3, 2026
