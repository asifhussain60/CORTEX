using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;

/// <summary>
/// EF Core implementation of ICashInOutRepository.
/// Provides database-backed CRUD operations for CashInOut entities.
/// </summary>
public class EFCoreCashInOutRepository : ICashInOutRepository
{
    private readonly TransactionInvoicesDbContext _context;

    public EFCoreCashInOutRepository(TransactionInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<CashInOut?> GetByIdAsync(string transactionId)
    {
        return await _context.CashTransactions
            .Include(c => c.TransactionBatch)
            .FirstOrDefaultAsync(c => c.TransactionId == transactionId);
    }

    public async Task<IEnumerable<CashInOut>> GetAllAsync()
    {
        return await _context.CashTransactions
            .Include(c => c.TransactionBatch)
            .ToListAsync();
    }

    public async Task<IEnumerable<CashInOut>> GetByBatchIdAsync(string batchId)
    {
        return await _context.CashTransactions
            .Where(c => c.BatchId == batchId)
            .ToListAsync();
    }

    public async Task<IEnumerable<CashInOut>> GetByTransactionTypeAsync(string transactionType)
    {
        return await _context.CashTransactions
            .Where(c => c.TransactionType == transactionType)
            .ToListAsync();
    }

    public async Task<IEnumerable<CashInOut>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.CashTransactions
            .Where(c => c.TransactionDate >= startDate && c.TransactionDate <= endDate)
            .ToListAsync();
    }

    public async Task<IEnumerable<CashInOut>> GetByStatusAsync(string status)
    {
        return await _context.CashTransactions
            .Where(c => c.Status == status)
            .ToListAsync();
    }

    public async Task<CashInOut> CreateAsync(CashInOut transaction)
    {
        _context.CashTransactions.Add(transaction);
        await _context.SaveChangesAsync();
        return transaction;
    }

    public async Task<CashInOut> UpdateAsync(CashInOut transaction)
    {
        _context.Entry(transaction).State = EntityState.Modified;
        await _context.SaveChangesAsync();
        return transaction;
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

    public async Task<int> CountAsync()
    {
        return await _context.CashTransactions.CountAsync();
    }
}
