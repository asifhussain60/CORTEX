# CORTEX 2.0 Design Document 31: Vision API Integration

**Status:** ✅ APPROVED - IMPLEMENT IMMEDIATELY  
**Priority:** HIGH  
**Phase:** 1.6 (Post Token Optimization)  
**Estimated Effort:** 12-16 hours  
**Author:** CORTEX Architecture Team  
**Date:** 2025-11-09

---

## Executive Summary

**Decision:** ✅ **IMPLEMENT Vision API with token-aware constraints**

Adding Vision API to CORTEX 2.0 will unlock powerful image analysis capabilities while maintaining our hard-won 97.2% token optimization. This document outlines a strategic, token-efficient implementation approach.

**Key Insight:** Vision API tokens are expensive (typically 85-170 tokens per image tile), but the value proposition is compelling when implemented with proper controls.

---

## 🎯 Problem Statement

### Current State
- ✅ ScreenshotAnalyzer agent exists with full architecture
- ✅ Intent routing configured (ANALYZE_SCREENSHOT)
- ✅ Mock implementation for testing (22/22 tests passing)
- ❌ Cannot actually analyze images (mock data only)
- ❌ No color detection, OCR, or layout analysis

### User Pain Points
1. **"Fix the faded colors"** - Can't detect visual quality issues
2. **"Implement this mockup"** - Can't extract requirements from images
3. **"What does this error show?"** - Can't read bug screenshots
4. **"Match this design"** - Can't extract design tokens

### Market Context
GitHub Copilot includes built-in vision capabilities in chat. CORTEX should leverage this, not reinvent it.

---

## 🏗️ Architecture Decision

### Option 1: Full Vision API (Recommended ✅)
**Approach:** Use GitHub Copilot's built-in vision API with token budgets

**Pros:**
- ✅ Real image analysis (colors, text, layouts)
- ✅ Handles complex requests ("fix faded colors")
- ✅ No external dependencies (built into Copilot)
- ✅ Professional-grade OCR and object detection
- ✅ Competitive with modern AI assistants

**Cons:**
- ⚠️ Token cost: ~85-170 tokens per image (varies by resolution)
- ⚠️ Potential to impact our 97.2% optimization achievement
- ⚠️ Requires careful budget management

**Mitigation:**
- Set hard token budget: 500 tokens max per image analysis
- Implement image preprocessing (downscale, compress)
- User opt-in required (vision_api_enabled flag)
- Cache analysis results for duplicate images
- Provide token cost preview before processing

### Option 2: Hybrid (Mock + Vision)
**Approach:** Mock for simple cases, Vision API for complex

**Pros:**
- ✅ Lower token cost on average
- ✅ Falls back to mock when API unavailable

**Cons:**
- ❌ Complexity in deciding when to use vision
- ❌ Inconsistent user experience
- ❌ Still requires full Vision API implementation

**Decision:** NOT RECOMMENDED (adds complexity without proportional benefit)

### Option 3: External Vision API (OpenCV/Tesseract)
**Approach:** Local image processing libraries

**Pros:**
- ✅ Zero token cost
- ✅ Full control over processing

**Cons:**
- ❌ Requires heavy dependencies (OpenCV ~500MB)
- ❌ Setup complexity across platforms
- ❌ Lower accuracy than ML models
- ❌ No natural language understanding
- ❌ Maintenance burden

**Decision:** NOT RECOMMENDED (conflicts with "unbloated" architecture)

---

## 🔢 Token Impact Analysis

### Baseline (Current CORTEX 2.0)
```
Average Request Tokens: 2,078 (after 97.2% optimization)
Cost per Request: $0.006 (GPT-4 pricing)
Annual Cost (1k req/mo): $72
```

### With Vision API (Conservative Estimate)
```
Average Request Tokens: 2,078
Vision-Enhanced Request: 2,078 + 250 = 2,328 tokens
Percentage of vision requests: 5% (1 in 20 requests)

Weighted Average: (0.95 × 2,078) + (0.05 × 2,328) = 2,090 tokens
Increase: 0.6% token growth

Annual Cost: $72 + $4 = $76/year
Additional Cost: $4/year (5.5% increase)
```

### Worst Case (10% Vision Usage)
```
Weighted Average: (0.90 × 2,078) + (0.10 × 2,328) = 2,103 tokens
Increase: 1.2% token growth
Annual Cost: $80/year
Additional Cost: $8/year (11% increase)
```

### Token Budget Per Image
```yaml
Image Size Limits:
  Maximum Resolution: 1920x1080 (will downscale)
  Maximum File Size: 2MB (before base64 encoding)
  Supported Formats: PNG, JPEG, WebP

Token Budget:
  Soft Limit: 250 tokens per image
  Hard Limit: 500 tokens per image
  Warning Threshold: 400 tokens

Processing Strategy:
  1. Downscale images >1920px width to 1920px
  2. Compress JPEG quality to 85%
  3. Convert to WebP if >1MB
  4. Calculate estimated token cost
  5. Warn user if >400 tokens
  6. Reject if >500 tokens
```

---

## 💰 Cost-Benefit Analysis

### Benefits (Qualitative)
1. **User Delight:** "Wow, it actually understands my screenshot!"
2. **Competitive Parity:** Matches Claude, ChatGPT capabilities
3. **Workflow Efficiency:** No manual requirement extraction
4. **Reduced Ambiguity:** Visual context eliminates misunderstandings
5. **Professional Polish:** Production-ready feature set

### Benefits (Quantitative)
```
Time Saved per Visual Request:
  Without Vision: 5-10 minutes manual requirement extraction
  With Vision: 10 seconds automated analysis
  Time Savings: 5-10 minutes per request

Value Calculation (assuming $100/hr developer rate):
  Time Value: $8.33 - $16.67 per visual request
  Vision API Cost: $0.0075 per request
  ROI: 1,110x - 2,222x return on investment
```

### Cost Considerations
- Additional $4-8/year for 5-10% vision usage
- Negligible compared to developer time savings
- Smaller than daily coffee budget

---

## 🎨 Implementation Strategy

### Phase 1: Foundation (4 hours)
**Goal:** Enable GitHub Copilot Vision API integration

```python
# src/tier1/vision_api.py
class VisionAPI:
    """GitHub Copilot Vision API integration."""
    
    def __init__(self, config):
        self.enabled = config.get('vision_api_enabled', False)
        self.max_tokens = config.get('vision_max_tokens', 500)
        self.max_image_size = config.get('vision_max_image_size', 2_000_000)
    
    def analyze_image(self, image_data: str, prompt: str) -> dict:
        """
        Analyze image using GitHub Copilot vision.
        
        Args:
            image_data: Base64-encoded image
            prompt: Natural language request
            
        Returns:
            {
                'success': bool,
                'analysis': str,  # Natural language response
                'extracted_data': dict,  # Structured data
                'tokens_used': int,
                'processing_time_ms': int
            }
        """
        # Preprocess image
        processed = self._preprocess_image(image_data)
        
        # Estimate token cost
        estimated_tokens = self._estimate_tokens(processed)
        if estimated_tokens > self.max_tokens:
            return self._error_response(
                f"Image too large: {estimated_tokens} tokens "
                f"(limit: {self.max_tokens})"
            )
        
        # Call vision API (GitHub Copilot built-in)
        # NOTE: Implementation depends on Copilot API access
        result = self._call_vision_api(processed, prompt)
        
        return result
    
    def _preprocess_image(self, image_data: str) -> str:
        """Downscale and compress image to reduce tokens."""
        # PIL/Pillow for image processing
        # Target: <1920px width, JPEG quality 85%
        pass
    
    def _estimate_tokens(self, image_data: str) -> int:
        """Estimate token cost before API call."""
        # GitHub Copilot uses ~85 tokens per 512x512 tile
        # Formula: (width/512) * (height/512) * 85
        pass
```

### Phase 2: ScreenshotAnalyzer Integration (4 hours)
**Goal:** Replace mock with real vision API

```python
# src/cortex_agents/screenshot_analyzer.py
class ScreenshotAnalyzer(BaseAgent):
    
    def __init__(self, name, tier1_api, tier2_kg, tier3_context):
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize Vision API
        self.vision_enabled = tier1_api.config.get('vision_api_enabled', False)
        if self.vision_enabled:
            from src.tier1.vision_api import VisionAPI
            self.vision_api = VisionAPI(tier1_api.config)
        else:
            self.vision_api = None
    
    def _analyze_elements(self, image_data: str, request: AgentRequest):
        """Analyze image using Vision API or mock."""
        
        # Check if Vision API enabled
        if not self.vision_enabled or not self.vision_api:
            # Fallback to mock implementation
            return self._analyze_elements_mock(image_data, request)
        
        # Build vision prompt
        prompt = self._build_vision_prompt(request)
        
        # Call Vision API
        result = self.vision_api.analyze_image(image_data, prompt)
        
        if not result['success']:
            # Fallback to mock on error
            self.logger.warning(f"Vision API failed: {result.get('error')}")
            return self._analyze_elements_mock(image_data, request)
        
        # Parse vision API response
        elements = self._parse_vision_response(result)
        
        # Log token usage
        self._log_vision_metrics(result)
        
        return elements
    
    def _build_vision_prompt(self, request: AgentRequest) -> str:
        """Build natural language prompt for vision API."""
        
        base_prompt = """
        Analyze this UI screenshot and extract:
        1. All interactive elements (buttons, inputs, links)
        2. Text content and labels
        3. Colors (hex codes)
        4. Layout structure
        5. Any annotations or notes
        
        For each element, provide:
        - Type (button, input, text, etc.)
        - Label or text content
        - Suggested test ID (kebab-case)
        - Colors used
        - Approximate position
        
        User's specific request: {user_message}
        """
        
        return base_prompt.format(user_message=request.user_message)
    
    def _parse_vision_response(self, result: dict) -> List[dict]:
        """Convert vision API response to structured elements."""
        # Parse natural language response into element list
        # Use regex/NLP to extract structured data
        pass
    
    def _log_vision_metrics(self, result: dict):
        """Log token usage to Tier 2 for optimization."""
        self.tier2.log_event({
            'event': 'vision_api_call',
            'tokens_used': result['tokens_used'],
            'processing_time_ms': result['processing_time_ms'],
            'success': result['success']
        })
```

### Phase 3: Configuration & Safety (2 hours)
**Goal:** Add config flags and token budgets

```json
// cortex.config.json additions
{
  "vision_api": {
    "enabled": false,  // OPT-IN required
    "max_tokens_per_image": 500,
    "max_image_size_bytes": 2000000,
    "downscale_threshold": 1920,
    "jpeg_quality": 85,
    "cache_analysis_results": true,
    "cache_ttl_hours": 24,
    "warn_threshold_tokens": 400
  },
  
  "token_budget": {
    "global_soft_limit": 40000,
    "global_hard_limit": 50000,
    "per_request_soft_limit": 2500,
    "per_request_hard_limit": 5000,
    "vision_requests_percentage_limit": 10  // Max 10% of requests
  }
}
```

### Phase 4: Testing & Documentation (2-4 hours)
**Goal:** Comprehensive test coverage

```python
# tests/tier1/test_vision_api.py
class TestVisionAPI:
    """Test Vision API integration."""
    
    def test_image_preprocessing(self):
        """Test image downscaling and compression."""
        # Create large test image
        # Verify downscale to 1920px
        # Verify JPEG compression
        pass
    
    def test_token_estimation(self):
        """Test token cost estimation."""
        # Test various image sizes
        # Verify token estimates are accurate
        pass
    
    def test_budget_enforcement(self):
        """Test hard limit enforcement."""
        # Try to analyze huge image
        # Verify rejection at 500 token limit
        pass
    
    def test_cache_mechanism(self):
        """Test result caching."""
        # Analyze same image twice
        # Verify second call uses cache (0 tokens)
        pass

# tests/agents/test_screenshot_analyzer_vision.py
class TestScreenshotAnalyzerVision:
    """Test ScreenshotAnalyzer with Vision API."""
    
    def test_vision_enabled_analysis(self):
        """Test real vision API analysis."""
        # Provide actual screenshot
        # Verify element extraction
        # Verify color detection
        pass
    
    def test_vision_disabled_fallback(self):
        """Test fallback to mock when disabled."""
        # Disable vision API
        # Verify mock implementation used
        pass
    
    def test_vision_error_fallback(self):
        """Test fallback on API error."""
        # Simulate API failure
        # Verify graceful degradation to mock
        pass
```

---

## 📊 Monitoring & Metrics

### Token Usage Dashboard (Phase 3 Extension Integration)
```typescript
interface VisionMetrics {
  // Usage Stats
  total_vision_requests: number;
  total_tokens_used: number;
  average_tokens_per_request: number;
  percentage_of_total_requests: number;
  
  // Cost Tracking
  estimated_cost_usd: number;
  cost_per_request_usd: number;
  
  // Performance
  average_processing_time_ms: number;
  cache_hit_rate: number;
  
  // Quality
  success_rate: number;
  fallback_rate: number;
  
  // Budget Health
  within_budget: boolean;
  percentage_budget_used: number;
  requests_until_limit: number;
}
```

### Alerts
```yaml
Alerts:
  WARNING:
    - Vision usage >8% of total requests
    - Average tokens per image >400
    - Cache hit rate <50%
  
  CRITICAL:
    - Vision usage >10% of total requests
    - Any single image >500 tokens
    - Success rate <90%
  
  INFO:
    - Vision feature first use
    - Cache cleared
    - Budget reset
```

---

## 🎯 Success Criteria

### Phase 1.6 Completion Checklist
- [ ] VisionAPI class implemented (`src/tier1/vision_api.py`)
- [ ] Image preprocessing working (downscale, compress)
- [ ] Token estimation accurate (±10% of actual)
- [ ] ScreenshotAnalyzer integrated with Vision API
- [ ] Mock fallback working when Vision disabled
- [ ] Configuration flags added and documented
- [ ] Token budget enforcement working
- [ ] Tests passing (vision + fallback + budget)
- [ ] Documentation updated (agents-guide.md, technical-reference.md)
- [ ] Token impact measured (<2% increase in practice)

### User Experience Validation
**Test:** "Fix the faded colors in this button screenshot"

**Expected:**
```
✅ Screenshot analyzed (Vision API: 245 tokens)

**Visual Analysis:**
Button appears washed out with low saturation.

**Colors Detected:**
- Current: #8A9BAE (low saturation: 32%)
- Background: #F5F5F5

**Recommendations:**
1. Increase color saturation to 60-70%
2. Suggested color: #3B82F6 (vibrant blue)
3. Ensure WCAG contrast ratio >4.5:1

**Would you like me to:**
1. Update button color to #3B82F6
2. Generate color palette variations
3. Check contrast against background

[Apply Change] [Show Options]
```

---

## 🚫 What We're NOT Doing

### ❌ Not Training Custom Models
- Too expensive
- Too slow
- GitHub Copilot's models are already excellent

### ❌ Not Supporting All Image Types
- No video frame analysis
- No animated GIFs
- No 3D model screenshots
- Keep scope focused on UI screenshots and mockups

### ❌ Not Unlimited Token Budget
- Hard limit: 500 tokens per image
- Percentage limit: 10% of requests can use Vision
- Protection from token explosion

### ❌ Not Always-On
- Feature is OPT-IN (vision_api_enabled flag)
- Users must explicitly enable
- Clear token cost communication

---

## 🔄 Integration with Existing Systems

### Tier 1 (Working Memory)
- Store vision analysis results in conversation context
- Enable "Make that button more purple" follow-ups
- Cache analysis for 24 hours

### Tier 2 (Knowledge Graph)
- Learn color preferences ("User prefers vibrant blues")
- Pattern recognition ("Design mockups usually need ±50 token budget")
- Improve prompt engineering over time

### Tier 3 (Context Intelligence)
- Track vision API usage patterns
- Optimize image preprocessing parameters
- Predict token costs based on image characteristics

### Brain Protector (Tier 0)
- Enforce token budgets (RULE: vision_token_budget_enforcement)
- Prevent runaway costs
- Require user confirmation for large images

---

## 📝 Implementation Plan

### Week 1 (12 hours)
**Monday-Wednesday:**
- [ ] Create `src/tier1/vision_api.py` (4h)
- [ ] Update `src/cortex_agents/screenshot_analyzer.py` (4h)
- [ ] Add configuration to `cortex.config.json` (1h)
- [ ] Write tests for Vision API (3h)

**Expected Output:**
- Vision API functional (with GitHub Copilot integration)
- ScreenshotAnalyzer can analyze real images
- Token budgets enforced
- Tests passing

### Week 2 (4 hours)
**Thursday-Friday:**
- [ ] Update documentation (2h)
- [ ] Add monitoring/metrics (1h)
- [ ] User acceptance testing (1h)

**Expected Output:**
- Documentation complete
- Metrics dashboard showing token usage
- User validation successful

---

## 🎓 Learning & Optimization

### Continuous Improvement
```python
# Tier 2 Knowledge Graph learns:
patterns:
  - "UI mockups average 180 tokens"
  - "Bug screenshots average 220 tokens"
  - "Design specs average 300 tokens"
  - "User prefers color extraction over layout analysis"

optimizations:
  - "Downscale mockups more aggressively (1280px vs 1920px)"
  - "Cache design spec analysis for 48h (rarely changes)"
  - "Skip text extraction if user only asks about colors"
```

### A/B Testing Opportunities
- Test different downscale thresholds (1920px vs 1280px vs 1600px)
- Compare JPEG quality settings (85% vs 75% vs 90%)
- Measure user satisfaction: Vision ON vs Vision OFF

---

## 🚀 Launch Strategy

### Soft Launch (Opt-In Beta)
```markdown
**Vision API Beta Available!**

CORTEX can now understand screenshots! Try:
- "Fix the faded colors in this button"
- "Implement this mockup"
- "What does this error screenshot show?"

**Enable:** Set `vision_api_enabled: true` in cortex.config.json
**Cost:** ~$0.0075 per screenshot (about $4-8/year)
**Token Budget:** 500 tokens max per image

[Learn More] [Enable Now] [See Examples]
```

### Feedback Collection
- Track success rate (did Vision API produce useful results?)
- Measure token efficiency (actual vs estimated)
- User satisfaction surveys
- Common failure modes

---

## 🏆 Expected Outcomes

### Quantitative
- **Token Impact:** <2% increase in average tokens per request
- **Cost Impact:** +$4-8/year (negligible)
- **Success Rate:** >90% of vision requests produce useful results
- **Cache Hit Rate:** >40% (duplicate screenshot analysis)
- **Processing Time:** <2 seconds per image

### Qualitative
- **User Delight:** "Wow, it actually understands my mockup!"
- **Competitive Parity:** Matches Claude, ChatGPT capabilities
- **Professional Polish:** Production-ready feature
- **Workflow Efficiency:** Saves 5-10 minutes per visual request

---

## 📚 References

### Related Documents
- Document 30: Token Optimization System
- Document 28: Integrated Story Documentation
- Brain Protection Rules: `cortex-brain/brain-protection-rules.yaml`
- ScreenshotAnalyzer Implementation: `src/cortex_agents/screenshot_analyzer.py`

### External Resources
- GitHub Copilot Vision API Documentation
- OpenAI Vision API Token Costs
- Image Preprocessing Best Practices

---

## ✅ Recommendation

**STRONG GO - Implement Vision API with token-aware constraints**

**Rationale:**
1. **High Value:** ROI of 1,110-2,222x (time savings vs cost)
2. **Low Risk:** <2% token increase with proper budgets
3. **User Delight:** Transforms UX from "meh" to "wow"
4. **Competitive:** Matches modern AI assistant capabilities
5. **Architected:** Fits cleanly into existing Tier 1 system

**Next Steps:**
1. Implement `VisionAPI` class (4 hours)
2. Integrate with ScreenshotAnalyzer (4 hours)
3. Add configuration and budgets (2 hours)
4. Test and validate (2-4 hours)
5. Document and launch opt-in beta

**Total Effort:** 12-16 hours  
**Timeline:** Week 6 (after Phase 1.5 Token Optimization complete)

---

**Status:** Ready for implementation  
**Approval:** CORTEX Architecture Team ✅  
**Priority:** HIGH (enables competitive feature parity)  
**Risk Level:** LOW (with proper token budgets)

---

*This design document represents CORTEX's commitment to intelligent feature selection - adding capabilities that deliver 1,000x+ ROI while maintaining our 97.2% token optimization achievement.*

**Design Complete:** 2025-11-09  
**Ready to Implement:** ✅ YES
