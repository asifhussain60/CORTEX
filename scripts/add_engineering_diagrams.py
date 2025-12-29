"""
Add Mermaid diagrams to engineering onboarding JSON

Generates technically accurate diagrams based on luum-fresh architecture patterns.
"""

import json
import os

def get_stage_diagrams():
    """Return Mermaid diagram definitions for each stage"""
    return {
        1: {
            "title": "N-Tier Architecture Overview",
            "type": "architecture",
            "mermaid_code": """graph TD
    A[Client Browser<br/>Blazor WebAssembly] -->|HTTP/HTTPS| B[API Gateway<br/>ASP.NET Core]
    B --> C[Service Layer<br/>Business Logic]
    C --> D[Data Access Layer<br/>EF Core Repositories]
    D --> E[(SQL Server 2022<br/>Primary Database)]
    C --> F[(Redis Cache<br/>Session & Data)]
    C --> G[(Elasticsearch<br/>Full-text Search)]
    B -->|WebSocket| H[SignalR Hub<br/>Real-time Updates]
    
    style A fill:#00d4ff22,stroke:#00d4ff,stroke-width:2px
    style B fill:#7b61ff22,stroke:#7b61ff,stroke-width:2px
    style C fill:#ffa50022,stroke:#ffa500,stroke-width:2px
    style D fill:#00ff8822,stroke:#00ff88,stroke-width:2px
    style E fill:#ff444422,stroke:#ff4444,stroke-width:2px
    style F fill:#ff444422,stroke:#ff4444,stroke-width:2px
    style G fill:#ff444422,stroke:#ff4444,stroke-width:2px
    style H fill:#7b61ff22,stroke:#7b61ff,stroke-width:2px"""
        },
        2: {
            "title": "Solution & Project Structure",
            "type": "structure",
            "mermaid_code": """graph LR
    subgraph Core["Core Solution (12 projects)"]
        API[API Project<br/>.NET 8]
        Services[Services Layer<br/>Business Logic]
        Domain[Domain Models<br/>Entities]
        Data[Data Access<br/>EF Core]
    end
    
    subgraph Frontend["Frontend Solution (8 projects)"]
        Blazor[Blazor WASM<br/>UI Components]
        Shared[Shared Models<br/>DTOs]
    end
    
    subgraph Tests["Test Solutions (18 projects)"]
        Unit[Unit Tests<br/>xUnit]
        Integration[Integration Tests]
        E2E[E2E Tests]
    end
    
    subgraph Infrastructure["Infrastructure (10 projects)"]
        Auth[Authentication<br/>Identity]
        Cache[Caching<br/>Redis]
        Search[Search<br/>Elasticsearch]
    end
    
    API --> Services
    Services --> Domain
    Services --> Data
    Data --> Domain
    Blazor --> API
    Blazor --> Shared
    
    style API fill:#00d4ff22,stroke:#00d4ff,stroke-width:2px
    style Services fill:#ffa50022,stroke:#ffa500,stroke-width:2px
    style Domain fill:#00ff8822,stroke:#00ff88,stroke-width:2px
    style Data fill:#7b61ff22,stroke:#7b61ff,stroke-width:2px"""
        },
        3: {
            "title": "Service Layer Request Flow",
            "type": "sequence",
            "mermaid_code": """sequenceDiagram
    participant Client as Client App
    participant API as API Controller
    participant Service as Service Layer
    participant Validator as Business Rules
    participant Repo as Repository
    participant Cache as Redis Cache
    participant DB as SQL Database
    
    Client->>+API: POST /api/timesheet/submit
    API->>API: Authenticate & Authorize
    API->>+Service: SubmitTimesheetAsync(dto)
    Service->>+Validator: ValidateBusinessRules()
    Validator-->>-Service: Validation Result
    
    alt Rules Valid
        Service->>+Cache: CheckCache(key)
        Cache-->>-Service: Cache Miss
        Service->>+Repo: GetEmployeeData()
        Repo->>+DB: SELECT * FROM Employees
        DB-->>-Repo: Employee Data
        Repo-->>-Service: Employee Entity
        Service->>Service: Apply Business Logic
        Service->>+Repo: SaveTimesheet()
        Repo->>+DB: INSERT INTO Timesheets
        DB-->>-Repo: Success
        Repo-->>-Service: Saved Entity
        Service->>Cache: UpdateCache(key, data)
        Service-->>-API: Success Result
        API-->>-Client: 200 OK + Response
    else Rules Invalid
        Service-->>API: Validation Errors
        API-->>Client: 400 Bad Request
    end"""
        },
        4: {
            "title": "Core Module Dependencies",
            "type": "dependency",
            "mermaid_code": """graph TB
    subgraph Presentation["Presentation Layer"]
        Controllers[API Controllers<br/>48 controllers]
        Blazor[Blazor Components<br/>203 components]
    end
    
    subgraph Business["Business Logic Layer"]
        TimeService[TimeTrackingService<br/>892 complexity]
        CommuteService[CommutingService<br/>723 complexity]
        ReportService[ReportingService<br/>456 complexity]
        AuthService[AuthService<br/>234 complexity]
    end
    
    subgraph Data["Data Access Layer"]
        TimeRepo[TimeRepo]
        CommuteRepo[CommuteRepo]
        ReportRepo[ReportRepo]
        UserRepo[UserRepo]
    end
    
    subgraph Domain["Domain Models"]
        Entities[Core Entities<br/>67 classes]
        DTOs[Data Transfer Objects<br/>124 classes]
    end
    
    Controllers --> TimeService
    Controllers --> CommuteService
    Controllers --> ReportService
    Controllers --> AuthService
    Blazor --> Controllers
    
    TimeService --> TimeRepo
    CommuteService --> CommuteRepo
    ReportService --> ReportRepo
    AuthService --> UserRepo
    
    TimeRepo --> Entities
    CommuteRepo --> Entities
    ReportRepo --> Entities
    UserRepo --> Entities
    
    TimeService -.-> DTOs
    CommuteService -.-> DTOs
    
    style TimeService fill:#ff444422,stroke:#ff4444,stroke-width:3px
    style CommuteService fill:#ffa50022,stroke:#ffa500,stroke-width:3px
    style ReportService fill:#00d4ff22,stroke:#00d4ff,stroke-width:2px
    style AuthService fill:#00ff8822,stroke:#00ff88,stroke-width:2px"""
        },
        5: {
            "title": "Testing Strategy Pyramid",
            "type": "testing",
            "mermaid_code": """graph TB
    subgraph E2E["E2E Tests (15%)"]
        E2E1[User Journeys<br/>32 scenarios]
        E2E2[Critical Flows<br/>18 scenarios]
    end
    
    subgraph Integration["Integration Tests (25%)"]
        INT1[API Tests<br/>145 tests]
        INT2[Database Tests<br/>89 tests]
        INT3[Service Integration<br/>67 tests]
    end
    
    subgraph Unit["Unit Tests (60%)"]
        UNIT1[Service Tests<br/>523 tests]
        UNIT2[Repository Tests<br/>198 tests]
        UNIT3[Model Tests<br/>156 tests]
        UNIT4[Helper Tests<br/>245 tests]
    end
    
    E2E1 --> INT1
    E2E2 --> INT2
    INT1 --> UNIT1
    INT2 --> UNIT2
    INT3 --> UNIT1
    
    style E2E1 fill:#ff444422,stroke:#ff4444,stroke-width:2px
    style INT1 fill:#ffa50022,stroke:#ffa500,stroke-width:2px
    style UNIT1 fill:#00ff8822,stroke:#00ff88,stroke-width:2px
    style UNIT2 fill:#00ff8822,stroke:#00ff88,stroke-width:2px
    style UNIT3 fill:#00ff8822,stroke:#00ff88,stroke-width:2px
    style UNIT4 fill:#00ff8822,stroke:#00ff88,stroke-width:2px"""
        },
        6: {
            "title": "System Evolution Roadmap",
            "type": "roadmap",
            "mermaid_code": """graph LR
    subgraph Current["Current State (Q4 2025)"]
        Legacy[Legacy Code<br/>Technical Debt: 1847h]
        Monolith[Monolithic Services<br/>High Complexity]
    end
    
    subgraph Phase1["Phase 1: Stabilize (Q1 2026)"]
        Refactor1[Refactor Hot Spots<br/>892→450 complexity]
        Tests1[Increase Coverage<br/>68%→80%]
    end
    
    subgraph Phase2["Phase 2: Modernize (Q2-Q3 2026)"]
        Microservices[Extract Microservices<br/>4 services]
        API[Redesign API<br/>RESTful + GraphQL]
    end
    
    subgraph Phase3["Phase 3: Scale (Q4 2026)"]
        Cloud[Cloud Native<br/>Kubernetes]
        Performance[Performance Tuning<br/>2x throughput]
    end
    
    Legacy --> Refactor1
    Monolith --> Refactor1
    Refactor1 --> Tests1
    Tests1 --> Microservices
    Microservices --> API
    API --> Cloud
    Cloud --> Performance
    
    style Legacy fill:#ff444422,stroke:#ff4444,stroke-width:2px
    style Refactor1 fill:#ffa50022,stroke:#ffa500,stroke-width:2px
    style Tests1 fill:#ffa50022,stroke:#ffa500,stroke-width:2px
    style Microservices fill:#00d4ff22,stroke:#00d4ff,stroke-width:2px
    style API fill:#00d4ff22,stroke:#00d4ff,stroke-width:2px
    style Cloud fill:#00ff8822,stroke:#00ff88,stroke-width:2px
    style Performance fill:#00ff8822,stroke:#00ff88,stroke-width:2px"""
        }
    }

def add_diagrams_to_json(json_path):
    """Add diagram definitions to engineering onboarding JSON"""
    
    # Read existing JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get diagram definitions
    diagrams = get_stage_diagrams()
    
    # Add diagrams to each stage
    for stage in data['stages']:
        stage_id = stage['id']
        if stage_id in diagrams:
            stage['diagram'] = diagrams[stage_id]
    
    # Write updated JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Added {len(diagrams)} diagrams to {json_path}")
    return True

if __name__ == '__main__':
    json_path = 'cortex-brain/dashboards/data/mock/engineering-onboarding.json'
    
    if os.path.exists(json_path):
        add_diagrams_to_json(json_path)
    else:
        print(f"❌ File not found: {json_path}")
        print(f"   Current directory: {os.getcwd()}")
