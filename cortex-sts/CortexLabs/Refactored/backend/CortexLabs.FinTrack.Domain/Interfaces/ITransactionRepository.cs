using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Domain.Interfaces;

/// <summary>
/// Repository contract for Transaction aggregate — fixes SMELL-02 (no DI)
/// and SMELL-09 (SQL injection) by enforcing parameterized access.
/// </summary>
public interface ITransactionRepository
{
    Task<Transaction?> GetByIdAsync(int id);
    Task<IReadOnlyList<Transaction>> GetByUserIdAsync(int userId, int page, int pageSize);
    Task<IReadOnlyList<Transaction>> GetAllAsync(int page, int pageSize);
    Task<int> CreateAsync(Transaction transaction);
    Task<bool> UpdateAsync(Transaction transaction);
    Task<bool> DeleteAsync(int id);
    Task<int> GetCountAsync();
    Task<int> GetCountByUserIdAsync(int userId);
    Task<decimal> GetTotalByUserIdAsync(int userId);
}
