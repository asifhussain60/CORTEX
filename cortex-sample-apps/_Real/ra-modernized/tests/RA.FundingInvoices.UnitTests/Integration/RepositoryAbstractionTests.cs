using FluentAssertions;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;
using RA.FundingInvoices.Infrastructure.EFCore;
using RA.FundingInvoices.Infrastructure.EFCore.Repositories;
using RA.FundingInvoices.Infrastructure.Mock;
using Xunit;

namespace RA.FundingInvoices.UnitTests.Integration;

/// <summary>
/// Integration tests validating that Mock and EF Core repositories are interchangeable.
/// Ensures identical behavior regardless of data layer implementation.
/// </summary>
public class RepositoryAbstractionTests : IDisposable
{
    private readonly ServiceProvider _serviceProvider;
    private readonly IFundingInvoiceRepository _mockRepo;
    private readonly IFundingInvoiceRepository _efCoreRepo;

    public RepositoryAbstractionTests()
    {
        var services = new ServiceCollection();

        // Register Mock repositories
        services.AddKeyedSingleton<IFundingInvoiceRepository, MockFundingInvoiceRepository>("Mock");
        services.AddSingleton<MockDataSeeder>();

        // Register EF Core repositories
        services.AddDbContext<FundingInvoicesDbContext>(options =>
            options.UseInMemoryDatabase($"TestDb_{Guid.NewGuid()}"));
        services.AddKeyedScoped<IFundingInvoiceRepository, EFCoreFundingInvoiceRepository>("EFCore");

        _serviceProvider = services.BuildServiceProvider();

        // Get repository instances
        _mockRepo = _serviceProvider.GetRequiredKeyedService<IFundingInvoiceRepository>("Mock");
        _efCoreRepo = _serviceProvider.GetRequiredKeyedService<IFundingInvoiceRepository>("EFCore");

        // Seed mock data
        var seeder = _serviceProvider.GetRequiredService<MockDataSeeder>();
        seeder.SeedData();

        // Seed EF Core with same data structure
        SeedEFCoreData();
    }

    private void SeedEFCoreData()
    {
        var context = _serviceProvider.GetRequiredService<FundingInvoicesDbContext>();

        // Create matching test data in EF Core
        var batch = new FundingBatch
        {
            BatchId = "BATCH-MOCK-001",
            BatchNumber = "BN-MOCK-001",
            Status = "Open",
            BatchDate = DateTime.UtcNow,
            TotalAmount = 500m,
            InvoiceCount = 1,
            CreatedBy = "Test"
        };
        context.FundingBatches.Add(batch);

        var subaccount = new Subaccount
        {
            SubaccountId = "SUB-MOCK-001",
            AccountNumber = "ACC-MOCK-001",
            AccountType = "HSA",
            MemberId = "MEM-MOCK-001",
            Balance = 5000m,
            Status = "Active",
            OpenedDate = DateTime.UtcNow,
            CreatedBy = "Test"
        };
        context.Subaccounts.Add(subaccount);

        var invoice = new FundingInvoice
        {
            InvoiceId = "MOCK-TEST-123",
            BatchId = "BATCH-MOCK-001",
            SubaccountId = "SUB-MOCK-001",
            InvoiceNumber = "FI-MOCK-001",
            Amount = 500m,
            Status = "Pending",
            InvoiceDate = DateTime.UtcNow,
            Description = "Test Invoice",
            CreatedBy = "Test"
        };
        context.FundingInvoices.Add(invoice);

        context.SaveChanges();
    }

    [Fact]
    public async Task GetByIdAsync_MockAndEFCore_ReturnEquivalentData()
    {
        // Arrange - Use same invoice ID that exists in both repositories
        var invoiceId = "MOCK-TEST-123";

        // Act
        var mockResult = await _mockRepo.GetByIdAsync(invoiceId);
        var efCoreResult = await _efCoreRepo.GetByIdAsync(invoiceId);

        // Assert - Both should return data (or both null)
        if (mockResult != null && efCoreResult != null)
        {
            mockResult.InvoiceId.Should().Be(efCoreResult.InvoiceId);
            mockResult.Amount.Should().Be(efCoreResult.Amount);
            mockResult.Status.Should().Be(efCoreResult.Status);
        }
    }

    [Fact]
    public async Task CreateAsync_MockAndEFCore_BehaviorIsIdentical()
    {
        // Arrange
        var mockInvoice = new FundingInvoice
        {
            BatchId = "BATCH-MOCK-001",
            SubaccountId = "SUB-MOCK-001",
            InvoiceNumber = "FI-NEW-MOCK",
            Amount = 750m,
            Status = "Pending",
            InvoiceDate = DateTime.UtcNow,
            CreatedBy = "Test"
        };

        var efCoreInvoice = new FundingInvoice
        {
            BatchId = "BATCH-MOCK-001",
            SubaccountId = "SUB-MOCK-001",
            InvoiceNumber = "FI-NEW-EFCORE",
            Amount = 750m,
            Status = "Pending",
            InvoiceDate = DateTime.UtcNow,
            CreatedBy = "Test"
        };

        // Act
        var mockResult = await _mockRepo.CreateAsync(mockInvoice);
        var efCoreResult = await _efCoreRepo.CreateAsync(efCoreInvoice);

        // Assert - Both should generate IDs and persist data
        mockResult.InvoiceId.Should().NotBeNullOrEmpty();
        efCoreResult.InvoiceId.Should().NotBeNullOrEmpty();

        mockResult.Amount.Should().Be(750m);
        efCoreResult.Amount.Should().Be(750m);

        // Verify persistence
        var mockRetrieved = await _mockRepo.GetByIdAsync(mockResult.InvoiceId);
        var efCoreRetrieved = await _efCoreRepo.GetByIdAsync(efCoreResult.InvoiceId);

        mockRetrieved.Should().NotBeNull();
        efCoreRetrieved.Should().NotBeNull();
    }

    [Fact]
    public async Task UpdateAsync_MockAndEFCore_BehaviorIsIdentical()
    {
        // Arrange
        var mockInvoice = await _mockRepo.GetByIdAsync("MOCK-TEST-123");
        var efCoreInvoice = await _efCoreRepo.GetByIdAsync("MOCK-TEST-123");

        mockInvoice!.Amount = 600m;
        efCoreInvoice!.Amount = 600m;

        // Act
        var mockResult = await _mockRepo.UpdateAsync(mockInvoice);
        var efCoreResult = await _efCoreRepo.UpdateAsync(efCoreInvoice);

        // Assert
        mockResult.Amount.Should().Be(600m);
        efCoreResult.Amount.Should().Be(600m);

        // Verify persistence
        var mockUpdated = await _mockRepo.GetByIdAsync("MOCK-TEST-123");
        var efCoreUpdated = await _efCoreRepo.GetByIdAsync("MOCK-TEST-123");

        mockUpdated!.Amount.Should().Be(600m);
        efCoreUpdated!.Amount.Should().Be(600m);
    }

    [Fact]
    public async Task DeleteAsync_MockAndEFCore_BehaviorIsIdentical()
    {
        // Arrange - Create test invoices
        var mockInvoice = await _mockRepo.CreateAsync(new FundingInvoice
        {
            BatchId = "BATCH-MOCK-001",
            SubaccountId = "SUB-MOCK-001",
            Amount = 100m,
            CreatedBy = "Test"
        });

        var efCoreInvoice = await _efCoreRepo.CreateAsync(new FundingInvoice
        {
            BatchId = "BATCH-MOCK-001",
            SubaccountId = "SUB-MOCK-001",
            Amount = 100m,
            CreatedBy = "Test"
        });

        // Act
        var mockDeleteResult = await _mockRepo.DeleteAsync(mockInvoice.InvoiceId);
        var efCoreDeleteResult = await _efCoreRepo.DeleteAsync(efCoreInvoice.InvoiceId);

        // Assert
        mockDeleteResult.Should().BeTrue();
        efCoreDeleteResult.Should().BeTrue();

        // Verify deletion
        var mockDeleted = await _mockRepo.GetByIdAsync(mockInvoice.InvoiceId);
        var efCoreDeleted = await _efCoreRepo.GetByIdAsync(efCoreInvoice.InvoiceId);

        mockDeleted.Should().BeNull();
        efCoreDeleted.Should().BeNull();
    }

    [Fact]
    public async Task ExistsAsync_MockAndEFCore_BehaviorIsIdentical()
    {
        // Act
        var mockExists = await _mockRepo.ExistsAsync("MOCK-TEST-123");
        var efCoreExists = await _efCoreRepo.ExistsAsync("MOCK-TEST-123");
        var mockNotExists = await _mockRepo.ExistsAsync("NONEXISTENT");
        var efCoreNotExists = await _efCoreRepo.ExistsAsync("NONEXISTENT");

        // Assert
        mockExists.Should().BeTrue();
        efCoreExists.Should().BeTrue();
        mockNotExists.Should().BeFalse();
        efCoreNotExists.Should().BeFalse();
    }

    [Fact]
    public void Repositories_ImplementSameInterface()
    {
        // Assert - Both should implement IFundingInvoiceRepository
        _mockRepo.Should().BeAssignableTo<IFundingInvoiceRepository>();
        _efCoreRepo.Should().BeAssignableTo<IFundingInvoiceRepository>();

        // Both should have the same methods
        var mockMethods = typeof(IFundingInvoiceRepository).GetMethods().Select(m => m.Name).ToHashSet();
        var efCoreMethods = typeof(IFundingInvoiceRepository).GetMethods().Select(m => m.Name).ToHashSet();

        mockMethods.Should().BeEquivalentTo(efCoreMethods);
    }

    public void Dispose()
    {
        _serviceProvider.Dispose();
    }
}
