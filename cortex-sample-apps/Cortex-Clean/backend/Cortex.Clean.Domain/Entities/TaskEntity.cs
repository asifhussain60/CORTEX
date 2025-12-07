using Cortex.Clean.Domain.Exceptions;
using Cortex.Clean.Domain.Services;

namespace Cortex.Clean.Domain.Entities;

/// <summary>
/// Represents a task in the task management system.
/// Domain entity with validation rules enforced.
/// </summary>
public class TaskEntity
{
    private string _title = string.Empty;

    /// <summary>
    /// Gets the unique identifier for this task.
    /// </summary>
    public int Id { get; private set; }

    /// <summary>
    /// Gets or sets the task title.
    /// Must be non-empty and less than or equal to 255 characters.
    /// </summary>
    public string Title
    {
        get => _title;
        private set
        {
            ValidateTitle(value);
            _title = value;
        }
    }

    /// <summary>
    /// Gets or sets whether the task is completed.
    /// </summary>
    public bool IsCompleted { get; private set; }

    /// <summary>
    /// Gets the date and time when the task was created.
    /// </summary>
    public DateTime CreatedAt { get; private set; }

    /// <summary>
    /// Creates a new task with the specified title.
    /// </summary>
    /// <param name="title">The task title (required, max 255 chars).</param>
    /// <exception cref="InvalidTaskException">Thrown when title is invalid.</exception>
    public TaskEntity(string title)
    {
        // Auto-increment ID simulation (EF Core will handle this)
        Id = 1;
        Title = title;
        IsCompleted = false;
        CreatedAt = DateTime.UtcNow;
    }

    /// <summary>
    /// Toggles the completion status of the task.
    /// </summary>
    public void ToggleCompletion()
    {
        IsCompleted = !IsCompleted;
    }

    /// <summary>
    /// Updates the task title.
    /// </summary>
    /// <param name="newTitle">The new title (required, max 255 chars).</param>
    /// <exception cref="InvalidTaskException">Thrown when title is invalid.</exception>
    public void UpdateTitle(string newTitle)
    {
        Title = newTitle;
    }

    /// <summary>
    /// Validates the task title using the domain validation service.
    /// </summary>
    /// <param name="title">The title to validate.</param>
    /// <exception cref="InvalidTaskException">Thrown when title is invalid.</exception>
    private static void ValidateTitle(string title)
    {
        TaskValidationService.ValidateTitle(title);
    }
}
