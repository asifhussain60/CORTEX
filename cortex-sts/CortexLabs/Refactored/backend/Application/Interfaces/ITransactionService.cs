// ✅ SMELL-17 FIXED: Interface contract for DI
// ✅ SMELL-6 FIXED: Pagination on all list queries

using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Application.Interfaces;

/// <summary>Contract for transaction management operations.</summary>
public interface ITransactionService
{
    Task<IEnumerable<Transaction>> GetTransactionsAsync(int page = 1, int pageSize = 25);
    Task<IEnumerable<Transaction>> SearchAsync(TransactionCategory? category, DateOnly? from, int page = 1, int pageSize = 25);
    Task<Transaction> CreateAsync(Transaction transaction);
    Task<TransactionCategory> AutoCategoriseAsync(decimal amount, string description);
}
