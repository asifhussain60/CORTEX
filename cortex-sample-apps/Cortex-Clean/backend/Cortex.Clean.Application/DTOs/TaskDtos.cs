using Cortex.Clean.Domain.Entities;

namespace Cortex.Clean.Application.DTOs;

/// <summary>
/// Data transfer object for Task entity.
/// </summary>
public record TaskDto(int Id, string Title, bool IsCompleted);

/// <summary>
/// Request DTO for creating a new task.
/// </summary>
public record CreateTaskRequest(string Title);

/// <summary>
/// Request DTO for updating a task.
/// </summary>
public record UpdateTaskRequest(string Title, bool IsCompleted);
