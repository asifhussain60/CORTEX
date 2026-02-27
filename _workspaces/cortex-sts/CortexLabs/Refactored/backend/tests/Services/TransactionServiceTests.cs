// CORE-008: TDD tests for TransactionService
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Tests.Services;

public class TransactionServiceTests
{
    private readonly Mock<ITransactionRepository> _repoMock = new();
    private readonly Mock<ILogger<TransactionService>> _loggerMock = new();
    private TransactionService CreateSut() => new(_repoMock.Object, _loggerMock.Object);

    [Fact]
    public async Task GetByUserAsync_ReturnsPaginatedTransactions()
    {
        var txs = new List<Transaction> { new() { Id = 1, Amount = 100m, Type = TransactionType.Income } };
        _repoMock.Setup(r => r.GetByUserAsync(1, 1, 50, default)).ReturnsAsync(txs);
        var result = await CreateSut().GetByUserAsync(1, 1, 50);
        result.Should().HaveCount(1);
    }

    [Fact]
    public async Task CreateAsync_AutoCategorizes_WhenCategoryEmpty()
    {
        var tx = new Transaction { Amount = 15_000m, CategoryName = "", Type = TransactionType.Expense };
        _repoMock.Setup(r => r.CreateAsync(It.IsAny<Transaction>(), default))
                 .ReturnsAsync((Transaction t, CancellationToken _) => t);
        var result = await CreateSut().CreateAsync(tx);
        result.CategoryName.Should().Be("large_purchase");
    }

    [Fact]
    public async Task CreateAsync_PreservesCategory_WhenAlreadySet()
    {
        var tx = new Transaction { Amount = 50m, CategoryName = "food", Type = TransactionType.Expense };
        _repoMock.Setup(r => r.CreateAsync(It.IsAny<Transaction>(), default))
                 .ReturnsAsync((Transaction t, CancellationToken _) => t);
        var result = await CreateSut().CreateAsync(tx);
        result.CategoryName.Should().Be("food");
    }
}