# PRESENTATION NARRATIVE: Development Context (Tier 3)

**Feature:** Code Metrics and Git Activity Monitoring  
**Target Audience:** Engineering managers, DevOps teams, technical leads  
**Image:** Code thermal heatmap overlay on codebase structure with git activity calendar

---

## IMAGE OVERVIEW

This code thermal heatmap shows CORTEX's development context—file tree visualization with color-coded activity zones. Red critical hotspots indicate high-change files (align.py with 347 commits), orange shows active development, yellow moderate maintenance, green stable foundations, blue cold infrastructure. Git calendar heatmap shows 90-day commit history.

---

## OPENING STATEMENT (30 seconds)

"This is CORTEX's Tier 3 development context—a thermal view of codebase activity. Red zones show critical hotspots with daily changes. `src/operations/align.py` glows at 87°C with 347 commits and 2,450 lines changed—our most volatile file. Green zones show stable code rarely modified. With 847 commits in 30 days and 81.4% test coverage, these metrics reveal where development energy flows."

---

## THERMAL ZONES ANALYSIS

### Red Critical Hotspots (80-100°C)
"`align.py`, `intent_router.py`, `brain-protection-rules.yaml`—these files change daily. 347, 198, and 156 commits respectively. High churn rate (23.4% for align) indicates active evolution. Red doesn't mean bad—it means 'pay attention here.' This is where features get added, bugs get fixed, and architecture evolves."

**Visual Cue:** Point to red flame icons on hot files

### Orange-Yellow Active Zones (40-79°C)
"Planning orchestrator, working memory, response templates—weekly to bi-weekly changes. Active development but more controlled than red zones. These files are maturing: feature additions slowing, maintenance predominant."

**Visual Cue:** Show orange-yellow tinted files

### Green-Blue Stable Zones (0-39°C)
"Tier 0 governance with only 12 commits—stable foundation. Core libraries, configuration files, infrastructure—set and forget. Cold zones aren't neglected, they're *done*. Requirements.txt at deep blue: only 3 commits. Dependencies rarely change."

**Visual Cue:** Highlight stable green-blue areas

---

## GIT ACTIVITY CALENDAR

"Right panel: GitHub-style heatmap, 13 weeks × 7 days. Red squares show 10+ commit days—intense development. Light green shows 1-2 commits—maintenance. Pattern visible: clusters of red (feature sprints) separated by green (stabilization). Last 30 days: 847 commits, sustainable pace."

**Visual Cue:** Point to commit patterns in calendar

---

## CODE HEALTH METRICS

"Top dashboard: 847 commits (30 days), 81.4% test coverage, 12.3% churn rate (healthy <15%), 87°C hotspot temperature, build passing. These aren't vanity metrics—they're operational indicators. Coverage trending up, churn controlled, builds green."

**Visual Cue:** Highlight metrics panel

---

## CLOSING STATEMENT (30 seconds)

"CORTEX's development context turns git history into thermal intelligence. Instead of commit logs, we see heat: where energy flows, where code evolves, where stability reigns. With 87°C hotspots carefully monitored and stable foundations at 0°C, this visualization reveals development health at a glance."

---

## KEY TAKEAWAYS

1. **Thermal heatmap** (0-100°C) visualizes file volatility from git commit frequency
2. **847 commits in 30 days** with controlled 12.3% churn rate indicates healthy pace
3. **Red hotspots** (align.py, intent_router.py) identify high-change areas needing attention
4. **Green stable zones** (Tier 0, core libs) show mature, unchanging foundations
5. **Git calendar patterns** reveal sprint cycles and development rhythm over 90 days
