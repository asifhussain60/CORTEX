using Cortex.Clean.Domain.Exceptions;

namespace Cortex.Clean.Domain.Services;

/// <summary>
/// Domain service for task validation logic.
/// Encapsulates business rules that don't naturally fit in entities.
/// </summary>
public class TaskValidationService
{
    /// <summary>
    /// Maximum allowed length for task title.
    /// </summary>
    public const int MaxTitleLength = 255;

    /// <summary>
    /// Validates a task title.
    /// </summary>
    /// <param name="title">The title to validate.</param>
    /// <exception cref="InvalidTaskException">Thrown when title is invalid.</exception>
    public static void ValidateTitle(string title)
    {
        if (string.IsNullOrWhiteSpace(title))
        {
            throw new InvalidTaskException("Task title is required.");
        }

        if (title.Length > MaxTitleLength)
        {
            throw new InvalidTaskException($"Task title cannot exceed {MaxTitleLength} characters.");
        }
    }

    /// <summary>
    /// Checks if a title is valid without throwing an exception.
    /// </summary>
    /// <param name="title">The title to check.</param>
    /// <param name="errorMessage">The validation error message if invalid.</param>
    /// <returns>True if valid; otherwise, false.</returns>
    public static bool IsValidTitle(string title, out string? errorMessage)
    {
        try
        {
            ValidateTitle(title);
            errorMessage = null;
            return true;
        }
        catch (InvalidTaskException ex)
        {
            errorMessage = ex.Message;
            return false;
        }
    }
}
