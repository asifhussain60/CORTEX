using PaymentProcessor.TransactionInvoices.Infrastructure.Mock;

namespace PaymentProcessor.TransactionInvoices.UnitTests.Mock;

public class MockDataSeederTests
{
    [Fact]
    public void SeedData_ShouldCreateExpectedCounts()
    {
        // Arrange
        var invoiceRepo = new MockTransactionInvoiceRepository();
        var batchRepo = new MockTransactionBatchRepository();
        var account_categoryRepo = new MockAccountCategoryRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, account_categoryRepo, cashRepo);

        // Act
        seeder.SeedData();
        var counts = seeder.GetSeedCounts();

        // Assert
        var actualAccountCategorys = await account_categoryRepo.GetAllAsync();
        var actualBatches = await batchRepo.GetAllAsync();
        var actualInvoices = await invoiceRepo.GetAllAsync();
        var actualTransactions = await cashRepo.GetAllAsync();

        actualAccountCategorys.Should().HaveCount(counts.AccountCategorys);
        actualBatches.Should().HaveCount(counts.Batches);
        actualInvoices.Should().HaveCount(counts.Invoices);
        actualTransactions.Should().HaveCount(counts.Transactions);
    }

    [Fact]
    public async Task SeedData_ShouldIncludeEdgeCases()
    {
        // Arrange
        var invoiceRepo = new MockTransactionInvoiceRepository();
        var batchRepo = new MockTransactionBatchRepository();
        var account_categoryRepo = new MockAccountCategoryRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, account_categoryRepo, cashRepo);

        // Act
        seeder.SeedData();

        // Assert - Check for edge case entities
        var zeroBalanceAccountCategory = await account_categoryRepo.GetByIdAsync("SUB-ZERO-BAL");
        zeroBalanceAccountCategory.Should().NotBeNull();
        zeroBalanceAccountCategory!.Balance.Should().Be(0m);

        var maxBalanceAccountCategory = await account_categoryRepo.GetByIdAsync("SUB-MAX-BAL");
        maxBalanceAccountCategory.Should().NotBeNull();
        maxBalanceAccountCategory!.Balance.Should().Be(999999.99m);

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
        var invoiceRepo = new MockTransactionInvoiceRepository();
        var batchRepo = new MockTransactionBatchRepository();
        var account_categoryRepo = new MockAccountCategoryRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, account_categoryRepo, cashRepo);

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
        var invoiceRepo = new MockTransactionInvoiceRepository();
        var batchRepo = new MockTransactionBatchRepository();
        var account_categoryRepo = new MockAccountCategoryRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, account_categoryRepo, cashRepo);

        // Act
        seeder.SeedData();

        // Assert - Check account type variety
        var allAccountCategorys = await account_categoryRepo.GetAllAsync();
        var accountTypes = allAccountCategorys.Select(s => s.AccountType).Distinct().ToList();

        accountTypes.Should().Contain("AccountTypeA");
        accountTypes.Should().Contain("AccountTypeB");
        accountTypes.Should().Contain("AccountTypeC");
    }

    [Fact]
    public async Task SeedData_ShouldIncludeTransactionTypes()
    {
        // Arrange
        var invoiceRepo = new MockTransactionInvoiceRepository();
        var batchRepo = new MockTransactionBatchRepository();
        var account_categoryRepo = new MockAccountCategoryRepository();
        var cashRepo = new MockCashInOutRepository();

        var seeder = new MockDataSeeder(invoiceRepo, batchRepo, account_categoryRepo, cashRepo);

        // Act
        seeder.SeedData();

        // Assert
        var cashInTransactions = await cashRepo.GetByTransactionTypeAsync("CashIn");
        var cashOutTransactions = await cashRepo.GetByTransactionTypeAsync("CashOut");

        cashInTransactions.Should().NotBeEmpty();
        cashOutTransactions.Should().NotBeEmpty();
    }
}
