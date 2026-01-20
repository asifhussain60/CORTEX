using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of ICashInOutRepository.
/// Provides database-backed CRUD operations for cash transactions.
/// </summary>
public class EFCoreCashInOutRepository : ICashInOutRepository
{
    private readonly FundingInvoicesDbContext _context;

    public EFCoreCashInOutRepository(FundingInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<CashInOut?> GetByIdAsync(string transactionId)
    {
        return await _context.CashTransactions
            .Include(c => c.FundingBatch)
            .FirstOrDefaultAsync(c => c.TransactionId == transactionId);
    }

    public async Task<IEnumerable<CashInOut>> GetAllAsync()
    {
        return await _context.CashTransactions
            .Include(c => c.FundingBatch)
            .ToListAsync();
    }

    public async Task<IEnumerable<CashInOut>> GetByBatchIdAsync(string batchId)
    {
        return await _context.CashTransactions
            .Where(c => c.BatchId == batchId)
            .OrderBy(c => c.TransactionDate)
            .ToListAsync();
    }

    public async Task<IEnumerable<CashInOut>> GetByTransactionTypeAsync(string transactionType)
    {
        return await _context.CashTransactions
            .Where(c => c.TransactionType == transactionType)
            .OrderByDescending(c => c.TransactionDate)
            .ToListAsync();
    }

    public async Task<IEnumerable<CashInOut>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.CashTransactions
            .Where(c => c.TransactionDate >= startDate && c.TransactionDate <= endDate)
            .OrderBy(c => c.TransactionDate)
            .ToListAsync();
    }

    public async Task<CashInOut> CreateAsync(CashInOut transaction)
    {
        if (string.IsNullOrEmpty(transaction.TransactionId))
        {
            transaction.TransactionId = Guid.NewGuid().ToString();
        }

        _context.CashTransactions.Add(transaction);
        await _context.SaveChangesAsync();
        
        return transaction;
    }

    public async Task<CashInOut> UpdateAsync(CashInOut transaction)
    {
        var existing = await _context.CashTransactions.FindAsync(transaction.TransactionId);
        if (existing == null)
        {
            throw new InvalidOperationException($"Cash transaction {transaction.TransactionId} not found.");
        }

        _context.Entry(existing).CurrentValues.SetValues(transaction);
        await _context.SaveChangesAsync();
        
        return existing;
    }

    public async Task<bool> DeleteAsync(string transactionId)
    {
        var transaction = await _context.CashTransactions.FindAsync(transactionId);
        if (transaction == null)
        {
            return false;
        }

        _context.CashTransactions.Remove(transaction);
        await _context.SaveChangesAsync();
        
        return true;
    }
}
