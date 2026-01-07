using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of ITransactionBatchRepository.
/// Provides database-backed CRUD operations for transaction batches.
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
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionBatch>> GetByStatusAsync(string status)
    {
        return await _context.TransactionBatches
            .Where(b => b.Status == status)
            .OrderByDescending(b => b.BatchDate)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.TransactionBatches
            .Where(b => b.BatchDate >= startDate && b.BatchDate <= endDate)
            .OrderBy(b => b.BatchDate)
            .ToListAsync();
    }

    public async Task<TransactionBatch> CreateAsync(TransactionBatch batch)
    {
        if (string.IsNullOrEmpty(batch.BatchId))
        {
            batch.BatchId = Guid.NewGuid().ToString();
        }

        _context.TransactionBatches.Add(batch);
        await _context.SaveChangesAsync();
        
        return batch;
    }

    public async Task<TransactionBatch> UpdateAsync(TransactionBatch batch)
    {
        var existing = await _context.TransactionBatches.FindAsync(batch.BatchId);
        if (existing == null)
        {
            throw new InvalidOperationException($"Transaction batch {batch.BatchId} not found.");
        }

        _context.Entry(existing).CurrentValues.SetValues(batch);
        await _context.SaveChangesAsync();
        
        return existing;
    }

    public async Task<TransactionBatch> UpdateStatusAsync(string batchId, string newStatus)
    {
        var batch = await _context.TransactionBatches.FindAsync(batchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Transaction batch {batchId} not found.");
        }

        batch.Status = newStatus;
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
}
