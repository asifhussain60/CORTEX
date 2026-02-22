// ✅ SMELL-18 FIXED: RFC 7807 ProblemDetails middleware — no raw stack traces exposed
// ✅ SMELL-11 FIXED: Structured logging via ILogger<T>

using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Api.Middleware;

/// <summary>
/// Global exception handler that returns RFC 7807 ProblemDetails responses.
/// No stack traces are ever sent to clients (SMELL-18 fix).
/// </summary>
public sealed class GlobalExceptionHandler : IExceptionHandler
{
    private readonly ILogger<GlobalExceptionHandler> _logger;

    public GlobalExceptionHandler(ILogger<GlobalExceptionHandler> logger)
    {
        _logger = logger;
    }

    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext, Exception exception, CancellationToken cancellationToken)
    {
        // ✅ SMELL-18 FIXED: Full exception logged server-side only
        _logger.LogError(exception, "Unhandled exception: {Message}", exception.Message);

        // ✅ SMELL-18 FIXED: Generic 500 returned to client — NO stack trace, NO inner exception
        httpContext.Response.StatusCode = StatusCodes.Status500InternalServerError;
        await httpContext.Response.WriteAsJsonAsync(new ProblemDetails
        {
            Status = StatusCodes.Status500InternalServerError,
            Title = "An unexpected error occurred.",
            Detail = "Please contact support if this problem persists.",
            Instance = httpContext.Request.Path
        }, cancellationToken);

        return true;
    }
}
