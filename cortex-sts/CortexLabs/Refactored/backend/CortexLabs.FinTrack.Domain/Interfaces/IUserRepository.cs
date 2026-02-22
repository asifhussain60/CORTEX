using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Domain.Interfaces;

/// <summary>
/// Repository contract for User aggregate — fixes SMELL-02 (no DI)
/// and SMELL-09 (SQL injection) by enforcing parameterized access.
/// </summary>
public interface IUserRepository
{
    Task<User?> GetByIdAsync(int id);
    Task<User?> GetByUsernameAsync(string username);
    Task<User?> GetByEmailAsync(string email);
    Task<IReadOnlyList<User>> GetAllAsync(int page, int pageSize);
    Task<int> CreateAsync(User user);
    Task<bool> UpdateAsync(User user);
    Task<bool> DeleteAsync(int id);
    Task<int> GetCountAsync();
}
