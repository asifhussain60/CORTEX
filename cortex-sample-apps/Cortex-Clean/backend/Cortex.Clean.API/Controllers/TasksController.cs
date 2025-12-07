using Cortex.Clean.Application.Commands;
using Cortex.Clean.Application.DTOs;
using Cortex.Clean.Application.Queries;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace Cortex.Clean.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class TasksController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly ILogger<TasksController> _logger;

    public TasksController(IMediator mediator, ILogger<TasksController> logger)
    {
        _mediator = mediator ?? throw new ArgumentNullException(nameof(mediator));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>
    /// Gets all tasks, optionally filtered by title.
    /// </summary>
    /// <param name="filter">Optional title filter (case-insensitive contains).</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>List of tasks.</returns>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<TaskDto>), StatusCodes.Status200OK)]
    public async Task<ActionResult<IEnumerable<TaskDto>>> GetTasks(
        [FromQuery] string? filter = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Fetching tasks with filter: {Filter}", filter ?? "none");
        
        var query = new GetTasksQuery { Filter = filter };
        var tasks = await _mediator.Send(query, cancellationToken);
        
        return Ok(tasks);
    }

    /// <summary>
    /// Gets a specific task by ID.
    /// </summary>
    /// <param name="id">The task ID.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The task, or 404 if not found.</returns>
    [HttpGet("{id:int}")]
    [ProducesResponseType(typeof(TaskDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<TaskDto>> GetTask(int id, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Fetching task with ID: {TaskId}", id);
        
        var query = new GetTaskByIdQuery(id);
        var task = await _mediator.Send(query, cancellationToken);
        
        if (task == null)
        {
            _logger.LogWarning("Task with ID {TaskId} not found", id);
            return NotFound(new { message = $"Task with ID {id} not found." });
        }
        
        return Ok(task);
    }

    /// <summary>
    /// Creates a new task.
    /// </summary>
    /// <param name="request">The task creation request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The created task.</returns>
    [HttpPost]
    [ProducesResponseType(typeof(TaskDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<TaskDto>> CreateTask(
        [FromBody] CreateTaskRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating task with title: {Title}", request.Title);
        
        var command = new CreateTaskCommand(request.Title);
        var task = await _mediator.Send(command, cancellationToken);
        
        return CreatedAtAction(
            nameof(GetTask),
            new { id = task.Id },
            task);
    }

    /// <summary>
    /// Updates an existing task.
    /// </summary>
    /// <param name="id">The task ID.</param>
    /// <param name="request">The update request.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>No content on success.</returns>
    [HttpPut("{id:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> UpdateTask(
        int id,
        [FromBody] UpdateTaskRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Updating task with ID: {TaskId}", id);
        
        var command = new UpdateTaskCommand(id, request.Title, request.IsCompleted);
        await _mediator.Send(command, cancellationToken);
        
        return NoContent();
    }

    /// <summary>
    /// Toggles task completion status.
    /// </summary>
    /// <param name="id">The task ID.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>No content on success.</returns>
    [HttpPatch("{id:int}/toggle")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> ToggleTask(int id, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Toggling completion status for task with ID: {TaskId}", id);
        
        var command = new ToggleTaskCompletionCommand(id);
        await _mediator.Send(command, cancellationToken);
        
        return NoContent();
    }

    /// <summary>
    /// Deletes a task.
    /// </summary>
    /// <param name="id">The task ID.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>No content on success.</returns>
    [HttpDelete("{id:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteTask(int id, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting task with ID: {TaskId}", id);
        
        var command = new DeleteTaskCommand(id);
        await _mediator.Send(command, cancellationToken);
        
        return NoContent();
    }
}

