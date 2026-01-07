using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of ITransactionInvoiceRepository.
/// Provides database-backed CRUD operations for transaction invoices.
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
            .Include(f => f.TransactionBatch)
            .Include(f => f.AccountCategory)
            .FirstOrDefaultAsync(f => f.InvoiceId == invoiceId);
    }

    public async Task<IEnumerable<TransactionInvoice>> GetAllAsync()
    {
        return await _context.TransactionInvoices
            .Include(f => f.TransactionBatch)
            .Include(f => f.AccountCategory)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionInvoice>> GetByBatchIdAsync(string batchId)
    {
        return await _context.TransactionInvoices
            .Include(f => f.AccountCategory)
            .Where(f => f.BatchId == batchId)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionInvoice>> GetByAccountCategoryIdAsync(string account_categoryId)
    {
        return await _context.TransactionInvoices
            .Include(f => f.TransactionBatch)
            .Where(f => f.AccountCategoryId == account_categoryId)
            .OrderByDescending(f => f.InvoiceDate)
            .ToListAsync();
    }

    public async Task<IEnumerable<TransactionInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.TransactionInvoices
            .Include(f => f.TransactionBatch)
            .Include(f => f.AccountCategory)
            .Where(f => f.InvoiceDate >= startDate && f.InvoiceDate <= endDate)
            .OrderBy(f => f.InvoiceDate)
            .ToListAsync();
    }

    public async Task<TransactionInvoice> CreateAsync(TransactionInvoice invoice)
    {
        if (string.IsNullOrEmpty(invoice.InvoiceId))
        {
            invoice.InvoiceId = Guid.NewGuid().ToString();
        }

        _context.TransactionInvoices.Add(invoice);
        await _context.SaveChangesAsync();
        
        return invoice;
    }

    public async Task<TransactionInvoice> UpdateAsync(TransactionInvoice invoice)
    {
        var existing = await _context.TransactionInvoices.FindAsync(invoice.InvoiceId);
        if (existing == null)
        {
            throw new InvalidOperationException($"Transaction invoice {invoice.InvoiceId} not found.");
        }

        _context.Entry(existing).CurrentValues.SetValues(invoice);
        await _context.SaveChangesAsync();
        
        return existing;
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
        return await _context.TransactionInvoices
            .AnyAsync(f => f.InvoiceId == invoiceId);
    }
}
