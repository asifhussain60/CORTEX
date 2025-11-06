# KDS Dashboard v8.0 - Quick Reference

## 🚀 Quick Start

```powershell
cd d:\PROJECTS\KDS\dashboard-wpf
dotnet restore
dotnet run --project KDS.Dashboard.WPF
```

## 📁 File Structure

```
dashboard-wpf/
├── KDS.Dashboard.WPF/
│   ├── Models/
│   │   ├── DataModels.cs
│   │   └── DummyData/
│   │       └── DummyDataGenerator.cs  ⚠️ DELETE IN PHASE 1
│   ├── ViewModels/
│   │   ├── ViewModelBase.cs
│   │   ├── ActivityViewModel.cs       ⚠️ USES DUMMY DATA
│   │   ├── ConversationsViewModel.cs  ⚠️ USES DUMMY DATA
│   │   ├── MetricsViewModel.cs        ⚠️ USES DUMMY DATA
│   │   ├── HealthViewModel.cs         ⚠️ USES DUMMY DATA
│   │   └── FeaturesViewModel.cs       ⚠️ USES DUMMY DATA
│   ├── Views/
│   │   ├── ActivityView.xaml
│   │   ├── ConversationsView.xaml
│   │   ├── MetricsView.xaml
│   │   ├── HealthView.xaml
│   │   └── FeaturesView.xaml
│   ├── App.xaml
│   ├── MainWindow.xaml
│   └── KDS.Dashboard.WPF.csproj
├── DUMMY-DATA-README.md        📖 Phase 1 instructions
├── README.md                   📖 Project overview
└── PHASE-0-IMPLEMENTATION-SUMMARY.md

Total: 21 files, ~2,500 lines of code
```

## 🎨 Color Palette

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary | Blue | #5B9BD5 | Icons, primary actions |
| Secondary | Green | #70AD47 | Success, positive metrics |
| Accent | Orange | #ED7D31 | Warnings, highlights |
| Background | Light Gray | #F8F9FA | Page background |
| Surface | White | #FFFFFF | Cards, panels |
| Text | Dark Gray | #2C3E50 | Primary text |
| Text Secondary | Gray | #7F8C8D | Descriptive text |

## 📊 Tab Overview

| Tab | Icon | Purpose | Dummy Data Count |
|-----|------|---------|------------------|
| Activity | 🔥 Flash | Real-time event stream | 50 events |
| Conversations | 💬 MessageText | Last 20 conversations | 20 conversations |
| Metrics | 📊 ChartLine | Development velocity | 3 metric cards |
| Health | ❤️ HeartPulse | Brain health status | 4 health cards |
| Features | ✅ FormatListChecks | Feature inventory | 8 features |

## 🔧 Key Components

### Data Models
```csharp
BrainEvent         // events.jsonl entries
Conversation       // conversation-history.jsonl entries
MetricsData        // development-context.yaml metrics
HealthData         // Brain health calculations
Feature            // Feature inventory items
FeatureStatus      // Enum: FullyImplemented, PartiallyImplemented, DesignedOnly
```

### ViewModels (MVVM)
```csharp
ViewModelBase              // INotifyPropertyChanged base
ActivityViewModel          // Event stream
ConversationsViewModel     // Conversation history
MetricsViewModel          // Development metrics
HealthViewModel           // Brain health
FeaturesViewModel         // Feature inventory
```

## ⚠️ Phase 0 Status

**Current:** Dummy data only (no real brain file access)

**Warning Badge:** "PHASE 0: MOCK DATA" (orange, top-right)

**Dummy Data Markers:**
- `// DUMMY DATA - DELETE THIS BLOCK IN PHASE 1`
- `/// ⚠️ USES DUMMY DATA`
- `/// ⚠️ DUMMY DATA GENERATOR`

## 🚦 Phase Transition

### Delete in Phase 1
```powershell
Remove-Item -Recurse Models/DummyData/
```

### Search and Remove
- `// DUMMY DATA`
- `DummyDataGenerator`
- `/// ⚠️ USES DUMMY DATA`

### Uncomment in Phase 1
- `// LIVE DATA - UNCOMMENT IN PHASE 1`

## 📦 Dependencies

```xml
<PackageReference Include="MaterialDesignThemes" Version="4.9.0" />
<PackageReference Include="MaterialDesignColors" Version="2.1.4" />
<PackageReference Include="LiveChartsCore.SkiaSharpView.WPF" Version="2.0.0-rc2" />
<PackageReference Include="Microsoft.Toolkit.Uwp.Notifications" Version="7.1.3" />
```

## 🧪 Build & Test

```powershell
# Restore packages
dotnet restore

# Build
dotnet build

# Run
dotnet run --project KDS.Dashboard.WPF

# Clean
dotnet clean
```

## 📖 Documentation

- `DUMMY-DATA-README.md` - Phase 1 deletion guide
- `README.md` - Project overview and quick start
- `PHASE-0-IMPLEMENTATION-SUMMARY.md` - Implementation details

## 🎯 Phase 1 Checklist

- [ ] Delete `Models/DummyData/` folder
- [ ] Remove all `// DUMMY DATA` blocks
- [ ] Uncomment live data code
- [ ] Implement FileSystemWatcher
- [ ] Add YAML/JSONL parsing
- [ ] Create ConfigurationHelper
- [ ] Wire up brain file paths
- [ ] Test with real KDS Brain
- [ ] Remove "PHASE 0" warning badge
- [ ] Update window title

## 🔗 Related Files

- Phase Plan: `../docs/KDS-V8-REAL-TIME-INTELLIGENCE-PLAN.md`
- KDS Config: `../kds.config.json`
- Brain Files: `../kds-brain/`

## 💡 Tips

1. **Dummy data is REALISTIC** - Events, conversations, and features match actual KDS v6/v8
2. **All ViewModels have live data code** - Just commented out, ready to uncomment
3. **FileSystemWatcher patterns** - Already documented in ViewModel comments
4. **Material Design icons** - Use `materialDesign:PackIcon Kind="IconName"`
5. **MVVM strictly enforced** - No business logic in code-behind

---

**Status:** Phase 0 Complete ✅  
**Next:** Phase 1 (Live Data Integration)  
**Timeline:** 2-3 weeks
