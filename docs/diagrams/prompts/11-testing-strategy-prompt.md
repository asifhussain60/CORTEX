# DALL-E Prompt: Testing Strategy

## Visual Composition
- **Layout:** Testing pyramid with quality gates and metrics dashboard
- **Orientation:** Portrait (9:16 aspect ratio) emphasizing vertical test hierarchy
- **Pyramid Structure:** Three-tier pyramid showing test distribution
- **Supporting Elements:** CI/CD integration, coverage metrics, quality gates

## Color Palette
- **Unit Tests (Base):** Green (#96ceb4) - Foundation layer
- **Integration Tests (Middle):** Blue (#4d96ff) - Integration layer
- **E2E/UI Tests (Top):** Purple (#9b59b6) - User-facing layer
- **Quality Gates:** Orange (#ff8c42) - Validation checkpoints
- **Coverage Metrics:** Turquoise (#4ecdc4) - Statistics panel
- **Pass/Fail Indicators:** Success Green (#28a745), Failure Red (#ff6b6b)
- **Background:** Light Gray (#f8f9fa) with test pattern overlay

## Components & Elements

### Testing Pyramid (Center)
- **Position:** Central 50% of canvas (30-80% vertical)
- **Visual:** Three-tier pyramid with distinct color bands
- **Total Height:** 600px
- **Base Width:** 500px tapering to 150px at top

#### Tier 1: Unit Tests (Base - Green)
- **Position:** Bottom tier (60% of pyramid height)
- **Visual:** Wide green trapezoid
- **Label:** "UNIT TESTS" in white text
- **Size:** 500px wide x 360px tall
- **Details Panel (Inside):**
  - **Test Count:** "1,247 tests"
  - **Coverage:** "92% code coverage"
  - **Speed:** "< 5s execution"
  - **Examples:** "Function tests, Class tests, Module tests"
- **Icon:** Microscope symbol at center
- **Status Bar:** Green progress bar showing "100% passing"

#### Tier 2: Integration Tests (Middle - Blue)
- **Position:** Middle tier (30% of pyramid height)
- **Visual:** Medium blue trapezoid
- **Label:** "INTEGRATION TESTS" in white text
- **Size:** 320px wide x 180px tall
- **Details Panel (Inside):**
  - **Test Count:** "342 tests"
  - **Coverage:** "78% API coverage"
  - **Speed:** "< 30s execution"
  - **Examples:** "API tests, Database tests, Service integration"
- **Icon:** Link/chain symbol at center
- **Status Bar:** Blue progress bar showing "98% passing"

#### Tier 3: E2E/UI Tests (Top - Purple)
- **Position:** Top tier (10% of pyramid height)
- **Visual:** Narrow purple trapezoid
- **Label:** "E2E & UI TESTS" in white text
- **Size:** 150px wide x 60px tall
- **Details Panel (Inside):**
  - **Test Count:** "87 tests"
  - **Coverage:** "Critical user paths"
  - **Speed:** "< 5min execution"
  - **Examples:** "User workflows, UI components, Browser tests"
- **Icon:** Computer/browser symbol at center
- **Status Bar:** Purple progress bar showing "95% passing"

### Test Ratio Display (Bottom-Right of Pyramid)
- **Position:** Bottom-right corner (85% from top)
- **Visual:** Circular pie chart showing test distribution
- **Label:** "TEST DISTRIBUTION"
- **Size:** 180px diameter
- **Segments:**
  - Green: 70% (Unit tests)
  - Blue: 20% (Integration tests)
  - Purple: 10% (E2E/UI tests)
- **Center Label:** "70:20:10 RATIO"

### Quality Gates (Left Side)
- **Position:** Left side of pyramid (20% from left edge)
- **Visual:** Vertical sequence of checkpoint circles
- **Label:** "QUALITY GATES" at top
- **Gates (Top to Bottom):**
  
  **Gate 1: Code Quality**
  - Circle with checkmark icon
  - Status: 🟢 Pass
  - Metrics: "Lint: 0 errors, Complexity: <10"
  
  **Gate 2: Coverage Threshold**
  - Circle with percentage icon
  - Status: 🟢 Pass
  - Metrics: "Unit: ≥80%, Integration: ≥60%"
  
  **Gate 3: Security Scan**
  - Circle with shield icon
  - Status: 🟢 Pass
  - Metrics: "0 High vulnerabilities"
  
  **Gate 4: Performance**
  - Circle with speedometer icon
  - Status: 🟡 Warning
  - Metrics: "Test execution: 2m 47s (target <2m)"
  
- **Connecting Lines:** Dotted lines from gates to pyramid tiers
- **Size:** Each gate 60px diameter

### CI/CD Integration (Right Side)
- **Position:** Right side of pyramid (80% from left edge)
- **Visual:** Vertical pipeline flow with stages
- **Label:** "CI/CD PIPELINE" at top
- **Stages:**
  
  **Stage 1: Commit**
  - Icon: Git commit symbol
  - Action: "Trigger on push"
  
  **Stage 2: Build**
  - Icon: Hammer/wrench
  - Action: "Compile & Package"
  
  **Stage 3: Test**
  - Icon: Play button
  - Action: "Run pyramid tests"
  - Connected to pyramid (arrow pointing)
  
  **Stage 4: Quality Check**
  - Icon: Magnifying glass
  - Action: "Validate gates"
  - Connected to quality gates (arrow pointing)
  
  **Stage 5: Deploy**
  - Icon: Rocket
  - Status: "✓ Deploy if all pass"
  
- **Size:** Each stage 80px x 50px
- **Style:** Vertical flow with arrows between stages

### Coverage Metrics Dashboard (Top)
- **Position:** Top of canvas (5% from top)
- **Visual:** Horizontal metrics bar with key statistics
- **Label:** "TEST METRICS DASHBOARD"
- **Metrics (Left to Right):**
  
  - **Total Tests:** "1,676 tests"
  - **Pass Rate:** "98.2%" (green)
  - **Execution Time:** "2m 47s"
  - **Code Coverage:** "87%" (green progress circle)
  - **Flaky Tests:** "3" (yellow warning)
  
- **Size:** 600px x 100px
- **Style:** Rounded rectangle with white background, colored badges

### Test Execution Timeline (Bottom)
- **Position:** Bottom of canvas (95% from top)
- **Visual:** Horizontal timeline showing test execution phases
- **Label:** "EXECUTION TIMELINE"
- **Phases (Left to Right):**
  - Unit Tests: 0-5s (green bar)
  - Integration Tests: 5-35s (blue bar)
  - E2E Tests: 35-167s (purple bar)
  - Reporting: 167-172s (turquoise bar)
- **Total Duration:** "2m 47s" label at right end
- **Style:** Stacked horizontal bars with time markers

## Typography & Labels

### Pyramid Tier Headers
- **Font:** Bold sans-serif, 24pt
- **Color:** White (#ffffff)
- **Position:** Center of each tier
- **Style:** ALL CAPS

### Detail Text Inside Tiers
- **Font:** Regular sans-serif, 11pt
- **Color:** White (#ffffff) with slight transparency
- **Position:** Below tier headers
- **Format:** Bulleted list

### Gate Labels
- **Font:** Medium sans-serif, 12pt
- **Position:** Below each gate circle
- **Color:** Dark Gray (#2c3e50)

### Metric Values
- **Font:** Bold sans-serif, 16pt
- **Position:** In metrics dashboard and ratio display
- **Color:** Matches tier color or status (green/yellow/red)

### Section Headers
- **Font:** Bold sans-serif, 18pt
- **Position:** Above each major component
- **Color:** Dark Gray (#2c3e50)
- **Style:** ALL CAPS

## Technical Accuracy

### Test Pyramid Principles
- **70:20:10 Ratio:** Unit tests form foundation, E2E tests are minimal
- **Speed Hierarchy:** Unit tests fastest (<5s), E2E slowest (<5min)
- **Coverage Goals:** Unit ≥80%, Integration ≥60%, E2E critical paths only
- **Cost vs Value:** More unit tests = cheaper, faster, more maintainable

### Quality Gate Requirements
- **Code Quality:** Linting, complexity analysis, style enforcement
- **Coverage:** Minimum thresholds enforced before deployment
- **Security:** Vulnerability scanning, dependency audits
- **Performance:** Test execution time budgets

### CI/CD Integration Points
- **Trigger:** Automated on every commit/PR
- **Parallel Execution:** Unit and integration tests run concurrently
- **Fast Feedback:** Unit tests complete first for quick failures
- **Deployment Gate:** All tests + quality gates must pass

### Test Types Shown
- **Unit:** Function-level, class-level, module-level isolation
- **Integration:** API contracts, database interactions, service communication
- **E2E:** User workflows, UI components, browser automation

## Style & Aesthetic
- **Design Language:** Modern software quality visualization
- **Detail Level:** High - show specific metrics and counts
- **Visual Metaphor:** Pyramid = solid testing foundation
- **Professional:** Enterprise quality assurance documentation
- **Data-Driven:** Emphasize metrics and measurable quality

## Mood & Atmosphere
- **Structured & Methodical:** Clear testing hierarchy
- **Quality-Focused:** Multiple validation checkpoints
- **Automated & Continuous:** CI/CD integration throughout
- **Transparent:** All metrics visible and measurable
- **Confidence-Inspiring:** High pass rates, comprehensive coverage

## Output Specifications
- **Resolution:** 1440x2560 (Portrait, 2K)
- **Format:** PNG with transparency
- **DPI:** 300
- **Accessibility:** WCAG AA contrast
- **File Size:** <550KB

## Usage Context
- **Quality Documentation:** Testing strategy overview
- **Developer Onboarding:** Understanding test approach
- **CI/CD Documentation:** Test pipeline visualization
- **Stakeholder Reports:** Quality metrics communication

## DALL-E Generation Instruction

**Primary Prompt:**
"Create professional testing pyramid diagram for software quality assurance. Center shows three-tier pyramid: wide green base (Unit Tests, 1247 tests, 92% coverage), medium blue middle (Integration Tests, 342 tests, 78% coverage), narrow purple top (E2E Tests, 87 tests, 5min execution). Pyramid annotated with test counts, coverage percentages, and execution times. Left side shows 4 quality gate checkpoints (Code Quality, Coverage, Security, Performance) with pass/warning status indicators. Right side shows vertical CI/CD pipeline (Commit → Build → Test → Quality Check → Deploy) connected to pyramid with arrows. Top has horizontal metrics dashboard showing total tests (1676), pass rate (98.2%), execution time (2m 47s), code coverage (87%). Bottom shows execution timeline with stacked bars (green/blue/purple/turquoise) showing test phase durations. Bottom-right has pie chart showing 70:20:10 test distribution. Light gray background. Portrait orientation. Professional quality assurance visualization."

**Refinement Prompt:**
"Add more detail to pyramid tier internals. Show status bars inside each tier indicating pass rate. Include specific icons (microscope for unit tests, chain for integration, browser for E2E). Make quality gates more prominent with larger checkmark/warning icons. Add connecting dotted lines from gates to relevant pyramid tiers. Include flaky test indicator (3 flaky tests) in metrics dashboard. Show time markers on execution timeline (0s, 5s, 35s, 167s)."