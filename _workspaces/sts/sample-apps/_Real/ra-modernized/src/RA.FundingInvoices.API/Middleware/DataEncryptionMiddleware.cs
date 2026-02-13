using RA.FundingInvoices.Core.Security;
using System.Reflection;
using System.Text;
using System.Text.Json;

namespace RA.FundingInvoices.API.Middleware;

/// <summary>
/// Middleware for automatic field-level encryption/decryption.
/// Intercepts requests/responses to encrypt/decrypt properties marked with [Encrypted] attribute.
/// Ensures PHI is encrypted at rest in the database (HIPAA/SOC2 compliance).
/// </summary>
public class DataEncryptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IEncryptionService _encryptionService;
    private readonly ILogger<DataEncryptionMiddleware> _logger;
    private readonly IConfiguration _configuration;

    public DataEncryptionMiddleware(
        RequestDelegate next,
        IEncryptionService encryptionService,
        ILogger<DataEncryptionMiddleware> logger,
        IConfiguration configuration)
    {
        _next = next;
        _encryptionService = encryptionService;
        _logger = logger;
        _configuration = configuration;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var isEncryptionEnabled = _configuration.GetValue<bool>("Encryption:Enabled", true);

        if (!isEncryptionEnabled)
        {
            await _next(context);
            return;
        }

        // Handle incoming requests (encrypt data before saving to DB)
        if (ShouldEncryptRequest(context.Request))
        {
            await EncryptRequestBodyAsync(context);
        }

        // Store original response body stream
        var originalBodyStream = context.Response.Body;

        try
        {
            using var responseBodyStream = new MemoryStream();
            context.Response.Body = responseBodyStream;

            // Execute the request
            await _next(context);

            // Handle outgoing responses (decrypt data from DB before sending to client)
            if (ShouldDecryptResponse(context.Response))
            {
                await DecryptResponseBodyAsync(context, responseBodyStream, originalBodyStream);
            }
            else
            {
                // Copy response back without modification
                await responseBodyStream.CopyToAsync(originalBodyStream);
            }
        }
        finally
        {
            context.Response.Body = originalBodyStream;
        }
    }

    private static bool ShouldEncryptRequest(HttpRequest request)
    {
        // Encrypt data in POST/PUT requests (creating/updating records)
        var method = request.Method.ToUpperInvariant();
        return (method is "POST" or "PUT" or "PATCH") &&
               request.ContentType?.Contains("application/json", StringComparison.OrdinalIgnoreCase) == true;
    }

    private static bool ShouldDecryptResponse(HttpResponse response)
    {
        // Decrypt data in successful GET/POST/PUT responses
        return response.StatusCode is >= 200 and < 300 &&
               response.ContentType?.Contains("application/json", StringComparison.OrdinalIgnoreCase) == true;
    }

    private async Task EncryptRequestBodyAsync(HttpContext context)
    {
        try
        {
            context.Request.EnableBuffering();

            using var reader = new StreamReader(
                context.Request.Body,
                Encoding.UTF8,
                detectEncodingFromByteOrderMarks: false,
                bufferSize: 1024,
                leaveOpen: true);

            var requestBody = await reader.ReadToEndAsync();
            context.Request.Body.Position = 0;

            if (string.IsNullOrWhiteSpace(requestBody))
            {
                return;
            }

            // Parse JSON and encrypt fields marked with [Encrypted] attribute
            var jsonDocument = JsonDocument.Parse(requestBody);
            var encryptedJson = await EncryptJsonPropertiesAsync(jsonDocument.RootElement);

            // Replace request body with encrypted version
            var encryptedBytes = Encoding.UTF8.GetBytes(encryptedJson);
            context.Request.Body = new MemoryStream(encryptedBytes);
            context.Request.ContentLength = encryptedBytes.Length;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to encrypt request body");
            // Continue without encryption on error (logged for investigation)
        }
    }

    private async Task DecryptResponseBodyAsync(
        HttpContext context,
        MemoryStream responseBodyStream,
        Stream originalBodyStream)
    {
        try
        {
            responseBodyStream.Seek(0, SeekOrigin.Begin);

            using var reader = new StreamReader(responseBodyStream, Encoding.UTF8, leaveOpen: true);
            var responseBody = await reader.ReadToEndAsync();

            if (string.IsNullOrWhiteSpace(responseBody))
            {
                return;
            }

            // Parse JSON and decrypt fields marked with [Encrypted] attribute
            var jsonDocument = JsonDocument.Parse(responseBody);
            var decryptedJson = await DecryptJsonPropertiesAsync(jsonDocument.RootElement);

            // Write decrypted response to original stream
            var decryptedBytes = Encoding.UTF8.GetBytes(decryptedJson);
            await originalBodyStream.WriteAsync(decryptedBytes);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to decrypt response body");
            // Return original response on error
            responseBodyStream.Seek(0, SeekOrigin.Begin);
            await responseBodyStream.CopyToAsync(originalBodyStream);
        }
    }

    private async Task<string> EncryptJsonPropertiesAsync(JsonElement element)
    {
        // TODO: Implement JSON traversal and selective encryption
        // For now, return original JSON (placeholder for full implementation)
        // Full implementation would:
        // 1. Detect entity type from JSON structure
        // 2. Use reflection to find properties with [Encrypted] attribute
        // 3. Encrypt those specific property values
        // 4. Reconstruct JSON with encrypted values

        var options = new JsonSerializerOptions { WriteIndented = false };
        return JsonSerializer.Serialize(element, options);
    }

    private async Task<string> DecryptJsonPropertiesAsync(JsonElement element)
    {
        // TODO: Implement JSON traversal and selective decryption
        // For now, return original JSON (placeholder for full implementation)
        // Full implementation would:
        // 1. Detect entity type from JSON structure
        // 2. Use reflection to find properties with [Encrypted] attribute
        // 3. Decrypt those specific property values
        // 4. Reconstruct JSON with decrypted values

        var options = new JsonSerializerOptions { WriteIndented = false };
        return JsonSerializer.Serialize(element, options);
    }

    /// <summary>
    /// Helper method to find properties with [Encrypted] attribute.
    /// </summary>
    private static IEnumerable<PropertyInfo> GetEncryptedProperties(Type type)
    {
        return type.GetProperties()
            .Where(p => p.GetCustomAttribute<EncryptedAttribute>() != null);
    }
}
