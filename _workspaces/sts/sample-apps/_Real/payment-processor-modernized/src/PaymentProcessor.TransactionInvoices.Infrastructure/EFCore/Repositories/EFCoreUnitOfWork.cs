using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of IUnitOfWork.
/// Coordinates transactions across multiple repositories.
/// </summary>
public class EFCoreUnitOfWork : IUnitOfWork
{
    private readonly TransactionInvoicesDbContext _context;
    private bool _disposed;

    public EFCoreUnitOfWork(TransactionInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<int> SaveChangesAsync()
    {
        return await _context.SaveChangesAsync();
    }

    public async Task BeginTransactionAsync()
    {
        if (_context.Database.CurrentTransaction == null)
        {
            await _context.Database.BeginTransactionAsync();
        }
    }

    public async Task CommitTransactionAsync()
    {
        try
        {
            await _context.SaveChangesAsync();
            await _context.Database.CurrentTransaction?.CommitAsync()!;
        }
        catch
        {
            await RollbackTransactionAsync();
            throw;
        }
    }

    public async Task RollbackTransactionAsync()
    {
        await _context.Database.CurrentTransaction?.RollbackAsync()!;
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed && disposing)
        {
            _context.Database.CurrentTransaction?.Dispose();
            _context.Dispose();
        }
        _disposed = true;
    }
}
