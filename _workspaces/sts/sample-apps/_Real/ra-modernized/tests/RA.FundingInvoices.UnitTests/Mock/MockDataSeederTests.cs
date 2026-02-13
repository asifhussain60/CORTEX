using RA.FundingInvoices.Infrastructure.Mock;

namespace RA.FundingInvoices.UnitTests.Mock;

public class MockDataSeederTests
{
    [Fact]
    public void SeedData_ShouldCreateExpectedCounts()
    {
        // Arrange
        var invoiceRepo = new MockFundingInvoiceRepository();
        var batchRepo = new MockFundingBatchRepository();
        var subaccountRepo = new MockSubaccountRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, subaccountRepo, cashRepo);

        // Act
        seeder.SeedData();
        var counts = seeder.GetSeedCounts();

        // Assert
        var actualSubaccounts = await subaccountRepo.GetAllAsync();
        var actualBatches = await batchRepo.GetAllAsync();
        var actualInvoices = await invoiceRepo.GetAllAsync();
        var actualTransactions = await cashRepo.GetAllAsync();

        actualSubaccounts.Should().HaveCount(counts.Subaccounts);
        actualBatches.Should().HaveCount(counts.Batches);
        actualInvoices.Should().HaveCount(counts.Invoices);
        actualTransactions.Should().HaveCount(counts.Transactions);
    }

    [Fact]
    public async Task SeedData_ShouldIncludeEdgeCases()
    {
        // Arrange
        var invoiceRepo = new MockFundingInvoiceRepository();
        var batchRepo = new MockFundingBatchRepository();
        var subaccountRepo = new MockSubaccountRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, subaccountRepo, cashRepo);

        // Act
        seeder.SeedData();

        // Assert - Check for edge case entities
        var zeroBalanceSubaccount = await subaccountRepo.GetByIdAsync("SUB-ZERO-BAL");
        zeroBalanceSubaccount.Should().NotBeNull();
        zeroBalanceSubaccount!.Balance.Should().Be(0m);

        var maxBalanceSubaccount = await subaccountRepo.GetByIdAsync("SUB-MAX-BAL");
        maxBalanceSubaccount.Should().NotBeNull();
        maxBalanceSubaccount!.Balance.Should().Be(999999.99m);

        var minAmountInvoice = await invoiceRepo.GetByIdAsync("INV-MIN-AMOUNT");
        minAmountInvoice.Should().NotBeNull();
        minAmountInvoice!.Amount.Should().Be(0.01m);

        var maxAmountInvoice = await invoiceRepo.GetByIdAsync("INV-MAX-AMOUNT");
        maxAmountInvoice.Should().NotBeNull();
        maxAmountInvoice!.Amount.Should().Be(99999.99m);
    }

    [Fact]
    public async Task SeedData_ShouldIncludeVariousStatuses()
    {
        // Arrange
        var invoiceRepo = new MockFundingInvoiceRepository();
        var batchRepo = new MockFundingBatchRepository();
        var subaccountRepo = new MockSubaccountRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, subaccountRepo, cashRepo);

        // Act
        seeder.SeedData();

        // Assert - Check batch statuses
        var completedBatch = await batchRepo.GetByIdAsync("BATCH-001");
        completedBatch.Should().NotBeNull();
        completedBatch!.Status.Should().Be("Completed");
        completedBatch.ProcessedDate.Should().HaveValue();

        var processingBatch = await batchRepo.GetByIdAsync("BATCH-002");
        processingBatch.Should().NotBeNull();
        processingBatch!.Status.Should().Be("Processing");

        var pendingBatch = await batchRepo.GetByIdAsync("BATCH-003");
        pendingBatch.Should().NotBeNull();
        pendingBatch!.Status.Should().Be("Pending");
    }

    [Fact]
    public async Task SeedData_ShouldIncludeAccountTypes()
    {
        // Arrange
        var invoiceRepo = new MockFundingInvoiceRepository();
        var batchRepo = new MockFundingBatchRepository();
        var subaccountRepo = new MockSubaccountRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, subaccountRepo, cashRepo);

        // Act
        seeder.SeedData();

        // Assert - Check account type variety
        var allSubaccounts = await subaccountRepo.GetAllAsync();
        var accountTypes = allSubaccounts.Select(s => s.AccountType).Distinct().ToList();

        accountTypes.Should().Contain("HSA");
        accountTypes.Should().Contain("FSA");
        accountTypes.Should().Contain("HRA");
    }

    [Fact]
    public async Task SeedData_ShouldIncludeTransactionTypes()
    {
        // Arrange
        var invoiceRepo = new MockFundingInvoiceRepository();
        var batchRepo = new MockFundingBatchRepository();
        var subaccountRepo = new MockSubaccountRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, subaccountRepo, cashRepo);

        // Act
        seeder.SeedData();

        // Assert
        var cashInTransactions = await cashRepo.GetByTransactionTypeAsync("CashIn");
        var cashOutTransactions = await cashRepo.GetByTransactionTypeAsync("CashOut");

        cashInTransactions.Should().NotBeEmpty();
        cashOutTransactions.Should().NotBeEmpty();
    }
}
