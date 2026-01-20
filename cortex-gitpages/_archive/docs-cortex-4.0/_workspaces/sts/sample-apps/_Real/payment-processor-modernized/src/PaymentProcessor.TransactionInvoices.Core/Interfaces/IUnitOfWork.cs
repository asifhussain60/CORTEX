namespace PaymentProcessor.TransactionInvoices.Core.Interfaces;

/// <summary>
/// Unit of Work pattern for coordinating repository transactions.
/// Ensures atomic operations across multiple repositories.
/// </summary>
public interface IUnitOfWork : IDisposable
{
    /// <summary>
    /// Gets the TransactionInvoice repository.
    /// </summary>
    ITransactionInvoiceRepository TransactionInvoices { get; }

    /// <summary>
    /// Gets the TransactionBatch repository.
    /// </summary>
    ITransactionBatchRepository TransactionBatches { get; }

    /// <summary>
    /// Gets the AccountCategory repository.
    /// </summary>
    IAccountCategoryRepository AccountCategorys { get; }

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
