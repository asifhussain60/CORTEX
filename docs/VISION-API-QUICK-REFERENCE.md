# 🎨 Vision API Quick Reference

**Version:** 1.0  
**Status:** ✅ ACTIVE  
**Last Updated:** 2025-11-09

---

## ⚡ Quick Start

### Automatic Analysis (Simplest)

```
[Attach screenshot in Copilot Chat]

"What's in this image?"
```

That's it! CORTEX automatically detects and analyzes.

---

## 🎯 Common Commands

| What You Want | What to Say |
|---------------|-------------|
| **General analysis** | "Analyze this screenshot" |
| **UI elements** | "What elements are in this?" |
| **Colors** | "Extract all colors" |
| **Test IDs** | "Generate test selectors" |
| **Layout** | "What's the layout structure?" |
| **Accessibility** | "Is this accessible?" |
| **Buttons** | "Find all buttons" |
| **Inputs** | "List all form inputs" |

---

## 💡 Example Workflows

### Design Review

```
[Attach mockup]
"Extract the color palette from this design"

Result:
- Primary: #3B82F6
- Secondary: #10B981  
- Text: #1F2937
- Background: #FFFFFF
```

### Test Automation

```
[Attach login page]
"Generate Playwright selectors for all inputs"

Result:
- getByLabel('Email')
- getByLabel('Password')
- getByRole('button', { name: 'Login' })
```

### Accessibility Check

```
[Attach button]
"Check if this button has good contrast"

Result:
- Background: #3B82F6
- Text: #FFFFFF
- Contrast ratio: 4.8:1
- ✅ WCAG AA compliant
```

---

## ⚙️ Configuration

Check if Vision API is enabled:

```json
// cortex.config.json
{
  "vision_api": {
    "enabled": true  // ← Must be true
  }
}
```

---

## 🔍 What Vision API Can Detect

### UI Elements
- ✅ Buttons
- ✅ Text inputs
- ✅ Dropdowns
- ✅ Links
- ✅ Images
- ✅ Icons
- ✅ Checkboxes/Radio buttons

### Visual Properties
- ✅ Colors (hex codes)
- ✅ Font sizes
- ✅ Spacing/padding
- ✅ Border styles
- ✅ Shadows
- ✅ Gradients

### Layout Information
- ✅ Grid/flex layouts
- ✅ Column structure
- ✅ Element positioning
- ✅ Responsive breakpoints
- ✅ Z-index layers

### Accessibility
- ✅ Contrast ratios
- ✅ Text size
- ✅ Touch target size
- ✅ Color-only information
- ✅ ARIA labels (if visible)

---

## 🚫 Limitations

### Cannot Detect
- ❌ JavaScript functionality
- ❌ Data binding
- ❌ API calls
- ❌ Hidden/computed CSS
- ❌ Animations (static frame only)

### Best Practices
- Use high-resolution screenshots
- Ensure good lighting/contrast
- Crop to relevant area only
- Avoid blurry/pixelated images

---

## 📊 Token Costs

| Image Size | Estimated Tokens | Cost (GPT-4) |
|------------|------------------|--------------|
| 512×512 | ~85 | $0.003 |
| 1024×768 | ~170 | $0.005 |
| 1920×1080 | ~320 | $0.010 |
| 3840×2160 | Auto-downscaled | $0.010 |

**Pro Tip:** Images are automatically downscaled and compressed to save tokens!

---

## 🐛 Troubleshooting

### "Vision API not engaging"

**Check:**
1. Is `vision_api.enabled = true` in config?
2. Did you explicitly mention the screenshot?
3. Is the image format supported? (PNG, JPEG, WebP)
4. Is the file size < 2MB?

**Solution:**
Say "analyze this screenshot" explicitly.

### "Generic/unhelpful results"

**Check:**
- Is the screenshot clear and high-res?
- Did you ask a specific question?
- Is there enough contrast in the image?

**Solution:**
Be more specific: "Extract button colors" vs "what's in this?"

### "Token budget exceeded"

**Check:**
- Image size (should be < 2MB)
- Resolution (will auto-downscale to 1920px)

**Solution:**
Crop to relevant area or use lower resolution.

---

## 🎓 Advanced Tips

### 1. Be Specific

❌ "What's in this?"  
✅ "Extract all button labels and colors"

### 2. Use Multiple Queries

```
[Attach screenshot]

Query 1: "List all UI elements"
Query 2: "Now extract colors for each element"
Query 3: "Generate Playwright selectors"
```

### 3. Leverage Caching

Same image + same question = instant cached result!

### 4. Batch Similar Images

Analyze multiple screenshots in sequence:
```
[Screenshot 1]
"Analyze layout"

[Screenshot 2] 
"Compare layout to previous"
```

---

## 📚 Learn More

- **Full Guide:** `.github/copilot-chat-integration.md`
- **Design Doc:** `cortex-brain/cortex-2.0-design/31-vision-api-integration.md`
- **Configuration:** `cortex.config.json` (vision_api section)
- **Tests:** `test_vision_integration.py`

---

## ⚡ TL;DR

1. Attach screenshot
2. Ask "What's in this?"
3. Get structured analysis
4. Profit! 🎉

---

*Quick Reference v1.0 | CORTEX 2.0 Vision Integration*
