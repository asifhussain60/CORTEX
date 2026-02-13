using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of IFundingInvoiceRepository.
/// Provides database-backed CRUD operations for funding invoices.
/// </summary>
public class EFCoreFundingInvoiceRepository : IFundingInvoiceRepository
{
    private readonly FundingInvoicesDbContext _context;

    public EFCoreFundingInvoiceRepository(FundingInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<FundingInvoice?> GetByIdAsync(string invoiceId)
    {
        return await _context.FundingInvoices
            .Include(f => f.FundingBatch)
            .Include(f => f.Subaccount)
            .FirstOrDefaultAsync(f => f.InvoiceId == invoiceId);
    }

    public async Task<IEnumerable<FundingInvoice>> GetAllAsync()
    {
        return await _context.FundingInvoices
            .Include(f => f.FundingBatch)
            .Include(f => f.Subaccount)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingInvoice>> GetByBatchIdAsync(string batchId)
    {
        return await _context.FundingInvoices
            .Include(f => f.Subaccount)
            .Where(f => f.BatchId == batchId)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingInvoice>> GetBySubaccountIdAsync(string subaccountId)
    {
        return await _context.FundingInvoices
            .Include(f => f.FundingBatch)
            .Where(f => f.SubaccountId == subaccountId)
            .OrderByDescending(f => f.InvoiceDate)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.FundingInvoices
            .Include(f => f.FundingBatch)
            .Include(f => f.Subaccount)
            .Where(f => f.InvoiceDate >= startDate && f.InvoiceDate <= endDate)
            .OrderBy(f => f.InvoiceDate)
            .ToListAsync();
    }

    public async Task<FundingInvoice> CreateAsync(FundingInvoice invoice)
    {
        if (string.IsNullOrEmpty(invoice.InvoiceId))
        {
            invoice.InvoiceId = Guid.NewGuid().ToString();
        }

        _context.FundingInvoices.Add(invoice);
        await _context.SaveChangesAsync();
        
        return invoice;
    }

    public async Task<FundingInvoice> UpdateAsync(FundingInvoice invoice)
    {
        var existing = await _context.FundingInvoices.FindAsync(invoice.InvoiceId);
        if (existing == null)
        {
            throw new InvalidOperationException($"Funding invoice {invoice.InvoiceId} not found.");
        }

        _context.Entry(existing).CurrentValues.SetValues(invoice);
        await _context.SaveChangesAsync();
        
        return existing;
    }

    public async Task<bool> DeleteAsync(string invoiceId)
    {
        var invoice = await _context.FundingInvoices.FindAsync(invoiceId);
        if (invoice == null)
        {
            return false;
        }

        _context.FundingInvoices.Remove(invoice);
        await _context.SaveChangesAsync();
        
        return true;
    }

    public async Task<bool> ExistsAsync(string invoiceId)
    {
        return await _context.FundingInvoices
            .AnyAsync(f => f.InvoiceId == invoiceId);
    }
}
