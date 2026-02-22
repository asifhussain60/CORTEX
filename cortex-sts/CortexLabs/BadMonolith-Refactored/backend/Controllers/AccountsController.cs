// ✅ CORTEX Refactored — AccountsController
// ✅ AP-002 RESOLVED: AccountsController restored — transfer endpoint no longer missing
// ✅ AP-009 RESOLVED: Rate limiting applied on transfer endpoint
// ✅ SMELL-3 RESOLVED: Thin controller, business logic in AccountService
// ✅ SMELL-9 RESOLVED: API versioning (api/v1)
// ✅ SMELL-18 RESOLVED: Structured error responses, no stack traces

using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using CortexLabs.FinTrack.Services.Interfaces;

namespace CortexLabs.FinTrack.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class AccountsController : ControllerBase
{
    private readonly IAccountService _accountService;
    private readonly ILogger<AccountsController> _logger;

    public AccountsController(IAccountService accountService, ILogger<AccountsController> logger)
    {
        _accountService = accountService ?? throw new ArgumentNullException(nameof(accountService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    /// <summary>Get account by ID.</summary>
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id)
    {
        var account = await _accountService.GetByIdAsync(id);
        if (account == null)
            return NotFound(new ErrorResponse("Account not found", 404));

        return Ok(account);
    }

    /// <summary>Get all accounts for a user.</summary>
    [HttpGet("user/{userId:int}")]
    public async Task<IActionResult> GetByUserId(int userId)
    {
        var accounts = await _accountService.GetByUserIdAsync(userId);
        return Ok(accounts);
    }

    /// <summary>Create a new account.</summary>
    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreateAccountDto dto)
    {
        try
        {
            var account = await _accountService.CreateAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id = account.Id }, account);
        }
        catch (ValidationException ex)
        {
            return BadRequest(new ErrorResponse(ex.Message, 400, ex.Errors));
        }
    }

    /// <summary>
    /// Transfer funds between accounts.
    /// AP-009: Rate-limited — max 10 transfers per minute per client.
    /// </summary>
    [HttpPost("transfer")]
    [EnableRateLimiting("transfer")]   // ✅ AP-009 RESOLVED: rate limiting on transfer
    public async Task<IActionResult> Transfer([FromBody] TransferRequest request)
    {
        _logger.LogInformation(
            "Transfer requested: from={From}, to={To}, amount={Amount}",
            request.FromAccountId, request.ToAccountId, request.Amount);

        try
        {
            var success = await _accountService.TransferAsync(
                request.FromAccountId,
                request.ToAccountId,
                request.Amount);

            if (!success)
                return BadRequest(new ErrorResponse("Transfer failed — check balances and account IDs", 400));

            return Ok(new { message = "Transfer successful" });
        }
        catch (ValidationException ex)
        {
            return BadRequest(new ErrorResponse(ex.Message, 400, ex.Errors));
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning("Transfer rejected: {Reason}", ex.Message);
            return UnprocessableEntity(new ErrorResponse(ex.Message, 422));
        }
    }
}

/// <summary>Request body for account transfer operations.</summary>
public record TransferRequest(int FromAccountId, int ToAccountId, decimal Amount);

/// <summary>Structured error response — RFC 7807 style, no stack traces to client.</summary>
public record ErrorResponse(string Message, int StatusCode, IEnumerable<string>? Errors = null);
