using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Tests.Services;

/// <summary>
/// TransactionService unit tests — verifies auto-categorization logic
/// extracted from inline if/else (SMELL-19 fix). Real assertions (SMELL-25 fix).
/// </summary>
public class TransactionServiceTests
{
    [Theory]
    [InlineData(2000, TransactionCategory.LargePurchase)]
    [InlineData(1001, TransactionCategory.LargePurchase)]
    [InlineData(500, TransactionCategory.MediumPurchase)]
    [InlineData(101, TransactionCategory.MediumPurchase)]
    [InlineData(100, TransactionCategory.Other)]
    [InlineData(50, TransactionCategory.Other)]
    [InlineData(0.01, TransactionCategory.Other)]
    public void AutoCategorize_ShouldReturnCorrectCategory(decimal amount, TransactionCategory expected)
    {
        // Act
        var result = TransactionService.AutoCategorize(amount);

        // Assert
        Assert.Equal(expected, result);
    }

    [Fact]
    public void AutoCategorize_BoundaryAt1000_ShouldBeMediumPurchase()
    {
        // 1000 is NOT > 1000, so it should be MediumPurchase
        Assert.Equal(TransactionCategory.MediumPurchase, TransactionService.AutoCategorize(1000m));
    }

    [Fact]
    public void AutoCategorize_BoundaryAt100_ShouldBeOther()
    {
        // 100 is NOT > 100, so it should be Other
        Assert.Equal(TransactionCategory.Other, TransactionService.AutoCategorize(100m));
    }
}
