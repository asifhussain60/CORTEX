// ✅ SMELL-17 FIXED: Interface contract for DI
// ✅ SMELL-6 FIXED: Pagination support

using CortexLabs.FinTrack.Domain.Entities;

namespace CortexLabs.FinTrack.Application.Interfaces;

/// <summary>Contract for account and transfer operations.</summary>
public interface IAccountService
{
    Task<IEnumerable<Account>> GetAccountsAsync(int page = 1, int pageSize = 25);
    Task<Account?> GetByIdAsync(int id);
    Task<TransferResult> TransferAsync(int fromId, int toId, decimal amount, int requestedBy);
}

/// <summary>Result of a transfer operation.</summary>
/// <param name="Success">Whether the transfer succeeded.</param>
/// <param name="Error">Optional error message if the transfer failed.</param>
public record TransferResult(bool Success, string? Error = null);
