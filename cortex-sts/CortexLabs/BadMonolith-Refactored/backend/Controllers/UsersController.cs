// ✅ CORTEX Refactored — UsersController
// ✅ SMELL-3 RESOLVED: Thin controller, logic in service
// ✅ SMELL-18 RESOLVED: Proper error handling, no stack traces exposed

using Microsoft.AspNetCore.Mvc;
using CortexLabs.FinTrack.Services;
using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Controllers;

[ApiController]
[Route("api/v1/[controller]")]  // ✅ SMELL-9 RESOLVED: API versioning
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(IUserService userService, ILogger<UsersController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    // ✅ SMELL-6 RESOLVED: Pagination parameters
    [HttpGet]
    public async Task<IActionResult> GetAll([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var users = await _userService.GetAllAsync(page, pageSize);
        return Ok(users);
    }

    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id)
    {
        var user = await _userService.GetByIdAsync(id);
        if (user == null)
            return NotFound(new ErrorResponse("User not found", 404));

        return Ok(user);
    }

    // ✅ SMELL-1 RESOLVED: Search via service with parameterized query
    [HttpGet("search")]
    public async Task<IActionResult> Search([FromQuery] string username)
    {
        if (string.IsNullOrWhiteSpace(username))
            return BadRequest(new ErrorResponse("Username is required", 400));

        var user = await _userService.GetByUsernameAsync(username);
        if (user == null)
            return NotFound(new ErrorResponse("User not found", 404));

        return Ok(user);
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreateUserDto dto)
    {
        try
        {
            var user = await _userService.CreateAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id = user.Id }, user);
        }
        catch (ValidationException ex)
        {
            // ✅ SMELL-18 RESOLVED: Structured error response, no stack trace
            return BadRequest(new ErrorResponse(ex.Message, 400, ex.Errors));
        }
    }

    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(int id, [FromBody] UpdateUserDto dto)
    {
        try
        {
            var success = await _userService.UpdateAsync(id, dto);
            if (!success)
                return NotFound(new ErrorResponse("User not found", 404));

            return NoContent();
        }
        catch (ValidationException ex)
        {
            return BadRequest(new ErrorResponse(ex.Message, 400, ex.Errors));
        }
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var success = await _userService.DeleteAsync(id);
        if (!success)
            return NotFound(new ErrorResponse("User not found", 404));

        return NoContent();
    }
}

/// <summary>
/// Structured error response — never exposes stack traces
/// </summary>
public record ErrorResponse(string Message, int StatusCode, IEnumerable<string>? Errors = null);
