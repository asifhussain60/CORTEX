namespace RA.FundingInvoices.Core.Interfaces;

/// <summary>
/// Unit of Work pattern for coordinating repository transactions.
/// Ensures atomic operations across multiple repositories.
/// </summary>
public interface IUnitOfWork : IDisposable
{
    /// <summary>
    /// Gets the FundingInvoice repository.
    /// </summary>
    IFundingInvoiceRepository FundingInvoices { get; }

    /// <summary>
    /// Gets the FundingBatch repository.
    /// </summary>
    IFundingBatchRepository FundingBatches { get; }

    /// <summary>
    /// Gets the Subaccount repository.
    /// </summary>
    ISubaccountRepository Subaccounts { get; }

    /// <summary>
    /// Gets the CashInOut repository.
    /// </summary>
    ICashInOutRepository CashTransactions { get; }

    /// <summary>
    /// Begins a new transaction.
    /// </summary>
    Task BeginTransactionAsync();

    /// <summary>
    /// Commits the current transaction (saves all changes).
    /// </summary>
    /// <returns>Number of entities saved.</returns>
    Task<int> CommitAsync();

    /// <summary>
    /// Rolls back the current transaction (discards all changes).
    /// </summary>
    Task RollbackAsync();

    /// <summary>
    /// Saves changes without explicit transaction management.
    /// </summary>
    /// <returns>Number of entities saved.</returns>
    Task<int> SaveChangesAsync();
}
