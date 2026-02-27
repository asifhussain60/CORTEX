// FIX SMELL-17: Service interface — Program.cs injects ITransactionService
// FIX SMELL-5: Dependency inversion
using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Application.Interfaces;

public interface ITransactionService
{
    Task<IReadOnlyList<Transaction>> GetByUserAsync(int userId, int page = 1, int pageSize = 50, CancellationToken ct = default);
    Task<IReadOnlyList<Transaction>> SearchAsync(string? category, DateTime? dateFrom, int page = 1, int pageSize = 50, CancellationToken ct = default);
    Task<Transaction> CreateAsync(Transaction tx, CancellationToken ct = default);
}
