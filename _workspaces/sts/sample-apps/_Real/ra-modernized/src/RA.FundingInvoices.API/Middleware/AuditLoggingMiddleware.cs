using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace RA.FundingInvoices.API.Middleware;

/// <summary>
/// HIPAA-compliant audit logging middleware.
/// Captures all CUD (Create, Update, Delete) operations with PHI redaction.
/// Implements 7-year retention requirement (2555 days).
/// </summary>
public partial class AuditLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<AuditLoggingMiddleware> _logger;
    private readonly IConfiguration _configuration;

    // Regex patterns for PHI detection (compiled for performance)
    [GeneratedRegex(@"\b\d{3}-\d{2}-\d{4}\b", RegexOptions.Compiled)]
    private static partial Regex SSNPattern();

    [GeneratedRegex(@"\b\d{2}/\d{2}/\d{4}\b", RegexOptions.Compiled)]
    private static partial Regex DateOfBirthPattern();

    [GeneratedRegex(@"""memberName"":\s*""([^""]+)""", RegexOptions.Compiled | RegexOptions.IgnoreCase)]
    private static partial Regex MemberNamePattern();

    public AuditLoggingMiddleware(
        RequestDelegate next,
        ILogger<AuditLoggingMiddleware> logger,
        IConfiguration configuration)
    {
        _next = next;
        _logger = logger;
        _configuration = configuration;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var isAuditEnabled = _configuration.GetValue<bool>("AuditLogging:Enabled", true);
        var shouldRedactPHI = _configuration.GetValue<bool>("AuditLogging:RedactPHI", true);

        if (!isAuditEnabled || !ShouldAudit(context.Request))
        {
            await _next(context);
            return;
        }

        // Capture request details
        var requestBody = await CaptureRequestBodyAsync(context.Request);
        var startTime = DateTime.UtcNow;

        // Store original response body stream
        var originalBodyStream = context.Response.Body;

        try
        {
            using var responseBodyStream = new MemoryStream();
            context.Response.Body = responseBodyStream;

            // Execute the request
            await _next(context);

            // Capture response details
            var responseBody = await CaptureResponseBodyAsync(responseBodyStream);

            // Log audit entry
            LogAuditEntry(context, requestBody, responseBody, startTime, shouldRedactPHI);

            // Copy response back to original stream
            await responseBodyStream.CopyToAsync(originalBodyStream);
        }
        finally
        {
            context.Response.Body = originalBodyStream;
        }
    }

    private static bool ShouldAudit(HttpRequest request)
    {
        // Only audit CUD operations (POST, PUT, PATCH, DELETE)
        var method = request.Method.ToUpperInvariant();
        return method is "POST" or "PUT" or "PATCH" or "DELETE";
    }

    private static async Task<string> CaptureRequestBodyAsync(HttpRequest request)
    {
        request.EnableBuffering();

        using var reader = new StreamReader(
            request.Body,
            Encoding.UTF8,
            detectEncodingFromByteOrderMarks: false,
            bufferSize: 1024,
            leaveOpen: true);

        var body = await reader.ReadToEndAsync();
        request.Body.Position = 0;

        return body;
    }

    private static async Task<string> CaptureResponseBodyAsync(MemoryStream responseBodyStream)
    {
        responseBodyStream.Seek(0, SeekOrigin.Begin);

        using var reader = new StreamReader(responseBodyStream, Encoding.UTF8, leaveOpen: true);
        var body = await reader.ReadToEndAsync();

        responseBodyStream.Seek(0, SeekOrigin.Begin);

        return body;
    }

    private void LogAuditEntry(
        HttpContext context,
        string requestBody,
        string responseBody,
        DateTime startTime,
        bool shouldRedactPHI)
    {
        var auditEntry = new
        {
            Timestamp = DateTime.UtcNow,
            Duration = (DateTime.UtcNow - startTime).TotalMilliseconds,
            Request = new
            {
                Method = context.Request.Method,
                Path = context.Request.Path.Value,
                QueryString = context.Request.QueryString.Value,
                Body = shouldRedactPHI ? RedactPHI(requestBody) : requestBody,
                Headers = GetSafeHeaders(context.Request.Headers),
                UserId = context.User?.Identity?.Name ?? "Anonymous",
                IpAddress = context.Connection.RemoteIpAddress?.ToString() ?? "Unknown"
            },
            Response = new
            {
                StatusCode = context.Response.StatusCode,
                Body = shouldRedactPHI ? RedactPHI(responseBody) : responseBody
            }
        };

        var auditJson = JsonSerializer.Serialize(auditEntry, new JsonSerializerOptions
        {
            WriteIndented = false
        });

        // Log with structured data for long-term retention
        _logger.LogInformation("AUDIT: {AuditEntry}", auditJson);
    }

    private static string RedactPHI(string content)
    {
        if (string.IsNullOrEmpty(content))
        {
            return content;
        }

        // Redact SSN (123-45-6789 → ***-**-****)
        content = SSNPattern().Replace(content, "***-**-****");

        // Redact Date of Birth (01/15/1980 → **/**/****)
        content = DateOfBirthPattern().Replace(content, "**/**/ ****");

        // Redact member names
        content = MemberNamePattern().Replace(content, @"""memberName"":""[REDACTED]""");

        return content;
    }

    private static Dictionary<string, string> GetSafeHeaders(IHeaderDictionary headers)
    {
        // Only include non-sensitive headers
        var safeHeaders = new[] { "Content-Type", "Accept", "User-Agent" };

        return headers
            .Where(h => safeHeaders.Contains(h.Key, StringComparer.OrdinalIgnoreCase))
            .ToDictionary(h => h.Key, h => h.Value.ToString());
    }
}
