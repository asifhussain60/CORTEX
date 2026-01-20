using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;
using System.Reflection;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Validation;

/// <summary>
/// Validates type safety constraints (decimal precision, string lengths, date formats).
/// Part of Phase 5a - Data Layer Transition & Schema Validation.
/// Ensures mock data values fit within database column constraints.
/// </summary>
public class TypeSafetyValidator
{
    /// <summary>
    /// Validates that decimal values in mock data fit database DECIMAL(precision, scale) constraints.
    /// </summary>
    public TypeSafetyValidationResult ValidateDecimalPrecision(
        decimal mockValue,
        IProperty dbProperty,
        string propertyName)
    {
        var result = new TypeSafetyValidationResult
        {
            PropertyName = propertyName,
            IsValid = true
        };

        var precision = dbProperty.GetPrecision();
        var scale = dbProperty.GetScale();

        if (precision == null || scale == null)
        {
            result.Warnings.Add($"Database precision/scale not defined for {propertyName}");
            return result;
        }

        // Calculate max value for DECIMAL(precision, scale)
        var maxValue = (decimal)Math.Pow(10, precision.Value - scale.Value) - (decimal)Math.Pow(10, -scale.Value);

        if (Math.Abs(mockValue) >= maxValue)
        {
            result.IsValid = false;
            result.Errors.Add($"Value {mockValue} exceeds DECIMAL({precision},{scale}) max: {maxValue}");
        }

        // Validate scale (decimal places)
        var decimalPlaces = GetDecimalPlaces(mockValue);
        if (decimalPlaces > scale.Value)
        {
            result.IsValid = false;
            result.Errors.Add($"Value {mockValue} has {decimalPlaces} decimal places, exceeds scale {scale.Value}");
        }

        return result;
    }

    /// <summary>
    /// Validates that string values in mock data fit database VARCHAR(n) or NVARCHAR(n) constraints.
    /// </summary>
    public TypeSafetyValidationResult ValidateStringLength(
        string? mockValue,
        IProperty dbProperty,
        string propertyName)
    {
        var result = new TypeSafetyValidationResult
        {
            PropertyName = propertyName,
            IsValid = true
        };

        if (mockValue == null)
            return result; // Null values handled by nullability checks

        var maxLength = dbProperty.GetMaxLength();

        if (maxLength == null)
        {
            result.Warnings.Add($"Database max length not defined for {propertyName}");
            return result;
        }

        if (mockValue.Length > maxLength.Value)
        {
            result.IsValid = false;
            result.Errors.Add($"String length {mockValue.Length} exceeds max {maxLength.Value} for {propertyName}");
            result.Errors.Add($"Value: '{mockValue.Substring(0, Math.Min(50, mockValue.Length))}...'");
        }

        return result;
    }

    /// <summary>
    /// Validates that DateTime values in mock data are within SQL Server date range.
    /// SQL Server datetime: 1753-01-01 to 9999-12-31
    /// SQL Server datetime2: 0001-01-01 to 9999-12-31
    /// </summary>
    public TypeSafetyValidationResult ValidateDateTimeRange(
        DateTime mockValue,
        IProperty dbProperty,
        string propertyName)
    {
        var result = new TypeSafetyValidationResult
        {
            PropertyName = propertyName,
            IsValid = true
        };

        var columnType = dbProperty.GetColumnType();

        if (columnType?.ToLowerInvariant().Contains("datetime2") == true)
        {
            // datetime2 range: 0001-01-01 to 9999-12-31
            if (mockValue < new DateTime(1, 1, 1) || mockValue > new DateTime(9999, 12, 31))
            {
                result.IsValid = false;
                result.Errors.Add($"DateTime {mockValue} outside datetime2 range (0001-01-01 to 9999-12-31)");
            }
        }
        else
        {
            // datetime range: 1753-01-01 to 9999-12-31
            if (mockValue < new DateTime(1753, 1, 1) || mockValue > new DateTime(9999, 12, 31))
            {
                result.IsValid = false;
                result.Errors.Add($"DateTime {mockValue} outside datetime range (1753-01-01 to 9999-12-31)");
            }
        }

        return result;
    }

    /// <summary>
    /// Gets the number of decimal places in a decimal value.
    /// </summary>
    private int GetDecimalPlaces(decimal value)
    {
        var bits = decimal.GetBits(Math.Abs(value));
        var scale = (bits[3] >> 16) & 0xFF;
        return scale;
    }
}

/// <summary>
/// Result of type safety validation for a specific property.
/// </summary>
public class TypeSafetyValidationResult
{
    public string PropertyName { get; set; } = string.Empty;
    public bool IsValid { get; set; }
    public List<string> Errors { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
}
