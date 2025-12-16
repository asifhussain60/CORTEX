using Microsoft.EntityFrameworkCore.Storage;
using RA.FundingInvoices.Core.Interfaces;
using RA.FundingInvoices.Infrastructure.Persistence.Repositories;

namespace RA.FundingInvoices.Infrastructure.Persistence;

/// <summary>
/// EF Core implementation of Unit of Work pattern.
/// Manages transactions and coordinates repositories to ensure data consistency.
/// </summary>
public class EFCoreUnitOfWork : IUnitOfWork
{
    private readonly FundingInvoicesDbContext _context;
    private IDbContextTransaction? _currentTransaction;
    private bool _disposed;

    // Lazy-loaded repositories
    private IFundingInvoiceRepository? _fundingInvoiceRepository;
    private IFundingBatchRepository? _fundingBatchRepository;
    private ISubaccountRepository? _subaccountRepository;
    private ICashInOutRepository? _cashInOutRepository;

    public EFCoreUnitOfWork(FundingInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public IFundingInvoiceRepository FundingInvoiceRepository
    {
        get
        {
            _fundingInvoiceRepository ??= new EFCoreFundingInvoiceRepository(_context);
            return _fundingInvoiceRepository;
        }
    }

    public IFundingBatchRepository FundingBatchRepository
    {
        get
        {
            _fundingBatchRepository ??= new EFCoreFundingBatchRepository(_context);
            return _fundingBatchRepository;
        }
    }

    public ISubaccountRepository SubaccountRepository
    {
        get
        {
            _subaccountRepository ??= new EFCoreSubaccountRepository(_context);
            return _subaccountRepository;
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
