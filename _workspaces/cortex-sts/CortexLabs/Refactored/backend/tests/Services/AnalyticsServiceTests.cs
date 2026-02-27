// CORE-008: TDD tests for AnalyticsService
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Tests.Services;

public class AnalyticsServiceTests
{
    private readonly Mock<ITransactionRepository> _repoMock = new();
    private readonly Mock<ILogger<AnalyticsService>> _loggerMock = new();
    private AnalyticsService CreateSut() => new(_repoMock.Object, _loggerMock.Object);

    [Fact]
    public async Task GetSummaryAsync_ReturnsHealthy_WhenIncomeExceedsExpenses()
    {
        var txs = new List<Transaction>
        {
            new() { Amount = 5000m, Type = TransactionType.Income },
            new() { Amount = 1000m, Type = TransactionType.Expense },
        };
        _repoMock.Setup(r => r.GetByUserAsync(1, 1, 1000, default)).ReturnsAsync(txs);
        var result = await CreateSut().GetSummaryAsync(1);
        result.HealthScore.Should().Be("healthy");
        result.TotalIncome.Should().Be(5000m);
        result.TotalExpenses.Should().Be(1000m);
    }

    [Fact]
    public async Task GetSummaryAsync_ReturnsCritical_WhenExpensesExceed150PercentOfIncome()
    {
        var txs = new List<Transaction>
        {
            new() { Amount = 1000m, Type = TransactionType.Income },
            new() { Amount = 2000m, Type = TransactionType.Expense },
        };
        _repoMock.Setup(r => r.GetByUserAsync(1, 1, 1000, default)).ReturnsAsync(txs);
        var result = await CreateSut().GetSummaryAsync(1);
        result.HealthScore.Should().Be("critical");
    }
}