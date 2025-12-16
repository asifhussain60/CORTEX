using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.Persistence.Repositories;

/// <summary>
/// EF Core implementation of IFundingInvoiceRepository.
/// Provides database-backed CRUD operations for FundingInvoice entities.
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
            .Include(i => i.FundingBatch)
            .Include(i => i.Subaccount)
            .FirstOrDefaultAsync(i => i.InvoiceId == invoiceId);
    }

    public async Task<IEnumerable<FundingInvoice>> GetAllAsync()
    {
        return await _context.FundingInvoices
            .Include(i => i.FundingBatch)
            .Include(i => i.Subaccount)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingInvoice>> GetByBatchIdAsync(string batchId)
    {
        return await _context.FundingInvoices
            .Include(i => i.Subaccount)
            .Where(i => i.BatchId == batchId)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingInvoice>> GetBySubaccountIdAsync(string subaccountId)
    {
        return await _context.FundingInvoices
            .Include(i => i.FundingBatch)
            .Where(i => i.SubaccountId == subaccountId)
            .ToListAsync();
    }

    public async Task<IEnumerable<FundingInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        return await _context.FundingInvoices
            .Include(i => i.FundingBatch)
            .Include(i => i.Subaccount)
            .Where(i => i.InvoiceDate >= startDate && i.InvoiceDate <= endDate)
            .ToListAsync();
    }

    public async Task<FundingInvoice> CreateAsync(FundingInvoice invoice)
    {
        _context.FundingInvoices.Add(invoice);
        await _context.SaveChangesAsync();
        return invoice;
    }

    public async Task<FundingInvoice> UpdateAsync(FundingInvoice invoice)
    {
        _context.Entry(invoice).State = EntityState.Modified;
        await _context.SaveChangesAsync();
        return invoice;
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
        return await _context.FundingInvoices.AnyAsync(i => i.InvoiceId == invoiceId);
    }

    public async Task<int> CountAsync()
    {
        return await _context.FundingInvoices.CountAsync();
    }
}
