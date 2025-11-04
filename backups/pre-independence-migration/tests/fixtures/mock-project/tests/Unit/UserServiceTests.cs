using Xunit;
using MyApp.Services;

namespace MyApp.Tests.Unit;

public class UserServiceTests
{
    [Fact]
    public async Task GetUsersAsync_ReturnsUsers()
    {
        // Arrange
        var service = new UserService();

        // Act
        var result = await service.GetUsersAsync();

        // Assert
        Assert.NotNull(result);
        Assert.NotEmpty(result);
    }
}
