using FluentAssertions;
using FluentValidation;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.API.Middleware;
using RA.FundingInvoices.Core.Exceptions;
using System.Text.Json;
using Xunit;

namespace RA.FundingInvoices.API.Tests.Middleware;

public class ProblemDetailsMiddlewareTests
{
    private readonly Mock<ILogger<ProblemDetailsMiddleware>> _mockLogger;
    private readonly Mock<IHostEnvironment> _mockHostEnvironment;

    public ProblemDetailsMiddlewareTests()
    {
        _mockLogger = new Mock<ILogger<ProblemDetailsMiddleware>>();
        _mockHostEnvironment = new Mock<IHostEnvironment>();
    }

    [Fact]
    public async Task InvokeAsync_NoException_CallsNextMiddleware()
    {
        // Arrange
        var context = new DefaultHttpContext();
        var nextCalled = false;
        RequestDelegate next = (_) =>
        {
            nextCalled = true;
            return Task.CompletedTask;
        };

        var middleware = new ProblemDetailsMiddleware(next, _mockLogger.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        nextCalled.Should().BeTrue();
        context.Response.StatusCode.Should().Be(StatusCodes.Status200OK);
    }

    [Fact]
    public async Task InvokeAsync_ValidationException_Returns400WithValidationProblemDetails()
    {
        // Arrange
        var context = new DefaultHttpContext();
        context.Response.Body = new MemoryStream();

        var validationErrors = new[]
        {
            new FluentValidation.Results.ValidationFailure("EmployerId", "EmployerId is required"),
            new FluentValidation.Results.ValidationFailure("Amount", "Amount must be greater than 0")
        };
        var validationException = new ValidationException(validationErrors);

        RequestDelegate next = (_) => throw validationException;

        var middleware = new ProblemDetailsMiddleware(next, _mockLogger.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        context.Response.StatusCode.Should().Be(StatusCodes.Status400BadRequest);
        context.Response.ContentType.Should().Be("application/problem+json");

        context.Response.Body.Seek(0, SeekOrigin.Begin);
        var responseBody = await new StreamReader(context.Response.Body).ReadToEndAsync();
        var problemDetails = JsonSerializer.Deserialize<JsonElement>(responseBody);

        problemDetails.GetProperty("status").GetInt32().Should().Be(400);
        problemDetails.GetProperty("title").GetString().Should().Contain("validation errors");
        problemDetails.GetProperty("errors").EnumerateObject().Should().HaveCount(2);
    }

    [Fact]
    public async Task InvokeAsync_NotFoundException_Returns404WithProblemDetails()
    {
        // Arrange
        var context = new DefaultHttpContext();
        context.Response.Body = new MemoryStream();
        context.Request.Path = "/api/v1/funding-invoices/INV-999";

        var notFoundException = new NotFoundException("FundingInvoice", "INV-999");
        RequestDelegate next = (_) => throw notFoundException;

        var middleware = new ProblemDetailsMiddleware(next, _mockLogger.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        context.Response.StatusCode.Should().Be(StatusCodes.Status404NotFound);
        context.Response.ContentType.Should().Be("application/problem+json");

        context.Response.Body.Seek(0, SeekOrigin.Begin);
        var responseBody = await new StreamReader(context.Response.Body).ReadToEndAsync();
        var problemDetails = JsonSerializer.Deserialize<JsonElement>(responseBody);

        problemDetails.GetProperty("status").GetInt32().Should().Be(404);
        problemDetails.GetProperty("title").GetString().Should().Be("Resource Not Found");
        problemDetails.GetProperty("detail").GetString().Should().Contain("INV-999");
        problemDetails.GetProperty("instance").GetString().Should().Be("/api/v1/funding-invoices/INV-999");
    }

    [Fact]
    public async Task InvokeAsync_InvalidOperationException_Returns409WithProblemDetails()
    {
        // Arrange
        var context = new DefaultHttpContext();
        context.Response.Body = new MemoryStream();
        context.Request.Path = "/api/v1/funding-batches/close";

        var invalidOpException = new InvalidOperationException("Batch total amount is zero. Cannot close batch with zero total.");
        RequestDelegate next = (_) => throw invalidOpException;

        var middleware = new ProblemDetailsMiddleware(next, _mockLogger.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        context.Response.StatusCode.Should().Be(StatusCodes.Status409Conflict);
        context.Response.ContentType.Should().Be("application/problem+json");

        context.Response.Body.Seek(0, SeekOrigin.Begin);
        var responseBody = await new StreamReader(context.Response.Body).ReadToEndAsync();
        var problemDetails = JsonSerializer.Deserialize<JsonElement>(responseBody);

        problemDetails.GetProperty("status").GetInt32().Should().Be(409);
        problemDetails.GetProperty("title").GetString().Should().Be("Business Logic Error");
        problemDetails.GetProperty("detail").GetString().Should().Contain("zero total");
    }

    [Fact]
    public async Task InvokeAsync_UnhandledException_Returns500WithProblemDetails_Development()
    {
        // Arrange
        var context = new DefaultHttpContext();
        context.Response.Body = new MemoryStream();

        var serviceProvider = new Mock<IServiceProvider>();
        _mockHostEnvironment.Setup(e => e.IsDevelopment()).Returns(true);
        serviceProvider.Setup(sp => sp.GetService(typeof(IHostEnvironment)))
            .Returns(_mockHostEnvironment.Object);
        context.RequestServices = serviceProvider.Object;

        var unhandledException = new InvalidCastException("Cannot cast Foo to Bar");
        RequestDelegate next = (_) => throw unhandledException;

        var middleware = new ProblemDetailsMiddleware(next, _mockLogger.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        context.Response.StatusCode.Should().Be(StatusCodes.Status500InternalServerError);
        context.Response.ContentType.Should().Be("application/problem+json");

        context.Response.Body.Seek(0, SeekOrigin.Begin);
        var responseBody = await new StreamReader(context.Response.Body).ReadToEndAsync();
        var problemDetails = JsonSerializer.Deserialize<JsonElement>(responseBody);

        problemDetails.GetProperty("status").GetInt32().Should().Be(500);
        problemDetails.GetProperty("title").GetString().Should().Contain("error occurred");
        problemDetails.GetProperty("detail").GetString().Should().Contain("Cannot cast Foo to Bar"); // Dev mode shows details
    }

    [Fact]
    public async Task InvokeAsync_UnhandledException_Returns500WithGenericMessage_Production()
    {
        // Arrange
        var context = new DefaultHttpContext();
        context.Response.Body = new MemoryStream();

        var serviceProvider = new Mock<IServiceProvider>();
        _mockHostEnvironment.Setup(e => e.IsDevelopment()).Returns(false); // Production mode
        serviceProvider.Setup(sp => sp.GetService(typeof(IHostEnvironment)))
            .Returns(_mockHostEnvironment.Object);
        context.RequestServices = serviceProvider.Object;

        var unhandledException = new InvalidCastException("Cannot cast Foo to Bar");
        RequestDelegate next = (_) => throw unhandledException;

        var middleware = new ProblemDetailsMiddleware(next, _mockLogger.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        context.Response.StatusCode.Should().Be(StatusCodes.Status500InternalServerError);

        context.Response.Body.Seek(0, SeekOrigin.Begin);
        var responseBody = await new StreamReader(context.Response.Body).ReadToEndAsync();
        var problemDetails = JsonSerializer.Deserialize<JsonElement>(responseBody);

        problemDetails.GetProperty("detail").GetString().Should().Contain("internal server error"); // Generic message
        problemDetails.GetProperty("detail").GetString().Should().NotContain("Cannot cast"); // No exception details
    }

    [Fact]
    public async Task InvokeAsync_LogsError_ForAllExceptions()
    {
        // Arrange
        var context = new DefaultHttpContext();
        context.Response.Body = new MemoryStream();

        var exception = new InvalidOperationException("Test error");
        RequestDelegate next = (_) => throw exception;

        var middleware = new ProblemDetailsMiddleware(next, _mockLogger.Object);

        // Act
        await middleware.InvokeAsync(context);

        // Assert
        _mockLogger.Verify(
            logger => logger.Log(
                LogLevel.Error,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Unhandled exception occurred")),
                exception,
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }
}
