# ChatGPT Image Prompt: CORTEX Plugin Architecture

**Diagram Type:** System Architecture - Plugin Ecosystem  
**Print Specifications:** 17" x 11" @ 300 DPI (5100 x 3300 pixels)  
**Output Format:** PNG with WHITE background (not transparent)  
**Orientation:** Landscape  
**Print Margins:** 0.5" (150px @ 300 DPI) on all sides  
**Color Scheme:** CORTEX Standard Palette (Red/Teal/Blue/Green/Gold)  

---

## 📋 AI Prompt

```
⚠️ CRITICAL REQUIREMENTS:
- PRINT MARGINS: Add 0.5" (150px @ 300 DPI) margin on ALL sides to prevent content cutoff
- COLOR SCHEME: Use CORTEX standard palette (Blue/Green/Teal/Gold) for different plugin categories

Create a professional system architecture diagram showing "CORTEX Plugin Architecture & Extensibility System":

**Print Specifications:**
- Size: 17" x 11" landscape (tabloid size)
- Resolution: 300 DPI (5100 x 3300 pixels)
- **MARGINS: 0.5" (150px @ 300 DPI) on all sides - CRITICAL for print**
- Format: Technical architecture diagram
- Style: Modern microservices/plugin architecture visualization
- **WHITE background (solid white #ffffff, NOT transparent)**

**Title Section:**
- Title: "CORTEX Plugin Architecture"
- Subtitle: "Extensible System with 12+ Plugins"
- Copyright: "© 2024-2025 Asif Hussain"

**CORE ARCHITECTURE (Top):**

**Center: CORTEX Core** (Show as stable foundation - gray #95a5a6)
- Plugin Registry
- Base Plugin Interface
- Command Registry
- Lifecycle Manager
- Event Bus

Label: "CORTEX Core - Stable Foundation"

**BASE PLUGIN CLASS (Show as blueprint/template):**
```
BasePlugin
├─ _get_metadata()
├─ initialize()
├─ execute()
├─ cleanup()
└─ register_commands()
```

**PLUGIN ECOSYSTEM (Middle - Show as connected modules arranged horizontally):**

Organize plugins in categories (left to right):

**🔧 SYSTEM PLUGINS** (Blue theme #3498db)

1. **Platform Switch Plugin**
   - Icon: Multi-platform icon
   - Commands: /setup, /env, /configure
   - Function: "Cross-platform setup (Mac/Win/Linux)"
   - Status: ✅ Complete

2. **Configuration Wizard Plugin**
   - Icon: Wizard hat
   - Function: "Interactive configuration"
   - Status: ✅ Complete

3. **System Refactor Plugin**
   - Icon: Wrench
   - Function: "Critical review & gap analysis"
   - Tests: 26
   - Status: ✅ Complete

**📚 DOCUMENTATION PLUGINS** (Green theme #2ecc71)

4. **Doc Refresh Plugin**
   - Icon: Document refresh
   - Function: "Story documentation refresh"
   - Tests: 26
   - Status: ✅ Complete

5. **Extension Scaffold Plugin**
   - Icon: Scaffolding
   - Function: "VS Code extension generator"
   - Tests: 30
   - Status: ✅ Reference

**🔍 QUALITY PLUGINS** (Purple theme #9b59b6)

6. **Code Review Plugin**
   - Icon: Magnifying glass over code
   - Function: "Automated code review"
   - Status: ✅ Complete

7. **Cleanup Plugin**
   - Icon: Broom
   - Function: "Workspace cleanup automation"
   - Status: ✅ Complete

**🎯 CUSTOM PLUGINS** (Orange theme #e67e22)

8-12. **Plugin Slots** (Show as empty plugin templates)
   - "Your Custom Plugin"
   - "Easy to add!"
   - Show dotted outlines indicating expandability

**PLUGIN LIFECYCLE FLOW (Bottom):**

Show horizontal flow:

1. **Registration**
   ```
   def register() -> BasePlugin:
       return MyPlugin()
   ```

2. **Discovery**
   "Plugin Registry Auto-discovers"
   
3. **Initialization**
   "initialize() called"

4. **Command Registration**
   "Commands added to registry"

5. **Execution**
   "execute(request, context)"

6. **Cleanup**
   "cleanup() on shutdown"

**FEATURES PANEL (Right side):**

**✨ Plugin Benefits:**
- ✅ No core modification needed
- ✅ Auto-discovered via registry
- ✅ Isolated from each other
- ✅ Command registration built-in
- ✅ Comprehensive testing required
- ✅ Easy to add/remove

**📊 Plugin Statistics:**
- Total Plugins: 12
- Test Coverage: 82 tests
- Command Registry: Operational
- Status: 100% Complete

**INTERACTION DIAGRAM (Center-bottom):**

Show how plugins interact:
```
User Request
    ↓
Intent Router
    ↓
Command Registry ← Plugins register commands
    ↓
Plugin Selected
    ↓
Plugin.execute()
    ↓
Result to User
```

**DEVELOPMENT GUIDE BOX (Bottom):**

**Adding a New Plugin (5 Steps):**
1. Create plugin file in `src/plugins/`
2. Inherit from BasePlugin
3. Implement required methods
4. (Optional) Register commands
5. Add to PluginRegistry

**Visual Style:**
- Clean, modular architecture diagram
- Plugin cards: Rounded rectangles with icons
- **CORTEX color scheme:** Blue (#45b7d1) for system, Green (#96ceb4) for docs, Teal (#4ecdc4) for quality, Gold (#ffd93d) for custom
- Color-coded by category
- Connection lines showing relationships
- Clear plugin → core connections
- **0.5" margins on all sides** (prevents content from being cut off when printed)
- Professional software architecture aesthetic
- Modern, clean design
- Sufficient white space
- Clear typography
- **WHITE background (solid white #ffffff, NOT transparent)**

**Card Design (for each plugin):**
- Header: Icon + Plugin Name
- Function: 1-line description
- Metrics: Tests, status
- Commands: If applicable
- Color-coded border by category

**Typography:**
- Plugin names: Bold, 12-14pt
- Functions: Regular, 10-11pt
- Code blocks: Monospace, 9-10pt
- Section titles: Bold, 16-18pt

Make this diagram show both the current plugin ecosystem AND the extensibility for future plugins. Should inspire developers to add their own plugins. Professional quality for technical documentation.
```

---

## 🎨 Color Scheme

| Category | Color | Hex |
|----------|-------|-----|
| System Plugins | Blue | #3498db |
| Documentation Plugins | Green | #2ecc71 |
| Quality Plugins | Purple | #9b59b6 |
| Custom Plugins | Orange | #e67e22 |
| Core Foundation | Gray | #95a5a6 |
| Success Status | Mint | #55efc4 |

---

## 📐 Layout

**Landscape (5100 x 3300 pixels):**
```
┌────────────────────────────────────────────┐
│  TITLE & SUBTITLE                  (400px) │
├────────────────────────────────────────────┤
│  CORTEX CORE + Base Plugin         (600px) │
├────────────────────────────────────────────┤
│  PLUGIN ECOSYSTEM                 (1200px) │
│  ┌────────┬────────┬────────┬────────┐    │
│  │System  │  Doc   │Quality │Custom  │    │
│  │(Blue)  │ (Grn)  │(Purp)  │(Orange)│    │
│  └────────┴────────┴────────┴────────┘    │
├────────────────────────────────────────────┤
│  LIFECYCLE FLOW                    (600px) │
├────────────────────────────────────────────┤
│  DEVELOPMENT GUIDE + Features      (500px) │
└────────────────────────────────────────────┘
```

---

## 📝 Usage Instructions

1. Copy AI prompt
2. Use any AI platform with image generation (ChatGPT-4 with DALL-E, Claude, Gemini, etc.)
3. Generate image
4. Download PNG
5. Save to: `docs/images/print-ready/06-plugin-architecture.png`

---

*Created: 2025-11-13 | Plugin system architecture visualization*
