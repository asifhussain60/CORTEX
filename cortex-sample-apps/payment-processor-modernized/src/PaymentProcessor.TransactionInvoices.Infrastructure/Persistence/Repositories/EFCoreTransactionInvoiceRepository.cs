using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;

/// <summary>
/// EF Core implementation of ITransactionInvoiceRepository.
/// Provides database-backed CRUD operations for TransactionInvoice entities.
/// </summary>
public class EFCoreTransactionInvoiceRepository : ITransactionInvoiceRepository
{
    private readonly TransactionInvoicesDbContext _context;

    public EFCoreTransactionInvoiceRepository(TransactionInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<TransactionInvoice?> GetByIdAsync(string invoiceId)
    {
        return await _context.TransactionInvoices
            .Include(i => i.TransactionBatch)
            .Include(i => i.AccountCategory)
            .FirstOrDefaultAsync(i => i.InvoiceId == invoiceId);
    }

    public async Task<IEnumerable<TransactionInvoice>> GetAllAsync()
    {
        return await _context.TransactionInvoices
            .Include(i => i.TransactionBatch)
            .Include(i => i.AccountCategory)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionInvoice>> GetByBatchIdAsync(string batchId)
    {
        return await _context.TransactionInvoices
            .Include(i => i.AccountCategory)
            .Where(i => i.BatchId == batchId)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionInvoice>> GetByAccountCategoryIdAsync(string account_categoryId)
    {
        return await _context.TransactionInvoices
            .Include(i => i.TransactionBatch)
            .Where(i => i.AccountCategoryId == account_categoryId)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.TransactionInvoices
            .Include(i => i.TransactionBatch)
            .Include(i => i.AccountCategory)
            .Where(i => i.InvoiceDate >= startDate && i.InvoiceDate <= endDate)
            .ToListAsync();
    }

    public async Task<TransactionInvoice> CreateAsync(TransactionInvoice invoice)
    {
        _context.TransactionInvoices.Add(invoice);
        await _context.SaveChangesAsync();
        return invoice;
    }

    public async Task<TransactionInvoice> UpdateAsync(TransactionInvoice invoice)
    {
        _context.Entry(invoice).State = EntityState.Modified;
        await _context.SaveChangesAsync();
        return invoice;
    }

    public async Task<bool> DeleteAsync(string invoiceId)
    {
        var invoice = await _context.TransactionInvoices.FindAsync(invoiceId);
        if (invoice == null)
        {
            return false;
        }

        _context.TransactionInvoices.Remove(invoice);
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task<bool> ExistsAsync(string invoiceId)
    {
        return await _context.TransactionInvoices.AnyAsync(i => i.InvoiceId == invoiceId);
    }

    public async Task<int> CountAsync()
    {
        return await _context.TransactionInvoices.CountAsync();
    }
}
