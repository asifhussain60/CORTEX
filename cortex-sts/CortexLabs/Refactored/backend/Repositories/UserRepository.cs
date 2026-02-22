// ✅ CORTEX Refactored — UserRepository
// ✅ SMELL-1 RESOLVED: Parameterized queries via EF Core

using Microsoft.EntityFrameworkCore;
using CortexLabs.FinTrack.Repositories.Interfaces;

namespace CortexLabs.FinTrack.Repositories;

/// <summary>
/// User repository — data access for users with parameterized queries
/// </summary>
public class UserRepository : IUserRepository
{
    private readonly FinTrackDbContext _context;

    public UserRepository(FinTrackDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<User?> GetByIdAsync(int id)
    {
        // ✅ SMELL-1 RESOLVED: Parameterized query via EF Core
        return await _context.Users.FindAsync(id);
    }

    public async Task<IEnumerable<User>> GetAllAsync()
    {
        return await _context.Users.ToListAsync();
    }

    // ✅ SMELL-6 RESOLVED: Pagination
    public async Task<IEnumerable<User>> GetPagedAsync(int page, int pageSize)
    {
        return await _context.Users
            .OrderBy(u => u.Id)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();
    }

    // ✅ SMELL-1 RESOLVED: No string concatenation, EF handles parameterization
    public async Task<User?> GetByUsernameAsync(string username)
    {
        return await _context.Users
            .FirstOrDefaultAsync(u => u.UserName == username);
    }

    public async Task<User?> GetByEmailAsync(string email)
    {
        return await _context.Users
            .FirstOrDefaultAsync(u => u.Email == email);
    }

    public async Task<User> CreateAsync(User entity)
    {
        _context.Users.Add(entity);
        await _context.SaveChangesAsync();
        return entity;
    }

    public async Task<bool> UpdateAsync(User entity)
    {
        _context.Users.Update(entity);
        var affected = await _context.SaveChangesAsync();
        return affected > 0;
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var entity = await GetByIdAsync(id);
        if (entity == null) return false;

        _context.Users.Remove(entity);
        var affected = await _context.SaveChangesAsync();
        return affected > 0;
    }
}
