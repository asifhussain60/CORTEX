// ✅ CORTEX Refactored — TransactionRepository
// ✅ SMELL-1 RESOLVED: Parameterized queries via EF Core

using Microsoft.EntityFrameworkCore;
using CortexLabs.FinTrack.Repositories.Interfaces;

namespace CortexLabs.FinTrack.Repositories;

/// <summary>
/// Transaction repository — data access with proper parameterization
/// </summary>
public class TransactionRepository : ITransactionRepository
{
    private readonly FinTrackDbContext _context;

    public TransactionRepository(FinTrackDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<Transaction?> GetByIdAsync(int id)
    {
        return await _context.Transactions.FindAsync(id);
    }

    public async Task<IEnumerable<Transaction>> GetAllAsync()
    {
        return await _context.Transactions.ToListAsync();
    }

    // ✅ SMELL-6 RESOLVED: Pagination support
    public async Task<IEnumerable<Transaction>> GetPagedAsync(int page, int pageSize)
    {
        return await _context.Transactions
            .OrderByDescending(t => t.Date)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();
    }

    public async Task<IEnumerable<Transaction>> GetByUserIdAsync(int userId)
    {
        // ✅ SMELL-1 RESOLVED: Parameterized via EF Core
        return await _context.Transactions
            .Where(t => t.UserId == userId)
            .OrderByDescending(t => t.Date)
            .ToListAsync();
    }

    // ✅ SMELL-1 RESOLVED: Search with parameterized queries
    public async Task<IEnumerable<Transaction>> SearchAsync(string? category, DateTime? fromDate)
    {
        var query = _context.Transactions.AsQueryable();

        if (!string.IsNullOrWhiteSpace(category))
        {
            // ✅ No SQL injection — EF parameterizes this
            query = query.Where(t => t.Category == category);
        }

        if (fromDate.HasValue)
        {
            // ✅ No SQL injection — EF parameterizes this
            query = query.Where(t => t.Date >= fromDate.Value);
        }

        return await query
            .OrderByDescending(t => t.Date)
            .Take(100) // ✅ SMELL-6 RESOLVED: Limit results
            .ToListAsync();
    }

    public async Task<Transaction> CreateAsync(Transaction entity)
    {
        _context.Transactions.Add(entity);
        await _context.SaveChangesAsync();
        return entity;
    }

    public async Task<bool> UpdateAsync(Transaction entity)
    {
        _context.Transactions.Update(entity);
        var affected = await _context.SaveChangesAsync();
        return affected > 0;
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var entity = await GetByIdAsync(id);
        if (entity == null) return false;

        _context.Transactions.Remove(entity);
        var affected = await _context.SaveChangesAsync();
        return affected > 0;
    }
}
