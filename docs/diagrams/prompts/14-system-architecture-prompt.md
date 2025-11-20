# DALL-E Prompt: System Architecture

## Visual Composition
- **Layout:** Comprehensive system architecture with multiple interconnected layers
- **Orientation:** Landscape (16:9 aspect ratio) showing full system scope
- **Architectural Style:** Layered architecture with hexagonal components
- **Integration View:** External services, internal modules, data flow

## Color Palette
- **Presentation Layer:** Purple (#9b59b6) - User interface
- **Application Layer:** Blue (#4d96ff) - Business logic
- **Domain Layer:** Turquoise (#4ecdc4) - Core domain
- **Infrastructure Layer:** Green (#96ceb4) - Data persistence
- **External Services:** Orange (#ff8c42) - Third-party integrations
- **Security Layer:** Red (#ff6b6b) - Authentication/authorization
- **Monitoring:** Yellow (#ffd93d) - Observability
- **Data Flow:** Gray (#6c757d) with directional arrows
- **Background:** Light gradient (#f8f9fa → #e9ecef)

## Components & Elements

### Layer 1: Presentation Layer (Top - Purple)
- **Position:** Top 15% of canvas
- **Visual:** Horizontal band with component hexagons
- **Label:** "PRESENTATION LAYER"
- **Color:** Purple gradient (#9b59b6 → #8e44ad)
- **Components (Left to Right):**
  
  **Component 1.1: GitHub Copilot Chat**
  - Hexagon (120px)
  - Icon: VS Code logo + chat bubble
  - Label: "Copilot Chat Interface"
  - Input: User natural language
  
  **Component 1.2: CLI Interface**
  - Hexagon (120px)
  - Icon: Terminal/command prompt
  - Label: "Command Line"
  - Input: Terminal commands
  
  **Component 1.3: VS Code Extension**
  - Hexagon (120px)
  - Icon: VS Code extension icon
  - Label: "CORTEX Extension"
  - Features: Quick actions, status bar
  
  **Component 1.4: Web UI (Future)**
  - Hexagon (120px, dashed outline)
  - Icon: Browser window
  - Label: "Web Dashboard"
  - Status: Planned

### Layer 2: Application Layer (Upper-Middle - Blue)
- **Position:** 25-45% from top
- **Visual:** Horizontal band with larger hexagons
- **Label:** "APPLICATION LAYER"
- **Color:** Blue gradient (#4d96ff → #3a7bd5)
- **Components (2 rows):**
  
  **Row 1: Orchestration (Left to Right)**
  
  **Component 2.1: Intent Router**
  - Hexagon (140px)
  - Icon: Traffic router symbol
  - Label: "Intent Detection & Routing"
  - Function: Parse requests, route to agents
  
  **Component 2.2: Agent Orchestrator**
  - Hexagon (140px)
  - Icon: Conductor with baton
  - Label: "Agent Coordination"
  - Function: Manage agent lifecycle
  
  **Component 2.3: Operation Manager**
  - Hexagon (140px)
  - Icon: Gear with checklist
  - Label: "Operation Execution"
  - Function: Execute workflows
  
  **Row 2: Agents (Left to Right)**
  
  **Component 2.4: Work Planner**
  - Hexagon (100px)
  - Icon: Calendar with tasks
  - Label: "Planning Agent"
  
  **Component 2.5: Code Executor**
  - Hexagon (100px)
  - Icon: Code brackets with play
  - Label: "Execution Agent"
  
  **Component 2.6: Tester**
  - Hexagon (100px)
  - Icon: Microscope
  - Label: "Testing Agent"
  
  **Component 2.7: Validator**
  - Hexagon (100px)
  - Icon: Checkmark shield
  - Label: "Validation Agent"

### Layer 3: Domain Layer (Middle - Turquoise)
- **Position:** 50-65% from top
- **Visual:** Horizontal band with core domain hexagons
- **Label:** "DOMAIN LAYER (Core Brain)"
- **Color:** Turquoise gradient (#4ecdc4 → #00b4d8)
- **Components (Left to Right):**
  
  **Component 3.1: Tier 0 - Brain Protection**
  - Hexagon (130px)
  - Icon: Shield with brain
  - Label: "Brain Protector"
  - Function: SKULL rule enforcement
  
  **Component 3.2: Tier 1 - Working Memory**
  - Hexagon (130px)
  - Icon: RAM chip
  - Label: "Conversation Manager"
  - Function: Active conversation tracking
  
  **Component 3.3: Tier 2 - Knowledge Graph**
  - Hexagon (130px)
  - Icon: Network nodes
  - Label: "Pattern Matcher"
  - Function: Learned patterns, relationships
  
  **Component 3.4: Tier 3 - Context Engine**
  - Hexagon (130px)
  - Icon: Book with magnifying glass
  - Label: "Document Analyzer"
  - Function: Codebase understanding

### Layer 4: Infrastructure Layer (Lower-Middle - Green)
- **Position:** 70-85% from top
- **Visual:** Horizontal band with data/service hexagons
- **Label:** "INFRASTRUCTURE LAYER"
- **Color:** Green gradient (#96ceb4 → #52b788)
- **Components (Left to Right):**
  
  **Component 4.1: SQLite Databases**
  - Hexagon (120px)
  - Icon: Database cylinder
  - Label: "Local Storage"
  - Databases: Tier1, Tier2, Tier3 DBs
  
  **Component 4.2: File System**
  - Hexagon (120px)
  - Icon: Folder tree
  - Label: "Brain Files"
  - Storage: YAML configs, logs
  
  **Component 4.3: Cache Layer**
  - Hexagon (120px)
  - Icon: Lightning bolt + database
  - Label: "Performance Cache"
  - Function: Fast data access
  
  **Component 4.4: Plugin Registry**
  - Hexagon (120px)
  - Icon: Puzzle piece
  - Label: "Plugin System"
  - Function: Extension management

### Security Layer (Left Side Vertical - Red)
- **Position:** Left edge, spanning 20-80% height
- **Visual:** Vertical band with shield components
- **Label:** "SECURITY & GOVERNANCE"
- **Color:** Red gradient (#ff6b6b → #dc3545)
- **Width:** 150px
- **Components (Top to Bottom):**
  
  **Component S.1: Authentication**
  - Icon: Key with user
  - Label: "Auth Manager"
  - Function: User identity verification
  
  **Component S.2: Authorization**
  - Icon: Lock with permissions
  - Label: "Access Control"
  - Function: Permission enforcement
  
  **Component S.3: Input Validation**
  - Icon: Shield with checkmark
  - Label: "Input Sanitizer"
  - Function: Injection prevention
  
  **Component S.4: Audit Logger**
  - Icon: Scroll with pen
  - Label: "Audit Trail"
  - Function: All actions logged

### Monitoring Layer (Right Side Vertical - Yellow)
- **Position:** Right edge, spanning 20-80% height
- **Visual:** Vertical band with monitoring components
- **Label:** "MONITORING & OBSERVABILITY"
- **Color:** Yellow gradient (#ffd93d → #ffc107)
- **Width:** 150px
- **Components (Top to Bottom):**
  
  **Component M.1: Health Monitor**
  - Icon: Heartbeat
  - Label: "System Health"
  - Metrics: CPU, Memory, Disk
  
  **Component M.2: Performance Tracker**
  - Icon: Speedometer
  - Label: "Performance"
  - Metrics: Response time, throughput
  
  **Component M.3: Error Tracker**
  - Icon: Bug with magnifying glass
  - Label: "Error Monitoring"
  - Function: Exception tracking
  
  **Component M.4: Usage Analytics**
  - Icon: Bar chart
  - Label: "Analytics"
  - Metrics: Commands, patterns

### External Services (Bottom - Orange)
- **Position:** Bottom 10% of canvas
- **Visual:** Horizontal row of service boxes
- **Label:** "EXTERNAL INTEGRATIONS"
- **Color:** Orange gradient (#ff8c42 → #fd7e14)
- **Services (Left to Right):**
  
  **Service 1: GitHub API**
  - Rectangle (100px x 60px)
  - Icon: GitHub logo
  - Function: Repository operations
  
  **Service 2: LLM Providers**
  - Rectangle (100px x 60px)
  - Icon: Cloud with AI
  - Options: OpenAI, Anthropic
  
  **Service 3: VS Code API**
  - Rectangle (100px x 60px)
  - Icon: VS Code logo
  - Function: Editor integration
  
  **Service 4: SQLite**
  - Rectangle (100px x 60px)
  - Icon: Database
  - Function: Embedded database
  
  **Service 5: Python Ecosystem**
  - Rectangle (100px x 60px)
  - Icon: Python logo
  - Function: Runtime environment

## Data Flow Arrows

### User Request Flow (Purple → Blue → Turquoise)
- **Path:** Presentation → Application → Domain
- **Style:** Solid arrows with gradient (4px)
- **Labels:** "User Request", "Intent Parsed", "Pattern Matched"
- **Example Flow:**
  - Copilot Chat → Intent Router → Work Planner → Tier 2 Knowledge Graph

### Response Flow (Turquoise → Blue → Purple)
- **Path:** Domain → Application → Presentation
- **Style:** Solid arrows with gradient (4px)
- **Labels:** "Context Enriched", "Response Generated", "User Reply"
- **Example Flow:**
  - Tier 1 Working Memory → Agent Orchestrator → Copilot Chat

### Data Persistence Flow (Blue ↔ Green)
- **Path:** Application ↔ Infrastructure
- **Style:** Bidirectional dashed arrows (3px)
- **Labels:** "Read/Write", "Cache", "Store"
- **Example Flow:**
  - Conversation Manager ↔ Tier1 SQLite Database

### Security Flow (Red → All Layers)
- **Path:** Security Layer → All components
- **Style:** Dotted lines with lock icons (2px)
- **Labels:** "Auth Check", "Validate Input", "Audit Log"
- **Coverage:** Security layer intersects all request/response flows

### Monitoring Flow (All Layers → Yellow)
- **Path:** All components → Monitoring Layer
- **Style:** Thin dotted lines with metrics icons (1px)
- **Labels:** "Health Check", "Performance Metric", "Error Report"
- **Coverage:** All components send telemetry to monitoring

### External Service Flow (Infrastructure ↔ Orange)
- **Path:** Infrastructure Layer ↔ External Services
- **Style:** Dashed arrows with API icon (3px)
- **Labels:** "API Call", "Response", "Integration"
- **Example Flow:**
  - Plugin Registry ↔ GitHub API

## Typography & Labels

### Layer Headers
- **Font:** Bold sans-serif, 24pt
- **Color:** White on layer background
- **Position:** Left side of each layer band
- **Style:** ALL CAPS with icon

### Component Labels
- **Font:** Medium sans-serif, 11pt
- **Color:** White on hexagon background
- **Position:** Below component icon inside hexagon
- **Format:** Title case

### Function Descriptions
- **Font:** Regular sans-serif, 8pt
- **Color:** Dark gray (#2c3e50)
- **Position:** Small callout box near component
- **Format:** Brief description

### Flow Labels
- **Font:** Italic sans-serif, 9pt
- **Position:** Along arrows
- **Color:** Matches arrow color
- **Background:** White pill for readability

### Legend (Bottom-Left Corner)
- **Font:** Regular sans-serif, 10pt
- **Position:** Bottom-left corner (5% from edges)
- **Content:**
  - Solid arrow: Request/Response flow
  - Dashed arrow: Data persistence
  - Dotted line: Security/Monitoring
  - Hexagon: Core component
  - Rectangle: External service

## Technical Accuracy

### Architectural Principles
- **Separation of Concerns:** Each layer has distinct responsibility
- **Dependency Direction:** Outer layers depend on inner layers
- **Security by Design:** Security layer intersects all flows
- **Observability:** Monitoring throughout system

### Layer Responsibilities
- **Presentation:** User interface, input/output handling
- **Application:** Business logic, orchestration, agent management
- **Domain:** Core CORTEX brain functionality, knowledge management
- **Infrastructure:** Data persistence, caching, plugin system
- **Security:** Cross-cutting authentication, authorization, validation
- **Monitoring:** Cross-cutting health checks, metrics, logging

### Integration Points
- **GitHub API:** Repository operations, PR management
- **LLM Providers:** OpenAI/Anthropic for AI capabilities
- **VS Code API:** Editor integration, extension capabilities
- **SQLite:** Embedded database for brain tiers
- **Python Ecosystem:** Runtime environment, package management

### Data Flow Patterns
- **Request-Response:** User → System → User
- **Event-Driven:** Agent coordination, plugin triggers
- **Pub/Sub:** Monitoring events, audit logs
- **Caching:** Performance optimization

## Style & Aesthetic
- **Design Language:** Modern enterprise architecture diagram
- **Detail Level:** High - show all major components and flows
- **Visual Metaphor:** Layered cake with cross-cutting concerns
- **Professional:** Enterprise architecture documentation quality
- **Comprehensive:** Full system view in single diagram

## Mood & Atmosphere
- **Structured & Organized:** Clear layer separation
- **Secure & Monitored:** Security and observability prominent
- **Extensible:** Plugin system visible
- **Enterprise-Ready:** Professional architecture
- **Integrated:** External service connections clear

## Output Specifications
- **Resolution:** 2560x1440 (Landscape, 2K)
- **Format:** PNG with transparency
- **DPI:** 300
- **Accessibility:** WCAG AA contrast
- **File Size:** <650KB

## Usage Context
- **Architecture Documentation:** System overview for developers
- **Technical Presentations:** Stakeholder communication
- **Onboarding:** New team member orientation
- **Design Reviews:** Architecture validation

## DALL-E Generation Instruction

**Primary Prompt:**
"Create comprehensive enterprise system architecture diagram for CORTEX AI assistant. Four horizontal layers: Presentation (purple #9b59b6, top 15%, hexagons for Copilot Chat/CLI/VS Code Extension), Application (blue #4d96ff, 2 rows showing Intent Router/Agent Orchestrator/Operation Manager + 4 agent hexagons), Domain (turquoise #4ecdc4, 4 brain tier hexagons: Tier 0-3), Infrastructure (green #96ceb4, SQLite/FileSystem/Cache/Plugins hexagons). Left vertical red security band (#ff6b6b, Auth/Access/Validation/Audit). Right vertical yellow monitoring band (#ffd93d, Health/Performance/Errors/Analytics). Bottom orange external services row (#ff8c42, GitHub/LLM/VSCode/SQLite/Python rectangles). Show data flows: purple-blue-turquoise request path, turquoise-blue-purple response path, dashed blue-green persistence, dotted security intersections, thin monitoring telemetry. All components as hexagons (100-140px) except external services (rectangles 100x60px). Light gradient background. Professional enterprise architecture style. Legend in bottom-left corner."

**Refinement Prompt:**
"Add more detail to components with specific icons (VS Code logo, GitHub logo, brain symbols, database cylinders, shield icons). Show bidirectional arrows between layers. Include component labels with brief function descriptions in small callout boxes. Make security and monitoring bands semi-transparent so underlying layers are visible. Add gradient effects to layer backgrounds. Include flow labels on major arrows ('User Request', 'Context Enriched', 'API Call'). Show lock icons on security flow lines and metric icons on monitoring lines."