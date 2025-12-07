namespace Cortex.Clean.Domain.Exceptions;

/// <summary>
/// Exception thrown when a task is not found.
/// </summary>
public class TaskNotFoundException : Exception
{
    public TaskNotFoundException(int taskId)
        : base($"Task with ID {taskId} was not found.")
    {
        TaskId = taskId;
    }

    public int TaskId { get; }
}
