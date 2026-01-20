namespace RA.FundingInvoices.Core.Exceptions;

/// <summary>
/// Exception thrown when a requested entity is not found.
/// Maps to HTTP 404 Not Found.
/// </summary>
public class NotFoundException : Exception
{
    public string EntityType { get; }
    public string EntityId { get; }

    public NotFoundException(string entityType, string entityId)
        : base($"{entityType} with ID '{entityId}' was not found.")
    {
        EntityType = entityType;
        EntityId = entityId;
    }

    public NotFoundException(string entityType, string entityId, string message)
        : base(message)
    {
        EntityType = entityType;
        EntityId = entityId;
    }

    public NotFoundException(string message) : base(message)
    {
        EntityType = "Entity";
        EntityId = string.Empty;
    }

    public NotFoundException(string message, Exception innerException)
        : base(message, innerException)
    {
        EntityType = "Entity";
        EntityId = string.Empty;
    }
}
