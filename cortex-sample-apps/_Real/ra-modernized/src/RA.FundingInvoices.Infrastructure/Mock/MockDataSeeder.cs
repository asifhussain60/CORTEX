using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.Mock;

/// <summary>
/// Seeds mock repositories with 100+ realistic test scenarios.
/// Covers success cases, error scenarios, edge cases, and relationship testing.
/// </summary>
public class MockDataSeeder
{
    private readonly MockFundingInvoiceRepository _invoiceRepo;
    private readonly MockFundingBatchRepository _batchRepo;
    private readonly MockSubaccountRepository _subaccountRepo;
    private readonly MockCashInOutRepository _cashRepo;

    public MockDataSeeder(
        IFundingInvoiceRepository invoiceRepo,
        IFundingBatchRepository batchRepo,
        ISubaccountRepository subaccountRepo,
        ICashInOutRepository cashRepo)
    {
        _invoiceRepo = (MockFundingInvoiceRepository)invoiceRepo;
        _batchRepo = (MockFundingBatchRepository)batchRepo;
        _subaccountRepo = (MockSubaccountRepository)subaccountRepo;
        _cashRepo = (MockCashInOutRepository)cashRepo;
    }

    public void SeedData()
    {
        SeedSubaccounts();
        SeedBatches();
        SeedInvoices();
        SeedCashTransactions();
    }

    private void SeedSubaccounts()
    {
        // Success scenarios - 20 valid subaccounts
        for (int i = 1; i <= 20; i++)
        {
            _subaccountRepo.Seed(new Subaccount
            {
                SubaccountId = $"SUB-{i:D6}",
                EmployerId = $"EMP-{(i % 5) + 1:D3}",
                MemberId = $"MEM-{i:D6}",
                MemberName = $"Test Member {i}",
                AccountType = i % 3 == 0 ? "HSA" : i % 3 == 1 ? "FSA" : "HRA",
                Balance = 1000m + (i * 100),
                CreatedDate = DateTime.UtcNow.AddDays(-i * 10)
            });
        }

        // Edge cases - Boundary values
        _subaccountRepo.Seed(new Subaccount
        {
            SubaccountId = "SUB-ZERO-BAL",
            EmployerId = "EMP-001",
            MemberId = "MEM-ZERO",
            MemberName = "Zero Balance Member",
            AccountType = "HSA",
            Balance = 0m,
            CreatedDate = DateTime.UtcNow
        });

        _subaccountRepo.Seed(new Subaccount
        {
            SubaccountId = "SUB-MAX-BAL",
            EmployerId = "EMP-001",
            MemberId = "MEM-MAX",
            MemberName = "Maximum Balance Member",
            AccountType = "HSA",
            Balance = 999999.99m,
            CreatedDate = DateTime.UtcNow
        });
    }

    private void SeedBatches()
    {
        // Success scenarios - Various statuses
        _batchRepo.Seed(new FundingBatch
        {
            BatchId = "BATCH-001",
            EmployerId = "EMP-001",
            CreatedDate = DateTime.UtcNow.AddDays(-30),
            ProcessedDate = DateTime.UtcNow.AddDays(-29),
            Status = "Completed",
            TotalInvoices = 25,
            TotalAmount = 12500m
        });

        _batchRepo.Seed(new FundingBatch
        {
            BatchId = "BATCH-002",
            EmployerId = "EMP-002",
            CreatedDate = DateTime.UtcNow.AddDays(-15),
            Status = "Processing",
            TotalInvoices = 10,
            TotalAmount = 5000m
        });

        _batchRepo.Seed(new FundingBatch
        {
            BatchId = "BATCH-003",
            EmployerId = "EMP-003",
            CreatedDate = DateTime.UtcNow.AddDays(-5),
            Status = "Pending",
            TotalInvoices = 0,
            TotalAmount = 0m
        });

        // Edge cases
        _batchRepo.Seed(new FundingBatch
        {
            BatchId = "BATCH-EMPTY",
            EmployerId = "EMP-999",
            CreatedDate = DateTime.UtcNow,
            Status = "Pending",
            TotalInvoices = 0,
            TotalAmount = 0m
        });

        _batchRepo.Seed(new FundingBatch
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
            _batchRepo.Seed(new FundingBatch
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
            _invoiceRepo.Seed(new FundingInvoice
            {
                InvoiceId = $"INV-{i:D6}",
                BatchId = $"BATCH-{(i % 10) + 1:D3}",
                SubaccountId = $"SUB-{(i % 20) + 1:D6}",
                Amount = 100m + (i * 10),
                CreatedDate = DateTime.UtcNow.AddDays(-i),
                ProcessedDate = i % 2 == 0 ? DateTime.UtcNow.AddDays(-i + 1) : null,
                Status = i % 2 == 0 ? "Completed" : "Pending"
            });
        }

        // Edge cases - Boundary values
        _invoiceRepo.Seed(new FundingInvoice
        {
            InvoiceId = "INV-MIN-AMOUNT",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-000001",
            Amount = 0.01m,
            CreatedDate = DateTime.UtcNow,
            Status = "Pending"
        });

        _invoiceRepo.Seed(new FundingInvoice
        {
            InvoiceId = "INV-MAX-AMOUNT",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-000002",
            Amount = 99999.99m,
            CreatedDate = DateTime.UtcNow,
            Status = "Pending"
        });

        // Error scenarios - Invalid references (for testing foreign key validation)
        _invoiceRepo.Seed(new FundingInvoice
        {
            InvoiceId = "INV-INVALID-BATCH",
            BatchId = "BATCH-NONEXISTENT",
            SubaccountId = "SUB-000001",
            Amount = 500m,
            CreatedDate = DateTime.UtcNow,
            Status = "Error"
        });

        _invoiceRepo.Seed(new FundingInvoice
        {
            InvoiceId = "INV-INVALID-SUB",
            BatchId = "BATCH-001",
            SubaccountId = "SUB-NONEXISTENT",
            Amount = 500m,
            CreatedDate = DateTime.UtcNow,
            Status = "Error"
        });

        // Date range testing - Old invoices
        for (int i = 1; i <= 10; i++)
        {
            _invoiceRepo.Seed(new FundingInvoice
            {
                InvoiceId = $"INV-OLD-{i:D3}",
                BatchId = "BATCH-LARGE",
                SubaccountId = $"SUB-{(i % 20) + 1:D6}",
                Amount = 250m,
                CreatedDate = DateTime.UtcNow.AddDays(-365 - i),
                ProcessedDate = DateTime.UtcNow.AddDays(-365 - i + 1),
                Status = "Completed"
            });
        }

        // Recent invoices
        for (int i = 1; i <= 10; i++)
        {
            _invoiceRepo.Seed(new FundingInvoice
            {
                InvoiceId = $"INV-RECENT-{i:D3}",
                BatchId = "BATCH-003",
                SubaccountId = $"SUB-{(i % 20) + 1:D6}",
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
                SubaccountId = $"SUB-{(i % 20) + 1:D6}",
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
                SubaccountId = $"SUB-{(i % 20) + 1:D6}",
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
            SubaccountId = "SUB-000001",
            TransactionType = "CashIn",
            Amount = 0.01m,
            TransactionDate = DateTime.UtcNow,
            Status = "Pending"
        });

        _cashRepo.Seed(new CashInOut
        {
            TransactionId = "TXN-MAX",
            InvoiceId = "INV-MAX-AMOUNT",
            SubaccountId = "SUB-000002",
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
            SubaccountId = "SUB-000001",
            TransactionType = "CashIn",
            Amount = 500m,
            TransactionDate = DateTime.UtcNow.AddDays(-1),
            Status = "Failed"
        });
    }

    /// <summary>
    /// Returns total count of seeded entities for verification.
    /// </summary>
    public (int Subaccounts, int Batches, int Invoices, int Transactions) GetSeedCounts()
    {
        return (
            Subaccounts: 22,      // 20 + 2 edge cases
            Batches: 15,          // 5 + 10 performance
            Invoices: 74,         // 50 + 2 edge + 2 error + 10 old + 10 recent
            Transactions: 53      // 30 cash-in + 20 cash-out + 2 edge + 1 error
        );
    }
}
