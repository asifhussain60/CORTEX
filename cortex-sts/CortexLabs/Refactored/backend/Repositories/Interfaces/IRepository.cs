// ✅ CORTEX Refactored — Repository Interfaces
// ✅ SMELL-1 RESOLVED: Parameterized queries via EF Core

namespace CortexLabs.FinTrack.Repositories.Interfaces;

public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<IEnumerable<T>> GetPagedAsync(int page, int pageSize);
    Task<T> CreateAsync(T entity);
    Task<bool> UpdateAsync(T entity);
    Task<bool> DeleteAsync(int id);
}

public interface IUserRepository : IRepository<User>
{
    Task<User?> GetByUsernameAsync(string username);
    Task<User?> GetByEmailAsync(string email);
}

public interface ITransactionRepository : IRepository<Transaction>
{
    Task<IEnumerable<Transaction>> GetByUserIdAsync(int userId);
    Task<IEnumerable<Transaction>> SearchAsync(string? category, DateTime? fromDate);
}

/// <summary>Repository contract for account data access.</summary>
public interface IAccountRepository : IRepository<Account>
{
    /// <summary>Get all accounts belonging to a specific user.</summary>
    Task<IEnumerable<Account>> GetByUserIdAsync(int userId);
}
