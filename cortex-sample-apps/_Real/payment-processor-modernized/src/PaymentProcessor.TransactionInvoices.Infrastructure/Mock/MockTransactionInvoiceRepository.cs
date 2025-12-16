using System.Collections.Concurrent;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Mock;

/// <summary>
/// In-memory mock implementation of ITransactionInvoiceRepository.
/// Thread-safe using ConcurrentDictionary for fast testing without database dependencies.
/// </summary>
public class MockTransactionInvoiceRepository : ITransactionInvoiceRepository
{
    private readonly ConcurrentDictionary<string, TransactionInvoice> _invoices = new();

    public Task<TransactionInvoice?> GetByIdAsync(string invoiceId)
    {
        _invoices.TryGetValue(invoiceId, out var invoice);
        return Task.FromResult(invoice);
    }

    public Task<IEnumerable<TransactionInvoice>> GetAllAsync()
    {
        return Task.FromResult(_invoices.Values.AsEnumerable());
    }

    public Task<IEnumerable<TransactionInvoice>> GetByBatchIdAsync(string batchId)
    {
        var invoices = _invoices.Values.Where(i => i.BatchId == batchId);
        return Task.FromResult(invoices);
    }

    public Task<IEnumerable<TransactionInvoice>> GetByAccountCategoryIdAsync(string account_categoryId)
    {
        var invoices = _invoices.Values.Where(i => i.AccountCategoryId == account_categoryId);
        return Task.FromResult(invoices);
    }

    public Task<IEnumerable<TransactionInvoice>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        var invoices = _invoices.Values.Where(i => 
            i.CreatedDate >= startDate && i.CreatedDate <= endDate);
        return Task.FromResult(invoices);
    }

    public Task<TransactionInvoice> CreateAsync(TransactionInvoice invoice)
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

    public Task<TransactionInvoice> UpdateAsync(TransactionInvoice invoice)
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
    internal void Seed(TransactionInvoice invoice)
    {
        _invoices.TryAdd(invoice.InvoiceId, invoice);
    }

    // Internal method for clearing data (test cleanup)
    internal void Clear()
    {
        _invoices.Clear();
    }
}
