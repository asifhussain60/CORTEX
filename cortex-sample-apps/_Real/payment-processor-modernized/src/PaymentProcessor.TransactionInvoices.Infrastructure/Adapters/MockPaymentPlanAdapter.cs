using Microsoft.Extensions.Logging;
using PaymentProcessor.TransactionInvoices.Core.Adapters;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Adapters;

/// <summary>
/// Mock implementation of IPaymentPlanAdapter for development/testing.
/// Phase 6 will replace this with real Paragon integration with Polly retry policies.
/// </summary>
public class MockPaymentPlanAdapter : IPaymentPlanAdapter
{
    private readonly ILogger<MockPaymentPlanAdapter> _logger;

    public MockPaymentPlanAdapter(ILogger<MockPaymentPlanAdapter> logger)
    {
        _logger = logger;
    }

    public Task<List<PaymentAuthorization>> GetPaymentAuthorizationsAsync(string employerId, string account_categoryId, List<string> planIds)
    {
        _logger.LogInformation("MOCK: GetPaymentAuthorizationsAsync called for Employer={EmployerId}, AccountCategory={AccountCategoryId}, Plans={PlanCount}", 
            employerId, account_categoryId, planIds.Count);

        // Return mock payment authorization with auto-debit enabled
        var mockAuth = new PaymentAuthorization
        {
            PaymentAuthorizationId = $"PA-MOCK-{Guid.NewGuid():N}",
            PaymentPlanId = planIds.FirstOrDefault() ?? "PLAN-001",
            IsAutoDebit = true,
            TransactionMethodId = "FM-MOCK-001",
            AccountType = "Checking",
            BankAccountLast4 = "1234"
        };

        return Task.FromResult(new List<PaymentAuthorization> { mockAuth });
    }

    public Task<List<PaymentPlan>> GetPaymentPlansAsync(string account_categoryId)
    {
        _logger.LogInformation("MOCK: GetPaymentPlansAsync called for AccountCategory={AccountCategoryId}", account_categoryId);

        // Return mock payment plan
        var mockPlan = new PaymentPlan
        {
            PaymentPlanId = $"RP-MOCK-{Guid.NewGuid():N}",
            PlanShortDescription = "Mock PaymentProcessor Plan",
            CachedTotalElectionAmount = 5000.00m,
            EmployerId = "EMP-MOCK-001"
        };

        return Task.FromResult(new List<PaymentPlan> { mockPlan });
    }
}
