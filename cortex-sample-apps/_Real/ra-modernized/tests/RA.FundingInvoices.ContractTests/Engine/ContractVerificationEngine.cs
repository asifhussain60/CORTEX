using System.Diagnostics;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.ContractTests.Reporting;

namespace RA.FundingInvoices.ContractTests.Engine;

/// <summary>
/// Core engine for WCF to REST contract verification.
/// Executes test scenarios and compares WCF vs REST responses.
/// </summary>
public class ContractVerificationEngine
{
    private readonly ILogger<ContractVerificationEngine> _logger;
    private readonly HttpClient _restClient;
    private readonly IWcfServiceProxy _wcfProxy;
    private readonly SchemaValidator _schemaValidator;

    public ContractVerificationEngine(
        HttpClient restClient,
        IWcfServiceProxy wcfProxy,
        SchemaValidator schemaValidator,
        ILogger<ContractVerificationEngine> logger)
    {
        _restClient = restClient;
        _wcfProxy = wcfProxy;
        _schemaValidator = schemaValidator;
        _logger = logger;
    }

    public async Task<VerificationReport> ExecuteVerificationAsync(TestScenarioCollection scenarios)
    {
        _logger.LogInformation("Starting contract verification with {ScenarioCount} scenarios", scenarios.TotalScenarios);

        var report = new VerificationReport
        {
            StartTime = DateTime.UtcNow,
            TotalScenarios = scenarios.TotalScenarios
        };

        foreach (var category in scenarios.Categories)
        {
            await VerifyCategoryAsync(category.Key, category.Value, report);
        }

        report.EndTime = DateTime.UtcNow;
        report.Duration = report.EndTime - report.StartTime;
        report.CalculateMetrics();

        _logger.LogInformation("Verification complete. Match rate: {MatchRate}%", report.MatchRate);

        // Generate reports
        var reportGenerator = new VerificationReportGenerator(report);
        var reportDirectory = Path.Combine(Directory.GetCurrentDirectory(), "reports", DateTime.Now.ToString("yyyy-MM-dd_HHmmss"));
        await reportGenerator.GenerateAllReportsAsync(reportDirectory);

        _logger.LogInformation("Reports generated in: {ReportDirectory}", reportDirectory);

        return report;
    }

    private async Task VerifyCategoryAsync(string wcfTransaction, CategoryScenarios scenarios, VerificationReport report)
    {
        _logger.LogInformation("Verifying transaction: {Transaction}", wcfTransaction);

        // Happy path scenarios
        foreach (var scenario in scenarios.HappyPath)
        {
            await VerifyScenarioAsync(wcfTransaction, scenario, report);
        }

        // Error cases
        foreach (var scenario in scenarios.ErrorCases)
        {
            await VerifyScenarioAsync(wcfTransaction, scenario, report);
        }

        // Edge cases
        if (scenarios.EdgeCases != null)
        {
            foreach (var scenario in scenarios.EdgeCases)
            {
                await VerifyScenarioAsync(wcfTransaction, scenario, report);
            }
        }

        // Boundary conditions
        if (scenarios.BoundaryConditions != null)
        {
            foreach (var scenario in scenarios.BoundaryConditions)
            {
                await VerifyScenarioAsync(wcfTransaction, scenario, report);
            }
        }

        // State transitions
        if (scenarios.StateTransitions != null)
        {
            foreach (var scenario in scenarios.StateTransitions)
            {
                await VerifyStateTransitionAsync(wcfTransaction, scenario, report);
            }
        }
    }

    private async Task VerifyScenarioAsync(string wcfTransaction, TestScenario scenario, VerificationReport report)
    {
        _logger.LogDebug("Executing scenario: {ScenarioId} - {Description}", scenario.Id, scenario.Description);

        var result = new ScenarioResult
        {
            ScenarioId = scenario.Id,
            Description = scenario.Description,
            WcfTransaction = wcfTransaction
        };

        try
        {
            // Execute WCF call
            var wcfStopwatch = Stopwatch.StartNew();
            var wcfResponse = await ExecuteWcfOperationAsync(wcfTransaction, scenario.Request);
            wcfStopwatch.Stop();
            result.WcfResponseTime = wcfStopwatch.ElapsedMilliseconds;
            result.WcfStatusCode = wcfResponse.StatusCode;
            result.WcfResponse = wcfResponse.Body;

            // Execute REST call
            var restStopwatch = Stopwatch.StartNew();
            var restResponse = await ExecuteRestOperationAsync(wcfTransaction, scenario.Request);
            restStopwatch.Stop();
            result.RestResponseTime = restStopwatch.ElapsedMilliseconds;
            result.RestStatusCode = (int)restResponse.StatusCode;
            result.RestResponse = await restResponse.Content.ReadAsStringAsync();

            // Compare status codes
            var expectedStatus = scenario.ExpectedResponse?.Status ?? 200;
            result.StatusCodeMatch = result.WcfStatusCode == expectedStatus && result.RestStatusCode == expectedStatus;

            if (!result.StatusCodeMatch)
            {
                result.Discrepancies.Add(new Discrepancy
                {
                    Field = "StatusCode",
                    WcfValue = result.WcfStatusCode.ToString(),
                    RestValue = result.RestStatusCode.ToString(),
                    Severity = DiscrepancySeverity.Critical
                });
            }

            // Compare response schemas
            if (result.StatusCodeMatch && result.RestStatusCode == 200 || result.RestStatusCode == 201)
            {
                var schemaMatch = _schemaValidator.ValidateResponseSchema(
                    wcfTransaction,
                    result.WcfResponse,
                    result.RestResponse);

                result.SchemaMatch = schemaMatch.IsValid;
                result.Discrepancies.AddRange(schemaMatch.Discrepancies);
            }

            // Validate business logic
            if (scenario.ExpectedResponse != null)
            {
                var businessLogicMatch = ValidateBusinessLogic(scenario.ExpectedResponse, result.RestResponse);
                result.BusinessLogicMatch = businessLogicMatch.IsValid;
                result.Discrepancies.AddRange(businessLogicMatch.Discrepancies);
            }

            result.IsMatch = result.StatusCodeMatch && result.SchemaMatch && result.BusinessLogicMatch;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing scenario {ScenarioId}", scenario.Id);
            result.IsMatch = false;
            result.Discrepancies.Add(new Discrepancy
            {
                Field = "Execution",
                WcfValue = "Success",
                RestValue = $"Exception: {ex.Message}",
                Severity = DiscrepancySeverity.Critical
            });
        }

        report.Results.Add(result);
    }

    private async Task<WcfResponse> ExecuteWcfOperationAsync(string transaction, object request)
    {
        return transaction switch
        {
            "XAddFundingInvoice" => await _wcfProxy.AddFundingInvoiceAsync(request),
            "XGenerateFundingInvoice" => await _wcfProxy.GenerateFundingInvoiceAsync(request),
            "Updater_CreateRAFundingInvoices" => await _wcfProxy.CreateBatchInvoicesAsync(request),
            "XCloseFundingBatch" => await _wcfProxy.CloseFundingBatchAsync(request),
            "XUpdateFundingBatch" => await _wcfProxy.UpdateFundingBatchAsync(request),
            _ => throw new ArgumentException($"Unknown WCF transaction: {transaction}")
        };
    }

    private async Task<HttpResponseMessage> ExecuteRestOperationAsync(string transaction, object request)
    {
        var endpoint = GetRestEndpoint(transaction);
        var json = JsonSerializer.Serialize(request, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });
        var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

        return endpoint.Method switch
        {
            "POST" => await _restClient.PostAsync(endpoint.Path, content),
            "PUT" => await _restClient.PutAsync(endpoint.Path, content),
            "GET" => await _restClient.GetAsync(endpoint.Path),
            _ => throw new ArgumentException($"Unknown HTTP method: {endpoint.Method}")
        };
    }

    private RestEndpoint GetRestEndpoint(string wcfTransaction)
    {
        return wcfTransaction switch
        {
            "XAddFundingInvoice" => new RestEndpoint { Method = "POST", Path = "/api/v1/funding-invoices" },
            "XGenerateFundingInvoice" => new RestEndpoint { Method = "POST", Path = "/api/v1/funding-invoices/generate" },
            "Updater_CreateRAFundingInvoices" => new RestEndpoint { Method = "POST", Path = "/api/v1/funding-invoices/batch" },
            "XCloseFundingBatch" => new RestEndpoint { Method = "POST", Path = "/api/v1/funding-batches/close" },
            "XUpdateFundingBatch" => new RestEndpoint { Method = "PUT", Path = "/api/v1/funding-batches/{id}" },
            _ => throw new ArgumentException($"Unknown WCF transaction: {wcfTransaction}")
        };
    }

    private ValidationResult ValidateBusinessLogic(ExpectedResponse expected, string actualResponseJson)
    {
        var result = new ValidationResult { IsValid = true };

        try
        {
            var actual = JsonSerializer.Deserialize<JsonElement>(actualResponseJson);

            // Validate expected fields
            if (expected.TotalAmount.HasValue)
            {
                var actualTotal = actual.GetProperty("totalAmount").GetDecimal();
                if (Math.Abs(actualTotal - expected.TotalAmount.Value) > 0.001m)
                {
                    result.IsValid = false;
                    result.Discrepancies.Add(new Discrepancy
                    {
                        Field = "totalAmount",
                        WcfValue = expected.TotalAmount.Value.ToString(),
                        RestValue = actualTotal.ToString(),
                        Severity = DiscrepancySeverity.High
                    });
                }
            }

            if (!string.IsNullOrEmpty(expected.InvoiceStatus))
            {
                var actualStatus = actual.GetProperty("status").GetString();
                if (actualStatus != expected.InvoiceStatus)
                {
                    result.IsValid = false;
                    result.Discrepancies.Add(new Discrepancy
                    {
                        Field = "status",
                        WcfValue = expected.InvoiceStatus,
                        RestValue = actualStatus!,
                        Severity = DiscrepancySeverity.High
                    });
                }
            }
        }
        catch (Exception ex)
        {
            result.IsValid = false;
            result.Discrepancies.Add(new Discrepancy
            {
                Field = "BusinessLogicValidation",
                WcfValue = "Valid",
                RestValue = $"Error: {ex.Message}",
                Severity = DiscrepancySeverity.Critical
            });
        }

        return result;
    }

    private async Task VerifyStateTransitionAsync(string wcfTransaction, StateTransitionScenario scenario, VerificationReport report)
    {
        // State transition verification logic
        // Track state changes through the operation lifecycle
        _logger.LogDebug("Verifying state transition: {ScenarioId}", scenario.Id);

        // This would involve multiple API calls to track state changes
        // Implementation depends on specific state transition requirements
    }
}

public class VerificationReport
{
    public DateTime StartTime { get; set; }
    public DateTime EndTime { get; set; }
    public TimeSpan Duration { get; set; }
    public int TotalScenarios { get; set; }
    public List<ScenarioResult> Results { get; set; } = new();
    
    public int PassedScenarios => Results.Count(r => r.IsMatch);
    public int FailedScenarios => Results.Count(r => !r.IsMatch);
    public double MatchRate => TotalScenarios > 0 ? (PassedScenarios / (double)TotalScenarios) * 100 : 0;
    
    public int CriticalDiscrepancies => Results.SelectMany(r => r.Discrepancies)
        .Count(d => d.Severity == DiscrepancySeverity.Critical);
    
    public int HighDiscrepancies => Results.SelectMany(r => r.Discrepancies)
        .Count(d => d.Severity == DiscrepancySeverity.High);
    
    public int MediumDiscrepancies => Results.SelectMany(r => r.Discrepancies)
        .Count(d => d.Severity == DiscrepancySeverity.Medium);

    public void CalculateMetrics()
    {
        // Additional metric calculations
    }

    public bool IsPassingGate => MatchRate == 100.0 && CriticalDiscrepancies == 0;
}

public class ScenarioResult
{
    public string ScenarioId { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string WcfTransaction { get; set; } = string.Empty;
    
    public int WcfStatusCode { get; set; }
    public int RestStatusCode { get; set; }
    public long WcfResponseTime { get; set; }
    public long RestResponseTime { get; set; }
    
    public string WcfResponse { get; set; } = string.Empty;
    public string RestResponse { get; set; } = string.Empty;
    
    public bool StatusCodeMatch { get; set; }
    public bool SchemaMatch { get; set; }
    public bool BusinessLogicMatch { get; set; }
    public bool IsMatch { get; set; }
    
    public List<Discrepancy> Discrepancies { get; set; } = new();
}

public class Discrepancy
{
    public string Field { get; set; } = string.Empty;
    public string WcfValue { get; set; } = string.Empty;
    public string RestValue { get; set; } = string.Empty;
    public DiscrepancySeverity Severity { get; set; }
    public string Description { get; set; } = string.Empty;
}

public enum DiscrepancySeverity
{
    Low,
    Medium,
    High,
    Critical
}

public class ValidationResult
{
    public bool IsValid { get; set; }
    public List<Discrepancy> Discrepancies { get; set; } = new();
}

public class WcfResponse
{
    public int StatusCode { get; set; }
    public string Body { get; set; } = string.Empty;
}

public class RestEndpoint
{
    public string Method { get; set; } = string.Empty;
    public string Path { get; set; } = string.Empty;
}

// Placeholder interfaces/classes for test scenario models
public class TestScenarioCollection
{
    public int TotalScenarios { get; set; }
    public Dictionary<string, CategoryScenarios> Categories { get; set; } = new();
}

public class CategoryScenarios
{
    public List<TestScenario> HappyPath { get; set; } = new();
    public List<TestScenario> ErrorCases { get; set; } = new();
    public List<TestScenario> EdgeCases { get; set; } = new();
    public List<TestScenario> BoundaryConditions { get; set; } = new();
    public List<StateTransitionScenario> StateTransitions { get; set; } = new();
}

public class TestScenario
{
    public string Id { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public object Request { get; set; } = new();
    public ExpectedResponse? ExpectedResponse { get; set; }
    public object? Setup { get; set; }
}

public class ExpectedResponse
{
    public int? Status { get; set; }
    public decimal? TotalAmount { get; set; }
    public string? InvoiceStatus { get; set; }
    public string? Result { get; set; }
    public string? ErrorType { get; set; }
}

public class StateTransitionScenario
{
    public string Id { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public object Setup { get; set; } = new();
    public List<string> ExpectedSequence { get; set; } = new();
}

public interface IWcfServiceProxy
{
    Task<WcfResponse> AddFundingInvoiceAsync(object request);
    Task<WcfResponse> GenerateFundingInvoiceAsync(object request);
    Task<WcfResponse> CreateBatchInvoicesAsync(object request);
    Task<WcfResponse> CloseFundingBatchAsync(object request);
    Task<WcfResponse> UpdateFundingBatchAsync(object request);
}
