// ✅ CORTEX Refactored — UserServiceTests
// ✅ AP-007 RESOLVED: XxxServiceTests class for every XxxService class (ENH-STS-04)
// ✅ SMELL-12 RESOLVED: Real assertions, not Assert.True(true)
// ✅ CORE-008 (TDD): tests written before implementation was reviewed

using Xunit;
using Moq;
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Services;
using CortexLabs.FinTrack.Services.Interfaces;
using CortexLabs.FinTrack.Repositories.Interfaces;

namespace CortexLabs.FinTrack.Tests;

/// <summary>
/// Unit tests for UserService — covers CRUD, validation delegation, and pagination.
/// </summary>
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _userRepoMock;
    private readonly Mock<IValidationService> _validationMock;
    private readonly Mock<ILogger<UserService>> _loggerMock;
    private readonly UserService _sut;

    public UserServiceTests()
    {
        _userRepoMock = new Mock<IUserRepository>();
        _validationMock = new Mock<IValidationService>();
        _loggerMock = new Mock<ILogger<UserService>>();
        _sut = new UserService(_userRepoMock.Object, _validationMock.Object, _loggerMock.Object);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Constructor guard clauses
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public void Constructor_NullRepository_Throws()
    {
        Assert.Throws<ArgumentNullException>(() =>
            new UserService(null!, _validationMock.Object, _loggerMock.Object));
    }

    [Fact]
    public void Constructor_NullValidationService_Throws()
    {
        Assert.Throws<ArgumentNullException>(() =>
            new UserService(_userRepoMock.Object, null!, _loggerMock.Object));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GetByIdAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task GetByIdAsync_ExistingUser_ReturnsMappedDto()
    {
        // Arrange
        var user = new User { Id = 1, UserName = "alice", Email = "alice@example.com", Role = "user", IsActive = true };
        _userRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(user);

        // Act
        var result = await _sut.GetByIdAsync(1);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(1, result!.Id);
        Assert.Equal("alice", result.UserName);
        Assert.Equal("alice@example.com", result.Email);
    }

    [Fact]
    public async Task GetByIdAsync_MissingUser_ReturnsNull()
    {
        _userRepoMock.Setup(r => r.GetByIdAsync(999)).ReturnsAsync((User?)null);

        var result = await _sut.GetByIdAsync(999);

        Assert.Null(result);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GetAllAsync (pagination)
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task GetAllAsync_ReturnsPagedUsers()
    {
        // Arrange
        var users = new List<User>
        {
            new() { Id = 1, UserName = "alice", Email = "alice@example.com", Role = "user", IsActive = true },
            new() { Id = 2, UserName = "bob", Email = "bob@example.com", Role = "user", IsActive = true }
        };
        _userRepoMock.Setup(r => r.GetPagedAsync(1, 20)).ReturnsAsync(users);

        // Act
        var result = (await _sut.GetAllAsync(1, 20)).ToList();

        // Assert
        Assert.Equal(2, result.Count);
        Assert.Equal("alice", result[0].UserName);
        Assert.Equal("bob", result[1].UserName);
    }

    [Fact]
    public async Task GetAllAsync_EmptyPage_ReturnsEmptyCollection()
    {
        _userRepoMock.Setup(r => r.GetPagedAsync(99, 20)).ReturnsAsync(new List<User>());

        var result = await _sut.GetAllAsync(99, 20);

        Assert.Empty(result);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // CreateAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task CreateAsync_ValidDto_CallsRepositoryAndReturnsMappedDto()
    {
        // Arrange
        var dto = new CreateUserDto("alice", "alice@example.com", "SecurePass1!", "user");
        _validationMock
            .Setup(v => v.ValidateUser(dto))
            .Returns(new ValidationResult(true, Array.Empty<string>()));

        var createdUser = new User { Id = 42, UserName = "alice", Email = "alice@example.com", Role = "user", IsActive = true };
        _userRepoMock.Setup(r => r.CreateAsync(It.IsAny<User>())).ReturnsAsync(createdUser);

        // Act
        var result = await _sut.CreateAsync(dto);

        // Assert
        Assert.Equal(42, result.Id);
        Assert.Equal("alice", result.UserName);
        _userRepoMock.Verify(r => r.CreateAsync(It.IsAny<User>()), Times.Once);
    }

    [Fact]
    public async Task CreateAsync_InvalidDto_ThrowsValidationException()
    {
        // Arrange
        var dto = new CreateUserDto("", "bad-email", "pw", "user");
        _validationMock
            .Setup(v => v.ValidateUser(dto))
            .Returns(new ValidationResult(false, new[] { "UserName is required", "Invalid email format" }));

        // Act & Assert
        var ex = await Assert.ThrowsAsync<ValidationException>(() => _sut.CreateAsync(dto));
        Assert.Contains("UserName is required", ex.Errors);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // UpdateAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task UpdateAsync_MissingUser_ReturnsFalse()
    {
        _userRepoMock.Setup(r => r.GetByIdAsync(999)).ReturnsAsync((User?)null);

        var result = await _sut.UpdateAsync(999, new UpdateUserDto(null, null, null));

        Assert.False(result);
    }

    [Fact]
    public async Task UpdateAsync_InvalidEmail_ThrowsValidationException()
    {
        // Arrange
        var user = new User { Id = 1, UserName = "alice", Email = "alice@example.com", Role = "user", IsActive = true };
        _userRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(user);
        _validationMock
            .Setup(v => v.ValidateEmail("bad"))
            .Returns(new ValidationResult(false, new[] { "Invalid email format" }));

        // Act & Assert
        await Assert.ThrowsAsync<ValidationException>(() =>
            _sut.UpdateAsync(1, new UpdateUserDto("bad", null, null)));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // DeleteAsync
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public async Task DeleteAsync_ExistingUser_CallsRepositoryDeleteAndReturnsTrue()
    {
        _userRepoMock.Setup(r => r.DeleteAsync(1)).ReturnsAsync(true);

        var result = await _sut.DeleteAsync(1);

        Assert.True(result);
        _userRepoMock.Verify(r => r.DeleteAsync(1), Times.Once);
    }

    [Fact]
    public async Task DeleteAsync_MissingUser_ReturnsFalse()
    {
        _userRepoMock.Setup(r => r.DeleteAsync(999)).ReturnsAsync(false);

        var result = await _sut.DeleteAsync(999);

        Assert.False(result);
    }
}
