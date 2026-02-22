// FIX SMELL-3 (god class split), SMELL-4 (business logic in service),
// SMELL-5 (circular dep eliminated), SMELL-8 (dead code removed),
// SMELL-10 (duplicate validation removed), SMELL-11 (ILogger),
// SMELL-17 (DI constructor injection)
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Application.Services;

public class UserService
{
    private readonly IUserRepository _repo;
    private readonly ILogger<UserService> _logger;

    // FIX SMELL-17: Constructor injection — no direct instantiation
    public UserService(IUserRepository repo, ILogger<UserService> logger)
    {
        _repo = repo;
        _logger = logger;
    }

    public async Task<IReadOnlyList<User>> GetPagedAsync(int page, int pageSize, CancellationToken ct = default)
    {
        _logger.LogInformation("Fetching users page={Page} pageSize={PageSize}", page, pageSize);
        return await _repo.GetPagedAsync(page, pageSize, ct);
    }

    public async Task<User?> SearchByUsernameAsync(string username, CancellationToken ct = default)
    {
        // FIX SMELL-1: no SQL injection — delegated to parameterized repository
        _logger.LogInformation("Searching user by username");
        return await _repo.GetByUsernameAsync(username, ct);
    }

    public async Task<User> CreateAsync(User user, CancellationToken ct = default)
    {
        // FIX SMELL-10: single authoritative validation via DataAnnotations on entity
        _logger.LogInformation("Creating user {UserName}", user.UserName);
        return await _repo.CreateAsync(user, ct);
    }

    public async Task SoftDeleteAsync(int id, CancellationToken ct = default)
    {
        // FIX SMELL-18: soft delete — no hard DELETE exposed
        _logger.LogInformation("Soft-deleting user {UserId}", id);
        await _repo.SoftDeleteAsync(id, ct);
    }
}