# Diagram Extraction Instructions

**Purpose:** Store Visual Studio diagram images from Vision API documentation

**Location:** This directory (`cortex-brain/documents/guidelines/architecture/diagrams/`)

---

## Required Diagrams

Extract the following diagrams from the Vision API documentation images provided by user:

### 1. layer-dependency-graph.png
**Source:** First attached image
**Content:** Shows dependency flow between 5 Clean Architecture layers
**Size:** Original resolution

### 2. project-reference-graph.png
**Source:** Second attached image
**Content:** Concrete project structure with .csproj references
**Size:** Original resolution

### 3. application-dependency-graph.png
**Source:** Third attached image
**Content:** Multi-application domain isolation pattern
**Size:** Original resolution

### 4. fee-calculation-dependencies.png
**Source:** Fourth attached image (top half)
**Content:** Dependency diagram for fee calculation example
**Size:** Original resolution

### 5. fee-calculation-sequence.png
**Source:** Fourth attached image (bottom half)
**Content:** Sequence diagram for fee calculation flow
**Size:** Original resolution

### 6. cancel-membership-dependencies.png
**Source:** Fifth attached image (top half)
**Content:** Dependency diagram for cancel membership example
**Size:** Original resolution

### 7. cancel-membership-sequence.png
**Source:** Fifth attached image (bottom half)
**Content:** Sequence diagram for cross-domain call
**Size:** Original resolution

---

## Extraction Process

**Manual Steps (User Action Required):**

1. Save each attached image from Vision API documentation
2. If needed, crop combined images to separate dependencies from sequences
3. Name files according to list above
4. Save to this directory

**Automated Reference:**
Once images are saved, they will be referenced in:
- `architecture-diagrams-and-patterns.md`
- Agent context for visual pattern matching
- Code review validation

---

## Image Specifications

**Format:** PNG (preferred) or JPEG
**Resolution:** Original (do not downscale)
**Color:** As provided in source documentation
**Naming:** Lowercase with hyphens (as listed above)

---

## Usage

These diagrams serve as visual references for:
- Agent training on architectural patterns
- Code review validation
- Developer onboarding
- Architecture decision records

---

**Status:** ⏳ PENDING USER ACTION - Images not yet extracted
**Next Action:** User to save attached images to this directory
