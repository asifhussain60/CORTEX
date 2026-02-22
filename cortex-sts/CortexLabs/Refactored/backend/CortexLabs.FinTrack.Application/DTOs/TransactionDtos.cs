using System.ComponentModel.DataAnnotations;
using CortexLabs.FinTrack.Domain.Enums;

namespace CortexLabs.FinTrack.Application.DTOs;

/// <summary>
/// Inbound DTO for creating transactions — fixes SMELL-07 (typed amount/category),
/// SMELL-15 (enums replace magic strings).
/// </summary>
public class CreateTransactionDto
{
    [Required]
    public int UserId { get; set; }

    [Required]
    [Range(0.01, double.MaxValue, ErrorMessage = "Amount must be positive")]
    public decimal Amount { get; set; }

    [Required]
    public TransactionType Type { get; set; }

    public TransactionCategory Category { get; set; } = TransactionCategory.Other;

    [StringLength(500)]
    public string Description { get; set; } = string.Empty;

    public DateTime? Date { get; set; }
}

/// <summary>
/// Outbound DTO for transaction data.
/// </summary>
public class TransactionDto
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public decimal Amount { get; set; }
    public TransactionType Type { get; set; }
    public TransactionCategory Category { get; set; }
    public string Description { get; set; } = string.Empty;
    public DateTime Date { get; set; }
    public DateTime CreatedAt { get; set; }
}
