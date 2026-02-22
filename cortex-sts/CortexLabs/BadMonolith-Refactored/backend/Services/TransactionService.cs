// ✅ CORTEX Refactored — TransactionService
// ✅ SMELL-1 RESOLVED: No SQL injection — parameterized via EF Core
// ✅ SMELL-4 RESOLVED: Business logic properly encapsulated
// ✅ SMELL-5 RESOLVED: No circular dependencies

using Microsoft.Extensions.Logging;
using CortexLabs.FinTrack.Repositories.Interfaces;
using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Services;

/// <summary>
/// Transaction service — handles financial transactions with proper business logic
/// </summary>
public class TransactionService : ITransactionService
{
    private readonly ITransactionRepository _transactionRepository;
    private readonly IValidationService _validationService;
    private readonly ILogger<TransactionService> _logger;

    // ✅ SMELL-15 RESOLVED: Business thresholds as constants
    private const decimal LargePurchaseThreshold = 10_000m;
    private const decimal MediumPurchaseThreshold = 1_000m;
    private const decimal HealthyRatio = 1.0m;
    private const decimal CriticalRatio = 1.5m;

    public TransactionService(
        ITransactionRepository transactionRepository,
        IValidationService validationService,
        ILogger<TransactionService> logger)
    {
        _transactionRepository = transactionRepository ?? throw new ArgumentNullException(nameof(transactionRepository));
        _validationService = validationService ?? throw new ArgumentNullException(nameof(validationService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<TransactionDto?> GetByIdAsync(int id)
    {
        var tx = await _transactionRepository.GetByIdAsync(id);
        return tx != null ? MapToDto(tx) : null;
    }

    // ✅ SMELL-6 RESOLVED: Pagination support
    public async Task<IEnumerable<TransactionDto>> GetAllAsync(int page = 1, int pageSize = 50)
    {
        _logger.LogDebug("Fetching transactions page {Page} with size {PageSize}", page, pageSize);
        var transactions = await _transactionRepository.GetPagedAsync(page, pageSize);
        return transactions.Select(MapToDto);
    }

    // ✅ SMELL-1 RESOLVED: Parameterized query via repository
    public async Task<IEnumerable<TransactionDto>> SearchAsync(string? category, DateTime? fromDate)
    {
        _logger.LogDebug("Searching transactions: category={Category}, fromDate={FromDate}", category, fromDate);
        var transactions = await _transactionRepository.SearchAsync(category, fromDate);
        return transactions.Select(MapToDto);
    }

    public async Task<TransactionDto> CreateAsync(CreateTransactionDto dto)
    {
        _logger.LogInformation("Creating transaction for user {UserId}", dto.UserId);

        // ✅ SMELL-10 RESOLVED: Centralized validation
        var validation = _validationService.ValidateTransaction(dto);
        if (!validation.IsValid)
        {
            throw new ValidationException(validation.Errors);
        }

        var category = string.IsNullOrEmpty(dto.Category) 
            ? AutoCategorize(dto.Amount, dto.Description) 
            : dto.Category;

        var transaction = new Transaction
        {
            Description = dto.Description,
            Amount = dto.Amount,
            Category = category,
            Type = dto.Type,
            Date = DateTime.UtcNow,
            UserId = dto.UserId,
            CreatedAt = DateTime.UtcNow
        };

        var created = await _transactionRepository.CreateAsync(transaction);
        _logger.LogInformation("Created transaction with id: {TransactionId}", created.Id);

        return MapToDto(created);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        _logger.LogInformation("Deleting transaction: {TransactionId}", id);
        return await _transactionRepository.DeleteAsync(id);
    }

    // ✅ SMELL-23 RESOLVED: Business logic in service, not UI
    public async Task<DashboardSummary> GetDashboardSummaryAsync(int userId)
    {
        _logger.LogDebug("Generating dashboard summary for user {UserId}", userId);

        var transactions = await _transactionRepository.GetByUserIdAsync(userId);
        var txList = transactions.ToList();

        var totalIncome = txList
            .Where(t => t.Type.Equals("income", StringComparison.OrdinalIgnoreCase))
            .Sum(t => t.Amount);

        var totalExpenses = txList
            .Where(t => t.Type.Equals("expense", StringComparison.OrdinalIgnoreCase))
            .Sum(t => t.Amount);

        var netPosition = totalIncome - totalExpenses;

        var healthScore = CalculateHealthScore(totalIncome, totalExpenses);

        var categories = GetCategoryBreakdown(txList, totalExpenses);

        return new DashboardSummary(
            totalIncome,
            totalExpenses,
            netPosition,
            healthScore,
            categories);
    }

    // ✅ Private helpers

    private static TransactionDto MapToDto(Transaction tx)
    {
        return new TransactionDto(
            tx.Id,
            tx.Description,
            tx.Amount,
            tx.Category,
            tx.Type,
            tx.Date,
            tx.UserId);
    }

    // ✅ SMELL-4 RESOLVED: Categorization logic in service
    private string AutoCategorize(decimal amount, string description)
    {
        if (amount >= LargePurchaseThreshold) return "large_purchase";
        if (amount >= MediumPurchaseThreshold) return "medium_purchase";

        var lowerDesc = description.ToLowerInvariant();
        if (lowerDesc.Contains("grocery") || lowerDesc.Contains("food")) return "food";
        if (lowerDesc.Contains("gas") || lowerDesc.Contains("fuel")) return "transport";
        if (lowerDesc.Contains("netflix") || lowerDesc.Contains("spotify")) return "entertainment";

        return "other";
    }

    private static string CalculateHealthScore(decimal income, decimal expenses)
    {
        if (income > expenses * HealthyRatio) return "Healthy";
        if (expenses > income * CriticalRatio) return "Critical";
        return "Warning";
    }

    private static IEnumerable<CategoryBreakdown> GetCategoryBreakdown(
        IEnumerable<Transaction> transactions, 
        decimal totalExpenses)
    {
        var expensesByCategory = transactions
            .Where(t => t.Type.Equals("expense", StringComparison.OrdinalIgnoreCase))
            .GroupBy(t => t.Category)
            .Select(g => new CategoryBreakdown(
                g.Key,
                g.Sum(t => t.Amount),
                totalExpenses > 0 
                    ? Math.Round(g.Sum(t => t.Amount) / totalExpenses * 100, 1) 
                    : 0));

        return expensesByCategory;
    }
}
