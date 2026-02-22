// FIX SMELL-17: Service interface — Program.cs injects IUserService, not concrete UserService
// FIX SMELL-5: Dependency inversion — callers depend on abstraction, not implementation
using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Application.Interfaces;

public interface IUserService
{
    Task<IReadOnlyList<User>> GetPagedAsync(int page, int pageSize, CancellationToken ct = default);
    Task<User?> SearchByUsernameAsync(string username, CancellationToken ct = default);
    Task<User> CreateAsync(User user, CancellationToken ct = default);
    Task SoftDeleteAsync(int id, CancellationToken ct = default);
}
