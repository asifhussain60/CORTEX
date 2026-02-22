using CortexLabs.FinTrack.Infrastructure.Data;
using CortexLabs.FinTrack.Infrastructure.Repositories;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using Microsoft.Extensions.Logging.Abstractions;

namespace CortexLabs.FinTrack.Tests.Endpoints;

/// <summary>
/// Integration tests for repository + database layer.
/// Uses in-memory SQLite (":memory:") for fast, isolated tests.
/// Fixes SMELL-25 (Assert.True(true) → real DB assertions).
/// </summary>
public class RepositoryIntegrationTests : IDisposable
{
    private readonly string _connectionString = "Data Source=:memory:";
    private readonly DatabaseInitializer _dbInit;

    public RepositoryIntegrationTests()
    {
        // For in-memory SQLite, we need a shared connection to keep the DB alive.
        // In tests, we use file-based temp DB instead.
        var tempFile = Path.GetTempFileName();
        _connectionString = $"Data Source={tempFile}";
        _dbInit = new DatabaseInitializer(_connectionString, NullLogger<DatabaseInitializer>.Instance);
        _dbInit.Initialize();
    }

    [Fact]
    public async Task UserRepository_CreateAndRetrieve_ShouldWork()
    {
        // Arrange
        var repo = new UserRepository(_connectionString);
        var user = new User
        {
            Username = "testuser",
            Email = "test@example.com",
            PasswordHash = "salt:hash",
            Role = UserRole.User
        };

        // Act
        var id = await repo.CreateAsync(user);
        var retrieved = await repo.GetByIdAsync(id);

        // Assert
        Assert.NotNull(retrieved);
        Assert.Equal("testuser", retrieved.Username);
        Assert.Equal("test@example.com", retrieved.Email);
        Assert.Equal(UserRole.User, retrieved.Role);
    }

    [Fact]
    public async Task UserRepository_GetByUsername_ShouldFindUser()
    {
        // Arrange
        var repo = new UserRepository(_connectionString);
        await repo.CreateAsync(new User
        {
            Username = "findme",
            Email = "find@example.com",
            PasswordHash = "salt:hash"
        });

        // Act
        var found = await repo.GetByUsernameAsync("findme");

        // Assert
        Assert.NotNull(found);
        Assert.Equal("find@example.com", found.Email);
    }

    [Fact]
    public async Task TransactionRepository_CreateAndCount_ShouldWork()
    {
        // Arrange
        var userRepo = new UserRepository(_connectionString);
        var userId = await userRepo.CreateAsync(new User
        {
            Username = "txnuser",
            Email = "txn@example.com",
            PasswordHash = "salt:hash"
        });

        var txnRepo = new TransactionRepository(_connectionString);
        await txnRepo.CreateAsync(new Transaction
        {
            UserId = userId,
            Amount = 250.50m,
            Type = TransactionType.Expense,
            Category = TransactionCategory.Food,
            Description = "Groceries"
        });

        // Act
        var count = await txnRepo.GetCountByUserIdAsync(userId);
        var total = await txnRepo.GetTotalByUserIdAsync(userId);

        // Assert
        Assert.Equal(1, count);
        Assert.Equal(250.50m, total);
    }

    [Fact]
    public async Task AccountRepository_Pagination_ShouldWork()
    {
        // Arrange
        var userRepo = new UserRepository(_connectionString);
        var userId = await userRepo.CreateAsync(new User
        {
            Username = "acctuser",
            Email = "acct@example.com",
            PasswordHash = "salt:hash"
        });

        var acctRepo = new AccountRepository(_connectionString);
        for (int i = 1; i <= 5; i++)
        {
            await acctRepo.CreateAsync(new Account
            {
                UserId = userId,
                Name = $"Account {i}",
                Type = AccountType.Checking,
                Currency = "USD"
            });
        }

        // Act — page 1, size 2
        var page1 = await acctRepo.GetAllAsync(1, 2);
        var page2 = await acctRepo.GetAllAsync(2, 2);
        var totalCount = await acctRepo.GetCountAsync();

        // Assert
        Assert.Equal(2, page1.Count);
        Assert.Equal(2, page2.Count);
        Assert.Equal(5, totalCount);
    }

    [Fact]
    public async Task UserRepository_Delete_ShouldRemoveUser()
    {
        // Arrange
        var repo = new UserRepository(_connectionString);
        var id = await repo.CreateAsync(new User
        {
            Username = "deleteme",
            Email = "delete@example.com",
            PasswordHash = "salt:hash"
        });

        // Act
        var deleted = await repo.DeleteAsync(id);
        var found = await repo.GetByIdAsync(id);

        // Assert
        Assert.True(deleted);
        Assert.Null(found);
    }

    public void Dispose()
    {
        // Clean up temp file if needed
        var path = _connectionString.Replace("Data Source=", "");
        if (File.Exists(path))
            File.Delete(path);
    }
}
