using System.Text.Json;

namespace PaymentProcessor.TransactionInvoices.ContractTests.Engine;

/// <summary>
/// Validates WCF XML schemas against REST JSON schemas.
/// Ensures field-level compatibility for contract verification.
/// </summary>
public class SchemaValidator
{
    private readonly ContractMappingConfig _mappingConfig;

    public SchemaValidator(ContractMappingConfig mappingConfig)
    {
        _mappingConfig = mappingConfig;
    }

    public ValidationResult ValidateResponseSchema(string wcfTransaction, string wcfResponse, string restResponse)
    {
        var result = new ValidationResult { IsValid = true };

        var mapping = _mappingConfig.GetMapping(wcfTransaction);
        if (mapping == null)
        {
            result.IsValid = false;
            result.Discrepancies.Add(new Discrepancy
            {
                Field = "Mapping",
                WcfValue = wcfTransaction,
                RestValue = "Not found",
                Severity = DiscrepancySeverity.Critical
            });
            return result;
        }

        // Parse responses
        var wcfData = ParseWcfResponse(wcfResponse);
        var restData = JsonSerializer.Deserialize<JsonElement>(restResponse);

        // Validate each field mapping
        foreach (var fieldMapping in mapping.ResponseMapping.FieldMappings)
        {
            if (!ValidateField(fieldMapping, wcfData, restData, result))
            {
                result.IsValid = false;
            }
        }

        // Validate type compatibility
        ValidateTypes(mapping.ResponseMapping.FieldMappings, wcfData, restData, result);

        // Validate nullability
        ValidateNullability(mapping.ResponseMapping.FieldMappings, wcfData, restData, result);

        return result;
    }

    private bool ValidateField(FieldMapping fieldMapping, Dictionary<string, object> wcfData, JsonElement restData, ValidationResult result)
    {
        // Check if WCF field exists
        if (!wcfData.ContainsKey(fieldMapping.WcfField))
        {
            if (fieldMapping.Required)
            {
                result.Discrepancies.Add(new Discrepancy
                {
                    Field = fieldMapping.WcfField,
                    WcfValue = "Missing",
                    RestValue = "N/A",
                    Severity = DiscrepancySeverity.Critical,
                    Description = $"Required WCF field '{fieldMapping.WcfField}' is missing"
                });
                return false;
            }
            return true;
        }

        // Check if REST field exists
        if (!restData.TryGetProperty(fieldMapping.RestField, out var restValue))
        {
            if (fieldMapping.Required)
            {
                result.Discrepancies.Add(new Discrepancy
                {
                    Field = fieldMapping.RestField,
                    WcfValue = "N/A",
                    RestValue = "Missing",
                    Severity = DiscrepancySeverity.Critical,
                    Description = $"Required REST field '{fieldMapping.RestField}' is missing"
                });
                return false;
            }
            return true;
        }

        // Validate value equality (with type conversion)
        var wcfValue = wcfData[fieldMapping.WcfField];
        var isMatch = CompareValues(wcfValue, restValue, fieldMapping.Type);

        if (!isMatch)
        {
            result.Discrepancies.Add(new Discrepancy
            {
                Field = fieldMapping.RestField,
                WcfValue = wcfValue?.ToString() ?? "null",
                RestValue = restValue.ToString(),
                Severity = DiscrepancySeverity.High,
                Description = $"Value mismatch for field '{fieldMapping.RestField}'"
            });
            return false;
        }

        return true;
    }

    private bool CompareValues(object? wcfValue, JsonElement restValue, string type)
    {
        if (wcfValue == null && restValue.ValueKind == JsonValueKind.Null)
            return true;

        if (wcfValue == null || restValue.ValueKind == JsonValueKind.Null)
            return false;

        return type.ToLower() switch
        {
            "string" => wcfValue.ToString() == restValue.GetString(),
            "decimal" or "number" => CompareDecimals(wcfValue, restValue),
            "int" or "integer" => Convert.ToInt32(wcfValue) == restValue.GetInt32(),
            "boolean" or "bool" => Convert.ToBoolean(wcfValue) == restValue.GetBoolean(),
            "datetime" => CompareDateTimes(wcfValue, restValue),
            _ => wcfValue.ToString() == restValue.ToString()
        };
    }

    private bool CompareDecimals(object wcfValue, JsonElement restValue)
    {
        var wcfDecimal = Convert.ToDecimal(wcfValue);
        var restDecimal = restValue.GetDecimal();
        return Math.Abs(wcfDecimal - restDecimal) < 0.001m; // Allow small floating point differences
    }

    private bool CompareDateTimes(object wcfValue, JsonElement restValue)
    {
        var wcfDateTime = Convert.ToDateTime(wcfValue);
        var restDateTime = DateTime.Parse(restValue.GetString()!);
        return (wcfDateTime - restDateTime).TotalSeconds < 1; // Allow 1 second difference
    }

    private void ValidateTypes(List<FieldMapping> fieldMappings, Dictionary<string, object> wcfData, JsonElement restData, ValidationResult result)
    {
        foreach (var mapping in fieldMappings)
        {
            if (!wcfData.ContainsKey(mapping.WcfField)) continue;
            if (!restData.TryGetProperty(mapping.RestField, out var restValue)) continue;

            var wcfType = wcfData[mapping.WcfField]?.GetType().Name ?? "null";
            var restType = GetJsonValueType(restValue);

            if (!AreTypesCompatible(mapping.Type, wcfType, restType))
            {
                result.IsValid = false;
                result.Discrepancies.Add(new Discrepancy
                {
                    Field = mapping.RestField,
                    WcfValue = $"{mapping.Type} ({wcfType})",
                    RestValue = restType,
                    Severity = DiscrepancySeverity.High,
                    Description = $"Type mismatch: Expected {mapping.Type}, got {restType}"
                });
            }
        }
    }

    private void ValidateNullability(List<FieldMapping> fieldMappings, Dictionary<string, object> wcfData, JsonElement restData, ValidationResult result)
    {
        foreach (var mapping in fieldMappings)
        {
            var wcfIsNull = !wcfData.ContainsKey(mapping.WcfField) || wcfData[mapping.WcfField] == null;
            var restIsNull = !restData.TryGetProperty(mapping.RestField, out var restValue) || 
                             restValue.ValueKind == JsonValueKind.Null;

            if (wcfIsNull != restIsNull)
            {
                result.IsValid = false;
                result.Discrepancies.Add(new Discrepancy
                {
                    Field = mapping.RestField,
                    WcfValue = wcfIsNull ? "null" : "not null",
                    RestValue = restIsNull ? "null" : "not null",
                    Severity = DiscrepancySeverity.Medium,
                    Description = "Nullability mismatch"
                });
            }
        }
    }

    private string GetJsonValueType(JsonElement element)
    {
        return element.ValueKind switch
        {
            JsonValueKind.String => "string",
            JsonValueKind.Number => "number",
            JsonValueKind.True or JsonValueKind.False => "boolean",
            JsonValueKind.Null => "null",
            JsonValueKind.Array => "array",
            JsonValueKind.Object => "object",
            _ => "unknown"
        };
    }

    private bool AreTypesCompatible(string schemaType, string wcfType, string restType)
    {
        var compatibilityMap = new Dictionary<string, List<string>>
        {
            { "string", new List<string> { "String", "string" } },
            { "decimal", new List<string> { "Decimal", "number" } },
            { "number", new List<string> { "Decimal", "Double", "Single", "number" } },
            { "int", new List<string> { "Int32", "Int64", "number" } },
            { "integer", new List<string> { "Int32", "Int64", "number" } },
            { "boolean", new List<string> { "Boolean", "boolean" } },
            { "bool", new List<string> { "Boolean", "boolean" } },
            { "datetime", new List<string> { "DateTime", "string" } }
        };

        var key = schemaType.ToLower();
        if (!compatibilityMap.ContainsKey(key))
            return false;

        return compatibilityMap[key].Contains(wcfType) && compatibilityMap[key].Contains(restType);
    }

    private Dictionary<string, object> ParseWcfResponse(string wcfResponse)
    {
        // This is a simplified parser - in reality, you'd parse actual WCF XML
        // For now, assume WCF responses are converted to key-value pairs
        // In production, use XDocument or XmlSerializer
        
        var result = new Dictionary<string, object>();
        
        try
        {
            // Placeholder: Parse WCF XML to dictionary
            // In reality, this would use XDocument.Parse() and extract values
            
            // For testing, assume wcfResponse is JSON (mock WCF service returns JSON)
            var json = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(wcfResponse);
            if (json != null)
            {
                foreach (var kvp in json)
                {
                    result[kvp.Key] = kvp.Value.ValueKind switch
                    {
                        JsonValueKind.String => kvp.Value.GetString()!,
                        JsonValueKind.Number => kvp.Value.GetDecimal(),
                        JsonValueKind.True or JsonValueKind.False => kvp.Value.GetBoolean(),
                        _ => kvp.Value.ToString()
                    };
                }
            }
        }
        catch
        {
            // Parse error - return empty dictionary
        }

        return result;
    }
}

public class ContractMappingConfig
{
    private readonly Dictionary<string, ContractMapping> _mappings = new();

    public void LoadMappings(string mappingJsonPath)
    {
        var json = File.ReadAllText(mappingJsonPath);
        var config = JsonSerializer.Deserialize<ContractMappingDocument>(json);

        if (config?.Mappings != null)
        {
            foreach (var mapping in config.Mappings)
            {
                _mappings[mapping.WcfTransaction] = mapping;
            }
        }
    }

    public ContractMapping? GetMapping(string wcfTransaction)
    {
        return _mappings.ContainsKey(wcfTransaction) ? _mappings[wcfTransaction] : null;
    }
}

public class ContractMappingDocument
{
    public List<ContractMapping> Mappings { get; set; } = new();
}

public class ContractMapping
{
    public string WcfTransaction { get; set; } = string.Empty;
    public RestEndpointInfo RestEndpoint { get; set; } = new();
    public RequestMapping RequestMapping { get; set; } = new();
    public ResponseMapping ResponseMapping { get; set; } = new();
    public List<string> BusinessLogic { get; set; } = new();
    public List<ErrorCase> ErrorCases { get; set; } = new();
}

public class RestEndpointInfo
{
    public string Method { get; set; } = string.Empty;
    public string Path { get; set; } = string.Empty;
    public string Controller { get; set; } = string.Empty;
    public string Action { get; set; } = string.Empty;
}

public class RequestMapping
{
    public Dictionary<string, string> WcfSchema { get; set; } = new();
    public Dictionary<string, string> RestSchema { get; set; } = new();
    public List<FieldMapping> FieldMappings { get; set; } = new();
}

public class ResponseMapping
{
    public Dictionary<string, string> WcfSchema { get; set; } = new();
    public Dictionary<string, string> RestSchema { get; set; } = new();
    public List<FieldMapping> FieldMappings { get; set; } = new();
}

public class FieldMapping
{
    public string WcfField { get; set; } = string.Empty;
    public string RestField { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public bool Required { get; set; }
}

public class ErrorCase
{
    public string Condition { get; set; } = string.Empty;
    public string WcfError { get; set; } = string.Empty;
    public int RestStatus { get; set; }
}
