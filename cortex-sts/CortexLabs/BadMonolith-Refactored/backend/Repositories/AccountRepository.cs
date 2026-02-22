// ✅ CORTEX Refactored — AccountRepository
// ✅ AP-002 RESOLVED: AccountRepository completes the account domain stack
// ✅ SMELL-1 RESOLVED: All queries parameterized via EF Core (no string concatenation)

using Microsoft.EntityFrameworkCore;
using CortexLabs.FinTrack.Repositories.Interfaces;

namespace CortexLabs.FinTrack.Repositories;

/// <summary>
/// Account repository — EF Core data access for accounts with parameterized queries.
/// </summary>
public class AccountRepository : IAccountRepository
{
    private readonly FinTrackDbContext _context;

    public AccountRepository(FinTrackDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    /// <inheritdoc/>
    public async Task<Account?> GetByIdAsync(int id) =>
        await _context.Accounts.FindAsync(id);

    /// <inheritdoc/>
    public async Task<IEnumerable<Account>> GetAllAsync() =>
        await _context.Accounts.ToListAsync();

    /// <inheritdoc/>
    public async Task<IEnumerable<Account>> GetPagedAsync(int page, int pageSize) =>
        await _context.Accounts
            .OrderBy(a => a.Id)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

    /// <inheritdoc/>
    public async Task<IEnumerable<Account>> GetByUserIdAsync(int userId) =>
        await _context.Accounts
            .Where(a => a.UserId == userId)
            .OrderBy(a => a.Name)
            .ToListAsync();

    /// <inheritdoc/>
    public async Task<Account> CreateAsync(Account entity)
    {
        _context.Accounts.Add(entity);
        await _context.SaveChangesAsync();
        return entity;
    }

    /// <inheritdoc/>
    public async Task<bool> UpdateAsync(Account entity)
    {
        _context.Accounts.Update(entity);
        var affected = await _context.SaveChangesAsync();
        return affected > 0;
    }

    /// <inheritdoc/>
    public async Task<bool> DeleteAsync(int id)
    {
        var account = await _context.Accounts.FindAsync(id);
        if (account == null) return false;
        _context.Accounts.Remove(account);
        var affected = await _context.SaveChangesAsync();
        return affected > 0;
    }
}
