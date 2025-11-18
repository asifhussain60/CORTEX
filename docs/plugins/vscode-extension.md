---
title: VS Code Extension
description: CORTEX VS Code extension features and usage
author: 
generated: true
version: ""
last_updated: 
---

# CORTEX VS Code Extension

**Purpose:** Documentation of the CORTEX VS Code extension  
**Audience:** VS Code users, extension developers  
**Version:**   
**Last Updated:** 

---

## Overview

The CORTEX VS Code extension provides seamless integration between CORTEX and Visual Studio Code, enabling natural language commands, visual feedback, and enhanced productivity.

---

## Features

### Natural Language Commands

Execute CORTEX operations directly from Command Palette:

- **CORTEX: Setup** - Initialize CORTEX environment
- **CORTEX: Refresh Story** - Update documentation
- **CORTEX: Cleanup** - Clean workspace
- **CORTEX: Health Check** - Validate system health
- **CORTEX: Help** - Show available commands

### Visual Indicators

- **Status Bar:** Shows CORTEX status (Ready, Busy, Error)
- **Tree View:** Browse CORTEX brain structure
- **Notifications:** Operation progress and completion
- **Decorations:** File annotations for CORTEX-tracked files

### Quick Actions

- **Right-click menu:** CORTEX operations on files/folders
- **Hover tooltips:** Show CORTEX metadata
- **Code lenses:** Inline operation triggers

---

## Installation

### From VSIX Package

```bash
code --install-extension cortex-extension-0.1.0.vsix
```

### From Source

```bash
cd cortex-extension
npm install
npm run compile
code --install-extension .
```

---

## Configuration

Edit VS Code settings:

```json
{
  "cortex.enabled": true,
  "cortex.autoStart": true,
  "cortex.showStatusBar": true,
  "cortex.notifyOnComplete": true,
  "cortex.rootPath": "/path/to/CORTEX"
}
```

---

## Usage

### Command Palette

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "CORTEX:"
3. Select operation

### Keyboard Shortcuts

- **Ctrl+Alt+C H** - CORTEX Help
- **Ctrl+Alt+C S** - CORTEX Setup
- **Ctrl+Alt+C R** - Refresh Story
- **Ctrl+Alt+C C** - Cleanup

---

## Related Documentation

- **Extension Development:** [Development Guide](development.md)
- **Configuration:** [Configuration Reference](../reference/configuration.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 