using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>
/// Transaction domain entity — fixes SMELL-01 (extracted from God Class),
/// SMELL-15 (enums replace magic strings), SMELL-07 (typed amount).
/// </summary>
public class Transaction
{
    public int Id { get; set; }

    public int UserId { get; set; }

    public decimal Amount { get; set; }

    public TransactionType Type { get; set; }

    public TransactionCategory Category { get; set; } = TransactionCategory.Other;

    public string Description { get; set; } = string.Empty;

    public DateTime Date { get; set; } = DateTime.UtcNow;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
