# Phase 4: Services & Repositories

**Duration:** Week 6-7 | **Coverage Gate:** 75% | **Owner:** Senior Developer

---

## 🎯 Objectives
- Implement service orchestration layer
- Create EF Core + Mock swappable repositories
- Write 40 component/integration tests
- Achieve 75% coverage

---

## 🔧 Key Implementations

### PrevalidationService.cs
```csharp
public class PrevalidationService : IPrevalidationService
{
    private readonly IPSFValidator _validator;
    private readonly IPrevalidationRepository _repository;
    private readonly IBlobStorageService _blobService;
    
    public async Task<ValidationResult> ValidateFileAsync(ValidationRequest request)
    {
        // 1. Validate request
        // 2. Call PSFValidator
        // 3. Save to database
        // 4. Upload to blob storage
        // 5. Return result
    }
}
```

### PrevalidationRepository.cs (EF Core)
```csharp
public class PrevalidationRepository : IPrevalidationRepository
{
    private readonly AppDbContext _context;
    
    public async Task<int> SaveValidationResultAsync(PrevalidationData data)
    {
        _context.Prevalidations.Add(data);
        await _context.SaveChangesAsync();
        return data.Id;
    }
}
```

### MockPrevalidationRepository.cs (Testing)
```csharp
public class MockPrevalidationRepository : IPrevalidationRepository
{
    private readonly List<PrevalidationData> _data = new();
    
    public Task<int> SaveValidationResultAsync(PrevalidationData data)
    {
        data.Id = _data.Count + 1;
        _data.Add(data);
        return Task.FromResult(data.Id);
    }
}
```

---

## 🧪 Tests (40 tests)
- PrevalidationServiceTests.cs (25 component tests)
- PrevalidationRepositoryTests.cs (15 integration tests)

---

## ✅ Deliverables
- [x] Service layer (3 services)
- [x] Repository layer (EF Core + Mock)
- [x] 40 tests, 75% coverage ✅ GATE MET

---

## 📊 Update Master Plan Progress

**BEFORE proceeding to Phase 4a:**

1. Update `MODERNIZATION-PLAN.md` progress tracker:
   ```
   PHASE 4: REST API CONTROLLERS [██████████] 100% ✅ Complete
   ```

2. Update Phase 4 checklist to all `[x]` completed

3. Update overall progress:
   ```
   OVERALL PROGRESS: ██████████████░░░░░░░░░░░░░░░░ 5/11 Phases (45%)
   ```

4. Verify coverage gate:
   ```powershell
   dotnet test --collect:"XPlat Code Coverage"
   # Target: 75% overall, Services ≥95%, Repositories ≥95%
   ```

5. Create completion report:
   ```powershell
   # Document service implementations and test metrics
   echo "Phase 4: Services (3), Repositories (2), Tests (40), Coverage (X%)" > PHASE-4-COMPLETE.md
   ```

**Next:** [Phase 4a: Contract Verification](phase-4a-contract-verification.md)
