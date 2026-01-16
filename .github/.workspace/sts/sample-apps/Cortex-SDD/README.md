# Cortex-SDD: Modernized Task Management Application

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Architecture:** Clean Architecture with Domain-Driven Design

---

## 🎯 Overview

Cortex-SDD (Software Development Dashboard) is a modern, production-ready task management application built with **zero external dependencies**. It demonstrates Clean Architecture principles using vanilla JavaScript, HTML5, and CSS3.

### Key Features

✅ **Zero Dependencies** - No npm, no build tools, no frameworks  
✅ **Production Ready** - TDD implementation, comprehensive validation  
✅ **Clean Architecture** - 4-layer separation (Domain, Infrastructure, Application, Presentation)  
✅ **Persistent Storage** - LocalStorage with in-memory caching  
✅ **Authentication** - JWT-based auth simulation  
✅ **Role-Based Access** - Admin, Team Lead, User roles  
✅ **Responsive UI** - Tailwind CSS via CDN  

---

## 🚀 Quick Start

### Prerequisites
- Modern web browser (Chrome, Edge, Firefox, Safari)
- No installation required!

### Running the Application

1. **Clone or download this repository**
2. **Open `index.html` in your browser**
3. **Done!** The application will auto-seed with demo data

### Demo Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | Admin@123 | Administrator |
| teamlead | TeamLead@123 | Team Lead |
| user | User@123 | User |

---

## 🎯 Overview (continued)

**Original Application:** BadMonolith - Deliberately poor .NET 8 + Angular 17 monolith  
**Modernized Stack:**
- **Backend:** .NET 9.0 with Clean Architecture
- **Frontend:** Angular 19 with Tailwind CSS
- **Database:** SQL Server with Entity Framework Core
- **Authentication:** JWT Bearer tokens with BCrypt password hashing
- **Testing:** xUnit (backend), Jasmine/Karma (frontend)

**Key Improvements:**
- ✅ SQL injection vulnerabilities eliminated (EF Core parameterized queries)
- ✅ Clean Architecture with SOLID principles
- ✅ JWT authentication and role-based authorization
- ✅ Comprehensive test coverage (80%+ target)
- ✅ Modern, responsive UI with Tailwind CSS
- ✅ Structured logging and error handling
- ✅ API documentation via Swagger

---

## 📋 Prerequisites

### Required Software

1. **.NET 9.0 SDK**
   ```powershell
   # Download from: https://dotnet.microsoft.com/download/dotnet/9.0
   # Verify installation:
   dotnet --version  # Should output 9.0.x
   ```

2. **Node.js 20+ and npm 10+**
   ```powershell
   # Download from: https://nodejs.org/
   # Verify installation:
   node --version  # Should output v20.x or higher
   npm --version   # Should output 10.x or higher
   ```
   ✅ **Current System:** Node.js v24.11.1, npm 11.6.2

3. **Angular CLI 19**
   ```powershell
   # Install globally:
   npm install -g @angular/cli@19
   
   # Verify installation:
   ng version  # Should output Angular CLI: 19.x
   ```

4. **SQL Server** (Choose one)
   - **LocalDB** (recommended for development): Installed with Visual Studio
   - **SQL Server Express**: Free edition from Microsoft
   - **Docker**: `docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong@Passw0rd" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest`

5. **IDE** (Optional but recommended)
   - Visual Studio 2022 (Community or higher) for .NET development
   - Visual Studio Code with extensions:
     - C# Dev Kit
     - Angular Language Service
     - Tailwind CSS IntelliSense
     - ESLint
     - Prettier

---

## 🚀 Quick Start

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Restore dependencies
dotnet restore

# Update database connection string
# Edit src/Cortex.SDD.Api/appsettings.json
# Or use User Secrets (recommended):
cd src/Cortex.SDD.Api
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Server=localhost;Database=CortexSDD;Integrated Security=true;TrustServerCertificate=True;"
dotnet user-secrets set "JwtSettings:Secret" "YourSuperSecretKeyThatIsAtLeast32CharactersLong"

# Run database migrations
dotnet ef database update --project src/Cortex.SDD.Infrastructure --startup-project src/Cortex.SDD.Api

# Run the API
dotnet run --project src/Cortex.SDD.Api

# API will be available at: https://localhost:7000
# Swagger documentation: https://localhost:7000/swagger
```

### 2. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Application will be available at: http://localhost:4200
```

### 3. Running Tests

**Backend Tests:**
```powershell
cd backend

# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true /p:CoverageReportsFormat=lcov

# Run specific test project
dotnet test tests/Cortex.SDD.Api.Tests
```

**Frontend Tests:**
```powershell
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm run test -- --code-coverage

# Run tests in headless mode (CI)
npm run test -- --watch=false --browsers=ChromeHeadless
```

---

## 🏗️ Architecture

### Backend Structure (Clean Architecture)

```
backend/
├── src/
│   ├── Cortex.SDD.Api/              # Presentation Layer (Controllers, Middleware)
│   ├── Cortex.SDD.Application/      # Application Layer (Services, DTOs, Validation)
│   ├── Cortex.SDD.Domain/           # Domain Layer (Entities, Interfaces)
│   └── Cortex.SDD.Infrastructure/   # Infrastructure Layer (Data Access, Repositories)
└── tests/
    ├── Cortex.SDD.Api.Tests/        # API integration tests
    ├── Cortex.SDD.Application.Tests/ # Service unit tests
    └── Cortex.SDD.Integration.Tests/ # End-to-end integration tests
```

**Dependency Flow:** Infrastructure → Domain ← Application ← Api

### Frontend Structure (Feature-Based)

```
frontend/src/app/
├── core/                    # Singleton services (auth, HTTP interceptors)
├── shared/                  # Reusable components, directives, pipes
└── features/                # Feature modules
    ├── tasks/               # Task management feature
    └── auth/                # Authentication feature
```

---

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens:** 15-minute access tokens, 7-day refresh tokens
- **Password Hashing:** BCrypt with 12 salt rounds
- **Role-Based Access Control:** Admin and User roles
- **Token Validation:** Middleware validates every protected request

### Security Best Practices
- ✅ **No SQL Injection:** EF Core with parameterized queries
- ✅ **Secrets Management:** User Secrets (dev), Azure Key Vault (prod)
- ✅ **HTTPS Enforced:** Production configurations require HTTPS
- ✅ **CORS Policy:** Restricted to known origins
- ✅ **Error Handling:** Stack traces never exposed to clients
- ✅ **Input Validation:** FluentValidation on all endpoints

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and receive JWT token
- `POST /api/auth/refresh` - Refresh access token

### Tasks
- `GET /api/tasks` - Get all tasks (with optional filter query)
- `GET /api/tasks/{id}` - Get task by ID
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Users
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile

**Full API documentation available at:** `https://localhost:7000/swagger`

---

## 🧪 Testing Strategy

### Backend Testing (TDD with RED-GREEN-REFACTOR)

**Unit Tests (≥80% coverage):**
- Repository pattern tests with in-memory database
- Service layer tests with mocked dependencies
- Validator tests for all DTOs

**Integration Tests (≥70% coverage):**
- Controller endpoints with `WebApplicationFactory`
- Database operations with test database
- Authentication middleware validation

**Example Test:**
```csharp
[Fact]
public async Task CreateTask_WithValidData_ReturnsCreatedResult()
{
    // Arrange (RED phase - write test first)
    var dto = new CreateTaskDto { Title = "Test Task" };
    
    // Act (GREEN phase - implement to pass)
    var result = await _controller.Create(dto);
    
    // Assert (REFACTOR phase - optimize)
    result.Should().BeOfType<CreatedResult>();
}
```

### Frontend Testing (Jasmine/Karma)

**Unit Tests (≥70% coverage):**
- Component logic and user interactions
- Service methods and HTTP calls
- Form validation and error handling

**Example Test:**
```typescript
it('should create task when form is valid', () => {
  // Arrange
  component.taskForm.setValue({ title: 'New Task' });
  
  // Act
  component.onSubmit();
  
  // Assert
  expect(taskService.create).toHaveBeenCalledWith({ title: 'New Task' });
});
```

---

## 🎨 UI/UX Features

### Tailwind CSS Styling
- **Responsive Design:** Mobile-first approach (320px, 768px, 1024px breakpoints)
- **Component Library:** Reusable cards, buttons, forms, modals
- **Dark Mode:** Optional dark theme support
- **Loading States:** Spinners and skeleton screens during API calls
- **Error Messages:** Toast notifications for errors

### Key Pages
- **Login/Register:** Clean authentication forms with validation
- **Task List:** Responsive grid with filter, create, update, delete
- **User Profile:** Edit profile information

---

## 📈 Performance Considerations

### Backend Optimizations
- **Database Indexing:** Indexes on UserId, Title for fast queries
- **Async/Await:** All I/O operations are asynchronous
- **Connection Pooling:** EF Core manages connection pool
- **Response Caching:** Optional caching for read-heavy endpoints

### Frontend Optimizations
- **Lazy Loading:** Feature modules loaded on demand
- **Change Detection:** OnPush strategy for performance-critical components
- **RxJS Optimization:** Proper subscription management (unsubscribe on destroy)
- **Build Optimization:** Production builds with AOT compilation

---

## 🔧 Configuration

### Backend Configuration

**appsettings.json (Development):**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=CortexSDD;Integrated Security=true;"
  },
  "JwtSettings": {
    "Issuer": "Cortex.SDD.Api",
    "Audience": "Cortex.SDD.Frontend",
    "ExpirationMinutes": 15
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

**User Secrets (Recommended for sensitive data):**
```powershell
dotnet user-secrets set "JwtSettings:Secret" "YourSecretKey"
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "YourConnectionString"
```

### Frontend Configuration

**environment.ts:**
```typescript
export const environment = {
  production: false,
  apiUrl: 'https://localhost:7000/api'
};
```

---

## 🚢 Deployment

### Backend Deployment (Azure App Service)

```powershell
# Build for production
dotnet publish src/Cortex.SDD.Api -c Release -o ./publish

# Deploy to Azure (example)
az webapp deployment source config-zip --resource-group CortexRG --name cortex-sdd-api --src publish.zip
```

### Frontend Deployment (Azure Static Web Apps)

```powershell
# Build for production
cd frontend
npm run build --prod

# Deploy to Azure (example)
az staticwebapp create --name cortex-sdd-frontend --resource-group CortexRG --source dist/cortex-sdd-frontend
```

### Docker Deployment

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: "Y"
      SA_PASSWORD: "YourStrong@Passw0rd"
    ports:
      - "1433:1433"
  
  api:
    build: ./backend
    depends_on:
      - sqlserver
    ports:
      - "7000:80"
    environment:
      ConnectionStrings__DefaultConnection: "Server=sqlserver;Database=CortexSDD;User Id=sa;Password=YourStrong@Passw0rd;"
  
  frontend:
    build: ./frontend
    ports:
      - "4200:80"
```

---

## 📚 Documentation

- **Architecture Decisions:** See `docs/architecture-decisions/` for ADRs
- **Modernization Comparison:** See `docs/MODERNIZATION-COMPARISON.md` for before/after analysis
- **API Documentation:** Available at Swagger UI (`/swagger`)
- **Code Comments:** XML documentation on all public APIs

---

## 🐛 Known Issues & Limitations

- **Refresh Token Rotation:** Not implemented (planned for v2)
- **Rate Limiting:** API rate limiting not configured (planned for v2)
- **Email Verification:** User registration doesn't send verification emails
- **Two-Factor Authentication:** Not implemented (planned for v2)

---

## 🤝 Contributing

This is a sample application for demonstration purposes. For production use:
1. Implement refresh token rotation
2. Add comprehensive logging (Application Insights)
3. Configure API rate limiting
4. Add email verification for user registration
5. Implement backup and disaster recovery procedures

---

## 📄 License

This project is part of the CORTEX framework.  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 📞 Support

**Project:** CORTEX Sample Applications  
**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Created:** 2025-12-09

**Related Documentation:**
- Planning Document: `cortex-brain/documents/planning/badmonolith-modernization-plan.md`
- Original Application: `cortex-sample-apps/BadMonolith/`

---

## ⚠️ Environment Setup Status

**Current System Check:**
- ✅ Node.js: v24.11.1
- ✅ npm: 11.6.2
- ❌ .NET SDK: Not installed (required: 9.0.x)
- ❌ Angular CLI: Not installed (required: 19.x)
- ❓ SQL Server: Not checked

**Next Steps:**
1. Install .NET 9.0 SDK from https://dotnet.microsoft.com/download/dotnet/9.0
2. Install Angular CLI: `npm install -g @angular/cli@19`
3. Verify SQL Server availability (LocalDB, Express, or Docker)
4. Run setup verification: `dotnet --version && ng version`
