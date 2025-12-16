using System.Collections.Concurrent;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.Mock;

/// <summary>
/// In-memory mock implementation of IFundingInvoiceRepository.
/// Thread-safe using ConcurrentDictionary for fast testing without database dependencies.
/// </summary>
public class MockFundingInvoiceRepository : IFundingInvoiceRepository
{
    private readonly ConcurrentDictionary<string, FundingInvoice> _invoices = new();

    public Task<FundingInvoice?> GetByIdAsync(string invoiceId)
    {
        _invoices.TryGetValue(invoiceId, out var invoice);
        return Task.FromResult(invoice);
    }

    public Task<IEnumerable<FundingInvoice>> GetAllAsync()
    {
        return Task.FromResult(_invoices.Values.AsEnumerable());
    }

    public Task<IEnumerable<FundingInvoice>> GetByBatchIdAsync(string batchId)
    {
        var invoices = _invoices.Values.Where(i => i.BatchId == batchId);
        return Task.FromResult(invoices);
    }

    public Task<IEnumerable<FundingInvoice>> GetBySubaccountIdAsync(string subaccountId)
    {
        var invoices = _invoices.Values.Where(i => i.SubaccountId == subaccountId);
        return Task.FromResult(invoices);
    }

    public Task<IEnumerable<FundingInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        var invoices = _invoices.Values.Where(i => 
            i.CreatedDate >= startDate && i.CreatedDate <= endDate);
        return Task.FromResult(invoices);
    }

    public Task<FundingInvoice> CreateAsync(FundingInvoice invoice)
    {
        if (string.IsNullOrEmpty(invoice.InvoiceId))
        {
            invoice.InvoiceId = $"INV-{Guid.NewGuid():N}";
        }

        invoice.CreatedDate = DateTime.UtcNow;

        if (!_invoices.TryAdd(invoice.InvoiceId, invoice))
        {
            throw new InvalidOperationException($"Invoice with ID {invoice.InvoiceId} already exists");
        }

        return Task.FromResult(invoice);
    }

    public Task<FundingInvoice> UpdateAsync(FundingInvoice invoice)
    {
        if (!_invoices.ContainsKey(invoice.InvoiceId))
        {
            throw new KeyNotFoundException($"Invoice with ID {invoice.InvoiceId} not found");
        }

        _invoices[invoice.InvoiceId] = invoice;
        return Task.FromResult(invoice);
    }

    public Task<bool> DeleteAsync(string invoiceId)
    {
        return Task.FromResult(_invoices.TryRemove(invoiceId, out _));
    }

    public Task<bool> ExistsAsync(string invoiceId)
    {
        return Task.FromResult(_invoices.ContainsKey(invoiceId));
    }

    // Internal method for seeding data
    internal void Seed(FundingInvoice invoice)
    {
        _invoices.TryAdd(invoice.InvoiceId, invoice);
    }

    // Internal method for clearing data (test cleanup)
    internal void Clear()
    {
        _invoices.Clear();
    }
}
