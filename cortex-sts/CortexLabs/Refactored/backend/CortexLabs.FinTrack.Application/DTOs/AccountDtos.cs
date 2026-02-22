using System.ComponentModel.DataAnnotations;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Application.DTOs;

/// <summary>
/// Inbound DTO for creating accounts — fixes SMELL-07 (typed fields).
/// </summary>
public class CreateAccountDto
{
    [Required]
    public int UserId { get; set; }

    [Required]
    [StringLength(100, MinimumLength = 1)]
    public string Name { get; set; } = string.Empty;

    [Required]
    public AccountType Type { get; set; }

    [Required]
    [StringLength(3, MinimumLength = 3)]
    public string Currency { get; set; } = "USD";

    public decimal InitialBalance { get; set; }
}

/// <summary>
/// Outbound DTO for account data.
/// </summary>
public class AccountDto
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public string Name { get; set; } = string.Empty;
    public AccountType Type { get; set; }
    public decimal Balance { get; set; }
    public string Currency { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}
