using System.Net;
using System.Text.Json;
using FluentValidation;
using Microsoft.AspNetCore.Mvc;
using RA.FundingInvoices.Core.Exceptions;

namespace RA.FundingInvoices.API.Middleware;

/// <summary>
/// Global exception handling middleware that converts exceptions to RFC 7807 ProblemDetails responses.
/// </summary>
public class ProblemDetailsMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ProblemDetailsMiddleware> _logger;

    public ProblemDetailsMiddleware(RequestDelegate next, ILogger<ProblemDetailsMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception occurred: {Message}", ex.Message);
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var problemDetails = exception switch
        {
            ValidationException validationEx => CreateValidationProblemDetails(context, validationEx),
            NotFoundException notFoundEx => CreateNotFoundProblemDetails(context, notFoundEx),
            InvalidOperationException invalidOpEx => CreateConflictProblemDetails(context, invalidOpEx),
            _ => CreateInternalServerErrorProblemDetails(context, exception)
        };

        context.Response.ContentType = "application/problem+json";
        context.Response.StatusCode = problemDetails.Status ?? (int)HttpStatusCode.InternalServerError;

        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        };

        await context.Response.WriteAsync(JsonSerializer.Serialize(problemDetails, options));
    }

    /// <summary>
    /// Creates ProblemDetails for FluentValidation errors.
    /// Maps to HTTP 400 Bad Request.
    /// </summary>
    private ProblemDetails CreateValidationProblemDetails(HttpContext context, ValidationException exception)
    {
        var errors = exception.Errors
            .GroupBy(e => e.PropertyName)
            .ToDictionary(
                g => g.Key,
                g => g.Select(e => e.ErrorMessage).ToArray()
            );

        return new ValidationProblemDetails(errors)
        {
            Title = "One or more validation errors occurred",
            Detail = "Please refer to the errors property for additional details.",
            Status = StatusCodes.Status400BadRequest,
            Instance = context.Request.Path,
            Type = "https://tools.ietf.org/html/rfc7231#section-6.5.1"
        };
    }

    /// <summary>
    /// Creates ProblemDetails for entity not found errors.
    /// Maps to HTTP 404 Not Found.
    /// </summary>
    private ProblemDetails CreateNotFoundProblemDetails(HttpContext context, NotFoundException exception)
    {
        return new ProblemDetails
        {
            Title = "Resource Not Found",
            Detail = exception.Message,
            Status = StatusCodes.Status404NotFound,
            Instance = context.Request.Path,
            Type = "https://tools.ietf.org/html/rfc7231#section-6.5.4"
        };
    }

    /// <summary>
    /// Creates ProblemDetails for business logic errors.
    /// Maps to HTTP 409 Conflict.
    /// </summary>
    private ProblemDetails CreateConflictProblemDetails(HttpContext context, InvalidOperationException exception)
    {
        return new ProblemDetails
        {
            Title = "Business Logic Error",
            Detail = exception.Message,
            Status = StatusCodes.Status409Conflict,
            Instance = context.Request.Path,
            Type = "https://tools.ietf.org/html/rfc7231#section-6.5.8"
        };
    }

    /// <summary>
    /// Creates ProblemDetails for unhandled exceptions.
    /// Maps to HTTP 500 Internal Server Error.
    /// </summary>
    private ProblemDetails CreateInternalServerErrorProblemDetails(HttpContext context, Exception exception)
    {
        // In production, don't expose internal exception details
        var isDevelopment = context.RequestServices
            .GetService<IHostEnvironment>()?.IsDevelopment() ?? false;

        return new ProblemDetails
        {
            Title = "An error occurred while processing your request",
            Detail = isDevelopment ? exception.Message : "An internal server error occurred. Please contact support.",
            Status = StatusCodes.Status500InternalServerError,
            Instance = context.Request.Path,
            Type = "https://tools.ietf.org/html/rfc7231#section-6.6.1"
        };
    }
}
