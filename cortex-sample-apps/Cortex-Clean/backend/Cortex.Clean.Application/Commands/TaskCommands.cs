using MediatR;
using Cortex.Clean.Application.DTOs;

namespace Cortex.Clean.Application.Commands;

/// <summary>
/// Command to create a new task.
/// </summary>
public record CreateTaskCommand(string Title) : IRequest<TaskDto>;

/// <summary>
/// Command to update an existing task.
/// </summary>
public record UpdateTaskCommand(int Id, string Title, bool IsCompleted) : IRequest<Unit>;

/// <summary>
/// Command to delete a task.
/// </summary>
public record DeleteTaskCommand(int Id) : IRequest<bool>;

/// <summary>
/// Command to toggle task completion status.
/// </summary>
public record ToggleTaskCompletionCommand(int Id) : IRequest<Unit>;
