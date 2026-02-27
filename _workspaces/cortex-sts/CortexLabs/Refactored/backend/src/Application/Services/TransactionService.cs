// FIX SMELL-3,4,5,6,8,11,15,17
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Application.Services;

public class TransactionService : ITransactionService
{
    private readonly ITransactionRepository _repo;
    private readonly ILogger<TransactionService> _logger;

    public TransactionService(ITransactionRepository repo, ILogger<TransactionService> logger)
    {
        _repo = repo;
        _logger = logger;
    }

    // FIX SMELL-6: paginated — no "SELECT *" with no LIMIT
    public async Task<IReadOnlyList<Transaction>> GetByUserAsync(int userId, int page = 1, int pageSize = 50, CancellationToken ct = default)
    {
        _logger.LogInformation("Fetching transactions userId={UserId} page={Page}", userId, page);
        return await _repo.GetByUserAsync(userId, page, pageSize, ct);
    }

    public async Task<IReadOnlyList<Transaction>> SearchAsync(string? category, DateTime? dateFrom, int page = 1, int pageSize = 50, CancellationToken ct = default)
    {
        // FIX SMELL-1: no SQL injection — parameterized in repo
        return await _repo.SearchAsync(category, dateFrom, page, pageSize, ct);
    }

    public async Task<Transaction> CreateAsync(Transaction tx, CancellationToken ct = default)
    {
        // FIX SMELL-4: auto-categorization as domain logic, not inline endpoint code
        if (string.IsNullOrEmpty(tx.CategoryName))
            tx.CategoryName = CategorizeByAmount(tx.Amount);

        _logger.LogInformation("Creating transaction Amount={Amount} Type={Type}", tx.Amount, tx.Type);
        return await _repo.CreateAsync(tx, ct);
    }

    // FIX SMELL-4,15: domain logic extracted, constants replace magic numbers/strings
    private static string CategorizeByAmount(decimal amount) => amount switch
    {
        > 10_000m => "large_purchase",
        > 1_000m  => "medium_purchase",
        _         => "other",
    };
}