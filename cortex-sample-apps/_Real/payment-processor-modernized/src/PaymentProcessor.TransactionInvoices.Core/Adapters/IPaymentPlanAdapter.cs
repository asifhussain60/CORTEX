namespace PaymentProcessor.TransactionInvoices.Core.Adapters;

/// <summary>
/// DTO representing a payment authorization from Paragon microservice.
/// Maps to IPaymentPlanService.GetTransactionOptionsAndPaymentAuthorizationsAsync response.
/// </summary>
public class PaymentAuthorization
{
    public string PaymentAuthorizationId { get; set; } = string.Empty;
    public string PaymentPlanId { get; set; } = string.Empty;
    public bool IsAutoDebit { get; set; }
    public string TransactionMethodId { get; set; } = string.Empty;
    public string AccountType { get; set; } = string.Empty;
    public string? BankAccountLast4 { get; set; }
}

/// <summary>
/// DTO representing a payment plan from Paragon microservice.
/// </summary>
public class PaymentPlan
{
    public string PaymentPlanId { get; set; } = string.Empty;
    public string PlanShortDescription { get; set; } = string.Empty;
    public decimal CachedTotalElectionAmount { get; set; }
    public string EmployerId { get; set; } = string.Empty;
}

/// <summary>
/// Adapter interface for Paragon IPaymentPlanService.
/// Provides abstraction with retry policies and circuit breaker.
/// </summary>
public interface IPaymentPlanAdapter
{
    /// <summary>
    /// Retrieves transaction options and payment authorizations for a list of plans.
    /// Wraps IPaymentPlanService.GetTransactionOptionsAndPaymentAuthorizationsAsync.
    /// </summary>
    /// <param name="employerId">Employer (or Customer) object ID</param>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <param name="planIds">List of payment plan IDs</param>
    /// <returns>List of payment authorizations</returns>
    Task<List<PaymentAuthorization>> GetPaymentAuthorizationsAsync(string employerId, string account_categoryId, List<string> planIds);

    /// <summary>
    /// Retrieves payment plans for a account_category.
    /// Wraps QFindPaymentProcessorPlansByAccountCategory query logic.
    /// </summary>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <returns>List of payment plans</returns>
    Task<List<PaymentPlan>> GetPaymentPlansAsync(string account_categoryId);
}
