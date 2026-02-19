using System.ComponentModel.DataAnnotations;

namespace PaymentProcessor.TransactionInvoices.Core.DTOs;

/// <summary>
/// Request DTO for creating batch transaction invoices (WCF: Updater_CreatePaymentTransactionInvoices)
/// </summary>
public class CreateBatchInvoicesDto
{
    [Required]
    public string EmployerId { get; set; } = string.Empty;

    [Required]
    [MinLength(1, ErrorMessage = "At least one account_category ID is required")]
    public List<int> AccountCategoryIds { get; set; } = new();

    [Required]
    public DateTime EffectiveDate { get; set; }

    [MaxLength(500)]
    public string? Description { get; set; }
}

/// <summary>
/// Response DTO for batch invoice creation results
/// </summary>
public class BatchInvoiceResultDto
{
    public Guid BatchId { get; set; }
    public int TotalInvoices { get; set; }
    public int SuccessCount { get; set; }
    public int FailureCount { get; set; }
    public List<FailedInvoiceDto> FailedAccountCategorys { get; set; } = new();
}

/// <summary>
/// Details of a failed invoice in batch processing
/// </summary>
public class FailedInvoiceDto
{
    public int AccountCategoryId { get; set; }
    public string Reason { get; set; } = string.Empty;
    public string ErrorType { get; set; } = string.Empty;
}

/// <summary>
/// Request DTO for generating a transaction invoice (WCF: XGenerateTransactionInvoice)
/// </summary>
public class GenerateTransactionInvoiceDto
{
    [Required]
    [Range(1, int.MaxValue)]
    public int AccountCategoryId { get; set; }

    [Required]
    [Range(0.01, double.MaxValue, ErrorMessage = "Invoice amount must be greater than zero")]
    public decimal InvoiceAmount { get; set; }

    [Required]
    public DateTime EffectiveDate { get; set; }

    [MaxLength(500)]
    public string? Description { get; set; }
}

/// <summary>
/// Response DTO for transaction invoice generation
/// </summary>
public class GenerateTransactionInvoiceResultDto
{
    public Guid? InvoiceId { get; set; }
    public bool InvoiceCreated { get; set; }
    public string Reason { get; set; } = string.Empty;
    public decimal PegAmount { get; set; }
}
