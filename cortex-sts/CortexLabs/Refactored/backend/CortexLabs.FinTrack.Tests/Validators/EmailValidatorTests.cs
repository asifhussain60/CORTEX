using CortexLabs.FinTrack.Application.Validators;

namespace CortexLabs.FinTrack.Tests.Validators;

/// <summary>
/// EmailValidator tests — verifies the extracted validation logic (SMELL-07 fix).
/// Real assertions replacing Assert.True(true) (SMELL-25 fix).
/// </summary>
public class EmailValidatorTests
{
    [Theory]
    [InlineData("user@example.com", true)]
    [InlineData("admin@cortex-labs.io", true)]
    [InlineData("first.last@domain.co.uk", true)]
    [InlineData("user+tag@gmail.com", true)]
    [InlineData("", false)]
    [InlineData(null, false)]
    [InlineData("notanemail", false)]
    [InlineData("@domain.com", false)]
    [InlineData("user@", false)]
    [InlineData("user@.com", false)]
    [InlineData("user@domain", false)]
    public void IsValid_ShouldReturnExpectedResult(string? email, bool expected)
    {
        // Act
        var result = EmailValidator.IsValid(email);

        // Assert
        Assert.Equal(expected, result);
    }
}
