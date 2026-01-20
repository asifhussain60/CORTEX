using Microsoft.AspNetCore.Http;
using System;
using System.Threading.Tasks;

namespace BadMonolith.Middleware
{
    /// <summary>
    /// Error handling middleware with intentional anti-patterns.
    /// 
    /// Anti-patterns demonstrated:
    /// ❌ Generic error responses (no useful information)
    /// ❌ No structured logging
    /// ❌ Stack traces exposed to clients
    /// ❌ No correlation ID tracking
    /// ❌ Exception details leaked in responses
    /// ❌ No graceful degradation
    /// </summary>
    public class ErrorHandlingMiddleware
    {
        private readonly RequestDelegate _next;

        public ErrorHandlingMiddleware(RequestDelegate next)
        {
            _next = next;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                // ❌ FLAW: No correlation ID generation or tracking
                // ❌ FLAW: No request logging
                
                await _next(context);
            }
            catch (Exception ex)
            {
                // ❌ FLAW: No structured logging (Serilog)
                // ❌ FLAW: Exception details not captured
                
                await HandleExceptionAsync(context, ex);
            }
        }

        // ❌ FLAW: Generic error response
        private static Task HandleExceptionAsync(HttpContext context, Exception exception)
        {
            // ❌ FLAW: Stack trace exposed to client
            var response = context.Response;
            response.ContentType = "application/json";

            // ❌ FLAW: All errors return 500 (no distinction)
            // ❌ FLAW: Generic message doesn't help debugging
            response.StatusCode = StatusCodes.Status500InternalServerError;

            // ❌ FLAW: Exception details exposed directly
            var errorResponse = new
            {
                message = "An error occurred",
                // ❌ FLAW: Exposing exception type to client
                error = exception.GetType().Name,
                // ❌ FLAW: Stack trace visible to attacker
                details = exception.Message,
                stackTrace = exception.StackTrace
            };

            // ❌ FLAW: No correlation ID for tracing
            // ❌ FLAW: No way to correlate with logs

            return response.WriteAsJsonAsync(errorResponse);
        }
    }
}
