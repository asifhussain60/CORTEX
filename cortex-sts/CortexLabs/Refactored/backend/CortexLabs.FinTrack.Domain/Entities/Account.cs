using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Domain.Entities;

/// <summary>
/// Account domain entity — fixes SMELL-07 (typed fields),
/// SMELL-01 (separate bounded context from God Class).
/// </summary>
public class Account
{
    public int Id { get; set; }

    public int UserId { get; set; }

    public string Name { get; set; } = string.Empty;

    public AccountType Type { get; set; } = AccountType.Checking;

    public decimal Balance { get; set; }

    public string Currency { get; set; } = "USD";

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
