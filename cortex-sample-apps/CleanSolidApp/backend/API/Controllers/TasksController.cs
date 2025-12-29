using CleanSolidApp.Application.Services;
using CleanSolidApp.Domain.Entities;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace CleanSolidApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TasksController : ControllerBase
    {
        private readonly ITaskService _service;

        public TasksController(ITaskService service)
        {
            _service = service;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<TaskItem>>> Get([FromQuery] string? filter)
        {
            var tasks = await _service.GetTasksAsync(filter);
            return Ok(tasks);
        }

        [HttpGet("{id:int}")]
        public async Task<ActionResult<TaskItem>> GetById(int id)
        {
            var task = await _service.GetTaskAsync(id);
            if (task == null) return NotFound();
            return Ok(task);
        }

        public record CreateTaskRequest(string Title);
        public record UpdateTaskStatusRequest(bool IsCompleted);

        [HttpPost]
        public async Task<ActionResult<TaskItem>> Create([FromBody] CreateTaskRequest request)
        {
            var created = await _service.CreateTaskAsync(request.Title);
            return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
        }

        [HttpPut("{id:int}")]
        public async Task<IActionResult> UpdateStatus(int id, [FromBody] UpdateTaskStatusRequest request)
        {
            await _service.CompleteTaskAsync(id, request.IsCompleted);
            return NoContent();
        }

        [HttpDelete("{id:int}")]
        public async Task<IActionResult> Delete(int id)
        {
            await _service.DeleteTaskAsync(id);
            return NoContent();
        }
    }
}
