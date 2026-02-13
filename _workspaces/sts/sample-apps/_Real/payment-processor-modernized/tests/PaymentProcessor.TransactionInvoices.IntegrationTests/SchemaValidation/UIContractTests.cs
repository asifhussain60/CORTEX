using FluentAssertions;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Newtonsoft.Json.Linq;
using PaymentProcessor.TransactionInvoices.API;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;
using PaymentProcessor.TransactionInvoices.Infrastructure.Mock;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;
using System.Net.Http.Json;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.IntegrationTests.SchemaValidation;

/// <summary>
/// Phase 5a - UI Component Contract Tests.
/// Validates JSON response shapes are identical from Mock and EF Core data layers.
/// MANDATORY: All tests must pass before production deployment.
/// Prevents UI runtime breaks when swapping data layers.
/// </summary>
public class UIContractTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public UIContractTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task TransactionInvoiceAPI_MockVsEFCore_MustReturnIdenticalJSONShape()
    {
        // Arrange
        var mockClient = _factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Remove existing repository registrations
                var descriptor = services.SingleOrDefault(d => d.ServiceType == typeof(ITransactionInvoiceRepository));
                if (descriptor != null)
                    services.Remove(descriptor);

                // Register Mock repository
                services.AddSingleton<ITransactionInvoiceRepository, MockTransactionInvoiceRepository>();
            });
        }).CreateClient();

        var efCoreClient = _factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Remove existing repository registrations
                var descriptor = services.SingleOrDefault(d => d.ServiceType == typeof(ITransactionInvoiceRepository));
                if (descriptor != null)
                    services.Remove(descriptor);

                // Register EF Core repository (would use real DbContext in production)
                services.AddScoped<ITransactionInvoiceRepository, EFCoreTransactionInvoiceRepository>();
            });
        }).CreateClient();

        // Act
        var mockResponse = await mockClient.GetAsync("/api/v1/transaction-invoices/MOCK-INVOICE-001");
        var efResponse = await efCoreClient.GetAsync("/api/v1/transaction-invoices/MOCK-INVOICE-001");

        // Assert - Both should succeed or both should fail
        mockResponse.IsSuccessStatusCode.Should().Be(efResponse.IsSuccessStatusCode,
            "Both data layers must have same success/failure behavior");

        if (mockResponse.IsSuccessStatusCode && efResponse.IsSuccessStatusCode)
        {
            var mockJson = await mockResponse.Content.ReadAsStringAsync();
            var efJson = await efResponse.Content.ReadAsStringAsync();

            // Deep JSON comparison
            var mockToken = JToken.Parse(mockJson);
            var efToken = JToken.Parse(efJson);

            JToken.DeepEquals(mockToken, efToken).Should().BeTrue(
                "UI must receive identical JSON structure from both data layers. " +
                $"Mock JSON: {mockJson}\nEF Core JSON: {efJson}");
        }
    }

    [Fact]
    public async Task TransactionInvoiceListAPI_MockVsEFCore_MustReturnIdenticalArrayStructure()
    {
        // Arrange
        var mockClient = CreateClientWithMockLayer();
        var efCoreClient = CreateClientWithEFCoreLayer();

        // Act
        var mockResponse = await mockClient.GetAsync("/api/v1/transaction-invoices");
        var efResponse = await efCoreClient.GetAsync("/api/v1/transaction-invoices");

        // Assert
        mockResponse.IsSuccessStatusCode.Should().BeTrue("Mock API should return invoice list");
        efResponse.IsSuccessStatusCode.Should().BeTrue("EF Core API should return invoice list");

        var mockJson = await mockResponse.Content.ReadAsStringAsync();
        var efJson = await efResponse.Content.ReadAsStringAsync();

        var mockArray = JArray.Parse(mockJson);
        var efArray = JArray.Parse(efJson);

        // Verify both return arrays
        mockArray.Should().NotBeNull();
        efArray.Should().NotBeNull();

        // Verify same number of properties in each object
        if (mockArray.Count > 0 && efArray.Count > 0)
        {
            var mockFirstItem = mockArray[0] as JObject;
            var efFirstItem = efArray[0] as JObject;

            var mockProperties = mockFirstItem?.Properties().Select(p => p.Name).OrderBy(n => n).ToList();
            var efProperties = efFirstItem?.Properties().Select(p => p.Name).OrderBy(n => n).ToList();

            mockProperties.Should().BeEquivalentTo(efProperties,
                "Both data layers must return same JSON properties");
        }
    }

    [Theory]
    [InlineData("/api/v1/transaction-batches/MOCK-BATCH-001")]
    [InlineData("/api/v1/account_categorys/MOCK-SUB-001")]
    public async Task AllEntityAPIs_MockVsEFCore_MustHaveIdenticalJSONSchema(string endpoint)
    {
        // Arrange
        var mockClient = CreateClientWithMockLayer();
        var efCoreClient = CreateClientWithEFCoreLayer();

        // Act
        var mockResponse = await mockClient.GetAsync(endpoint);
        var efResponse = await efCoreClient.GetAsync(endpoint);

        // Assert - Compare status codes
        mockResponse.StatusCode.Should().Be(efResponse.StatusCode,
            $"Both data layers must return same HTTP status for {endpoint}");

        // If both successful, compare JSON shape
        if (mockResponse.IsSuccessStatusCode && efResponse.IsSuccessStatusCode)
        {
            var mockJson = await mockResponse.Content.ReadAsStringAsync();
            var efJson = await efResponse.Content.ReadAsStringAsync();

            var mockToken = JToken.Parse(mockJson);
            var efToken = JToken.Parse(efJson);

            // Compare property names (ignore values which may differ)
            var mockProps = GetPropertyNames(mockToken);
            var efProps = GetPropertyNames(efToken);

            mockProps.Should().BeEquivalentTo(efProps,
                $"JSON schema must be identical for {endpoint}");
        }
    }

    [Fact]
    public async Task ErrorResponses_MockVsEFCore_MustHaveIdenticalFormat()
    {
        // Arrange - Request non-existent resource
        var mockClient = CreateClientWithMockLayer();
        var efCoreClient = CreateClientWithEFCoreLayer();

        // Act
        var mockResponse = await mockClient.GetAsync("/api/v1/transaction-invoices/DOES-NOT-EXIST");
        var efResponse = await efCoreClient.GetAsync("/api/v1/transaction-invoices/DOES-NOT-EXIST");

        // Assert - Both should return 404
        mockResponse.StatusCode.Should().Be(System.Net.HttpStatusCode.NotFound);
        efResponse.StatusCode.Should().Be(System.Net.HttpStatusCode.NotFound);

        var mockJson = await mockResponse.Content.ReadAsStringAsync();
        var efJson = await efResponse.Content.ReadAsStringAsync();

        // Error response format should be identical
        if (!string.IsNullOrWhiteSpace(mockJson) && !string.IsNullOrWhiteSpace(efJson))
        {
            var mockError = JToken.Parse(mockJson);
            var efError = JToken.Parse(efJson);

            var mockErrorProps = GetPropertyNames(mockError);
            var efErrorProps = GetPropertyNames(efError);

            mockErrorProps.Should().BeEquivalentTo(efErrorProps,
                "Error response structure must be identical");
        }
    }

    [Fact]
    public async Task CreateInvoiceAPI_MockVsEFCore_MustAcceptIdenticalPayload()
    {
        // Arrange
        var mockClient = CreateClientWithMockLayer();
        var efCoreClient = CreateClientWithEFCoreLayer();

        var payload = new
        {
            invoiceId = "UI-TEST-001",
            batchId = "MOCK-BATCH-001",
            account_categoryId = "MOCK-SUB-001",
            amount = 5000.00m,
            status = "Pending"
        };

        // Act
        var mockResponse = await mockClient.PostAsJsonAsync("/api/v1/transaction-invoices", payload);
        
        var efPayload = new
        {
            invoiceId = "UI-TEST-002",
            batchId = "MOCK-BATCH-001",
            account_categoryId = "MOCK-SUB-001",
            amount = 5000.00m,
            status = "Pending"
        };
        var efResponse = await efCoreClient.PostAsJsonAsync("/api/v1/transaction-invoices", efPayload);

        // Assert - Both should have same response type (success or validation error)
        var mockIsSuccess = mockResponse.IsSuccessStatusCode;
        var efIsSuccess = efResponse.IsSuccessStatusCode;

        mockIsSuccess.Should().Be(efIsSuccess,
            "Both data layers must handle POST requests identically");

        // If successful, verify response structure
        if (mockIsSuccess && efIsSuccess)
        {
            var mockJson = await mockResponse.Content.ReadAsStringAsync();
            var efJson = await efResponse.Content.ReadAsStringAsync();

            var mockToken = JToken.Parse(mockJson);
            var efToken = JToken.Parse(efJson);

            var mockProps = GetPropertyNames(mockToken);
            var efProps = GetPropertyNames(efToken);

            mockProps.Should().BeEquivalentTo(efProps,
                "CREATE response structure must be identical");
        }
    }

    /// <summary>
    /// Helper: Creates HTTP client configured with Mock data layer.
    /// </summary>
    private HttpClient CreateClientWithMockLayer()
    {
        return _factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Configure Mock repositories
                var descriptors = services.Where(d =>
                    d.ServiceType == typeof(ITransactionInvoiceRepository) ||
                    d.ServiceType == typeof(ITransactionBatchRepository) ||
                    d.ServiceType == typeof(IAccountCategoryRepository)).ToList();

                foreach (var descriptor in descriptors)
                {
                    services.Remove(descriptor);
                }

                services.AddSingleton<ITransactionInvoiceRepository, MockTransactionInvoiceRepository>();
                services.AddSingleton<ITransactionBatchRepository, MockTransactionBatchRepository>();
                services.AddSingleton<IAccountCategoryRepository, MockAccountCategoryRepository>();
            });
        }).CreateClient();
    }

    /// <summary>
    /// Helper: Creates HTTP client configured with EF Core data layer.
    /// </summary>
    private HttpClient CreateClientWithEFCoreLayer()
    {
        return _factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Configure EF Core repositories (would use real DbContext in production)
                var descriptors = services.Where(d =>
                    d.ServiceType == typeof(ITransactionInvoiceRepository) ||
                    d.ServiceType == typeof(ITransactionBatchRepository) ||
                    d.ServiceType == typeof(IAccountCategoryRepository)).ToList();

                foreach (var descriptor in descriptors)
                {
                    services.Remove(descriptor);
                }

                services.AddScoped<ITransactionInvoiceRepository, EFCoreTransactionInvoiceRepository>();
                services.AddScoped<ITransactionBatchRepository, EFCoreTransactionBatchRepository>();
                services.AddScoped<IAccountCategoryRepository, EFCoreAccountCategoryRepository>();
            });
        }).CreateClient();
    }

    /// <summary>
    /// Helper: Extracts all property names from a JToken recursively.
    /// </summary>
    private List<string> GetPropertyNames(JToken token)
    {
        var propertyNames = new List<string>();

        if (token is JObject obj)
        {
            foreach (var property in obj.Properties())
            {
                propertyNames.Add(property.Name);
            }
        }
        else if (token is JArray array && array.Count > 0)
        {
            // For arrays, analyze first item
            propertyNames.AddRange(GetPropertyNames(array[0]));
        }

        return propertyNames.OrderBy(n => n).ToList();
    }
}
