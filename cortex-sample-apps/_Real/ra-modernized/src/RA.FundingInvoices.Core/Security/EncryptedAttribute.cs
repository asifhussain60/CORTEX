namespace RA.FundingInvoices.Core.Security;

/// <summary>
/// Marks a property for automatic field-level encryption.
/// Used by DataEncryptionMiddleware to identify sensitive data.
/// </summary>
/// <remarks>
/// Apply to properties containing PHI (Protected Health Information):
/// - SSN (Social Security Number)
/// - Account numbers
/// - Member names
/// - Date of birth
/// - Any other PII/PHI that requires encryption at rest
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
    /// <param name="reason">Optional compliance reason (e.g., "HIPAA PHI", "SOC2 PII")</param>
    public EncryptedAttribute(string? reason = null)
    {
        Reason = reason;
    }
}
