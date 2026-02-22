// ✅ CORTEX Refactored — ValidationServiceTests
// ✅ SMELL-12 RESOLVED: Real assertions, not Assert.True(true)

using Xunit;
using CortexLabs.FinTrack.Services;
using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Tests;

/// <summary>
/// Unit tests for ValidationService — comprehensive coverage
/// </summary>
public class ValidationServiceTests
{
    private readonly IValidationService _sut;

    public ValidationServiceTests()
    {
        _sut = new ValidationService();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Email Validation Tests
    // ═══════════════════════════════════════════════════════════════════════════

    [Theory]
    [InlineData("test@example.com", true)]
    [InlineData("user@domain.org", true)]
    [InlineData("name.surname@company.co.uk", true)]
    public void ValidateEmail_ValidEmail_ReturnsValid(string email, bool expectedValid)
    {
        // Act
        var result = _sut.ValidateEmail(email);

        // Assert
        Assert.Equal(expectedValid, result.IsValid);
        Assert.Empty(result.Errors);
    }

    [Theory]
    [InlineData(null, "Email is required")]
    [InlineData("", "Email is required")]
    [InlineData("   ", "Email is required")]
    public void ValidateEmail_EmptyOrNull_ReturnsError(string? email, string expectedError)
    {
        // Act
        var result = _sut.ValidateEmail(email!);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(expectedError, result.Errors);
    }

    [Theory]
    [InlineData("notanemail")]
    [InlineData("missing@dot")]
    [InlineData("@nodomain.com")]
    public void ValidateEmail_InvalidFormat_ReturnsError(string email)
    {
        // Act
        var result = _sut.ValidateEmail(email);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains("Invalid email format", result.Errors);
    }

    [Fact]
    public void ValidateEmail_TooShort_ReturnsError()
    {
        // Act
        var result = _sut.ValidateEmail("a@b");

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.Contains("at least"));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Transaction Validation Tests
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public void ValidateTransaction_ValidDto_ReturnsValid()
    {
        // Arrange
        var dto = new CreateTransactionDto(
            Description: "Grocery shopping",
            Amount: 50.00m,
            Category: "food",
            Type: "expense",
            UserId: 1);

        // Act
        var result = _sut.ValidateTransaction(dto);

        // Assert
        Assert.True(result.IsValid);
        Assert.Empty(result.Errors);
    }

    [Fact]
    public void ValidateTransaction_EmptyDescription_ReturnsError()
    {
        // Arrange
        var dto = new CreateTransactionDto(
            Description: "",
            Amount: 50.00m,
            Category: "food",
            Type: "expense",
            UserId: 1);

        // Act
        var result = _sut.ValidateTransaction(dto);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains("Description is required", result.Errors);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-50)]
    [InlineData(-0.01)]
    public void ValidateTransaction_NonPositiveAmount_ReturnsError(decimal amount)
    {
        // Arrange
        var dto = new CreateTransactionDto(
            Description: "Test",
            Amount: amount,
            Category: "food",
            Type: "expense",
            UserId: 1);

        // Act
        var result = _sut.ValidateTransaction(dto);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains("Amount must be positive", result.Errors);
    }

    [Theory]
    [InlineData("income")]
    [InlineData("expense")]
    [InlineData("INCOME")]
    [InlineData("EXPENSE")]
    public void ValidateTransaction_ValidType_ReturnsValid(string type)
    {
        // Arrange
        var dto = new CreateTransactionDto(
            Description: "Test",
            Amount: 50m,
            Category: "test",
            Type: type,
            UserId: 1);

        // Act
        var result = _sut.ValidateTransaction(dto);

        // Assert
        Assert.True(result.IsValid);
    }

    [Theory]
    [InlineData("transfer")]
    [InlineData("refund")]
    [InlineData("")]
    [InlineData("invalid")]
    public void ValidateTransaction_InvalidType_ReturnsError(string type)
    {
        // Arrange
        var dto = new CreateTransactionDto(
            Description: "Test",
            Amount: 50m,
            Category: "test",
            Type: type,
            UserId: 1);

        // Act
        var result = _sut.ValidateTransaction(dto);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains("Type must be 'income' or 'expense'", result.Errors);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // User Validation Tests
    // ═══════════════════════════════════════════════════════════════════════════

    [Fact]
    public void ValidateUser_ValidDto_ReturnsValid()
    {
        // Arrange
        var dto = new CreateUserDto(
            UserName: "johndoe",
            Email: "john@example.com",
            Password: "SecureP@ss123");

        // Act
        var result = _sut.ValidateUser(dto);

        // Assert
        Assert.True(result.IsValid);
        Assert.Empty(result.Errors);
    }

    [Fact]
    public void ValidateUser_ShortUsername_ReturnsError()
    {
        // Arrange
        var dto = new CreateUserDto(
            UserName: "jo",
            Email: "john@example.com",
            Password: "SecureP@ss123");

        // Act
        var result = _sut.ValidateUser(dto);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.Contains("Username"));
    }

    [Fact]
    public void ValidateUser_ShortPassword_ReturnsError()
    {
        // Arrange
        var dto = new CreateUserDto(
            UserName: "johndoe",
            Email: "john@example.com",
            Password: "short");

        // Act
        var result = _sut.ValidateUser(dto);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains("Password must be at least 8 characters", result.Errors);
    }

    [Fact]
    public void ValidateUser_InvalidRole_ReturnsError()
    {
        // Arrange
        var dto = new CreateUserDto(
            UserName: "johndoe",
            Email: "john@example.com",
            Password: "SecureP@ss123",
            Role: "superadmin");

        // Act
        var result = _sut.ValidateUser(dto);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains("Invalid role", result.Errors);
    }
}
