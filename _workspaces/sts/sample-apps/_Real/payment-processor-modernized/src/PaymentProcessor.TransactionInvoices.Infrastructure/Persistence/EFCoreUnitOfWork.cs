using Microsoft.EntityFrameworkCore.Storage;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence;

/// <summary>
/// EF Core implementation of Unit of Work pattern.
/// Manages transactions and coordinates repositories to ensure data consistency.
/// </summary>
public class EFCoreUnitOfWork : IUnitOfWork
{
    private readonly TransactionInvoicesDbContext _context;
    private IDbContextTransaction? _currentTransaction;
    private bool _disposed;

    // Lazy-loaded repositories
    private ITransactionInvoiceRepository? _transactionInvoiceRepository;
    private ITransactionBatchRepository? _transactionBatchRepository;
    private IAccountCategoryRepository? _account_categoryRepository;
    private ICashInOutRepository? _cashInOutRepository;

    public EFCoreUnitOfWork(TransactionInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public ITransactionInvoiceRepository TransactionInvoiceRepository
    {
        get
        {
            _transactionInvoiceRepository ??= new EFCoreTransactionInvoiceRepository(_context);
            return _transactionInvoiceRepository;
        }
    }

    public ITransactionBatchRepository TransactionBatchRepository
    {
        get
        {
            _transactionBatchRepository ??= new EFCoreTransactionBatchRepository(_context);
            return _transactionBatchRepository;
        }
    }

    public IAccountCategoryRepository AccountCategoryRepository
    {
        get
        {
            _account_categoryRepository ??= new EFCoreAccountCategoryRepository(_context);
            return _account_categoryRepository;
        }
    }

    public ICashInOutRepository CashInOutRepository
    {
        get
        {
            _cashInOutRepository ??= new EFCoreCashInOutRepository(_context);
            return _cashInOutRepository;
        }
    }

    public async Task<int> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync();
    }

    public async Task BeginTransactionAsync()
    {
        if (_currentTransaction != null)
        {
            throw new InvalidOperationException("A transaction is already in progress.");
        }

        _currentTransaction = await _context.Database.BeginTransactionAsync();
    }

    public async Task CommitTransactionAsync()
    {
        if (_currentTransaction == null)
        {
            throw new InvalidOperationException("No transaction in progress to commit.");
        }

        try
        {
            await _context.SaveChangesAsync();
            await _currentTransaction.CommitAsync();
        }
        catch
        {
            await RollbackTransactionAsync();
            throw;
        }
        finally
        {
            if (_currentTransaction != null)
            {
                await _currentTransaction.DisposeAsync();
                _currentTransaction = null;
            }
        }
    }

    public async Task RollbackTransactionAsync()
    {
        if (_currentTransaction == null)
        {
            throw new InvalidOperationException("No transaction in progress to rollback.");
        }

        try
        {
            await _currentTransaction.RollbackAsync();
        }
        finally
        {
            if (_currentTransaction != null)
            {
                await _currentTransaction.DisposeAsync();
                _currentTransaction = null;
            }
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                // Dispose transaction if active
                if (_currentTransaction != null)
                {
                    _currentTransaction.Dispose();
                    _currentTransaction = null;
                }

                // Dispose context
                _context.Dispose();
            }

            _disposed = true;
        }
    }
}
