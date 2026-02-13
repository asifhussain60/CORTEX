using System.Collections.Concurrent;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.Mock;

/// <summary>
/// In-memory mock implementation of ISubaccountRepository.
/// Supports complex filtering and search operations.
/// </summary>
public class MockSubaccountRepository : ISubaccountRepository
{
    private readonly ConcurrentDictionary<string, Subaccount> _subaccounts = new();

    public Task<Subaccount?> GetByIdAsync(string subaccountId)
    {
        _subaccounts.TryGetValue(subaccountId, out var subaccount);
        return Task.FromResult(subaccount);
    }

    public Task<IEnumerable<Subaccount>> GetAllAsync()
    {
        return Task.FromResult(_subaccounts.Values.AsEnumerable());
    }

    public Task<IEnumerable<Subaccount>> GetByEmployerIdAsync(string employerId)
    {
        var subaccounts = _subaccounts.Values.Where(s => s.EmployerId == employerId);
        return Task.FromResult(subaccounts);
    }

    public Task<IEnumerable<Subaccount>> GetByAccountTypeAsync(string accountType)
    {
        var subaccounts = _subaccounts.Values.Where(s => s.AccountType == accountType);
        return Task.FromResult(subaccounts);
    }

    public Task<IEnumerable<Subaccount>> SearchAsync(string searchTerm)
    {
        var subaccounts = _subaccounts.Values.Where(s =>
            s.MemberId.Contains(searchTerm, StringComparison.OrdinalIgnoreCase) ||
            s.MemberName.Contains(searchTerm, StringComparison.OrdinalIgnoreCase));
        return Task.FromResult(subaccounts);
    }

    public Task<Subaccount> CreateAsync(Subaccount subaccount)
    {
        if (string.IsNullOrEmpty(subaccount.SubaccountId))
        {
            subaccount.SubaccountId = $"SUB-{Guid.NewGuid():N}";
        }

        subaccount.CreatedDate = DateTime.UtcNow;

        if (!_subaccounts.TryAdd(subaccount.SubaccountId, subaccount))
        {
            throw new InvalidOperationException($"Subaccount with ID {subaccount.SubaccountId} already exists");
        }

        return Task.FromResult(subaccount);
    }

    public Task<Subaccount> UpdateAsync(Subaccount subaccount)
    {
        if (!_subaccounts.ContainsKey(subaccount.SubaccountId))
        {
            throw new KeyNotFoundException($"Subaccount with ID {subaccount.SubaccountId} not found");
        }

        _subaccounts[subaccount.SubaccountId] = subaccount;
        return Task.FromResult(subaccount);
    }

    public Task<bool> DeleteAsync(string subaccountId)
    {
        return Task.FromResult(_subaccounts.TryRemove(subaccountId, out _));
    }

    internal void Seed(Subaccount subaccount)
    {
        _subaccounts.TryAdd(subaccount.SubaccountId, subaccount);
    }

    internal void Clear()
    {
        _subaccounts.Clear();
    }
}
