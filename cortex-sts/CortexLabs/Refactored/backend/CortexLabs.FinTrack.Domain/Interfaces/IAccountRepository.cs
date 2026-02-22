using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Domain.Interfaces;

/// <summary>
/// Repository contract for Account aggregate — fixes SMELL-02 (no DI)
/// and SMELL-09 (SQL injection) by enforcing parameterized access.
/// </summary>
public interface IAccountRepository
{
    Task<Account?> GetByIdAsync(int id);
    Task<IReadOnlyList<Account>> GetByUserIdAsync(int userId);
    Task<IReadOnlyList<Account>> GetAllAsync(int page, int pageSize);
    Task<int> CreateAsync(Account account);
    Task<bool> UpdateAsync(Account account);
    Task<bool> DeleteAsync(int id);
    Task<int> GetCountAsync();
}
