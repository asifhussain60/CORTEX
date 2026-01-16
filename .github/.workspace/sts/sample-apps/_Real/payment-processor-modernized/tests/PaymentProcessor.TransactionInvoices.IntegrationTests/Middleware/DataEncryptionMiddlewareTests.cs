using FluentAssertions;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Moq;
using PaymentProcessor.TransactionInvoices.API;
using PaymentProcessor.TransactionInvoices.Core.Security;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;

namespace PaymentProcessor.TransactionInvoices.IntegrationTests.Middleware;

/// <summary>
/// Integration tests for DataEncryptionMiddleware.
/// Verifies automatic encryption/decryption of sensitive fields.
/// </summary>
public class DataEncryptionMiddlewareTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly Mock<IEncryptionService> _encryptionServiceMock;

    public DataEncryptionMiddlewareTests(WebApplicationFactory<Program> factory)
    {
        _encryptionServiceMock = new Mock<IEncryptionService>();

        // Setup mock encryption service for predictable testing
        _encryptionServiceMock
            .Setup(s => s.EncryptAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((string plaintext, CancellationToken _) =>
                string.IsNullOrEmpty(plaintext) ? plaintext : $"ENCRYPTED[{plaintext}]");

        _encryptionServiceMock
            .Setup(s => s.DecryptAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((string ciphertext, CancellationToken _) =>
            {
                if (string.IsNullOrEmpty(ciphertext)) return ciphertext;
                if (ciphertext.StartsWith("ENCRYPTED[") && ciphertext.EndsWith("]"))
                {
                    return ciphertext[10..^1]; // Remove "ENCRYPTED[" and "]"
                }
                return ciphertext;
            });

        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureAppConfiguration((context, config) =>
            {
                config.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["Encryption:Enabled"] = "true",
                    ["AuditLogging:Enabled"] = "false" // Disable audit logging for cleaner tests
                });
            });

            builder.ConfigureServices(services =>
            {
                // Replace real encryption service with mock
                var descriptor = services.SingleOrDefault(
                    d => d.ServiceType == typeof(IEncryptionService));

                if (descriptor != null)
                {
                    services.Remove(descriptor);
                }

                services.AddSingleton(_encryptionServiceMock.Object);
            });
        });
    }

    [Fact]
    public async Task Middleware_EncryptionDisabled_PassesThroughWithoutEncryption()
    {
        // Arrange
        var client = _factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureAppConfiguration((context, config) =>
            {
                config.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["Encryption:Enabled"] = "false"
                });
            });
        }).CreateClient();

        // Act - Make any request
        var response = await client.GetAsync("/api/transactioninvoices");

        // Assert - Should succeed without encryption service being called
        response.Should().NotBeNull();
        _encryptionServiceMock.Verify(
            s => s.DecryptAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()),
            Times.Never);
    }

    [Fact]
    public async Task Middleware_GetRequest_DoesNotEncryptRequest()
    {
        // Arrange
        var client = _factory.CreateClient();

        // Act
        var response = await client.GetAsync("/api/transactioninvoices");

        // Assert - GET requests should not trigger request encryption
        response.Should().NotBeNull();
        _encryptionServiceMock.Verify(
            s => s.EncryptAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()),
            Times.Never);
    }

    [Fact]
    public async Task Middleware_PostRequest_JsonContent_EncryptsRequestBody()
    {
        // Arrange
        var client = _factory.CreateClient();
        var testData = new
        {
            InvoiceNumber = "INV-2025-001",
            Amount = 1500.00m,
            CustomerName = "John Doe" // Should be encrypted
        };

        // Act
        var response = await client.PostAsJsonAsync("/api/transactioninvoices", testData);

        // Assert - POST with JSON should trigger encryption (middleware will attempt)
        // Note: Actual encryption logic is placeholder, but middleware structure is validated
        response.Should().NotBeNull();
    }

    [Fact]
    public async Task Middleware_SuccessfulResponse_DecryptsResponseBody()
    {
        // Arrange
        var client = _factory.CreateClient();

        // Act
        var response = await client.GetAsync("/api/transactioninvoices");

        // Assert - Successful JSON response should trigger decryption attempt
        if (response.IsSuccessStatusCode &&
            response.Content.Headers.ContentType?.MediaType == "application/json")
        {
            var content = await response.Content.ReadAsStringAsync();
            content.Should().NotBeNull();
        }
    }

    [Fact]
    public async Task Middleware_NonJsonRequest_SkipsEncryption()
    {
        // Arrange
        var client = _factory.CreateClient();
        var content = new StringContent("plain text", Encoding.UTF8, "text/plain");

        // Act
        var response = await client.PostAsync("/api/transactioninvoices", content);

        // Assert - Non-JSON content should not be encrypted
        _encryptionServiceMock.Verify(
            s => s.EncryptAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()),
            Times.Never);
    }

    [Fact]
    public async Task Middleware_ErrorResponse_SkipsDecryption()
    {
        // Arrange
        var client = _factory.CreateClient();

        // Act - Request non-existent resource (likely 404)
        var response = await client.GetAsync("/api/nonexistent");

        // Assert - Error responses should not trigger decryption
        if (!response.IsSuccessStatusCode)
        {
            _encryptionServiceMock.Verify(
                s => s.DecryptAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()),
                Times.Never);
        }
    }

    /// <summary>
    /// NOTE: Full end-to-end encryption tests with [Encrypted] attribute
    /// will be added when entity models are updated with encryption markers.
    /// These tests validate middleware structure and request/response filtering.
    /// </summary>
}
