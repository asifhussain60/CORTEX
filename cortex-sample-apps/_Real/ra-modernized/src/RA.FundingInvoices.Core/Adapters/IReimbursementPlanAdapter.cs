namespace RA.FundingInvoices.Core.Adapters;

/// <summary>
/// DTO representing a payment authorization from Paragon microservice.
/// Maps to IReimbursementPlanService.GetFundingOptionsAndPaymentAuthorizationsAsync response.
/// </summary>
public class PaymentAuthorization
{
    public string PaymentAuthorizationId { get; set; } = string.Empty;
    public string ReimbursementPlanId { get; set; } = string.Empty;
    public bool IsAutoDebit { get; set; }
    public string FundingMethodId { get; set; } = string.Empty;
    public string AccountType { get; set; } = string.Empty;
    public string? BankAccountLast4 { get; set; }
}

/// <summary>
/// DTO representing a reimbursement plan from Paragon microservice.
/// </summary>
public class ReimbursementPlan
{
    public string ReimbursementPlanId { get; set; } = string.Empty;
    public string PlanShortDescription { get; set; } = string.Empty;
    public decimal CachedTotalElectionAmount { get; set; }
    public string EmployerId { get; set; } = string.Empty;
}

/// <summary>
/// Adapter interface for Paragon IReimbursementPlanService.
/// Provides abstraction with retry policies and circuit breaker.
/// </summary>
public interface IReimbursementPlanAdapter
{
    /// <summary>
    /// Retrieves funding options and payment authorizations for a list of plans.
    /// Wraps IReimbursementPlanService.GetFundingOptionsAndPaymentAuthorizationsAsync.
    /// </summary>
    /// <param name="employerId">Employer (or Member) object ID</param>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <param name="planIds">List of reimbursement plan IDs</param>
    /// <returns>List of payment authorizations</returns>
    Task<List<PaymentAuthorization>> GetPaymentAuthorizationsAsync(string employerId, string subaccountId, List<string> planIds);

    /// <summary>
    /// Retrieves reimbursement plans for a subaccount.
    /// Wraps QFindRAPlansBySubaccount query logic.
    /// </summary>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <returns>List of reimbursement plans</returns>
    Task<List<ReimbursementPlan>> GetReimbursementPlansAsync(string subaccountId);
}
