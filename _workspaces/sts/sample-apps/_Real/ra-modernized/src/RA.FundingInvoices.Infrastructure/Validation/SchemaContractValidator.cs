using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;
using System.Reflection;

namespace RA.FundingInvoices.Infrastructure.Validation;

/// <summary>
/// Validates that mock data entities match database schema exactly.
/// Part of Phase 5a - Data Layer Transition & Schema Validation.
/// Ensures zero runtime UI breaks when swapping from Mock to EF Core in production.
/// </summary>
public class SchemaContractValidator
{
    /// <summary>
    /// Validates that a mock entity instance matches the database schema definition.
    /// Checks properties, types, nullability to ensure 100% compatibility.
    /// </summary>
    /// <param name="mockInstance">Mock entity instance to validate</param>
    /// <param name="dbEntityType">EF Core entity type metadata from database model</param>
    /// <returns>Validation result with detailed mismatch information</returns>
    public SchemaContractValidationResult ValidateContract(object mockInstance, IEntityType dbEntityType)
    {
        var result = new SchemaContractValidationResult
        {
            EntityTypeName = dbEntityType.ClrType.Name
        };

        try
        {
            // Get all database properties
            var dbProperties = dbEntityType.GetProperties()
                .Where(p => !p.IsShadowProperty()) // Exclude shadow properties
                .ToDictionary(p => p.Name, p => p);

            // Get all mock instance properties
            var mockProperties = mockInstance.GetType()
                .GetProperties(BindingFlags.Public | BindingFlags.Instance)
                .ToDictionary(p => p.Name, p => p);

            // Check for missing properties (in DB but not in Mock)
            var missingProps = dbProperties.Keys.Except(mockProperties.Keys).ToList();
            result.MissingProperties.AddRange(missingProps);

            // Check for extra properties (in Mock but not in DB)
            var extraProps = mockProperties.Keys.Except(dbProperties.Keys).ToList();
            result.ExtraProperties.AddRange(extraProps);

            // Validate type and nullability for common properties
            foreach (var propName in dbProperties.Keys.Intersect(mockProperties.Keys))
            {
                var dbProp = dbProperties[propName];
                var mockProp = mockProperties[propName];

                // Type validation
                var dbType = dbProp.ClrType;
                var mockType = mockProp.PropertyType;

                if (!AreTypesCompatible(mockType, dbType))
                {
                    result.TypeMismatches.Add(new PropertyTypeMismatch
                    {
                        PropertyName = propName,
                        MockType = mockType.Name,
                        DbType = dbType.Name,
                        Detail = $"Mock type '{mockType.FullName}' incompatible with DB type '{dbType.FullName}'"
                    });
                }

                // Nullability validation
                var dbIsNullable = dbProp.IsNullable;
                var mockIsNullable = IsNullableType(mockType);

                if (mockIsNullable != dbIsNullable)
                {
                    result.NullabilityMismatches.Add(new PropertyNullabilityMismatch
                    {
                        PropertyName = propName,
                        MockIsNullable = mockIsNullable,
                        DbIsNullable = dbIsNullable,
                        Detail = $"Mock nullable: {mockIsNullable}, DB nullable: {dbIsNullable}"
                    });
                }
            }

            // Set validation status
            result.IsValid = !result.MissingProperties.Any() &&
                            !result.ExtraProperties.Any() &&
                            !result.TypeMismatches.Any() &&
                            !result.NullabilityMismatches.Any();
        }
        catch (Exception ex)
        {
            result.Errors.Add($"Validation failed: {ex.Message}");
            result.IsValid = false;
        }

        return result;
    }

    /// <summary>
    /// Checks if mock type is compatible with database type.
    /// Handles nullable value types, reference types, and type equivalence.
    /// </summary>
    private bool AreTypesCompatible(Type mockType, Type dbType)
    {
        // Exact match
        if (mockType == dbType)
            return true;

        // Handle nullable value types (e.g., int? vs int)
        var mockUnderlyingType = Nullable.GetUnderlyingType(mockType) ?? mockType;
        var dbUnderlyingType = Nullable.GetUnderlyingType(dbType) ?? dbType;

        return mockUnderlyingType == dbUnderlyingType;
    }

    /// <summary>
    /// Determines if a type is nullable (reference type or Nullable&lt;T&gt;).
    /// </summary>
    private bool IsNullableType(Type type)
    {
        // Value type nullable check (e.g., int?)
        if (Nullable.GetUnderlyingType(type) != null)
            return true;

        // Reference type nullable check (C# 8.0+ nullable reference types)
        if (!type.IsValueType)
            return true; // Reference types are nullable by default

        return false;
    }
}
