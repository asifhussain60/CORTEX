using CortexLabs.FinTrack.Application.DTOs;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// Account service — fixes SMELL-01 (God Class decomposition),
/// SMELL-02 (DI-driven), SMELL-07 (typed balance/currency).
/// </summary>
public class AccountService
{
    private readonly IAccountRepository _accountRepository;
    private readonly ILogger<AccountService> _logger;

    public AccountService(
        IAccountRepository accountRepository,
        ILogger<AccountService> logger)
    {
        _accountRepository = accountRepository ?? throw new ArgumentNullException(nameof(accountRepository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<AccountDto?> GetByIdAsync(int id)
    {
        var account = await _accountRepository.GetByIdAsync(id);
        return account is null ? null : MapToDto(account);
    }

    public async Task<IReadOnlyList<AccountDto>> GetByUserIdAsync(int userId)
    {
        var accounts = await _accountRepository.GetByUserIdAsync(userId);
        return accounts.Select(MapToDto).ToList();
    }

    public async Task<PagedResponse<AccountDto>> GetAllAsync(int page, int pageSize)
    {
        page = Math.Max(1, page);
        pageSize = Math.Clamp(pageSize, 1, 100);

        var accounts = await _accountRepository.GetAllAsync(page, pageSize);
        var totalCount = await _accountRepository.GetCountAsync();

        return new PagedResponse<AccountDto>
        {
            Items = accounts.Select(MapToDto).ToList(),
            Page = page,
            PageSize = pageSize,
            TotalCount = totalCount
        };
    }

    public async Task<(AccountDto? Account, string? Error)> CreateAsync(CreateAccountDto dto)
    {
        var account = new Account
        {
            UserId = dto.UserId,
            Name = dto.Name,
            Type = dto.Type,
            Balance = dto.InitialBalance,
            Currency = dto.Currency.ToUpperInvariant(),
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        var id = await _accountRepository.CreateAsync(account);
        account.Id = id;

        _logger.LogInformation(
            "Account created: {AccountId} for user {UserId}, type {AccountType}",
            id, dto.UserId, dto.Type);

        return (MapToDto(account), null);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var result = await _accountRepository.DeleteAsync(id);
        if (result)
            _logger.LogInformation("Account deleted: {AccountId}", id);
        return result;
    }

    private static AccountDto MapToDto(Account account) => new()
    {
        Id = account.Id,
        UserId = account.UserId,
        Name = account.Name,
        Type = account.Type,
        Balance = account.Balance,
        Currency = account.Currency,
        CreatedAt = account.CreatedAt
    };
}
