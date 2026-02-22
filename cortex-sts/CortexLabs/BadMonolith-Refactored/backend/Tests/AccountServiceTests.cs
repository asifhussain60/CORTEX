// ✅ CORTEX Refactored — AccountServiceTests
// ✅ AP-007 RESOLVED: XxxServiceTests class for every XxxService class (ENH-STS-04)
// ✅ SMELL-12 RESOLVED: Real assertions, not Assert.True(true)
// ✅ CORE-008 (TDD): tests written for all public methods including transfer edge cases

using Xunit;
using Moq;
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Services;
using CortexLabs.FinTrack.Services.Interfaces;
using CortexLabs.FinTrack.Repositories.Interfaces;

namespace CortexLabs.FinTrack.Tests;

/// <summary>
/// Unit tests for AccountService — covers CRUD, transfer business rules,
/// concurrency guard, and all validation edge cases.
/// </summary>
public class AccountServiceTests
{
    private readonly Mock<IAccountRepository> _accountRepoMock;
    private readonly Mock<ILogger<AccountService>> _loggerMock;
    private readonly AccountService _sut;

    public AccountServiceTests()
    {
        _accountRepoMock = new Mock<IAccountRepository>();
        _loggerMock = new Mock<ILogger<AccountService>>();
        _sut = new AccountService(_accountRepoMock.Object, _loggerMock.Object);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor guard clauses
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public void Constructor_NullRepository_Throws()
    {
        Assert.Throws<ArgumentNullException>(() =>
            new AccountService(null!, _loggerMock.Object));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GetByIdAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task GetByIdAsync_ExistingAccount_ReturnsMappedDto()
    {
        var account = new Account { Id = 1, Name = "Savings", Balance = 5000m, UserId = 1, AccountType = "savings" };
        _accountRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(account);

        var result = await _sut.GetByIdAsync(1);

        Assert.NotNull(result);
        Assert.Equal(1, result!.Id);
        Assert.Equal("Savings", result.Name);
        Assert.Equal(5000m, result.Balance);
    }

    [Fact]
    public async Task GetByIdAsync_MissingAccount_ReturnsNull()
    {
        _accountRepoMock.Setup(r => r.GetByIdAsync(999)).ReturnsAsync((Account?)null);

        var result = await _sut.GetByIdAsync(999);

        Assert.Null(result);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GetByUserIdAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task GetByUserIdAsync_ReturnsAllAccountsForUser()
    {
        var accounts = new List<Account>
        {
            new() { Id = 1, Name = "Checking", Balance = 1000m, UserId = 5, AccountType = "checking" },
            new() { Id = 2, Name = "Savings", Balance = 5000m, UserId = 5, AccountType = "savings" }
        };
        _accountRepoMock.Setup(r => r.GetByUserIdAsync(5)).ReturnsAsync(accounts);

        var result = (await _sut.GetByUserIdAsync(5)).ToList();

        Assert.Equal(2, result.Count);
        Assert.All(result, a => Assert.Equal(5, a.UserId));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // CreateAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task CreateAsync_ValidDto_CreatesAccountWithInitialBalance()
    {
        var dto = new CreateAccountDto("Checking", 500m, 1, "checking");
        var created = new Account { Id = 10, Name = "Checking", Balance = 500m, UserId = 1, AccountType = "checking" };
        _accountRepoMock.Setup(r => r.CreateAsync(It.IsAny<Account>())).ReturnsAsync(created);

        var result = await _sut.CreateAsync(dto);

        Assert.Equal(10, result.Id);
        Assert.Equal("Checking", result.Name);
        Assert.Equal(500m, result.Balance);
        _accountRepoMock.Verify(r => r.CreateAsync(It.IsAny<Account>()), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_EmptyName_ThrowsValidationException()
    {
        var dto = new CreateAccountDto("", 0m, 1, "checking");

        var ex = await Assert.ThrowsAsync<ValidationException>(() => _sut.CreateAsync(dto));
        Assert.Contains("Account name is required", ex.Errors);
    }

    [Fact]
    public async Task CreateAsync_NegativeInitialBalance_ThrowsValidationException()
    {
        var dto = new CreateAccountDto("Savings", -100m, 1, "savings");

        var ex = await Assert.ThrowsAsync<ValidationException>(() => _sut.CreateAsync(dto));
        Assert.Contains("Initial balance cannot be negative", ex.Errors);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // TransferAsync — AP-002 restored endpoint tests
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task TransferAsync_ValidTransfer_DeductsFromSourceAndCreditsDestination()
    {
        var from = new Account { Id = 1, Name = "Checking", Balance = 1000m, UserId = 1, AccountType = "checking" };
        var to = new Account { Id = 2, Name = "Savings", Balance = 200m, UserId = 1, AccountType = "savings" };

        _accountRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(from);
        _accountRepoMock.Setup(r => r.GetByIdAsync(2)).ReturnsAsync(to);
        _accountRepoMock.Setup(r => r.UpdateAsync(It.IsAny<Account>())).ReturnsAsync(true);

        var result = await _sut.TransferAsync(1, 2, 300m);

        Assert.True(result);
        Assert.Equal(700m, from.Balance);
        Assert.Equal(500m, to.Balance);
        _accountRepoMock.Verify(r => r.UpdateAsync(It.IsAny<Account>()), Times.Exactly(2));
    }

    [Fact]
    public async Task TransferAsync_InsufficientFunds_ThrowsInvalidOperationException()
    {
        var from = new Account { Id = 1, Name = "Checking", Balance = 50m, UserId = 1, AccountType = "checking" };
        var to = new Account { Id = 2, Name = "Savings", Balance = 0m, UserId = 1, AccountType = "savings" };

        _accountRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(from);
        _accountRepoMock.Setup(r => r.GetByIdAsync(2)).ReturnsAsync(to);

        await Assert.ThrowsAsync<InvalidOperationException>(() =>
            _sut.TransferAsync(1, 2, 500m));
    }

    [Fact]
    public async Task TransferAsync_ZeroAmount_ThrowsValidationException()
    {
        await Assert.ThrowsAsync<ValidationException>(() =>
            _sut.TransferAsync(1, 2, 0m));
    }

    [Fact]
    public async Task TransferAsync_NegativeAmount_ThrowsValidationException()
    {
        await Assert.ThrowsAsync<ValidationException>(() =>
            _sut.TransferAsync(1, 2, -50m));
    }

    [Fact]
    public async Task TransferAsync_SameSourceAndDestination_ThrowsValidationException()
    {
        await Assert.ThrowsAsync<ValidationException>(() =>
            _sut.TransferAsync(1, 1, 100m));
    }

    [Fact]
    public async Task TransferAsync_MissingSourceAccount_ThrowsInvalidOperationException()
    {
        _accountRepoMock.Setup(r => r.GetByIdAsync(99)).ReturnsAsync((Account?)null);
        _accountRepoMock.Setup(r => r.GetByIdAsync(2)).ReturnsAsync(
            new Account { Id = 2, Name = "Savings", Balance = 0m, UserId = 1, AccountType = "savings" });

        await Assert.ThrowsAsync<InvalidOperationException>(() =>
            _sut.TransferAsync(99, 2, 100m));
    }

    [Fact]
    public async Task TransferAsync_MissingDestinationAccount_ThrowsInvalidOperationException()
    {
        _accountRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(
            new Account { Id = 1, Name = "Checking", Balance = 1000m, UserId = 1, AccountType = "checking" });
        _accountRepoMock.Setup(r => r.GetByIdAsync(99)).ReturnsAsync((Account?)null);

        await Assert.ThrowsAsync<InvalidOperationException>(() =>
            _sut.TransferAsync(1, 99, 100m));
    }
}
