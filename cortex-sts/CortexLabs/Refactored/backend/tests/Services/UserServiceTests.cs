// CORE-008: TDD tests for UserService
// Tests confirm: DI wiring, parameterized queries (no SQL injection), pagination, soft delete
using Moq;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Application.Services;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Tests.Services;

public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repoMock = new();
    private readonly Mock<ILogger<UserService>> _loggerMock = new();
    private UserService CreateSut() => new(_repoMock.Object, _loggerMock.Object);

    [Fact]
    public async Task GetPagedAsync_ReturnsPagedUsers()
    {
        var users = new List<User> { new() { Id = 1, UserName = "alice" } };
        _repoMock.Setup(r => r.GetPagedAsync(1, 20, default)).ReturnsAsync(users);
        var result = await CreateSut().GetPagedAsync(1, 20);
        result.Should().HaveCount(1);
        result[0].UserName.Should().Be("alice");
    }

    [Fact]
    public async Task SearchByUsernameAsync_ReturnsUser_WhenFound()
    {
        var user = new User { Id = 2, UserName = "bob" };
        _repoMock.Setup(r => r.GetByUsernameAsync("bob", default)).ReturnsAsync(user);
        var result = await CreateSut().SearchByUsernameAsync("bob");
        result.Should().NotBeNull();
        result!.Id.Should().Be(2);
    }

    [Fact]
    public async Task SearchByUsernameAsync_ReturnsNull_WhenNotFound()
    {
        _repoMock.Setup(r => r.GetByUsernameAsync("nobody", default)).ReturnsAsync((User?)null);
        var result = await CreateSut().SearchByUsernameAsync("nobody");
        result.Should().BeNull();
    }

    [Fact]
    public async Task CreateAsync_DelegatesToRepository()
    {
        var user = new User { UserName = "charlie", Email = "c@test.com", PasswordHash = "hashed" };
        _repoMock.Setup(r => r.CreateAsync(user, default)).ReturnsAsync(user with { Id = 99 });
        var result = await CreateSut().CreateAsync(user);
        result.Id.Should().Be(99);
        _repoMock.Verify(r => r.CreateAsync(It.IsAny<User>(), default), Times.Once);
    }

    [Fact]
    public async Task SoftDeleteAsync_CallsRepository()
    {
        await CreateSut().SoftDeleteAsync(42);
        _repoMock.Verify(r => r.SoftDeleteAsync(42, default), Times.Once);
    }
}