using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Mock;

/// <summary>
/// Seeds mock repositories with 100+ realistic test scenarios.
/// Covers success cases, error scenarios, edge cases, and relationship testing.
/// </summary>
public class MockDataSeeder
{
    private readonly MockTransactionInvoiceRepository _invoiceRepo;
    private readonly MockTransactionBatchRepository _batchRepo;
    private readonly MockAccountCategoryRepository _account_categoryRepo;
    private readonly MockCashInOutRepository _cashRepo;

    public MockDataSeeder(
        ITransactionInvoiceRepository invoiceRepo,
        ITransactionBatchRepository batchRepo,
        IAccountCategoryRepository account_categoryRepo,
        ICashInOutRepository cashRepo)
    {
        _invoiceRepo = (MockTransactionInvoiceRepository)invoiceRepo;
        _batchRepo = (MockTransactionBatchRepository)batchRepo;
        _account_categoryRepo = (MockAccountCategoryRepository)account_categoryRepo;
        _cashRepo = (MockCashInOutRepository)cashRepo;
    }

    public void SeedData()
    {
        SeedAccountCategorys();
        SeedBatches();
        SeedInvoices();
        SeedCashTransactions();
    }

    private void SeedAccountCategorys()
    {
        // Success scenarios - 20 valid account_categorys
        for (int i = 1; i <= 20; i++)
        {
            _account_categoryRepo.Seed(new AccountCategory
            {
                AccountCategoryId = $"SUB-{i:D6}",
                EmployerId = $"EMP-{(i % 5) + 1:D3}",
                CustomerId = $"MEM-{i:D6}",
                CustomerName = $"Test Customer {i}",
                AccountType = i % 3 == 0 ? "AccountTypeA" : i % 3 == 1 ? "AccountTypeB" : "AccountTypeC",
                Balance = 1000m + (i * 100),
                CreatedDate = DateTime.UtcNow.AddDays(-i * 10)
            });
        }

        // Edge cases - Boundary values
        _account_categoryRepo.Seed(new AccountCategory
        {
            AccountCategoryId = "SUB-ZERO-BAL",
            EmployerId = "EMP-001",
            CustomerId = "MEM-ZERO",
            CustomerName = "Zero Balance Customer",
            AccountType = "AccountTypeA",
            Balance = 0m,
            CreatedDate = DateTime.UtcNow
        });

        _account_categoryRepo.Seed(new AccountCategory
        {
            AccountCategoryId = "SUB-MAX-BAL",
            EmployerId = "EMP-001",
            CustomerId = "MEM-MAX",
            CustomerName = "Maximum Balance Customer",
            AccountType = "AccountTypeA",
            Balance = 999999.99m,
            CreatedDate = DateTime.UtcNow
        });
    }

    private void SeedBatches()
    {
        // Success scenarios - Various statuses
        _batchRepo.Seed(new TransactionBatch
        {
            BatchId = "BATCH-001",
            EmployerId = "EMP-001",
            CreatedDate = DateTime.UtcNow.AddDays(-30),
            ProcessedDate = DateTime.UtcNow.AddDays(-29),
            Status = "Completed",
            TotalInvoices = 25,
            TotalAmount = 12500m
        });

        _batchRepo.Seed(new TransactionBatch
        {
            BatchId = "BATCH-002",
            EmployerId = "EMP-002",
            CreatedDate = DateTime.UtcNow.AddDays(-15),
            Status = "Processing",
            TotalInvoices = 10,
            TotalAmount = 5000m
        });

        _batchRepo.Seed(new TransactionBatch
        {
            BatchId = "BATCH-003",
            EmployerId = "EMP-003",
            CreatedDate = DateTime.UtcNow.AddDays(-5),
            Status = "Pending",
            TotalInvoices = 0,
            TotalAmount = 0m
        });

        // Edge cases
        _batchRepo.Seed(new TransactionBatch
        {
            BatchId = "BATCH-EMPTY",
            EmployerId = "EMP-999",
            CreatedDate = DateTime.UtcNow,
            Status = "Pending",
            TotalInvoices = 0,
            TotalAmount = 0m
        });

        _batchRepo.Seed(new TransactionBatch
        {
            BatchId = "BATCH-LARGE",
            EmployerId = "EMP-001",
            CreatedDate = DateTime.UtcNow.AddDays(-60),
            ProcessedDate = DateTime.UtcNow.AddDays(-59),
            Status = "Completed",
            TotalInvoices = 1000,
            TotalAmount = 500000m
        });

        // Create 10 more batches for performance testing
        for (int i = 4; i <= 13; i++)
        {
            _batchRepo.Seed(new TransactionBatch
            {
                BatchId = $"BATCH-{i:D3}",
                EmployerId = $"EMP-{(i % 5) + 1:D3}",
                CreatedDate = DateTime.UtcNow.AddDays(-i * 7),
                ProcessedDate = i % 2 == 0 ? DateTime.UtcNow.AddDays(-(i * 7) + 1) : null,
                Status = i % 2 == 0 ? "Completed" : "Pending",
                TotalInvoices = i * 5,
                TotalAmount = i * 1000m
            });
        }
    }

    private void SeedInvoices()
    {
        // Success scenarios - 50 valid invoices
        for (int i = 1; i <= 50; i++)
        {
            _invoiceRepo.Seed(new TransactionInvoice
            {
                InvoiceId = $"INV-{i:D6}",
                BatchId = $"BATCH-{(i % 10) + 1:D3}",
                AccountCategoryId = $"SUB-{(i % 20) + 1:D6}",
                Amount = 100m + (i * 10),
                CreatedDate = DateTime.UtcNow.AddDays(-i),
                ProcessedDate = i % 2 == 0 ? DateTime.UtcNow.AddDays(-i + 1) : null,
                Status = i % 2 == 0 ? "Completed" : "Pending"
            });
        }

        // Edge cases - Boundary values
        _invoiceRepo.Seed(new TransactionInvoice
        {
            InvoiceId = "INV-MIN-AMOUNT",
            BatchId = "BATCH-001",
            AccountCategoryId = "SUB-000001",
            Amount = 0.01m,
            CreatedDate = DateTime.UtcNow,
            Status = "Pending"
        });

        _invoiceRepo.Seed(new TransactionInvoice
        {
            InvoiceId = "INV-MAX-AMOUNT",
            BatchId = "BATCH-001",
            AccountCategoryId = "SUB-000002",
            Amount = 99999.99m,
            CreatedDate = DateTime.UtcNow,
            Status = "Pending"
        });

        // Error scenarios - Invalid references (for testing foreign key validation)
        _invoiceRepo.Seed(new TransactionInvoice
        {
            InvoiceId = "INV-INVALID-BATCH",
            BatchId = "BATCH-NONEXISTENT",
            AccountCategoryId = "SUB-000001",
            Amount = 500m,
            CreatedDate = DateTime.UtcNow,
            Status = "Error"
        });

        _invoiceRepo.Seed(new TransactionInvoice
        {
            InvoiceId = "INV-INVALID-SUB",
            BatchId = "BATCH-001",
            AccountCategoryId = "SUB-NONEXISTENT",
            Amount = 500m,
            CreatedDate = DateTime.UtcNow,
            Status = "Error"
        });

        // Date range testing - Old invoices
        for (int i = 1; i <= 10; i++)
        {
            _invoiceRepo.Seed(new TransactionInvoice
            {
                InvoiceId = $"INV-OLD-{i:D3}",
                BatchId = "BATCH-LARGE",
                AccountCategoryId = $"SUB-{(i % 20) + 1:D6}",
                Amount = 250m,
                CreatedDate = DateTime.UtcNow.AddDays(-365 - i),
                ProcessedDate = DateTime.UtcNow.AddDays(-365 - i + 1),
                Status = "Completed"
            });
        }

        // Recent invoices
        for (int i = 1; i <= 10; i++)
        {
            _invoiceRepo.Seed(new TransactionInvoice
            {
                InvoiceId = $"INV-RECENT-{i:D3}",
                BatchId = "BATCH-003",
                AccountCategoryId = $"SUB-{(i % 20) + 1:D6}",
                Amount = 150m,
                CreatedDate = DateTime.UtcNow.AddHours(-i),
                Status = "Pending"
            });
        }
    }

    private void SeedCashTransactions()
    {
        // Success scenarios - Cash-in transactions
        for (int i = 1; i <= 30; i++)
        {
            _cashRepo.Seed(new CashInOut
            {
                TransactionId = $"TXN-IN-{i:D6}",
                InvoiceId = $"INV-{i:D6}",
                AccountCategoryId = $"SUB-{(i % 20) + 1:D6}",
                TransactionType = "CashIn",
                Amount = 100m + (i * 10),
                TransactionDate = DateTime.UtcNow.AddDays(-i),
                Status = "Completed"
            });
        }

        // Cash-out transactions
        for (int i = 1; i <= 20; i++)
        {
            _cashRepo.Seed(new CashInOut
            {
                TransactionId = $"TXN-OUT-{i:D6}",
                InvoiceId = $"INV-{(i + 30):D6}",
                AccountCategoryId = $"SUB-{(i % 20) + 1:D6}",
                TransactionType = "CashOut",
                Amount = 50m + (i * 5),
                TransactionDate = DateTime.UtcNow.AddDays(-i),
                Status = "Completed"
            });
        }

        // Edge cases
        _cashRepo.Seed(new CashInOut
        {
            TransactionId = "TXN-MIN",
            InvoiceId = "INV-MIN-AMOUNT",
            AccountCategoryId = "SUB-000001",
            TransactionType = "CashIn",
            Amount = 0.01m,
            TransactionDate = DateTime.UtcNow,
            Status = "Pending"
        });

        _cashRepo.Seed(new CashInOut
        {
            TransactionId = "TXN-MAX",
            InvoiceId = "INV-MAX-AMOUNT",
            AccountCategoryId = "SUB-000002",
            TransactionType = "CashIn",
            Amount = 99999.99m,
            TransactionDate = DateTime.UtcNow,
            Status = "Pending"
        });

        // Error scenarios
        _cashRepo.Seed(new CashInOut
        {
            TransactionId = "TXN-FAILED",
            InvoiceId = "INV-000001",
            AccountCategoryId = "SUB-000001",
            TransactionType = "CashIn",
            Amount = 500m,
            TransactionDate = DateTime.UtcNow.AddDays(-1),
            Status = "Failed"
        });
    }

    /// <summary>
    /// Returns total count of seeded entities for verification.
    /// </summary>
    public (int AccountCategorys, int Batches, int Invoices, int Transactions) GetSeedCounts()
    {
        return (
            AccountCategorys: 22,      // 20 + 2 edge cases
            Batches: 15,          // 5 + 10 performance
            Invoices: 74,         // 50 + 2 edge + 2 error + 10 old + 10 recent
            Transactions: 53      // 30 cash-in + 20 cash-out + 2 edge + 1 error
        );
    }
}
