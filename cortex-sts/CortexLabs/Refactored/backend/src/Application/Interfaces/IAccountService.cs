// FIX SMELL-17: Service interface — Program.cs injects IAccountService
// FIX SMELL-5: Dependency inversion — transfer logic behind abstraction
using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Application.Interfaces;

public interface IAccountService
{
    Task<IReadOnlyList<Account>> GetByUserAsync(int userId, CancellationToken ct = default);
    // FIX SMELL-4: transfer validation contract declared on interface
    Task TransferAsync(int fromId, int toId, decimal amount, CancellationToken ct = default);
}
