// FIX SMELL-5 SMELL-17
namespace CortexLabs.FinTrack.Domain.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
public interface ITransactionRepository {
    Task<Transaction?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Transaction>> GetByUserAsync(int userId, int page, int pageSize, CancellationToken ct = default);
    Task<IReadOnlyList<Transaction>> SearchAsync(string? category, DateTime? dateFrom, int page, int pageSize, CancellationToken ct = default);
    Task<Transaction> CreateAsync(Transaction tx, CancellationToken ct = default);
}