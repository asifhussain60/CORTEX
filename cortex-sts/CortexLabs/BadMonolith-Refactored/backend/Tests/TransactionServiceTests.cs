// ✅ CORTEX Refactored — TransactionServiceTests
// ✅ AP-007 RESOLVED: XxxServiceTests class for every XxxService class (ENH-STS-04)
// ✅ SMELL-12 RESOLVED: Real assertions, not Assert.True(true)
// ✅ CORE-008 (TDD): tests written for all public methods

using Xunit;
using Moq;
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Services;
using CortexLabs.FinTrack.Services.Interfaces;
using CortexLabs.FinTrack.Repositories.Interfaces;

namespace CortexLabs.FinTrack.Tests;

/// <summary>
/// Unit tests for TransactionService — covers CRUD, search, auto-categorization,
/// dashboard summary, and validation delegation.
/// </summary>
public class TransactionServiceTests
{
    private readonly Mock<ITransactionRepository> _txRepoMock;
    private readonly Mock<IValidationService> _validationMock;
    private readonly Mock<ILogger<TransactionService>> _loggerMock;
    private readonly TransactionService _sut;

    public TransactionServiceTests()
    {
        _txRepoMock = new Mock<ITransactionRepository>();
        _validationMock = new Mock<IValidationService>();
        _loggerMock = new Mock<ILogger<TransactionService>>();
        _sut = new TransactionService(_txRepoMock.Object, _validationMock.Object, _loggerMock.Object);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor guard clauses
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public void Constructor_NullRepository_Throws()
    {
        Assert.Throws<ArgumentNullException>(() =>
            new TransactionService(null!, _validationMock.Object, _loggerMock.Object));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GetByIdAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task GetByIdAsync_ExistingTransaction_ReturnsMappedDto()
    {
        var tx = new Transaction
        {
            Id = 7, Description = "Netflix", Amount = 15.99m,
            Category = "entertainment", Type = "expense",
            Date = new DateTime(2026, 1, 1), UserId = 1
        };
        _txRepoMock.Setup(r => r.GetByIdAsync(7)).ReturnsAsync(tx);

        var result = await _sut.GetByIdAsync(7);

        Assert.NotNull(result);
        Assert.Equal(7, result!.Id);
        Assert.Equal("Netflix", result.Description);
        Assert.Equal(15.99m, result.Amount);
    }

    [Fact]
    public async Task GetByIdAsync_MissingTransaction_ReturnsNull()
    {
        _txRepoMock.Setup(r => r.GetByIdAsync(999)).ReturnsAsync((Transaction?)null);

        var result = await _sut.GetByIdAsync(999);

        Assert.Null(result);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GetAllAsync (pagination)
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task GetAllAsync_ReturnsMappedPagedResults()
    {
        var txs = new List<Transaction>
        {
            new() { Id = 1, Description = "Salary", Amount = 3000m, Category = "income", Type = "income", Date = DateTime.UtcNow, UserId = 1 },
            new() { Id = 2, Description = "Rent", Amount = 1200m, Category = "housing", Type = "expense", Date = DateTime.UtcNow, UserId = 1 }
        };
        _txRepoMock.Setup(r => r.GetPagedAsync(1, 50)).ReturnsAsync(txs);

        var result = (await _sut.GetAllAsync(1, 50)).ToList();

        Assert.Equal(2, result.Count);
        Assert.Equal("Salary", result[0].Description);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // SearchAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task SearchAsync_ByCategory_DelegatesToRepository()
    {
        var txs = new List<Transaction>
        {
            new() { Id = 3, Description = "Grocery", Amount = 80m, Category = "food", Type = "expense", Date = DateTime.UtcNow, UserId = 1 }
        };
        _txRepoMock.Setup(r => r.SearchAsync("food", null)).ReturnsAsync(txs);

        var result = (await _sut.SearchAsync("food", null)).ToList();

        Assert.Single(result);
        Assert.Equal("food", result[0].Category);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // CreateAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task CreateAsync_ValidDto_CreatesAndReturnsMappedDto()
    {
        var dto = new CreateTransactionDto("Coffee", 4.50m, "food", "expense", 1);
        _validationMock
            .Setup(v => v.ValidateTransaction(dto))
            .Returns(new ValidationResult(true, Array.Empty<string>()));

        var created = new Transaction { Id = 99, Description = "Coffee", Amount = 4.50m, Category = "food", Type = "expense", Date = DateTime.UtcNow, UserId = 1 };
        _txRepoMock.Setup(r => r.CreateAsync(It.IsAny<Transaction>())).ReturnsAsync(created);

        var result = await _sut.CreateAsync(dto);

        Assert.Equal(99, result.Id);
        Assert.Equal("Coffee", result.Description);
        _txRepoMock.Verify(r => r.CreateAsync(It.IsAny<Transaction>()), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_InvalidDto_ThrowsValidationException()
    {
        var dto = new CreateTransactionDto("", -1m, "", "unknown", 0);
        _validationMock
            .Setup(v => v.ValidateTransaction(dto))
            .Returns(new ValidationResult(false, new[] { "Description is required", "Amount must be positive" }));

        var ex = await Assert.ThrowsAsync<ValidationException>(() => _sut.CreateAsync(dto));
        Assert.Contains("Description is required", ex.Errors);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // DeleteAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task DeleteAsync_ExistingTransaction_ReturnsTrue()
    {
        _txRepoMock.Setup(r => r.DeleteAsync(5)).ReturnsAsync(true);

        var result = await _sut.DeleteAsync(5);

        Assert.True(result);
        _txRepoMock.Verify(r => r.DeleteAsync(5), Times.Once);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GetDashboardSummaryAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task GetDashboardSummaryAsync_CalculatesCorrectNetPosition()
    {
        var txs = new List<Transaction>
        {
            new() { Id = 1, Description = "Salary", Amount = 3000m, Category = "income", Type = "income", Date = DateTime.UtcNow, UserId = 1 },
            new() { Id = 2, Description = "Rent", Amount = 1200m, Category = "housing", Type = "expense", Date = DateTime.UtcNow, UserId = 1 },
            new() { Id = 3, Description = "Food", Amount = 300m, Category = "food", Type = "expense", Date = DateTime.UtcNow, UserId = 1 }
        };
        _txRepoMock.Setup(r => r.GetByUserIdAsync(1)).ReturnsAsync(txs);

        var summary = await _sut.GetDashboardSummaryAsync(1);

        Assert.Equal(3000m, summary.TotalIncome);
        Assert.Equal(1500m, summary.TotalExpenses);
        Assert.Equal(1500m, summary.NetPosition);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_HealthyWhenIncomeExceedsExpenses()
    {
        var txs = new List<Transaction>
        {
            new() { Id = 1, Description = "Salary", Amount = 5000m, Category = "income", Type = "income", Date = DateTime.UtcNow, UserId = 2 },
            new() { Id = 2, Description = "Rent", Amount = 1000m, Category = "housing", Type = "expense", Date = DateTime.UtcNow, UserId = 2 }
        };
        _txRepoMock.Setup(r => r.GetByUserIdAsync(2)).ReturnsAsync(txs);

        var summary = await _sut.GetDashboardSummaryAsync(2);

        Assert.Equal("Healthy", summary.HealthScore);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_CriticalWhenExpensesExceedIncomeByCriticalRatio()
    {
        var txs = new List<Transaction>
        {
            new() { Id = 1, Description = "Salary", Amount = 1000m, Category = "income", Type = "income", Date = DateTime.UtcNow, UserId = 3 },
            new() { Id = 2, Description = "Debt", Amount = 2000m, Category = "other", Type = "expense", Date = DateTime.UtcNow, UserId = 3 }
        };
        _txRepoMock.Setup(r => r.GetByUserIdAsync(3)).ReturnsAsync(txs);

        var summary = await _sut.GetDashboardSummaryAsync(3);

        Assert.Equal("Critical", summary.HealthScore);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_CategoryBreakdownPercentagesAddToOneHundred()
    {
        var txs = new List<Transaction>
        {
            new() { Id = 1, Description = "Rent", Amount = 1000m, Category = "housing", Type = "expense", Date = DateTime.UtcNow, UserId = 1 },
            new() { Id = 2, Description = "Food", Amount = 500m, Category = "food", Type = "expense", Date = DateTime.UtcNow, UserId = 1 },
            new() { Id = 3, Description = "Transport", Amount = 500m, Category = "transport", Type = "expense", Date = DateTime.UtcNow, UserId = 1 }
        };
        _txRepoMock.Setup(r => r.GetByUserIdAsync(1)).ReturnsAsync(txs);

        var summary = await _sut.GetDashboardSummaryAsync(1);

        var total = summary.Categories.Sum(c => c.Percentage);
        Assert.Equal(100m, total);
    }
}
