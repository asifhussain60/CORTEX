# Phase 5: Integration & Performance Testing

**Duration:** Week 8-10 | **Coverage Gate:** 90% | **Owner:** QA Lead + Dev Lead

---

## 🎯 Objectives
- Integration tests (API + DB + External services)
- Performance testing (baseline: 2-5 sec, target: 1-3 sec)
- Achieve 90% overall coverage

---

## 🧪 Integration Tests (20 tests)

### PrevalidationApiIntegrationTests.cs
```csharp
public class PrevalidationApiIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task POST_ValidateFile_ValidFile_Returns200()
    {
        var content = new MultipartFormDataContent();
        content.Add(new ByteArrayContent(validFileData), "file", "valid.psf");
        content.Add(new StringContent("TestUser"), "userName");
        
        var response = await _client.PostAsync("/api/v1/prevalidations/validate", content);
        
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}
```

---

## ⚡ Performance Tests (10 tests)

### PerformanceTests.cs
```csharp
[Fact]
public async Task ValidateFile_1MBFile_CompletesWithin2Seconds()
{
    var stopwatch = Stopwatch.StartNew();
    var result = await _service.ValidateFileAsync(1MBStream);
    stopwatch.Stop();
    
    Assert.True(stopwatch.ElapsedMilliseconds < 2000);
}

[Fact]
public async Task ValidateFile_100ConcurrentRequests_AllCompleteWithin10Seconds()
{
    var tasks = Enumerable.Range(0, 100)
        .Select(_ => _service.ValidateFileAsync(testStream));
    
    var stopwatch = Stopwatch.StartNew();
    await Task.WhenAll(tasks);
    stopwatch.Stop();
    
    Assert.True(stopwatch.ElapsedMilliseconds < 10000);
}
```

**Performance Baseline:**
- Current ASMX: 2-5 sec, 50 MB memory
- Target REST: 1-3 sec, 30 MB memory (50% faster, 40% less)

---

## ✅ Deliverables
- [x] 20 integration tests
- [x] 10 performance tests
- [x] 90% coverage ✅ GATE MET

---

## 📊 Update Master Plan Progress

**BEFORE proceeding to Phase 5a:**

1. Update `MODERNIZATION-PLAN.md` progress tracker:
   ```
   PHASE 5: LEGACY SERVICE MIGRATION [██████████] 100% ✅ Complete
   ```

2. Update Phase 5 checklist to all `[x]` completed

3. Update overall progress:
   ```
   OVERALL PROGRESS: ████████████████████░░░░░░░░░░ 7/11 Phases (64%)
   ```

4. Verify shadow testing results:
   ```powershell
   # Shadow testing discrepancy must be <0.1%
   echo "Shadow testing: ASMX vs REST discrepancy = X%" >> PHASE-5-COMPLETE.md
   ```

5. Performance benchmarks:
   ```powershell
   # Document latency improvements
   echo "P95 Latency: ASMX (X ms) → REST (Y ms)" >> PHASE-5-COMPLETE.md
   ```

**Next:** [Phase 5a: Schema Validation](phase-5a-schema-validation.md)
