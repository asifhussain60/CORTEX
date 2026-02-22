// ✅ CORTEX Refactored — TransactionsController
// ✅ SMELL-3 RESOLVED: Thin controller
// ✅ SMELL-9 RESOLVED: API versioning

using Microsoft.AspNetCore.Mvc;
using CortexLabs.FinTrack.Services;
using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class TransactionsController : ControllerBase
{
    private readonly ITransactionService _transactionService;
    private readonly ILogger<TransactionsController> _logger;

    public TransactionsController(
        ITransactionService transactionService,
        ILogger<TransactionsController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    // ✅ SMELL-6 RESOLVED: Pagination
    [HttpGet]
    public async Task<IActionResult> GetAll([FromQuery] int page = 1, [FromQuery] int pageSize = 50)
    {
        var transactions = await _transactionService.GetAllAsync(page, pageSize);
        return Ok(transactions);
    }

    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id)
    {
        var tx = await _transactionService.GetByIdAsync(id);
        if (tx == null)
            return NotFound(new ErrorResponse("Transaction not found", 404));

        return Ok(tx);
    }

    // ✅ SMELL-1 RESOLVED: Parameterized search
    [HttpGet("search")]
    public async Task<IActionResult> Search(
        [FromQuery] string? category,
        [FromQuery] DateTime? fromDate)
    {
        var transactions = await _transactionService.SearchAsync(category, fromDate);
        return Ok(transactions);
    }

    [HttpGet("dashboard/{userId:int}")]
    public async Task<IActionResult> GetDashboard(int userId)
    {
        var summary = await _transactionService.GetDashboardSummaryAsync(userId);
        return Ok(summary);
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreateTransactionDto dto)
    {
        try
        {
            var tx = await _transactionService.CreateAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id = tx.Id }, tx);
        }
        catch (ValidationException ex)
        {
            return BadRequest(new ErrorResponse(ex.Message, 400, ex.Errors));
        }
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var success = await _transactionService.DeleteAsync(id);
        if (!success)
            return NotFound(new ErrorResponse("Transaction not found", 404));

        return NoContent();
    }
}
