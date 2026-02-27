namespace CortexLabs.FinTrack.Domain.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
public interface IAccountRepository {
    Task<Account?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Account>> GetByUserAsync(int userId, CancellationToken ct = default);
    Task TransferAsync(int fromId, int toId, decimal amount, CancellationToken ct = default);
    Task UpdateAsync(Account account, CancellationToken ct = default);
}