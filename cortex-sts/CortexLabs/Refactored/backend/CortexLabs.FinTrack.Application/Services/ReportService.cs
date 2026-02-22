using CortexLabs.FinTrack.Application.DTOs;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// Report service — fixes SMELL-01 (God Class) and SMELL-13 (report logic
/// was inlined in a single endpoint with N+1 queries). Aggregation now
/// happens through repository methods.
/// </summary>
public class ReportService
{
    private readonly ITransactionRepository _transactionRepository;
    private readonly IAccountRepository _accountRepository;
    private readonly ILogger<ReportService> _logger;

    public ReportService(
        ITransactionRepository transactionRepository,
        IAccountRepository accountRepository,
        ILogger<ReportService> logger)
    {
        _transactionRepository = transactionRepository ?? throw new ArgumentNullException(nameof(transactionRepository));
        _accountRepository = accountRepository ?? throw new ArgumentNullException(nameof(accountRepository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<UserReportDto> GenerateUserReportAsync(int userId)
    {
        var accounts = await _accountRepository.GetByUserIdAsync(userId);
        var totalTransactions = await _transactionRepository.GetCountByUserIdAsync(userId);
        var transactionTotal = await _transactionRepository.GetTotalByUserIdAsync(userId);

        _logger.LogInformation("Report generated for user {UserId}", userId);

        return new UserReportDto
        {
            UserId = userId,
            TotalAccounts = accounts.Count,
            TotalTransactions = totalTransactions,
            TransactionTotal = transactionTotal,
            TotalBalance = accounts.Sum(a => a.Balance),
            GeneratedAt = DateTime.UtcNow
        };
    }
}

/// <summary>
/// Report DTO — structured output replacing the raw anonymous object from BadMonolith.
/// </summary>
public class UserReportDto
{
    public int UserId { get; set; }
    public int TotalAccounts { get; set; }
    public int TotalTransactions { get; set; }
    public decimal TransactionTotal { get; set; }
    public decimal TotalBalance { get; set; }
    public DateTime GeneratedAt { get; set; }
}
