using RA.FundingInvoices.Core.Interfaces;
using RA.FundingInvoices.Infrastructure.Mock;

namespace RA.FundingInvoices.UnitTests.Mock;

public class MockFundingInvoiceRepositoryTests
{
    private readonly MockFundingInvoiceRepository _repository;

    public MockFundingInvoiceRepositoryTests()
    {
        _repository = new MockFundingInvoiceRepository();
    }

    [Fact]
    public async Task CreateAsync_ShouldGenerateId_WhenIdIsEmpty()
    {
        // Arrange
        var invoice = new FundingInvoice
        {
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 500m,
            Status = "Pending"
        };

        // Act
        var result = await _repository.CreateAsync(invoice);

        // Assert
        result.InvoiceId.Should().NotBeNullOrEmpty();
        result.InvoiceId.Should().StartWith("INV-");
        result.CreatedDate.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(1));
    }

    [Fact]
    public async Task CreateAsync_ShouldThrow_WhenDuplicateId()
    {
        // Arrange
        var invoice1 = new FundingInvoice
        {
            InvoiceId = "INV-DUPLICATE",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 500m
        };

        var invoice2 = new FundingInvoice
        {
            InvoiceId = "INV-DUPLICATE",
            BatchId = "BATCH-002",
            SubaccountId = "SUB-002",
            Amount = 300m
        };

        // Act
        await _repository.CreateAsync(invoice1);
        var act = async () => await _repository.CreateAsync(invoice2);

        // Assert
        await act.Should().ThrowAsync<InvalidOperationException>()
            .WithMessage("*already exists*");
    }

    [Fact]
    public async Task GetByIdAsync_ShouldReturnInvoice_WhenExists()
    {
        // Arrange
        var invoice = new FundingInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 500m
        };
        await _repository.CreateAsync(invoice);

        // Act
        var result = await _repository.GetByIdAsync("INV-001");

        // Assert
        result.Should().NotBeNull();
        result!.InvoiceId.Should().Be("INV-001");
        result.Amount.Should().Be(500m);
    }

    [Fact]
    public async Task GetByIdAsync_ShouldReturnNull_WhenNotExists()
    {
        // Act
        var result = await _repository.GetByIdAsync("INV-NONEXISTENT");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task GetByBatchIdAsync_ShouldReturnMatchingInvoices()
    {
        // Arrange
        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 100m
        });

        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-002",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-002",
            Amount = 200m
        });

        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-003",
            BatchId = "BATCH-002",
            SubaccountId = "SUB-003",
            Amount = 300m
        });

        // Act
        var result = await _repository.GetByBatchIdAsync("BATCH-001");

        // Assert
        result.Should().HaveCount(2);
        result.Should().OnlyContain(i => i.BatchId == "BATCH-001");
    }

    [Fact]
    public async Task GetBySubaccountIdAsync_ShouldReturnMatchingInvoices()
    {
        // Arrange
        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 100m
        });

        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-002",
            BatchId = "BATCH-002",
            SubaccountId = "SUB-001",
            Amount = 200m
        });

        // Act
        var result = await _repository.GetBySubaccountIdAsync("SUB-001");

        // Assert
        result.Should().HaveCount(2);
        result.Should().OnlyContain(i => i.SubaccountId == "SUB-001");
    }

    [Fact]
    public async Task GetByDateRangeAsync_ShouldReturnInvoicesInRange()
    {
        // Arrange
        _repository.Seed(new FundingInvoice
        {
            InvoiceId = "INV-OLD",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 100m,
            CreatedDate = DateTime.UtcNow.AddDays(-30)
        });

        _repository.Seed(new FundingInvoice
        {
            InvoiceId = "INV-RECENT",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 200m,
            CreatedDate = DateTime.UtcNow.AddDays(-5)
        });

        _repository.Seed(new FundingInvoice
        {
            InvoiceId = "INV-FUTURE",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 300m,
            CreatedDate = DateTime.UtcNow.AddDays(5)
        });

        // Act
        var result = await _repository.GetByDateRangeAsync(
            DateTime.UtcNow.AddDays(-10),
            DateTime.UtcNow);

        // Assert
        result.Should().ContainSingle();
        result.First().InvoiceId.Should().Be("INV-RECENT");
    }

    [Fact]
    public async Task UpdateAsync_ShouldModifyInvoice_WhenExists()
    {
        // Arrange
        var invoice = new FundingInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 500m,
            Status = "Pending"
        };
        await _repository.CreateAsync(invoice);

        // Act
        invoice.Amount = 750m;
        invoice.Status = "Completed";
        var result = await _repository.UpdateAsync(invoice);

        // Assert
        result.Amount.Should().Be(750m);
        result.Status.Should().Be("Completed");

        var retrieved = await _repository.GetByIdAsync("INV-001");
        retrieved!.Amount.Should().Be(750m);
    }

    [Fact]
    public async Task UpdateAsync_ShouldThrow_WhenNotExists()
    {
        // Arrange
        var invoice = new FundingInvoice
        {
            InvoiceId = "INV-NONEXISTENT",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 500m
        };

        // Act
        var act = async () => await _repository.UpdateAsync(invoice);

        // Assert
        await act.Should().ThrowAsync<KeyNotFoundException>()
            .WithMessage("*not found*");
    }

    [Fact]
    public async Task DeleteAsync_ShouldRemoveInvoice_WhenExists()
    {
        // Arrange
        var invoice = new FundingInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 500m
        };
        await _repository.CreateAsync(invoice);

        // Act
        var result = await _repository.DeleteAsync("INV-001");

        // Assert
        result.Should().BeTrue();

        var retrieved = await _repository.GetByIdAsync("INV-001");
        retrieved.Should().BeNull();
    }

    [Fact]
    public async Task DeleteAsync_ShouldReturnFalse_WhenNotExists()
    {
        // Act
        var result = await _repository.DeleteAsync("INV-NONEXISTENT");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task ExistsAsync_ShouldReturnTrue_WhenExists()
    {
        // Arrange
        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 500m
        });

        // Act
        var result = await _repository.ExistsAsync("INV-001");

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task ExistsAsync_ShouldReturnFalse_WhenNotExists()
    {
        // Act
        var result = await _repository.ExistsAsync("INV-NONEXISTENT");

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public async Task GetAllAsync_ShouldReturnAllInvoices()
    {
        // Arrange
        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-001",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-001",
            Amount = 100m
        });

        await _repository.CreateAsync(new FundingInvoice
        {
            InvoiceId = "INV-002",
            BatchId = "BATCH-002",
            SubaccountId = "SUB-002",
            Amount = 200m
        });

        // Act
        var result = await _repository.GetAllAsync();

        // Assert
        result.Should().HaveCount(2);
    }

    [Fact]
    public async Task Repository_ShouldBeThreadSafe()
    {
        // Arrange
        var tasks = new List<Task>();

        // Act - Create 100 invoices concurrently
        for (int i = 0; i < 100; i++)
        {
            var index = i;
            tasks.Add(Task.Run(async () =>
            {
                await _repository.CreateAsync(new FundingInvoice
                {
                    InvoiceId = $"INV-{index:D6}",
                    BatchId = "BATCH-001",
                    SubaccountId = "SUB-001",
                    Amount = 100m + index
                });
            }));
        }

        await Task.WhenAll(tasks);

        // Assert
        var all = await _repository.GetAllAsync();
        all.Should().HaveCount(100);
    }
}
