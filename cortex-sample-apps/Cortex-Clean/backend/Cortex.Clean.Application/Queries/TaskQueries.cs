using MediatR;
using Cortex.Clean.Application.DTOs;

namespace Cortex.Clean.Application.Queries;

/// <summary>
/// Query to get all tasks with optional filter.
/// </summary>
public record GetTasksQuery(string? Filter = null) : IRequest<IEnumerable<TaskDto>>;

/// <summary>
/// Query to get a single task by ID.
/// </summary>
public record GetTaskByIdQuery(int Id) : IRequest<TaskDto?>;
