using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;

/// <summary>
/// EF Core implementation of ITransactionBatchRepository.
/// Provides database-backed CRUD operations for TransactionBatch entities.
/// </summary>
public class EFCoreTransactionBatchRepository : ITransactionBatchRepository
{
    private readonly TransactionInvoicesDbContext _context;

    public EFCoreTransactionBatchRepository(TransactionInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<TransactionBatch?> GetByIdAsync(string batchId)
    {
        return await _context.TransactionBatches
            .Include(b => b.TransactionInvoices)
            .Include(b => b.CashTransactions)
            .FirstOrDefaultAsync(b => b.BatchId == batchId);
    }

    public async Task<IEnumerable<TransactionBatch>> GetAllAsync()
    {
        return await _context.TransactionBatches
            .Include(b => b.TransactionInvoices)
            .Include(b => b.CashTransactions)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionBatch>> GetByStatusAsync(string status)
    {
        return await _context.TransactionBatches
            .Where(b => b.Status == status)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.TransactionBatches
            .Where(b => b.BatchDate >= startDate && b.BatchDate <= endDate)
            .ToListAsync();
    }

    public async Task<TransactionBatch?> GetByBatchNumberAsync(string batchNumber)
    {
        return await _context.TransactionBatches
            .Include(b => b.TransactionInvoices)
            .Include(b => b.CashTransactions)
            .FirstOrDefaultAsync(b => b.BatchNumber == batchNumber);
    }

    public async Task<TransactionBatch> CreateAsync(TransactionBatch batch)
    {
        _context.TransactionBatches.Add(batch);
        await _context.SaveChangesAsync();
        return batch;
    }

    public async Task<TransactionBatch> UpdateAsync(TransactionBatch batch)
    {
        _context.Entry(batch).State = EntityState.Modified;
        await _context.SaveChangesAsync();
        return batch;
    }

    public async Task<bool> DeleteAsync(string batchId)
    {
        var batch = await _context.TransactionBatches.FindAsync(batchId);
        if (batch == null)
        {
            return false;
        }

        _context.TransactionBatches.Remove(batch);
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task<int> CountAsync()
    {
        return await _context.TransactionBatches.CountAsync();
    }
}
