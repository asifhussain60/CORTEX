using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.Persistence.Repositories;

/// <summary>
/// EF Core implementation of IFundingBatchRepository.
/// Provides database-backed CRUD operations for FundingBatch entities.
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
            .Include(b => b.CashTransactions)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingBatch>> GetByStatusAsync(string status)
    {
        return await _context.FundingBatches
            .Where(b => b.Status == status)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.FundingBatches
            .Where(b => b.BatchDate >= startDate && b.BatchDate <= endDate)
            .ToListAsync();
    }

    public async Task<FundingBatch?> GetByBatchNumberAsync(string batchNumber)
    {
        return await _context.FundingBatches
            .Include(b => b.FundingInvoices)
            .Include(b => b.CashTransactions)
            .FirstOrDefaultAsync(b => b.BatchNumber == batchNumber);
    }

    public async Task<FundingBatch> CreateAsync(FundingBatch batch)
    {
        _context.FundingBatches.Add(batch);
        await _context.SaveChangesAsync();
        return batch;
    }

    public async Task<FundingBatch> UpdateAsync(FundingBatch batch)
    {
        _context.Entry(batch).State = EntityState.Modified;
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

    public async Task<int> CountAsync()
    {
        return await _context.FundingBatches.CountAsync();
    }
}
