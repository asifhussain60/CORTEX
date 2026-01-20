using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Mock;

/// <summary>
/// Mock implementation of Unit of Work pattern.
/// Provides transaction simulation for coordinated repository operations.
/// </summary>
public class MockUnitOfWork : IUnitOfWork
{
    private bool _isTransactionActive;
    private readonly List<Action> _pendingActions = new();

    public ITransactionInvoiceRepository TransactionInvoices { get; }
    public ITransactionBatchRepository TransactionBatches { get; }
    public IAccountCategoryRepository AccountCategorys { get; }
    public ICashInOutRepository CashTransactions { get; }

    public MockUnitOfWork(
        ITransactionInvoiceRepository transactionInvoices,
        ITransactionBatchRepository transactionBatches,
        IAccountCategoryRepository account_categorys,
        ICashInOutRepository cashTransactions)
    {
        TransactionInvoices = transactionInvoices;
        TransactionBatches = transactionBatches;
        AccountCategorys = account_categorys;
        CashTransactions = cashTransactions;
    }

    public Task BeginTransactionAsync()
    {
        _isTransactionActive = true;
        _pendingActions.Clear();
        return Task.CompletedTask;
    }

    public Task<int> CommitAsync()
    {
        if (!_isTransactionActive)
        {
            throw new InvalidOperationException("No active transaction to commit");
        }

        // Execute all pending actions
        foreach (var action in _pendingActions)
        {
            action();
        }

        var changeCount = _pendingActions.Count;
        _pendingActions.Clear();
        _isTransactionActive = false;

        return Task.FromResult(changeCount);
    }

    public Task RollbackAsync()
    {
        if (!_isTransactionActive)
        {
            throw new InvalidOperationException("No active transaction to rollback");
        }

        _pendingActions.Clear();
        _isTransactionActive = false;

        return Task.CompletedTask;
    }

    public Task<int> SaveChangesAsync()
    {
        // Mock implementation - changes are immediately persisted in in-memory repositories
        // Return simulated change count
        return Task.FromResult(1);
    }

    public void Dispose()
    {
        if (_isTransactionActive)
        {
            _pendingActions.Clear();
            _isTransactionActive = false;
        }
    }
}
