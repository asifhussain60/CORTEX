// FIX SMELL-5 SMELL-17
namespace CortexLabs.FinTrack.Domain.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
public interface IUserRepository {
    Task<User?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<User?> GetByUsernameAsync(string username, CancellationToken ct = default);
    Task<IReadOnlyList<User>> GetPagedAsync(int page, int pageSize, CancellationToken ct = default);
    Task<User> CreateAsync(User user, CancellationToken ct = default);
    Task UpdateAsync(User user, CancellationToken ct = default);
    Task SoftDeleteAsync(int id, CancellationToken ct = default);
}