# CortexLabs FinTrack — Refactored

**Refactored by:** CORTEX Workflow Templates  
**Date:** 2026-02-22  
**Original:** `cortex-sts/CortexLabs/BadMonolith/`

## Architecture Summary

| Layer | Before | After |
|-------|--------|-------|
| Backend Entry | 591-line `Program.cs` (God class) | Minimal `Program.cs` + DI-wired services |
| Services | 2 classes with circular deps | Clean DI with interface segregation |
| Security | SQL injection, hardcoded secrets | Parameterized queries, secrets in config |
| Frontend | 466-line `app.ts` (God file) | Modular services + components |
| Styles | Inline `<style>` in HTML | Extracted `styles.css` |
| Testing | `Assert.True(true)` stubs | Real assertions with coverage |

## Smells Resolved

| ID | Category | Resolution |
|----|----------|------------|
| SMELL-1 | Security | Parameterized SQL queries |
| SMELL-2 | Security | Secrets moved to `appsettings.Production.json` |
| SMELL-3 | SOLID | Services decomposed (User, Transaction, Account, Report) |
| SMELL-4 | SOLID | Business logic extracted to domain services |
| SMELL-5 | SOLID | Circular dependency eliminated via DI |
| SMELL-7 | Quality | PascalCase enforced on all properties |
| SMELL-8 | Quality | Dead code removed (NotificationService, ReportGenerator) |
| SMELL-10 | Quality | Duplicate validation consolidated to `ValidationService` |
| SMELL-13 | Security | CORS restricted to specific origins |
| SMELL-17 | SOLID | Full DI wiring with `IServiceCollection` |
| SMELL-18 | Security | Stack traces hidden, structured error responses |
| SMELL-21 | Frontend | CSS extracted to separate file |
| SMELL-22 | Frontend | TypeScript strict mode, no `any` |
| SMELL-23 | Frontend | Business logic moved to services |
| SMELL-24 | Frontend | API abstraction layer added |

## File Structure

```
backend/
├── Program.cs                    # Minimal startup (~50 lines)
├── appsettings.json             # No secrets
├── appsettings.Production.json  # Secrets placeholder
├── CortexLabs.FinTrack.csproj
├── Controllers/
│   ├── UsersController.cs
│   ├── TransactionsController.cs
│   ├── AccountsController.cs
│   └── ReportsController.cs
├── Services/
│   ├── Interfaces/
│   │   ├── IUserService.cs
│   │   ├── ITransactionService.cs
│   │   ├── IAccountService.cs
│   │   └── IValidationService.cs
│   ├── UserService.cs
│   ├── TransactionService.cs
│   ├── AccountService.cs
│   └── ValidationService.cs
├── Repositories/
│   ├── Interfaces/
│   │   └── IRepository.cs
│   ├── UserRepository.cs
│   └── TransactionRepository.cs
├── Models/
│   ├── Transaction.cs
│   ├── User.cs
│   ├── Account.cs
│   └── Report.cs
├── DTOs/
│   ├── TransactionDto.cs
│   ├── UserDto.cs
│   └── ErrorResponse.cs
└── Tests/
    ├── UserServiceTests.cs
    ├── TransactionServiceTests.cs
    └── ValidationServiceTests.cs

frontend/
├── package.json
├── tsconfig.json                # strict: true
├── src/
│   ├── index.html              # No inline styles
│   ├── styles.css              # Extracted CSS
│   ├── main.ts                 # Entry point only
│   ├── services/
│   │   ├── ApiService.ts       # HTTP abstraction
│   │   ├── TransactionService.ts
│   │   └── UserService.ts
│   ├── models/
│   │   ├── Transaction.ts
│   │   ├── User.ts
│   │   └── Account.ts
│   └── components/
│       ├── Dashboard.ts
│       ├── TransactionList.ts
│       └── UserList.ts
```

## Running the Refactored App

```bash
# Backend
cd backend
dotnet restore
dotnet run

# Frontend  
cd frontend
npm install
npm run dev
```

## Validation Commands

```bash
# Backend tests
cd backend/Tests
dotnet test

# Frontend type check
cd frontend
npx tsc --noEmit
```
