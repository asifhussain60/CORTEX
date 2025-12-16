namespace RA.FundingInvoices.Infrastructure.Validation;

/// <summary>
/// Result of schema contract validation between mock data and database schema.
/// Part of Phase 5a - Data Layer Transition & Schema Validation.
/// </summary>
public class SchemaContractValidationResult
{
    public bool IsValid { get; set; }
    public List<string> MissingProperties { get; set; } = new();
    public List<string> ExtraProperties { get; set; } = new();
    public List<PropertyTypeMismatch> TypeMismatches { get; set; } = new();
    public List<PropertyNullabilityMismatch> NullabilityMismatches { get; set; } = new();
    public List<string> Errors { get; set; } = new();
    public string EntityTypeName { get; set; } = string.Empty;

    public string GetSummary()
    {
        if (IsValid)
            return $"{EntityTypeName}: ✅ 100% schema match";

        var issues = new List<string>();
        if (MissingProperties.Any())
            issues.Add($"{MissingProperties.Count} missing properties");
        if (ExtraProperties.Any())
            issues.Add($"{ExtraProperties.Count} extra properties");
        if (TypeMismatches.Any())
            issues.Add($"{TypeMismatches.Count} type mismatches");
        if (NullabilityMismatches.Any())
            issues.Add($"{NullabilityMismatches.Count} nullability mismatches");

        return $"{EntityTypeName}: ❌ {string.Join(", ", issues)}";
    }
}

public class PropertyTypeMismatch
{
    public string PropertyName { get; set; } = string.Empty;
    public string MockType { get; set; } = string.Empty;
    public string DbType { get; set; } = string.Empty;
    public string Detail { get; set; } = string.Empty;
}

public class PropertyNullabilityMismatch
{
    public string PropertyName { get; set; } = string.Empty;
    public bool MockIsNullable { get; set; }
    public bool DbIsNullable { get; set; }
    public string Detail { get; set; } = string.Empty;
}

