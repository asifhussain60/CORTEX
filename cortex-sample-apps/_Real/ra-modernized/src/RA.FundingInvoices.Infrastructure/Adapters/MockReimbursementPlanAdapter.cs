using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.Adapters;

namespace RA.FundingInvoices.Infrastructure.Adapters;

/// <summary>
/// Mock implementation of IReimbursementPlanAdapter for development/testing.
/// Phase 6 will replace this with real Paragon integration with Polly retry policies.
/// </summary>
public class MockReimbursementPlanAdapter : IReimbursementPlanAdapter
{
    private readonly ILogger<MockReimbursementPlanAdapter> _logger;

    public MockReimbursementPlanAdapter(ILogger<MockReimbursementPlanAdapter> logger)
    {
        _logger = logger;
    }

    public Task<List<PaymentAuthorization>> GetPaymentAuthorizationsAsync(string employerId, string subaccountId, List<string> planIds)
    {
        _logger.LogInformation("MOCK: GetPaymentAuthorizationsAsync called for Employer={EmployerId}, Subaccount={SubaccountId}, Plans={PlanCount}", 
            employerId, subaccountId, planIds.Count);

        // Return mock payment authorization with auto-debit enabled
        var mockAuth = new PaymentAuthorization
        {
            PaymentAuthorizationId = $"PA-MOCK-{Guid.NewGuid():N}",
            ReimbursementPlanId = planIds.FirstOrDefault() ?? "PLAN-001",
            IsAutoDebit = true,
            FundingMethodId = "FM-MOCK-001",
            AccountType = "Checking",
            BankAccountLast4 = "1234"
        };

        return Task.FromResult(new List<PaymentAuthorization> { mockAuth });
    }

    public Task<List<ReimbursementPlan>> GetReimbursementPlansAsync(string subaccountId)
    {
        _logger.LogInformation("MOCK: GetReimbursementPlansAsync called for Subaccount={SubaccountId}", subaccountId);

        // Return mock reimbursement plan
        var mockPlan = new ReimbursementPlan
        {
            ReimbursementPlanId = $"RP-MOCK-{Guid.NewGuid():N}",
            PlanShortDescription = "Mock RA Plan",
            CachedTotalElectionAmount = 5000.00m,
            EmployerId = "EMP-MOCK-001"
        };

        return Task.FromResult(new List<ReimbursementPlan> { mockPlan });
    }
}
