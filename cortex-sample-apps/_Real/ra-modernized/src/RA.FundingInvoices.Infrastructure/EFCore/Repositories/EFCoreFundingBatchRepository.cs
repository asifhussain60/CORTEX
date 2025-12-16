using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of IFundingBatchRepository.
/// Provides database-backed CRUD operations for funding batches.
/// </summary>
public class EFCoreFundingBatchRepository : IFundingBatchRepository
{
    private readonly FundingInvoicesDbContext _context;

    public EFCoreFundingBatchRepository(FundingInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<FundingBatch?> GetByIdAsync(string batchId)
    {
        return await _context.FundingBatches
            .Include(b => b.FundingInvoices)
            .Include(b => b.CashTransactions)
            .FirstOrDefaultAsync(b => b.BatchId == batchId);
    }

    public async Task<IEnumerable<FundingBatch>> GetAllAsync()
    {
        return await _context.FundingBatches
            .Include(b => b.FundingInvoices)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingBatch>> GetByStatusAsync(string status)
    {
        return await _context.FundingBatches
            .Where(b => b.Status == status)
            .OrderByDescending(b => b.BatchDate)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.FundingBatches
            .Where(b => b.BatchDate >= startDate && b.BatchDate <= endDate)
            .OrderBy(b => b.BatchDate)
            .ToListAsync();
    }

    public async Task<FundingBatch> CreateAsync(FundingBatch batch)
    {
        if (string.IsNullOrEmpty(batch.BatchId))
        {
            batch.BatchId = Guid.NewGuid().ToString();
        }

        _context.FundingBatches.Add(batch);
        await _context.SaveChangesAsync();
        
        return batch;
    }

    public async Task<FundingBatch> UpdateAsync(FundingBatch batch)
    {
        var existing = await _context.FundingBatches.FindAsync(batch.BatchId);
        if (existing == null)
        {
            throw new InvalidOperationException($"Funding batch {batch.BatchId} not found.");
        }

        _context.Entry(existing).CurrentValues.SetValues(batch);
        await _context.SaveChangesAsync();
        
        return existing;
    }

    public async Task<FundingBatch> UpdateStatusAsync(string batchId, string newStatus)
    {
        var batch = await _context.FundingBatches.FindAsync(batchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Funding batch {batchId} not found.");
        }

        batch.Status = newStatus;
        await _context.SaveChangesAsync();
        
        return batch;
    }

    public async Task<bool> DeleteAsync(string batchId)
    {
        var batch = await _context.FundingBatches.FindAsync(batchId);
        if (batch == null)
        {
            return false;
        }

        _context.FundingBatches.Remove(batch);
        await _context.SaveChangesAsync();
        
        return true;
    }
}
