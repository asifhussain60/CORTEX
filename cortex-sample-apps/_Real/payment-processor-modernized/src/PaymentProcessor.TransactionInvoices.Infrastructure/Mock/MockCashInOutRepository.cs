using System.Collections.Concurrent;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Mock;

/// <summary>
/// In-memory mock implementation of ICashInOutRepository.
/// Tracks cash transactions with relationship to invoices.
/// </summary>
public class MockCashInOutRepository : ICashInOutRepository
{
    private readonly ConcurrentDictionary<string, CashInOut> _transactions = new();

    public Task<CashInOut?> GetByIdAsync(string transactionId)
    {
        _transactions.TryGetValue(transactionId, out var transaction);
        return Task.FromResult(transaction);
    }

    public Task<IEnumerable<CashInOut>> GetAllAsync()
    {
        return Task.FromResult(_transactions.Values.AsEnumerable());
    }

    public Task<IEnumerable<CashInOut>> GetByInvoiceIdAsync(string invoiceId)
    {
        var transactions = _transactions.Values.Where(t => t.InvoiceId == invoiceId);
        return Task.FromResult(transactions);
    }

    public Task<IEnumerable<CashInOut>> GetByAccountCategoryIdAsync(string account_categoryId)
    {
        var transactions = _transactions.Values.Where(t => t.AccountCategoryId == account_categoryId);
        return Task.FromResult(transactions);
    }

    public Task<IEnumerable<CashInOut>> GetByTransactionTypeAsync(string transactionType)
    {
        var transactions = _transactions.Values.Where(t => t.TransactionType == transactionType);
        return Task.FromResult(transactions);
    }

    public Task<CashInOut> CreateAsync(CashInOut transaction)
    {
        if (string.IsNullOrEmpty(transaction.TransactionId))
        {
            transaction.TransactionId = $"TXN-{Guid.NewGuid():N}";
        }

        transaction.TransactionDate = DateTime.UtcNow;

        if (!_transactions.TryAdd(transaction.TransactionId, transaction))
        {
            throw new InvalidOperationException($"Transaction with ID {transaction.TransactionId} already exists");
        }

        return Task.FromResult(transaction);
    }

    public Task<CashInOut> UpdateAsync(CashInOut transaction)
    {
        if (!_transactions.ContainsKey(transaction.TransactionId))
        {
            throw new KeyNotFoundException($"Transaction with ID {transaction.TransactionId} not found");
        }

        _transactions[transaction.TransactionId] = transaction;
        return Task.FromResult(transaction);
    }

    public Task<bool> DeleteAsync(string transactionId)
    {
        return Task.FromResult(_transactions.TryRemove(transactionId, out _));
    }

    internal void Seed(CashInOut transaction)
    {
        _transactions.TryAdd(transaction.TransactionId, transaction);
    }

    internal void Clear()
    {
        _transactions.Clear();
    }
}
