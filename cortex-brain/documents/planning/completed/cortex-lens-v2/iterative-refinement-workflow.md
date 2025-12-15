# CORTEX Lens V2 - Iterative Refinement Workflow

**Author:** Asif Hussain  
**Version:** 1.0  
**Date:** December 14, 2025  

---

## 🎯 Purpose

Step-by-step guide for iterative UI refinement process using live dashboard preview and structured documentation.

---

## 🔄 Workflow Phases

### **Phase 1: Ground Work Setup**

**Objective:** Prepare foundation for iterative refinement

**Steps:**
1. Extract D3 visualizations from Admin Dashboard
2. Migrate mock data to CORTEX Lens structure
3. Create folder structure in `src/cortex_lens/dashboard/`
4. Setup data binding layer (mock/live abstraction)
5. Build initial dashboard template

**Deliverables:**
- ✅ D3 visualizations extracted and standalone
- ✅ Mock data available in `src/cortex_lens/dashboard/mock_data/`
- ✅ Dashboard builder working with mock data
- ✅ Initial HTML/CSS/JS template functional

**Validation:**
- Dashboard renders without errors
- All 10 tabs visible (even if empty)
- Mock data loads correctly
- CSS styling applied

---

### **Phase 2: Serve Dashboard Locally**

**Objective:** Enable live preview for refinement

**PowerShell HTTP Server:**

```powershell
# Start simple HTTP server in output folder
$port = 8080
$outputPath = "d:\PROJECTS\CORTEX\cortex-lens-output"

# Navigate to output folder
Set-Location $outputPath

# Start Python HTTP server (simple and reliable)
python -m http.server $port

# Dashboard available at: http://localhost:8080
```

**Alternative: PowerShell-Only Server:**

```powershell
# Create server script: serve-dashboard.ps1
$port = 8080
$outputPath = "d:\PROJECTS\CORTEX\cortex-lens-output"

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()

Write-Host "[SERVER] Dashboard serving at http://localhost:$port"
Write-Host "[SERVER] Press Ctrl+C to stop"

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    
    $filePath = Join-Path $outputPath $request.Url.LocalPath.TrimStart('/')
    if ($filePath -eq $outputPath) { $filePath = Join-Path $outputPath "index.html" }
    
    if (Test-Path $filePath) {
        $content = [System.IO.File]::ReadAllBytes($filePath)
        $response.ContentLength64 = $content.Length
        $response.OutputStream.Write($content, 0, $content.Length)
    } else {
        $response.StatusCode = 404
    }
    
    $response.Close()
}
```

**Usage:**
```powershell
# Option 1: Python HTTP server (recommended)
cd d:\PROJECTS\CORTEX\cortex-lens-output
python -m http.server 8080

# Option 2: Custom PowerShell script
.\serve-dashboard.ps1
```

**Deliverables:**
- ✅ HTTP server running on localhost
- ✅ Dashboard accessible in browser
- ✅ Server keeps running during refinement

**Validation:**
- Open `http://localhost:8080` in browser
- Dashboard loads without errors
- Tab navigation works
- CSS/JS assets load correctly

---

### **Phase 3: Iterative Tab Refinement**

**Objective:** Refine each tab one at a time with user feedback

**Per-Tab Workflow:**

#### **Step 1: Review Current Tab**
- Open dashboard in browser
- Navigate to target tab
- Examine current implementation
- Identify gaps or issues

#### **Step 2: User Feedback Session**
- **User examines tab:** What works? What doesn't?
- **User provides requirements:**
  - Visual design changes
  - Data to display
  - Visualizations needed (D3 charts, graphs)
  - Layout adjustments
  - Interactive features

#### **Step 3: Document Requirements**
Create/update tab sub-plan:

**File:** `tab-refinements/tab-{number}-{name}.md`

**Template:**
```markdown
# Tab {Number}: {Name}

**Status:** 🚧 In Refinement  
**Iteration:** 1  
**Last Updated:** {Date}

## 📋 Requirements

### User Feedback (Iteration 1)
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

### Visual Design
- Layout: [Description]
- Colors: [Palette]
- Typography: [Fonts, sizes]
- Spacing: [Grid, padding]

### Data Requirements
- Data sources: [Which collectors?]
- Data format: [Structure]
- Mock data: [Sample JSON]

### Visualizations
- D3 Force Graph: [Architecture relationships]
- Tree Map: [Code distribution]
- Sankey: [Data flows]
- Heatmap: [Complexity/Security]
- Timeline: [Trends]

### Interactive Features
- Tooltips: [On hover]
- Filters: [By category]
- Drill-down: [Details on click]
- Export: [CSV, PNG]

## 🎨 Implementation Plan

1. [Task 1]
2. [Task 2]
3. [Task 3]

## ✅ Acceptance Criteria

- [ ] Visual design matches requirements
- [ ] All data displays correctly
- [ ] Visualizations render without errors
- [ ] Interactive features work
- [ ] Responsive layout
- [ ] No console errors

## 📝 Change Log

### Iteration 1 ({Date})
- Initial requirements gathered
- [Changes made]

### Iteration 2 ({Date})
- [User feedback]
- [Changes made]
```

#### **Step 4: Implement Changes**
- Update HTML template in `src/cortex_lens/dashboard/templates/`
- Modify CSS in `src/cortex_lens/dashboard/styles/`
- Adjust JS in `src/cortex_lens/dashboard/visualizations/`
- Update mock data in `src/cortex_lens/dashboard/mock_data/samples/`

#### **Step 5: Regenerate Dashboard**
```bash
# Rebuild dashboard with changes
cortex-lens analyze /path/to/sample-repo --mock-data --output d:\PROJECTS\CORTEX\cortex-lens-output
```

#### **Step 6: Refresh Browser**
- Reload `http://localhost:8080`
- Navigate to updated tab
- Validate changes

#### **Step 7: User Validation**
- **User reviews changes:** Approved or more refinement?
- **If approved:** Mark tab complete, move to next tab
- **If refinement needed:** Return to Step 2 (new iteration)

#### **Step 8: Update Logs**
- Add entry to `requirements-log.md`
- Update `master-plan.md` progress
- Increment iteration count in tab sub-plan

---

### **Phase 4: Final Integration**

**Objective:** Replace mock data with live AST collectors

**Steps:**
1. Review all tab sub-plans
2. Map mock data to live collectors
3. Update data binding layer (`LiveDataSource`)
4. Test each tab with real repository
5. Validate data accuracy
6. Performance optimization
7. Final polish

**Deliverables:**
- ✅ All tabs working with live data
- ✅ Zero mock data dependencies
- ✅ Performance acceptable (<2s load)
- ✅ Documentation complete

---

## 📊 Tracking Progress

### **Tab Completion Checklist**

| Tab # | Name | Status | Iterations | Completion Date |
|-------|------|--------|------------|-----------------|
| 1 | Executive Summary | ☐ Not Started | 0 | - |
| 2 | Architecture Overview | ☐ Not Started | 0 | - |
| 3 | Code Quality | ☐ Not Started | 0 | - |
| 4 | Security Analysis | ☐ Not Started | 0 | - |
| 5 | API Endpoints | ☐ Not Started | 0 | - |
| 6 | Tech Stack | ☐ Not Started | 0 | - |
| 7 | Dependencies | ☐ Not Started | 0 | - |
| 8 | Test Coverage | ☐ Not Started | 0 | - |
| 9 | Documentation Health | ☐ Not Started | 0 | - |
| 10 | Recommendations | ☐ Not Started | 0 | - |

---

## 🔧 Tools & Commands

### **Generate Dashboard**
```bash
cortex-lens analyze <repo_path> --mock-data --output <output_folder>
```

### **Start Server**
```powershell
cd <output_folder>
python -m http.server 8080
```

### **View Dashboard**
```
http://localhost:8080
```

### **Stop Server**
```
Ctrl+C (in PowerShell terminal)
```

---

## 📝 Documentation Requirements

**After Each Refinement Session:**
1. ✅ Update tab sub-plan with user feedback
2. ✅ Log requirements in `requirements-log.md`
3. ✅ Update master plan progress
4. ✅ Commit changes to git (optional but recommended)

**After Tab Completion:**
1. ✅ Mark tab complete in progress table
2. ✅ Update master plan with final design
3. ✅ Archive iteration history
4. ✅ Move to next tab

---

## 🎯 Success Criteria

**Ground Work Complete When:**
- ✅ Dashboard serves without errors
- ✅ All 10 tabs visible
- ✅ Mock data loads correctly
- ✅ CSS styling applied

**Tab Refinement Complete When:**
- ✅ User approves visual design
- ✅ All data displays correctly
- ✅ Visualizations functional
- ✅ No console errors
- ✅ Acceptance criteria met

**Final Integration Complete When:**
- ✅ All tabs work with live data
- ✅ Zero mock dependencies
- ✅ Performance acceptable
- ✅ Documentation complete

---

**Process Owner:** Asif Hussain  
**Last Updated:** December 14, 2025
