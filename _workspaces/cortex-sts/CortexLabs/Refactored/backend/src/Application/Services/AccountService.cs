// FIX SMELL-4 (business logic in service), SMELL-11 (ILogger), SMELL-17 (DI)
using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;

namespace CortexLabs.FinTrack.Application.Services;

public class AccountService : IAccountService
{
    private readonly IAccountRepository _repo;
    private readonly ILogger<AccountService> _logger;

    public AccountService(IAccountRepository repo, ILogger<AccountService> logger)
    {
        _repo = repo;
        _logger = logger;
    }

    public async Task<IReadOnlyList<Account>> GetByUserAsync(int userId, CancellationToken ct = default)
        => await _repo.GetByUserAsync(userId, ct);

    // FIX SMELL-4: transfer validation in service, not in endpoint
    // FIX SMELL-19: overdraft check enforced
    public async Task TransferAsync(int fromId, int toId, decimal amount, CancellationToken ct = default)
    {
        if (amount <= 0) throw new ArgumentOutOfRangeException(nameof(amount), "Transfer amount must be positive.");
        if (fromId == toId) throw new ArgumentException("Cannot transfer to same account.");

        var from = await _repo.GetByIdAsync(fromId, ct) ?? throw new KeyNotFoundException($"Account {fromId} not found.");
        if (from.Balance < amount) throw new InvalidOperationException("Insufficient funds.");

        _logger.LogInformation("Transfer from={From} to={To} amount={Amount}", fromId, toId, amount);
        // FIX: atomic transfer in repository (wrapped in SQLite transaction)
        await _repo.TransferAsync(fromId, toId, amount, ct);
    }
}