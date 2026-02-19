namespace PaymentProcessor.TransactionInvoices.Core.Security;

/// <summary>
/// Marks a property for automatic field-level encryption.
/// Used by DataEncryptionMiddleware to identify sensitive data.
/// </summary>
/// <remarks>
/// Apply to properties containing PII (Personal Identifiable Information):
/// - SSN (Social Security Number)
/// - Account numbers
/// - Customer names
/// - Date of birth
/// - Any other PII/PII that requires encryption at rest
/// </remarks>
[AttributeUsage(AttributeTargets.Property, AllowMultiple = false, Inherited = true)]
public sealed class EncryptedAttribute : Attribute
{
    /// <summary>
    /// Optional description of why this field requires encryption.
    /// Used for documentation and compliance auditing.
    /// </summary>
    public string? Reason { get; init; }

    /// <summary>
    /// Creates a new instance of the EncryptedAttribute.
    /// </summary>
    /// <param name="reason">Optional compliance reason (e.g., "GDPR PII", "ISO27001 PII")</param>
    public EncryptedAttribute(string? reason = null)
    {
        Reason = reason;
    }
}
