using CortexLabs.FinTrack.Application.Services;

namespace CortexLabs.FinTrack.Tests.Services;

/// <summary>
/// UserService unit tests — fixes SMELL-25 (Assert.True(true) → real assertions).
/// Tests password hashing, validation, and mapping logic.
/// </summary>
public class UserServiceTests
{
    [Fact]
    public void HashPassword_ShouldReturnSaltedHash()
    {
        // Arrange & Act
        var hash = UserService.HashPassword("SecureP@ss123");

        // Assert — format is "salt:base64hash"
        Assert.Contains(":", hash);
        var parts = hash.Split(':');
        Assert.Equal(2, parts.Length);
        Assert.Equal(16, parts[0].Length);  // salt is 16 chars
        Assert.NotEmpty(parts[1]);          // hash is not empty
    }

    [Fact]
    public void HashPassword_SameInput_ShouldProduceDifferentHashes()
    {
        // Arrange & Act
        var hash1 = UserService.HashPassword("SecureP@ss123");
        var hash2 = UserService.HashPassword("SecureP@ss123");

        // Assert — different salts produce different hashes
        Assert.NotEqual(hash1, hash2);
    }

    [Fact]
    public void VerifyPassword_CorrectPassword_ShouldReturnTrue()
    {
        // Arrange
        var hash = UserService.HashPassword("SecureP@ss123");

        // Act & Assert
        Assert.True(UserService.VerifyPassword("SecureP@ss123", hash));
    }

    [Fact]
    public void VerifyPassword_WrongPassword_ShouldReturnFalse()
    {
        // Arrange
        var hash = UserService.HashPassword("SecureP@ss123");

        // Act & Assert
        Assert.False(UserService.VerifyPassword("WrongPassword", hash));
    }

    [Fact]
    public void VerifyPassword_MalformedHash_ShouldReturnFalse()
    {
        // Act & Assert
        Assert.False(UserService.VerifyPassword("any", "nocolon"));
    }
}
