using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.API.Middleware;
using System.Text;

namespace RA.FundingInvoices.UnitTests.Middleware;

public class AuditLoggingMiddlewareTests
{
    private readonly Mock<ILogger<AuditLoggingMiddleware>> _mockLogger;
    private readonly Mock<IConfiguration> _mockConfiguration;

    public AuditLoggingMiddlewareTests()
    {
        _mockLogger = new Mock<ILogger<AuditLoggingMiddleware>>();
        _mockConfiguration = new Mock<IConfiguration>();

        // Setup default configuration
        _mockConfiguration.Setup(c => c["AuditLogging:Enabled"]).Returns("true");
        _mockConfiguration.Setup(c => c["AuditLogging:RedactPHI"]).Returns("true");
    }

    [Fact]
    public async Task InvokeAsync_ShouldLogAuditEntry_ForPOSTRequest()
    {
        // Arrange
        var context = CreateHttpContext("POST", "/api/invoices", "{\"amount\": 500}");
        var middleware = new AuditLoggingMiddleware(
            next: async (ctx) =>
            {
                ctx.Response.StatusCode = 201;
                await ctx.Response.WriteAsync("{\"invoiceId\": \"INV-001\"}");
            },
            _mockLogger.Object,
            _mockConfiguration.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("AUDIT")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);

        context.Response.StatusCode.Should().Be(201);
    }

    [Fact]
    public async Task InvokeAsync_ShouldNotLog_ForGETRequest()
    {
        // Arrange
        var context = CreateHttpContext("GET", "/api/invoices", "");
        var middleware = new AuditLoggingMiddleware(
            next: async (ctx) =>
            {
                ctx.Response.StatusCode = 200;
                await ctx.Response.WriteAsync("[]");
            },
            _mockLogger.Object,
            _mockConfiguration.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                It.IsAny<LogLevel>(),
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("AUDIT")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Never);
    }

    [Fact]
    public async Task InvokeAsync_ShouldRedactSSN_WhenEnabled()
    {
        // Arrange
        var requestBody = "{\"ssn\": \"123-45-6789\"}";
        var context = CreateHttpContext("POST", "/api/members", requestBody);
        
        string? loggedMessage = null;
        _mockLogger.Setup(x => x.Log(
            It.IsAny<LogLevel>(),
            It.IsAny<EventId>(),
            It.IsAny<It.IsAnyType>(),
            It.IsAny<Exception>(),
            It.IsAny<Func<It.IsAnyType, Exception?, string>>()))
            .Callback(new InvocationAction(invocation =>
            {
                loggedMessage = invocation.Arguments[2]?.ToString();
            }));

        var middleware = new AuditLoggingMiddleware(
            next: async (ctx) =>
            {
                ctx.Response.StatusCode = 200;
                await ctx.Response.WriteAsync("{}");
            },
            _mockLogger.Object,
            _mockConfiguration.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        loggedMessage.Should().NotBeNull();
        loggedMessage.Should().Contain("***-**-****");
        loggedMessage.Should().NotContain("123-45-6789");
    }

    [Fact]
    public async Task InvokeAsync_ShouldRedactMemberName_WhenEnabled()
    {
        // Arrange
        var requestBody = "{\"memberName\": \"John Doe\"}";
        var context = CreateHttpContext("POST", "/api/subaccounts", requestBody);
        
        string? loggedMessage = null;
        _mockLogger.Setup(x => x.Log(
            It.IsAny<LogLevel>(),
            It.IsAny<EventId>(),
            It.IsAny<It.IsAnyType>(),
            It.IsAny<Exception>(),
            It.IsAny<Func<It.IsAnyType, Exception?, string>>()))
            .Callback(new InvocationAction(invocation =>
            {
                loggedMessage = invocation.Arguments[2]?.ToString();
            }));

        var middleware = new AuditLoggingMiddleware(
            next: async (ctx) =>
            {
                ctx.Response.StatusCode = 200;
                await ctx.Response.WriteAsync("{}");
            },
            _mockLogger.Object,
            _mockConfiguration.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        loggedMessage.Should().NotBeNull();
        loggedMessage.Should().Contain("[REDACTED]");
        loggedMessage.Should().NotContain("John Doe");
    }

    [Fact]
    public async Task InvokeAsync_ShouldNotLog_WhenDisabled()
    {
        // Arrange
        _mockConfiguration.Setup(c => c["AuditLogging:Enabled"]).Returns("false");
        
        var context = CreateHttpContext("POST", "/api/invoices", "{\"amount\": 500}");
        var middleware = new AuditLoggingMiddleware(
            next: async (ctx) =>
            {
                ctx.Response.StatusCode = 201;
                await ctx.Response.WriteAsync("{}");
            },
            _mockLogger.Object,
            _mockConfiguration.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                It.IsAny<LogLevel>(),
                It.IsAny<EventId>(),
                It.IsAny<It.IsAnyType>(),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Never);
    }

    [Theory]
    [InlineData("PUT")]
    [InlineData("PATCH")]
    [InlineData("DELETE")]
    public async Task InvokeAsync_ShouldLogAuditEntry_ForCUDOperations(string method)
    {
        // Arrange
        var context = CreateHttpContext(method, "/api/invoices/123", "{\"amount\": 600}");
        var middleware = new AuditLoggingMiddleware(
            next: async (ctx) =>
            {
                ctx.Response.StatusCode = 200;
                await ctx.Response.WriteAsync("{}");
            },
            _mockLogger.Object,
            _mockConfiguration.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("AUDIT")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    private static HttpContext CreateHttpContext(string method, string path, string body)
    {
        var context = new DefaultHttpContext();
        context.Request.Method = method;
        context.Request.Path = path;
        context.Request.ContentType = "application/json";

        if (!string.IsNullOrEmpty(body))
        {
            var bytes = Encoding.UTF8.GetBytes(body);
            context.Request.Body = new MemoryStream(bytes);
            context.Request.ContentLength = bytes.Length;
        }

        context.Response.Body = new MemoryStream();

        return context;
    }
}
