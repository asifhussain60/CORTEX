# Package 12.1: VS Code Extension Foundation

**Duration:** 3 days (24 hours)  
**Priority:** HIGH  
**Status:** ⏳ READY FOR EXECUTION  
**Dependencies:** None

---

## 🎯 Objective

Create a production-ready VS Code extension that integrates CORTEX commands into the Command Palette and enhances GitHub Copilot Chat with native IDE capabilities.

---

## 📋 Task Breakdown

### Task 12.1.1: Extension Scaffold (4h)
**Description:** Generate VS Code extension project structure using Yeoman generator.

**Steps:**
```bash
# Install Yeoman and VS Code extension generator
npm install -g yo generator-code

# Generate extension
yo code

# Prompts:
#   Type: New Extension (TypeScript)
#   Name: cortex
#   Identifier: cortex
#   Description: CORTEX AI Development Intelligence for VS Code
#   Initialize git: Yes
#   Package manager: npm
```

**Deliverables:**
- `extensions/vscode/` directory structure
- `package.json` with metadata
- `src/extension.ts` entry point
- `tsconfig.json` for TypeScript compilation
- `.vscodeignore` for marketplace packaging

**Success Criteria:**
- ✅ Extension compiles without errors
- ✅ Extension activates in VS Code debugger
- ✅ 3/3 scaffold tests passing

---

### Task 12.1.2: Command Palette Integration (6h)
**Description:** Register 8 core CORTEX commands in Command Palette.

**Commands to Implement:**
1. `cortex.help` - Show CORTEX help
2. `cortex.plan` - Create planning folder
3. `cortex.startTdd` - Start TDD workflow
4. `cortex.systemMaintenance` - Run 6-phase maintenance
5. `cortex.sanitize` - Sanitize code
6. `cortex.refine` - 7-phase refinement
7. `cortex.onboard` - Interactive onboarding
8. `cortex.adoPlanning` - ADO work item planning

**Implementation:**
```typescript
// src/commands/index.ts
export async function registerCommands(context: vscode.ExtensionContext) {
    // Register each command
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.help', async () => {
            // Call Python backend via child_process
            const result = await executeCortexCommand('help');
            // Show result in Output channel
            showOutput(result);
        })
    );
    
    // ... register remaining commands
}

// src/utils/executeCortexCommand.ts
async function executeCortexCommand(cmd: string): Promise<string> {
    // Use WorkspaceRegistry to get CORTEX installation path
    const cortexPath = await getCortexPath();
    
    // Execute: python {cortexPath}/src/main.py {cmd}
    return exec(`python "${cortexPath}/src/main.py" "${cmd}"`);
}
```

**Deliverables:**
- `src/commands/index.ts` - Command registration
- `src/utils/executeCortexCommand.ts` - Python backend executor
- `src/utils/output.ts` - Output channel for CORTEX responses
- 8 commands visible in Command Palette (`Ctrl+Shift+P` → "CORTEX:")

**Success Criteria:**
- ✅ All 8 commands appear in Command Palette
- ✅ Commands execute successfully (call Python backend)
- ✅ Output displayed in "CORTEX" Output channel
- ✅ 8/8 command tests passing

---

### Task 12.1.3: GitHub Copilot Chat Integration (8h)
**Description:** Enhance GitHub Copilot Chat with CORTEX context using VS Code Chat API.

**Implementation:**
```typescript
// src/chat/copilotIntegration.ts
import * as vscode from 'vscode';

export function activateCopilotIntegration(context: vscode.ExtensionContext) {
    // Register CORTEX as a chat participant
    const cortexParticipant = vscode.chat.createChatParticipant(
        'cortex',
        async (request, context, stream, token) => {
            // 1. Parse user request
            const userMessage = request.prompt;
            
            // 2. Get CORTEX context
            const cortexContext = await getCortexContext();
            
            // 3. Enhance prompt with CORTEX instructions
            const enhancedPrompt = `
Follow instructions in ${cortexContext.promptPath}

User Request: ${userMessage}
            `;
            
            // 4. Stream response
            stream.markdown(enhancedPrompt);
            
            return {};
        }
    );
    
    context.subscriptions.push(cortexParticipant);
}

async function getCortexContext() {
    // Read .github/prompts/CORTEX.prompt.md
    // Return CORTEX capabilities, commands, response templates
}
```

**Deliverables:**
- `src/chat/copilotIntegration.ts` - Copilot Chat participant
- `src/chat/contextProvider.ts` - CORTEX context extraction
- Chat command: `@cortex <message>` in Copilot Chat
- Automatic injection of `.github/prompts/CORTEX.prompt.md`

**Success Criteria:**
- ✅ `@cortex` participant visible in Copilot Chat
- ✅ CORTEX context automatically injected
- ✅ All CORTEX commands work via chat
- ✅ 5/5 Copilot API tests passing

---

### Task 12.1.4: CORTEX Dashboard Webview (4h)
**Description:** Create a webview panel showing CORTEX metrics, brain status, and quick actions.

**Dashboard Features:**
- **Brain Health:** Tier 0-3 database stats
- **Recent Plans:** Last 5 planning sessions
- **TDD Status:** Test coverage, failing tests
- **Quick Actions:** Buttons for common commands
- **System Info:** CORTEX version, Python version, workspace detection

**Implementation:**
```typescript
// src/webview/dashboard.ts
export class CortexDashboard {
    private panel: vscode.WebviewPanel | undefined;
    
    public show(context: vscode.ExtensionContext) {
        this.panel = vscode.window.createWebviewPanel(
            'cortexDashboard',
            'CORTEX Dashboard',
            vscode.ViewColumn.One,
            { enableScripts: true }
        );
        
        // Load dashboard HTML
        this.panel.webview.html = this.getDashboardHtml();
        
        // Handle messages from webview
        this.panel.webview.onDidReceiveMessage(async message => {
            if (message.command === 'executeCortexCommand') {
                await vscode.commands.executeCommand(message.cortexCommand);
            }
        });
    }
    
    private getDashboardHtml(): string {
        // Glassmorphism design from docs/assets/css/main.css
        return `<!DOCTYPE html>...`;
    }
}
```

**Deliverables:**
- `src/webview/dashboard.ts` - Dashboard webview
- `media/dashboard.html` - Dashboard UI (glassmorphism)
- `media/dashboard.css` - Dashboard styles
- Command: `cortex.showDashboard` to open webview

**Success Criteria:**
- ✅ Dashboard opens via command
- ✅ Real-time brain stats displayed
- ✅ Quick action buttons functional
- ✅ 4/4 webview tests passing

---

### Task 12.1.5: Marketplace Preparation (2h)
**Description:** Prepare extension for VS Code Marketplace publication.

**Assets Needed:**
- `README.md` - Extension description, features, installation
- `CHANGELOG.md` - Version history
- `icon.png` - CORTEX logo (128x128)
- `LICENSE` - Source-available license
- Screenshots (3-5) - Command Palette, Dashboard, Copilot integration

**package.json Updates:**
```json
{
  "publisher": "asifhussain60",
  "repository": "https://github.com/asifhussain60/CORTEX",
  "icon": "media/icon.png",
  "galleryBanner": {
    "color": "#0a0e27",
    "theme": "dark"
  },
  "categories": ["AI", "Programming Languages", "Testing", "Other"],
  "keywords": ["copilot", "ai", "tdd", "planning", "testing"],
  "badges": [
    {
      "url": "https://img.shields.io/badge/Status-Production%20Ready-success",
      "description": "Production Ready"
    }
  ]
}
```

**Deliverables:**
- Complete `README.md` with examples
- High-quality screenshots
- `icon.png` (CORTEX logo)
- Draft marketplace listing

**Success Criteria:**
- ✅ All marketplace assets present
- ✅ README includes installation, usage, troubleshooting
- ✅ Extension passes `vsce package` validation

---

## 📊 Test Coverage

| Test Category | Count | Description |
|---------------|-------|-------------|
| Scaffold Tests | 3 | Extension activation, compilation, basic structure |
| Command Tests | 8 | Each CORTEX command executes successfully |
| Copilot API Tests | 5 | Chat participant registration, context injection |
| Webview Tests | 4 | Dashboard rendering, message passing, quick actions |

**Total:** 20 tests  
**Target Pass Rate:** 95%+ (19/20 minimum)

---

## 🎯 Success Criteria

Package 12.1 is complete when:
1. ✅ Extension compiles without errors
2. ✅ 8 commands visible in Command Palette
3. ✅ `@cortex` participant works in Copilot Chat
4. ✅ Dashboard webview functional
5. ✅ 19/20 tests passing (95%+)
6. ✅ Marketplace assets complete
7. ✅ Extension ready for Package 12.4 publication

---

## 📚 Resources

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Chat API Documentation](https://code.visualstudio.com/api/extension-guides/chat)
- [Webview Guide](https://code.visualstudio.com/api/extension-guides/webview)
- [Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)

---

**Author:** Asif Hussain  
**Last Updated:** December 29, 2025
