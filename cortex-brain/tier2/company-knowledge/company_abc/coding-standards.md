# Company ABC - Coding Standards

**Version:** 2.1.0  
**Last Updated:** 2026-01-06  
**Applies To:** All development teams

---

## 🎯 C# / .NET Coding Standards

### Naming Conventions

**Classes & Interfaces:**
- PascalCase
- Interfaces start with 'I' prefix
- Examples: `UserService`, `IOrderRepository`

**Methods & Properties:**
- PascalCase
- Verb-first for methods: `GetUser()`, `CreateOrder()`

**Variables & Parameters:**
- camelCase
- Descriptive names (no abbreviations)
- Examples: `userId`, `orderDate`

**Constants:**
- PascalCase
- Examples: `MaxRetryCount`, `DefaultTimeout`

**Private Fields:**
- camelCase with underscore prefix
- Examples: `_logger`, `_dbContext`

### File Organization

```csharp
// 1. Usings (sorted alphabetically)
using Microsoft.AspNetCore.Mvc;
using System;

// 2. Namespace
namespace CompanyAbc.Services.Users;

// 3. Class/Interface
public class UserService : IUserService
{
    // 4. Private fields
    private readonly ILogger<UserService> _logger;
    
    // 5. Constructor
    public UserService(ILogger<UserService> logger)
    {
        _logger = logger;
    }
    
    // 6. Public methods
    public async Task<User> GetUserAsync(Guid userId)
    {
        // Implementation
    }
    
    // 7. Private methods
    private void ValidateUser(User user)
    {
        // Implementation
    }
}
```

### Error Handling

**Use Exceptions (not error codes):**
```csharp
// ✅ GOOD
if (user == null)
    throw new NotFoundException($"User {userId} not found");

// ❌ BAD
if (user == null)
    return new ErrorResult(404, "Not found");
```

**Custom Exception Hierarchy:**
- `DomainException` (base)
  - `NotFoundException`
  - `ValidationException`
  - `BusinessRuleViolationException`

### Async/Await

**Always use async suffix:**
```csharp
// ✅ GOOD
public async Task<User> GetUserAsync(Guid userId)

// ❌ BAD
public async Task<User> GetUser(Guid userId)
```

**Avoid async void (except event handlers):**
```csharp
// ✅ GOOD
public async Task ProcessOrderAsync()

// ❌ BAD
public async void ProcessOrder()
```

### Dependency Injection

**Use constructor injection (not property injection):**
```csharp
// ✅ GOOD
public class UserService
{
    private readonly IUserRepository _repository;
    
    public UserService(IUserRepository repository)
    {
        _repository = repository;
    }
}

// ❌ BAD
public class UserService
{
    public IUserRepository Repository { get; set; }
}
```

### Logging

**Use structured logging:**
```csharp
// ✅ GOOD
_logger.LogInformation("User {UserId} created order {OrderId}", userId, orderId);

// ❌ BAD
_logger.LogInformation($"User {userId} created order {orderId}");
```

**Log Levels:**
- `Trace`: Detailed debugging (not in production)
- `Debug`: Debugging information
- `Information`: General flow (API calls, business events)
- `Warning`: Unexpected but recoverable
- `Error`: Errors that require attention
- `Critical`: System failures

---

## 🎨 TypeScript / React Coding Standards

### Naming Conventions

**Components:**
- PascalCase
- Example: `UserProfile.tsx`

**Hooks:**
- camelCase with 'use' prefix
- Example: `useUserData.ts`

**Utilities:**
- camelCase
- Example: `formatCurrency.ts`

**Constants:**
- UPPER_SNAKE_CASE
- Example: `MAX_FILE_SIZE`

### Component Structure

```typescript
// 1. Imports (React, then libraries, then local)
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { UserService } from '@/services/userService';

// 2. Types/Interfaces
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

// 3. Component
export const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  // Hooks at top
  const { data: user, isLoading } = useQuery(['user', userId], () => 
    UserService.getUser(userId)
  );
  
  // Event handlers
  const handleUpdate = () => {
    // Implementation
  };
  
  // Render
  if (isLoading) return <Spinner />;
  
  return (
    <div className="user-profile">
      {/* JSX */}
    </div>
  );
};
```

### TypeScript Usage

**Always use explicit types:**
```typescript
// ✅ GOOD
const userId: string = "123";
function getUser(id: string): Promise<User> { }

// ❌ BAD
const userId = "123";
function getUser(id) { }
```

**Use interfaces for objects:**
```typescript
// ✅ GOOD
interface User {
  id: string;
  name: string;
  email: string;
}

// ❌ BAD (type for objects)
type User = {
  id: string;
  name: string;
  email: string;
}
```

### React Best Practices

**Use functional components (not class components):**
```typescript
// ✅ GOOD
export const UserProfile: React.FC<Props> = (props) => { }

// ❌ BAD
export class UserProfile extends React.Component { }
```

**Memoize expensive computations:**
```typescript
const sortedUsers = useMemo(() => 
  users.sort((a, b) => a.name.localeCompare(b.name)),
  [users]
);
```

---

## 🗄️ Database Standards

### Naming Conventions

**Tables:** PascalCase (singular)
- Example: `User`, `Order`

**Columns:** PascalCase
- Example: `UserId`, `CreatedDate`

**Indexes:** `IX_{TableName}_{ColumnNames}`
- Example: `IX_User_Email`

**Foreign Keys:** `FK_{TableName}_{ReferencedTable}`
- Example: `FK_Order_User`

### Required Columns

All tables must have:
```sql
Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID()
CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE()
CreatedBy NVARCHAR(100) NOT NULL
ModifiedDate DATETIME2 NULL
ModifiedBy NVARCHAR(100) NULL
IsDeleted BIT NOT NULL DEFAULT 0  -- Soft delete
```

---

## 🧪 Testing Standards

### Unit Test Naming

**Pattern:** `MethodName_Scenario_ExpectedResult`

```csharp
[Fact]
public void GetUser_ValidUserId_ReturnsUser()
{
    // Arrange
    var userId = Guid.NewGuid();
    
    // Act
    var user = _service.GetUser(userId);
    
    // Assert
    Assert.NotNull(user);
}
```

### Test Coverage

**Minimum Requirements:**
- Unit tests: 80% code coverage
- Integration tests: Critical paths covered
- E2E tests: Happy path + top 3 user journeys

---

## 📦 API Standards

### RESTful Conventions

**HTTP Methods:**
- GET: Retrieve (safe, idempotent)
- POST: Create (not idempotent)
- PUT: Update (idempotent)
- DELETE: Remove (idempotent)
- PATCH: Partial update

**URL Structure:**
```
/api/v{version}/{resource}/{id?}/{sub-resource?}
```

Examples:
- `GET /api/v1/users` - List users
- `GET /api/v1/users/123` - Get user 123
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/123/orders` - List orders for user 123

### Response Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid auth
- `403 Forbidden` - No permission
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## ✅ Code Review Checklist

Before submitting PR, verify:

- [ ] Code follows naming conventions
- [ ] No hardcoded values (use configuration)
- [ ] Error handling implemented
- [ ] Logging added for key operations
- [ ] Unit tests written (>80% coverage)
- [ ] No commented-out code
- [ ] No console.log() or Debug.WriteLine() left in code
- [ ] API endpoints documented in Swagger
- [ ] Database migrations included (if schema changes)
