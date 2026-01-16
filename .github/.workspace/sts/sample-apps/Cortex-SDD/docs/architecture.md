# Cortex-SDD Architecture Documentation

**Author:** Asif Hussain  
**Version:** 1.0.0  
**Last Updated:** December 9, 2025

---

## 🏛️ Architecture Overview

Cortex-SDD follows **Clean Architecture** principles with **Domain-Driven Design (DDD)** patterns, implementing a 4-layer architecture that ensures separation of concerns, testability, and maintainability.

---

## 📐 Architectural Layers

### Layer 1: Domain Layer (Core)
**Location:** `js/domain/`  
**Purpose:** Core business logic and entities  
**Dependencies:** NONE (fully isolated)

#### Components:
- **`entities.js`** - Business entities (Task, User, Comment)
- **`enums.js`** - Domain enumerations (Priority, Status, Role)

#### Characteristics:
- ✅ No external dependencies
- ✅ Pure business logic
- ✅ Framework-agnostic
- ✅ Highly testable
- ✅ Reusable across projects

#### Example:
```javascript
export class Task {
    constructor(title, description, priority, status) {
        // Validation
        if (!title || title.trim() === '') {
            throw new Error('Task title is required');
        }
        // Domain logic
        this.id = generateId();
        this.title = title.trim();
        // ...
    }
    
    isOverdue() {
        // Business rule
        return new Date() > new Date(this.dueDate);
    }
}
```

---

### Layer 2: Infrastructure Layer
**Location:** `js/infrastructure/`  
**Purpose:** External systems, data access, security  
**Dependencies:** Domain Layer, Utilities

#### Components:
- **`mock-db.js`** - In-memory database with localStorage
- **`repositories.js`** - Repository pattern (TaskRepository, UserRepository)
- **`security.js`** - Authentication, authorization, cryptography

#### Characteristics:
- ✅ Repository pattern for data access
- ✅ Singleton database instance
- ✅ localStorage persistence
- ✅ Security abstractions
- ✅ Swappable implementations

#### Data Flow:
```
Component → Repository → Database → LocalStorage
         ←              ←          ←
```

#### Example:
```javascript
export class TaskRepository extends BaseRepository {
    async getAll() {
        return [...this.getCollection()];
    }
    
    async create(taskData) {
        const task = new Task(...taskData);
        this.getCollection().push(task);
        this.save(); // Persist to localStorage
        return task;
    }
}
```

---

### Layer 3: Application Layer
**Location:** `js/application/`  
**Purpose:** Use cases, business workflows, validation  
**Dependencies:** Domain Layer, Infrastructure Layer

#### Components (To Be Implemented - Phase 2):
- **`services.js`** - Business logic services (TaskService, AuthService)
- **`validators.js`** - Input validation
- **`dtos.js`** - Data transfer objects

#### Characteristics:
- ✅ Orchestrates domain logic
- ✅ Coordinates repositories
- ✅ Validates inputs
- ✅ Transforms data
- ✅ Implements use cases

#### Example (Phase 2):
```javascript
export class TaskService {
    constructor() {
        this.taskRepo = new TaskRepository();
        this.userRepo = new UserRepository();
    }
    
    async createTask(dto) {
        // Validate
        TaskValidator.validate(dto);
        
        // Business logic
        const task = await this.taskRepo.create(dto);
        
        // Notify assignee
        await this.notifyAssignee(task);
        
        return task;
    }
}
```

---

### Layer 4: Presentation Layer
**Location:** `js/presentation/`  
**Purpose:** UI components, routing, user interaction  
**Dependencies:** Application Layer

#### Components (To Be Implemented - Phase 3):
- **`router.js`** - Client-side routing
- **`components/`** - UI components (navbar, task-list, task-form, etc.)

#### Characteristics:
- ✅ Component-based architecture
- ✅ Event-driven
- ✅ Reactive updates
- ✅ Separation from business logic
- ✅ Testable UI

#### Example (Phase 3):
```javascript
export class TaskListComponent {
    constructor(container, taskService) {
        this.container = container;
        this.taskService = taskService;
    }
    
    async render() {
        const tasks = await this.taskService.getTasks();
        this.container.innerHTML = tasks.map(this.renderTask).join('');
    }
}
```

---

## 🔄 Data Flow

### Create Task Flow:
```
1. User clicks "Create Task" (Presentation)
   ↓
2. TaskFormComponent validates input (Presentation)
   ↓
3. TaskService orchestrates creation (Application)
   ↓
4. TaskValidator validates DTO (Application)
   ↓
5. TaskRepository creates entity (Infrastructure)
   ↓
6. Task entity validates business rules (Domain)
   ↓
7. MockDatabase stores in memory (Infrastructure)
   ↓
8. StorageManager persists to localStorage (Utils)
   ↓
9. TaskService returns result (Application)
   ↓
10. TaskListComponent updates UI (Presentation)
```

---

## 🏗️ Design Patterns

### 1. Repository Pattern
**Purpose:** Abstract data access  
**Location:** `js/infrastructure/repositories.js`

```javascript
interface Repository<T> {
    getAll(): Promise<T[]>
    getById(id: string): Promise<T>
    create(data: Object): Promise<T>
    update(id: string, data: Object): Promise<T>
    delete(id: string): Promise<boolean>
}
```

### 2. Service Pattern
**Purpose:** Encapsulate business logic  
**Location:** `js/application/services.js`

```javascript
class TaskService {
    constructor(taskRepo, userRepo, validator) {
        // Dependencies injected
    }
    
    async createTask(dto) {
        // Orchestrate use case
    }
}
```

### 3. Singleton Pattern
**Purpose:** Single database instance  
**Location:** `js/infrastructure/mock-db.js`

```javascript
let dbInstance = null;

export function getDatabase() {
    if (!dbInstance) {
        dbInstance = new MockDatabase();
    }
    return dbInstance;
}
```

### 4. Factory Pattern
**Purpose:** Object creation  
**Location:** Domain entities

```javascript
class Task {
    static fromJSON(obj) {
        return new Task(
            obj.title,
            obj.description,
            // ...
        );
    }
}
```

### 5. Observer Pattern
**Purpose:** Event-driven updates  
**Location:** Presentation layer (Phase 3)

---

## 🔐 Security Architecture

### Authentication Flow:
```
1. User submits credentials
   ↓
2. AuthService validates credentials
   ↓
3. UserRepository fetches user
   ↓
4. PasswordHasher verifies password
   ↓
5. JWTManager generates token
   ↓
6. AuthManager stores token + user
   ↓
7. Token included in subsequent requests
```

### Authorization Checks:
```javascript
// Role-based checks
AuthManager.hasRole(Role.Admin)

// Resource-based checks
AuthorizationHelper.canEditTask(user, task)
```

---

## 💾 Data Persistence Strategy

### In-Memory + LocalStorage Hybrid:

```
┌─────────────────┐
│  Application    │
└────────┬────────┘
         │
┌────────▼────────┐
│  MockDatabase   │ ← In-memory collections
│  (Singleton)    │
└────────┬────────┘
         │
┌────────▼────────┐
│ StorageManager  │ ← localStorage wrapper
└────────┬────────┘
         │
┌────────▼────────┐
│  localStorage   │ ← Browser persistence
└─────────────────┘
```

### Benefits:
- ✅ Fast reads (in-memory)
- ✅ Persistent across sessions (localStorage)
- ✅ Automatic sync on changes
- ✅ Rollback capability

---

## 🧪 Testing Strategy

### Test Pyramid:

```
        /\
       /UI\        ← E2E Tests (10%)
      /────\
     /Service\     ← Integration Tests (20%)
    /────────\
   / Unit Tests\   ← Unit Tests (70%)
  /────────────\
```

### Test Layers:
1. **Domain Tests** - Entity validation, business rules
2. **Infrastructure Tests** - Repository CRUD, database operations
3. **Application Tests** - Service logic, validation
4. **Presentation Tests** - Component rendering, user interaction

### TDD Cycle:
```
RED → GREEN → REFACTOR
 ↑               ↓
 └───────────────┘
```

---

## 📊 Performance Considerations

### Optimization Strategies:

1. **Lazy Loading**
   - Components loaded on demand
   - Routes loaded dynamically

2. **Debouncing**
   - Search inputs debounced (300ms)
   - Filter changes debounced

3. **Caching**
   - In-memory cache for database
   - Component-level caching

4. **Virtual Scrolling** (Future)
   - For large task lists
   - Render visible items only

---

## 🔄 State Management

### Current Approach:
- **Global State:** AuthManager (current user, token)
- **Component State:** Local component variables
- **Persistence:** localStorage via StorageManager

### Future Enhancement (Phase 4):
```javascript
class StateManager {
    constructor() {
        this.state = {};
        this.subscribers = [];
    }
    
    setState(key, value) {
        this.state[key] = value;
        this.notify(key, value);
    }
    
    subscribe(key, callback) {
        this.subscribers.push({ key, callback });
    }
}
```

---

## 🚀 Scalability Path

### From Demo to Production:

1. **Phase 1 (Current):** Mock data, localStorage
2. **Phase 2:** RESTful API, backend integration
3. **Phase 3:** Real database (PostgreSQL/MongoDB)
4. **Phase 4:** Microservices architecture
5. **Phase 5:** Cloud deployment (AWS/Azure)

### Migration Strategy:
- Replace `MockDatabase` with `ApiClient`
- Keep repository interfaces unchanged
- Swap infrastructure implementation
- No changes to domain or application layers

---

## 📈 Metrics & Monitoring

### Key Metrics (Phase 4):
- Task completion rate
- Average task duration
- User activity
- Storage usage
- Error rates
- Performance metrics

### Logging Levels:
```javascript
Logger.debug()  // Development
Logger.info()   // Informational
Logger.warn()   // Warnings
Logger.error()  // Errors
```

---

## 🎯 Architecture Benefits

### Achieved Goals:
✅ **Maintainability** - Clear layer separation  
✅ **Testability** - Each layer independently testable  
✅ **Flexibility** - Easy to swap implementations  
✅ **Scalability** - Ready for backend integration  
✅ **Reusability** - Components can be reused  
✅ **Performance** - Optimized data flow  

### SOLID Principles:
- **S**ingle Responsibility - Each class has one job
- **O**pen/Closed - Open for extension, closed for modification
- **L**iskov Substitution - Interfaces can be swapped
- **I**nterface Segregation - Small, focused interfaces
- **D**ependency Inversion - Depend on abstractions

---

## 🔮 Future Architecture Enhancements

### Phase 2-5 Roadmap:
1. **WebSocket Integration** - Real-time updates
2. **Service Workers** - Offline capability
3. **IndexedDB** - Larger data storage
4. **Web Components** - Custom HTML elements
5. **PWA** - Progressive Web App features
6. **GraphQL** - Flexible API queries

---

**Architecture Review:** ✅ Production-ready foundation for scaling

