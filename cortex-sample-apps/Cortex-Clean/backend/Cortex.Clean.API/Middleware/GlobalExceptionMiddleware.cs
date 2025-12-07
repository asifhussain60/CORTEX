using Cortex.Clean.Domain.Exceptions;
using FluentValidation;
using System.Net;
using System.Text.Json;

namespace Cortex.Clean.API.Middleware;

public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;

    public GlobalExceptionMiddleware(RequestDelegate next, ILogger<GlobalExceptionMiddleware> logger)
    {
        _next = next ?? throw new ArgumentNullException(nameof(next));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var response = context.Response;
        response.ContentType = "application/json";

        HttpStatusCode statusCode;
        string message;
        List<object> errors;

        switch (exception)
        {
            case ValidationException validationEx:
                statusCode = HttpStatusCode.BadRequest;
                message = "Validation failed.";
                errors = validationEx.Errors.Select(e => new { e.PropertyName, e.ErrorMessage }).Cast<object>().ToList();
                break;

            case InvalidTaskException invalidTaskEx:
                statusCode = HttpStatusCode.BadRequest;
                message = invalidTaskEx.Message;
                errors = new List<object>();
                break;

            case TaskNotFoundException notFoundEx:
                statusCode = HttpStatusCode.NotFound;
                message = notFoundEx.Message;
                errors = new List<object>();
                break;

            default:
                statusCode = HttpStatusCode.InternalServerError;
                message = "An unexpected error occurred. Please try again later.";
                errors = new List<object>();
                break;
        }

        _logger.LogError(
            exception,
            "Exception occurred: {Message} | StatusCode: {StatusCode}",
            exception.Message,
            statusCode);

        response.StatusCode = (int)statusCode;

        var result = JsonSerializer.Serialize(new
        {
            statusCode = (int)statusCode,
            message,
            errors = errors.Any() ? errors : null
        }, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        await response.WriteAsync(result);
    }
}

public static class GlobalExceptionMiddlewareExtensions
{
    public static IApplicationBuilder UseGlobalExceptionHandler(this IApplicationBuilder app)
    {
        return app.UseMiddleware<GlobalExceptionMiddleware>();
    }
}
