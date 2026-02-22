// ✅ SMELL-17 FIXED: DI interfaces — all services registered via interface, not concrete type
// ✅ SMELL-6 FIXED: All list-returning methods accept pagination parameters

using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Application.Interfaces;

/// <summary>Contract for user management operations.</summary>
public interface IUserService
{
    Task<IEnumerable<User>> GetUsersAsync(int page = 1, int pageSize = 25);
    Task<User?> GetByIdAsync(int id);
    Task<User?> FindByUsernameAsync(string username);
    Task<User> CreateAsync(User user);
    Task<bool> DeleteAsync(int id, int deletedBy);
}
