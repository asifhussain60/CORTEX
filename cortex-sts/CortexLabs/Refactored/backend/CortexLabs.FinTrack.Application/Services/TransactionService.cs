using CortexLabs.FinTrack.Application.DTOs;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using CortexLabs.FinTrack.Domain.Interfaces;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// Transaction service — fixes SMELL-01 (God Class), SMELL-15 (magic strings),
/// SMELL-19 (auto-categorization logic extracted from endpoint).
/// </summary>
public class TransactionService
{
    private readonly ITransactionRepository _transactionRepository;
    private readonly ILogger<TransactionService> _logger;

    public TransactionService(
        ITransactionRepository transactionRepository,
        ILogger<TransactionService> logger)
    {
        _transactionRepository = transactionRepository ?? throw new ArgumentNullException(nameof(transactionRepository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<TransactionDto?> GetByIdAsync(int id)
    {
        var txn = await _transactionRepository.GetByIdAsync(id);
        return txn is null ? null : MapToDto(txn);
    }

    public async Task<PagedResponse<TransactionDto>> GetAllAsync(int page, int pageSize)
    {
        page = Math.Max(1, page);
        pageSize = Math.Clamp(pageSize, 1, 100);

        var transactions = await _transactionRepository.GetAllAsync(page, pageSize);
        var totalCount = await _transactionRepository.GetCountAsync();

        return new PagedResponse<TransactionDto>
        {
            Items = transactions.Select(MapToDto).ToList(),
            Page = page,
            PageSize = pageSize,
            TotalCount = totalCount
        };
    }

    public async Task<PagedResponse<TransactionDto>> GetByUserIdAsync(int userId, int page, int pageSize)
    {
        page = Math.Max(1, page);
        pageSize = Math.Clamp(pageSize, 1, 100);

        var transactions = await _transactionRepository.GetByUserIdAsync(userId, page, pageSize);
        var totalCount = await _transactionRepository.GetCountByUserIdAsync(userId);

        return new PagedResponse<TransactionDto>
        {
            Items = transactions.Select(MapToDto).ToList(),
            Page = page,
            PageSize = pageSize,
            TotalCount = totalCount
        };
    }

    public async Task<(TransactionDto? Transaction, string? Error)> CreateAsync(CreateTransactionDto dto)
    {
        if (dto.Amount <= 0)
            return (null, "Amount must be positive");

        var transaction = new Transaction
        {
            UserId = dto.UserId,
            Amount = dto.Amount,
            Type = dto.Type,
            Category = dto.Category == TransactionCategory.Other
                ? AutoCategorize(dto.Amount)
                : dto.Category,
            Description = dto.Description,
            Date = dto.Date ?? DateTime.UtcNow,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        var id = await _transactionRepository.CreateAsync(transaction);
        transaction.Id = id;

        _logger.LogInformation(
            "Transaction created: {TxnId} for user {UserId}, amount {Amount}",
            id, dto.UserId, dto.Amount);

        return (MapToDto(transaction), null);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var result = await _transactionRepository.DeleteAsync(id);
        if (result)
            _logger.LogInformation("Transaction deleted: {TxnId}", id);
        return result;
    }

    public async Task<decimal> GetTotalByUserIdAsync(int userId)
    {
        return await _transactionRepository.GetTotalByUserIdAsync(userId);
    }

    /// <summary>
    /// Auto-categorisation based on amount thresholds — extracted from inline
    /// if/else chain in BadMonolith endpoint (SMELL-19).
    /// </summary>
    internal static TransactionCategory AutoCategorize(decimal amount)
    {
        return amount switch
        {
            > 1000m => TransactionCategory.LargePurchase,
            > 100m => TransactionCategory.MediumPurchase,
            _ => TransactionCategory.Other
        };
    }

    private static TransactionDto MapToDto(Transaction txn) => new()
    {
        Id = txn.Id,
        UserId = txn.UserId,
        Amount = txn.Amount,
        Type = txn.Type,
        Category = txn.Category,
        Description = txn.Description,
        Date = txn.Date,
        CreatedAt = txn.CreatedAt
    };
}
