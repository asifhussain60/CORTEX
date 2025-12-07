using Cortex.Clean.Domain.Entities;

namespace Cortex.Clean.Domain.Interfaces;

/// <summary>
/// Repository interface for Task entity operations.
/// Defines contract for data access without implementation details.
/// </summary>
public interface ITaskRepository
{
    /// <summary>
    /// Gets all tasks, optionally filtered by title.
    /// </summary>
    /// <param name="filter">Optional title filter (case-insensitive contains).</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>List of tasks matching the filter.</returns>
    Task<IEnumerable<TaskEntity>> GetAllAsync(string? filter = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a task by ID.
    /// </summary>
    /// <param name="id">The task ID.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The task, or null if not found.</returns>
    Task<TaskEntity?> GetByIdAsync(int id, CancellationToken cancellationToken = default);

    /// <summary>
    /// Adds a new task.
    /// </summary>
    /// <param name="task">The task to add.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The added task with generated ID.</returns>
    Task<TaskEntity> AddAsync(TaskEntity task, CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates an existing task.
    /// </summary>
    /// <param name="task">The task to update.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task UpdateAsync(TaskEntity task, CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a task by ID.
    /// </summary>
    /// <param name="id">The task ID to delete.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>True if deleted; false if not found.</returns>
    Task<bool> DeleteAsync(int id, CancellationToken cancellationToken = default);

    /// <summary>
    /// Saves all pending changes to the database.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task SaveChangesAsync(CancellationToken cancellationToken = default);
}
