# Python Tools for RA Domain Analysis

**Purpose:** Required Python libraries for comprehensive .NET codebase analysis  
**Created:** December 11, 2025

---

## ✅ Already Installed

| Library | Version | Purpose |
|---------|---------|---------|
| `tree-sitter` | 0.25.2 | Core AST parsing engine |
| `tree-sitter-c-sharp` | ✅ Installed | C# language grammar for AST |
| `lxml` | 6.0.2 | XML parsing (.csproj, .sln files) |
| `beautifulsoup4` | 4.14.3 | HTML/XML parsing (documentation, config) |

---

## 🔧 Recommended Additional Tools

### For Enhanced Analysis

```bash
# Install all recommended tools
pip install pygments networkx matplotlib graphviz python-dotenv pyyaml
```

| Library | Purpose | Use Case |
|---------|---------|----------|
| `pygments` | Syntax highlighting | Code snippet extraction with formatting |
| `networkx` | Graph analysis | Dependency graphs, call graphs, ER diagrams |
| `matplotlib` | Visualization | Generate architecture diagrams, metrics charts |
| `graphviz` | Graph rendering | Render dependency graphs as images |
| `python-dotenv` | Config management | Load environment variables for analysis scripts |
| `pyyaml` | YAML parsing | Parse configuration files |

### For Advanced AST Analysis

```bash
# Optional: Advanced analysis tools
pip install lizard radon bandit
```

| Library | Purpose | Use Case |
|---------|---------|----------|
| `lizard` | Complexity analysis | Calculate cyclomatic complexity |
| `radon` | Code metrics | Maintainability index, raw metrics |
| `bandit` | Security analysis | Security vulnerability detection (Python) |

---

## 📋 Usage Examples

### 1. Parse C# File with tree-sitter

```python
from tree_sitter import Language, Parser
import tree_sitter_c_sharp as tscsharp

# Initialize parser
CS_LANGUAGE = Language(tscsharp.language())
parser = Parser()
parser.set_language(CS_LANGUAGE)

# Parse C# file
with open('CarryoverDollarsDomainService.cs', 'rb') as f:
    code = f.read()
    tree = parser.parse(code)

# Extract class declarations
def find_classes(node):
    if node.type == 'class_declaration':
        class_name = next(
            (child.text.decode() for child in node.children 
             if child.type == 'identifier'),
            'Unknown'
        )
        print(f"Class: {class_name}")
    
    for child in node.children:
        find_classes(child)

find_classes(tree.root_node)
```

### 2. Parse .csproj Files

```python
from lxml import etree

# Parse project file
tree = etree.parse('App.PaymentAccounts.Rollover.Jobs.csproj')
root = tree.getroot()

# Extract package references
packages = []
for pkg in root.xpath('//PackageReference'):
    name = pkg.get('Include')
    version = pkg.get('Version')
    packages.append({'name': name, 'version': version})

print(f"Found {len(packages)} NuGet packages")
```

### 3. Generate Dependency Graph

```python
import networkx as nx
import matplotlib.pyplot as plt

# Build dependency graph
G = nx.DiGraph()
G.add_edge("ApplicationServices", "Domain")
G.add_edge("Rollover.Jobs", "ApplicationServices")
G.add_edge("FlexPlan.Jobs", "ApplicationServices")

# Visualize
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=3000, font_size=10, arrows=True)
plt.savefig('dependency-graph.png')
```

### 4. Calculate Cyclomatic Complexity (if lizard installed)

```python
import lizard

# Analyze C# file
analysis = lizard.analyze_file('CarryoverDollarsDomainService.cs')

for func in analysis.function_list:
    print(f"{func.name}: Complexity {func.cyclomatic_complexity}, "
          f"LOC {func.nloc}, Parameters {func.parameter_count}")
```

---

## 🚀 Analysis Script Template

**Location:** `cortex_brain/admin/RA-Domain/scripts/analyze_csharp.py`

```python
#!/usr/bin/env python3
"""
RA Domain C# Analysis Script
Extracts classes, methods, and dependencies from C# codebase
"""

import os
import json
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_c_sharp as tscsharp
from lxml import etree
from collections import defaultdict

# Initialize C# parser
CS_LANGUAGE = Language(tscsharp.language())
parser = Parser()
parser.set_language(CS_LANGUAGE)

def analyze_csharp_file(filepath):
    """Parse C# file and extract metadata"""
    with open(filepath, 'rb') as f:
        code = f.read()
        tree = parser.parse(code)
    
    classes = []
    methods = []
    
    def traverse(node):
        if node.type == 'class_declaration':
            class_name = next(
                (child.text.decode() for child in node.children 
                 if child.type == 'identifier'),
                'Unknown'
            )
            classes.append({
                'name': class_name,
                'line': node.start_point[0] + 1
            })
        
        elif node.type == 'method_declaration':
            method_name = next(
                (child.text.decode() for child in node.children 
                 if child.type == 'identifier'),
                'Unknown'
            )
            methods.append({
                'name': method_name,
                'line': node.start_point[0] + 1
            })
        
        for child in node.children:
            traverse(child)
    
    traverse(tree.root_node)
    
    return {
        'file': str(filepath),
        'classes': classes,
        'methods': methods
    }

def analyze_csproj(filepath):
    """Extract NuGet packages from .csproj"""
    tree = etree.parse(str(filepath))
    root = tree.getroot()
    
    packages = []
    for pkg in root.xpath('//PackageReference'):
        packages.append({
            'name': pkg.get('Include'),
            'version': pkg.get('Version')
        })
    
    return packages

def main():
    repo_path = Path('C:/PROJECTS/Product.PaymentAccounts')
    output_path = Path('C:/PROJECTS/CORTEX/cortex_brain/admin/RA-Domain/ast-outputs')
    
    # Analyze all C# files
    results = defaultdict(list)
    
    print("Analyzing C# files...")
    for cs_file in repo_path.rglob('*.cs'):
        try:
            analysis = analyze_csharp_file(cs_file)
            results['files'].append(analysis)
        except Exception as e:
            print(f"Error analyzing {cs_file}: {e}")
    
    # Analyze all project files
    print("Analyzing .csproj files...")
    for csproj in repo_path.rglob('*.csproj'):
        try:
            packages = analyze_csproj(csproj)
            results['projects'].append({
                'project': str(csproj),
                'packages': packages
            })
        except Exception as e:
            print(f"Error analyzing {csproj}: {e}")
    
    # Save results
    output_file = output_path / 'complete-analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Analysis complete. Results saved to {output_file}")
    print(f"Total C# files: {len(results['files'])}")
    print(f"Total projects: {len(results['projects'])}")

if __name__ == '__main__':
    main()
```

---

## 📊 Expected Analysis Outputs

| Output File | Content | Tool Used |
|-------------|---------|-----------|
| `complete-analysis.json` | All classes, methods, properties | tree-sitter-c-sharp |
| `dependency-graph.png` | Project dependencies visual | networkx + matplotlib |
| `nuget-packages.json` | All NuGet packages and versions | lxml |
| `complexity-report.txt` | Cyclomatic complexity per method | lizard (optional) |
| `architecture-diagram.png` | Layer visualization | graphviz |

---

## 🔍 Next Steps

1. **Install Recommended Tools:**
   ```bash
   pip install pygments networkx matplotlib graphviz python-dotenv pyyaml
   ```

2. **Create Analysis Script:**
   - Use template above
   - Customize for specific extraction needs

3. **Run Analysis:**
   ```bash
   python cortex_brain/admin/RA-Domain/scripts/analyze_csharp.py
   ```

4. **Review Outputs:**
   - Check `ast-outputs/complete-analysis.json`
   - Visualize with generated diagrams

---

**Status:** ✅ READY - All core tools installed

**tree-sitter-c-sharp:** ✅ Installed and ready for C# AST parsing

