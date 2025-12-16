using System.Collections.Concurrent;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Mock;

/// <summary>
/// In-memory mock implementation of IAccountCategoryRepository.
/// Supports complex filtering and search operations.
/// </summary>
public class MockAccountCategoryRepository : IAccountCategoryRepository
{
    private readonly ConcurrentDictionary<string, AccountCategory> _account_categorys = new();

    public Task<AccountCategory?> GetByIdAsync(string account_categoryId)
    {
        _account_categorys.TryGetValue(account_categoryId, out var account_category);
        return Task.FromResult(account_category);
    }

    public Task<IEnumerable<AccountCategory>> GetAllAsync()
    {
        return Task.FromResult(_account_categorys.Values.AsEnumerable());
    }

    public Task<IEnumerable<AccountCategory>> GetByEmployerIdAsync(string employerId)
    {
        var account_categorys = _account_categorys.Values.Where(s => s.EmployerId == employerId);
        return Task.FromResult(account_categorys);
    }

    public Task<IEnumerable<AccountCategory>> GetByAccountTypeAsync(string accountType)
    {
        var account_categorys = _account_categorys.Values.Where(s => s.AccountType == accountType);
        return Task.FromResult(account_categorys);
    }

    public Task<IEnumerable<AccountCategory>> SearchAsync(string searchTerm)
    {
        var account_categorys = _account_categorys.Values.Where(s =>
            s.CustomerId.Contains(searchTerm, StringComparison.OrdinalIgnoreCase) ||
            s.CustomerName.Contains(searchTerm, StringComparison.OrdinalIgnoreCase));
        return Task.FromResult(account_categorys);
    }

    public Task<AccountCategory> CreateAsync(AccountCategory account_category)
    {
        if (string.IsNullOrEmpty(account_category.AccountCategoryId))
        {
            account_category.AccountCategoryId = $"SUB-{Guid.NewGuid():N}";
        }

        account_category.CreatedDate = DateTime.UtcNow;

        if (!_account_categorys.TryAdd(account_category.AccountCategoryId, account_category))
        {
            throw new InvalidOperationException($"AccountCategory with ID {account_category.AccountCategoryId} already exists");
        }

        return Task.FromResult(account_category);
    }

    public Task<AccountCategory> UpdateAsync(AccountCategory account_category)
    {
        if (!_account_categorys.ContainsKey(account_category.AccountCategoryId))
        {
            throw new KeyNotFoundException($"AccountCategory with ID {account_category.AccountCategoryId} not found");
        }

        _account_categorys[account_category.AccountCategoryId] = account_category;
        return Task.FromResult(account_category);
    }

    public Task<bool> DeleteAsync(string account_categoryId)
    {
        return Task.FromResult(_account_categorys.TryRemove(account_categoryId, out _));
    }

    internal void Seed(AccountCategory account_category)
    {
        _account_categorys.TryAdd(account_category.AccountCategoryId, account_category);
    }

    internal void Clear()
    {
        _account_categorys.Clear();
    }
}
