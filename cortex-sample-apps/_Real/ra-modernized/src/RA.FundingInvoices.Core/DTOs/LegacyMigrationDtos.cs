using System.ComponentModel.DataAnnotations;

namespace RA.FundingInvoices.Core.DTOs;

/// <summary>
/// Request DTO for creating batch funding invoices (WCF: Updater_CreateRAFundingInvoices)
/// </summary>
public class CreateBatchInvoicesDto
{
    [Required]
    public string EmployerId { get; set; } = string.Empty;

    [Required]
    [MinLength(1, ErrorMessage = "At least one subaccount ID is required")]
    public List<int> SubaccountIds { get; set; } = new();

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
    public List<FailedInvoiceDto> FailedSubaccounts { get; set; } = new();
}

/// <summary>
/// Details of a failed invoice in batch processing
/// </summary>
public class FailedInvoiceDto
{
    public int SubaccountId { get; set; }
    public string Reason { get; set; } = string.Empty;
    public string ErrorType { get; set; } = string.Empty;
}

/// <summary>
/// Request DTO for generating a funding invoice (WCF: XGenerateFundingInvoice)
/// </summary>
public class GenerateFundingInvoiceDto
{
    [Required]
    [Range(1, int.MaxValue)]
    public int SubaccountId { get; set; }

    [Required]
    [Range(0.01, double.MaxValue, ErrorMessage = "Invoice amount must be greater than zero")]
    public decimal InvoiceAmount { get; set; }

    [Required]
    public DateTime EffectiveDate { get; set; }

    [MaxLength(500)]
    public string? Description { get; set; }
}

/// <summary>
/// Response DTO for funding invoice generation
/// </summary>
public class GenerateFundingInvoiceResultDto
{
    public Guid? InvoiceId { get; set; }
    public bool InvoiceCreated { get; set; }
    public string Reason { get; set; } = string.Empty;
    public decimal PegAmount { get; set; }
}
