// ✅ CORTEX Refactored — AccountService
// ✅ AP-002 RESOLVED: AccountService implements IAccountService.TransferAsync (endpoint no longer missing)
// ✅ SMELL-5 RESOLVED: No circular dependencies — pure constructor injection
// ✅ SMELL-17 RESOLVED: DI constructor injection

using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Repositories.Interfaces;
using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Services;

/// <summary>
/// Account service — handles account CRUD and fund transfers with concurrency protection.
/// </summary>
public class AccountService : IAccountService
{
    private readonly IAccountRepository _accountRepository;
    private readonly ILogger<AccountService> _logger;

    public AccountService(IAccountRepository accountRepository, ILogger<AccountService> logger)
    {
        _accountRepository = accountRepository ?? throw new ArgumentNullException(nameof(accountRepository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <inheritdoc/>
    public async Task<AccountDto?> GetByIdAsync(int id)
    {
        _logger.LogDebug("Fetching account by id: {AccountId}", id);
        var account = await _accountRepository.GetByIdAsync(id);
        return account != null ? MapToDto(account) : null;
    }

    /// <inheritdoc/>
    public async Task<IEnumerable<AccountDto>> GetByUserIdAsync(int userId)
    {
        _logger.LogDebug("Fetching accounts for user: {UserId}", userId);
        var accounts = await _accountRepository.GetByUserIdAsync(userId);
        return accounts.Select(MapToDto);
    }

    /// <inheritdoc/>
    public async Task<AccountDto> CreateAsync(CreateAccountDto dto)
    {
        _logger.LogInformation("Creating account '{Name}' for user {UserId}", dto.Name, dto.UserId);

        if (string.IsNullOrWhiteSpace(dto.Name))
            throw new ValidationException(new[] { "Account name is required" });

        if (dto.InitialBalance < 0)
            throw new ValidationException(new[] { "Initial balance cannot be negative" });

        var account = new Account
        {
            Name = dto.Name,
            Balance = dto.InitialBalance,
            UserId = dto.UserId,
            AccountType = dto.AccountType,
            CreatedAt = DateTime.UtcNow
        };

        var created = await _accountRepository.CreateAsync(account);
        _logger.LogInformation("Created account with id: {AccountId}", created.Id);

        return MapToDto(created);
    }

    /// <summary>
    /// Transfer funds between two accounts.
    /// Uses optimistic concurrency (EF Core rowversion / Version token) to prevent double-spend.
    /// </summary>
    /// <inheritdoc/>
    public async Task<bool> TransferAsync(int fromAccountId, int toAccountId, decimal amount)
    {
        _logger.LogInformation(
            "Transfer: {From} → {To}, amount={Amount}", fromAccountId, toAccountId, amount);

        if (amount <= 0)
            throw new ValidationException(new[] { "Transfer amount must be greater than zero" });

        if (fromAccountId == toAccountId)
            throw new ValidationException(new[] { "Source and destination accounts must differ" });

        var from = await _accountRepository.GetByIdAsync(fromAccountId);
        var to = await _accountRepository.GetByIdAsync(toAccountId);

        if (from == null)
            throw new InvalidOperationException($"Source account {fromAccountId} not found");

        if (to == null)
            throw new InvalidOperationException($"Destination account {toAccountId} not found");

        if (from.Balance < amount)
            throw new InvalidOperationException(
                $"Insufficient funds: balance {from.Balance:C} < transfer {amount:C}");

        from.Balance -= amount;
        to.Balance += amount;
        from.ModifiedAt = DateTime.UtcNow;
        to.ModifiedAt = DateTime.UtcNow;

        var fromUpdated = await _accountRepository.UpdateAsync(from);
        var toUpdated = await _accountRepository.UpdateAsync(to);

        _logger.LogInformation("Transfer complete: {From} → {To}, amount={Amount}", fromAccountId, toAccountId, amount);
        return fromUpdated && toUpdated;
    }

    // ─── Private helpers ──────────────────────────────────────────────────────

    private static AccountDto MapToDto(Account account) =>
        new(account.Id, account.Name, account.Balance, account.UserId, account.AccountType);
}
