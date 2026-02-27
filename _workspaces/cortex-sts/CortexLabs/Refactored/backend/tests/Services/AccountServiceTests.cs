// CORE-008: TDD tests for AccountService transfer validation
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Tests.Services;

public class AccountServiceTests
{
    private readonly Mock<IAccountRepository> _repoMock = new();
    private readonly Mock<ILogger<AccountService>> _loggerMock = new();
    private AccountService CreateSut() => new(_repoMock.Object, _loggerMock.Object);

    [Fact]
    public async Task TransferAsync_ThrowsOnNegativeAmount()
    {
        var act = () => CreateSut().TransferAsync(1, 2, -50m);
        await act.Should().ThrowAsync<ArgumentOutOfRangeException>();
    }

    [Fact]
    public async Task TransferAsync_ThrowsOnSameAccount()
    {
        var act = () => CreateSut().TransferAsync(1, 1, 100m);
        await act.Should().ThrowAsync<ArgumentException>();
    }

    [Fact]
    public async Task TransferAsync_ThrowsOnInsufficientFunds()
    {
        _repoMock.Setup(r => r.GetByIdAsync(1, default))
                 .ReturnsAsync(new Account { Id = 1, Balance = 10m });
        var act = () => CreateSut().TransferAsync(1, 2, 100m);
        await act.Should().ThrowAsync<InvalidOperationException>().WithMessage("*Insufficient*");
    }

    [Fact]
    public async Task TransferAsync_CallsRepository_OnValidTransfer()
    {
        _repoMock.Setup(r => r.GetByIdAsync(1, default))
                 .ReturnsAsync(new Account { Id = 1, Balance = 500m });
        await CreateSut().TransferAsync(1, 2, 100m);
        _repoMock.Verify(r => r.TransferAsync(1, 2, 100m, default), Times.Once);
    }
}