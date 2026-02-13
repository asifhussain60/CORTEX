using Microsoft.AspNetCore.Mvc;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Services;

namespace RA.FundingInvoices.API.Controllers;

/// <summary>
/// REST API controller for funding batch operations.
/// Migrated from WCF transactions: XCloseFundingBatch, XUpdateFundingBatch.
/// </summary>
[ApiController]
[Route("api/v1/funding-batches")]
[Produces("application/json")]
public class FundingBatchController : ControllerBase
{
    private readonly IFundingBatchService _fundingBatchService;
    private readonly ILogger<FundingBatchController> _logger;

    public FundingBatchController(
        IFundingBatchService fundingBatchService,
        ILogger<FundingBatchController> logger)
    {
        _fundingBatchService = fundingBatchService;
        _logger = logger;
    }

    /// <summary>
    /// Creates a new funding batch.
    /// </summary>
    /// <param name="request">Batch creation request</param>
    /// <returns>Created batch details</returns>
    /// <response code="201">Batch created successfully</response>
    /// <response code="400">Validation errors</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/funding-batches
    ///     {
    ///         "description": "December 2025 Payroll Batch",
    ///         "employerId": "EMP-001",
    ///         "createdBy": "system"
    ///     }
    ///     
    /// </remarks>
    [HttpPost]
    [ProducesResponseType(typeof(FundingBatchResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<FundingBatchResponse>> CreateBatch([FromBody] CreateFundingBatchRequest request)
    {
        _logger.LogInformation("Creating funding batch for Employer={EmployerId}", request.EmployerId);

        var result = await _fundingBatchService.CreateAsync(request);

        _logger.LogInformation("Successfully created funding batch {BatchId}", result.BatchId);

        return CreatedAtAction(
            nameof(GetBatchById),
            new { id = result.BatchId },
            result
        );
    }

    /// <summary>
    /// Closes a funding batch with state transition validation and auto-debit processing.
    /// </summary>
    /// <param name="request">Batch closure request</param>
    /// <returns>Closure result with payment details</returns>
    /// <response code="200">Batch closed successfully</response>
    /// <response code="400">Validation errors (zero total, invalid status, etc.)</response>
    /// <response code="404">Batch not found</response>
    /// <response code="409">Business logic error (batch already closed, replenishment failure, etc.)</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/funding-batches/close
    ///     {
    ///         "batchId": "BATCH-001",
    ///         "description": "December 2025 Batch",
    ///         "excludedInvoiceIds": ["INV-999"],
    ///         "closedBy": "system"
    ///     }
    ///     
    /// Sample response:
    /// 
    ///     {
    ///         "result": "batch closed",
    ///         "cashInOutId": "CIO-123",
    ///         "paymentId": "PAY-456",
    ///         "batch": {
    ///             "batchId": "BATCH-001",
    ///             "status": "Pending",
    ///             "totalAmount": 5000.00
    ///         }
    ///     }
    ///     
    /// </remarks>
    [HttpPost("close")]
    [ProducesResponseType(typeof(CloseFundingBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<CloseFundingBatchResponse>> CloseBatch([FromBody] CloseFundingBatchRequest request)
    {
        _logger.LogInformation("Closing funding batch {BatchId}", request.BatchId);

        var result = await _fundingBatchService.CloseAsync(request);

        _logger.LogInformation("Successfully closed batch {BatchId}. Status: {Status}, Payment: {PaymentId}",
            request.BatchId, result.Batch.Status, result.PaymentId);

        return Ok(result);
    }

    /// <summary>
    /// Reopens a closed funding batch.
    /// </summary>
    /// <param name="request">Batch reopen request</param>
    /// <returns>Reopened batch details</returns>
    /// <response code="200">Batch reopened successfully</response>
    /// <response code="400">Validation errors</response>
    /// <response code="404">Batch not found</response>
    /// <response code="409">Business logic error (batch not closed, etc.)</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/funding-batches/reopen
    ///     {
    ///         "batchId": "BATCH-001",
    ///         "description": "Reopened for corrections",
    ///         "updatedBy": "admin"
    ///     }
    ///     
    /// </remarks>
    [HttpPost("reopen")]
    [ProducesResponseType(typeof(FundingBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<FundingBatchResponse>> ReopenBatch([FromBody] ReopenFundingBatchRequest request)
    {
        _logger.LogInformation("Reopening funding batch {BatchId}", request.BatchId);

        var result = await _fundingBatchService.ReopenAsync(request);

        _logger.LogInformation("Successfully reopened batch {BatchId}. New status: {Status}",
            request.BatchId, result.Status);

        return Ok(result);
    }

    /// <summary>
    /// Updates funding batch metadata (description, employer).
    /// </summary>
    /// <param name="id">Batch identifier</param>
    /// <param name="request">Update request</param>
    /// <returns>Updated batch details</returns>
    /// <response code="200">Batch updated successfully</response>
    /// <response code="400">Validation errors</response>
    /// <response code="404">Batch not found</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     PUT /api/v1/funding-batches/BATCH-001
    ///     {
    ///         "description": "Updated batch description",
    ///         "employerId": "EMP-002",
    ///         "updatedBy": "admin"
    ///     }
    ///     
    /// </remarks>
    [HttpPut("{id}")]
    [ProducesResponseType(typeof(FundingBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<FundingBatchResponse>> UpdateBatch(string id, [FromBody] UpdateFundingBatchRequest request)
    {
        _logger.LogInformation("Updating funding batch {BatchId}", id);

        // Ensure ID from route matches ID in request
        if (!string.IsNullOrWhiteSpace(request.BatchId) && request.BatchId != id)
        {
            return BadRequest(new ProblemDetails
            {
                Title = "ID Mismatch",
                Detail = $"Route ID '{id}' does not match request BatchId '{request.BatchId}'.",
                Status = StatusCodes.Status400BadRequest,
                Instance = HttpContext.Request.Path
            });
        }

        // Set BatchId from route if not present in request
        request.BatchId = id;

        var result = await _fundingBatchService.UpdateAsync(request);

        _logger.LogInformation("Successfully updated batch {BatchId}", id);

        return Ok(result);
    }

    /// <summary>
    /// Retrieves a funding batch by ID.
    /// </summary>
    /// <param name="id">Batch identifier</param>
    /// <returns>Batch details</returns>
    /// <response code="200">Batch found</response>
    /// <response code="404">Batch not found</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(FundingBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<FundingBatchResponse>> GetBatchById(string id)
    {
        _logger.LogInformation("Retrieving funding batch {BatchId}", id);

        var batch = await _fundingBatchService.GetByIdAsync(id);

        if (batch == null)
        {
            _logger.LogWarning("Funding batch {BatchId} not found", id);
            return NotFound(new ProblemDetails
            {
                Title = "Batch Not Found",
                Detail = $"Funding batch with ID '{id}' was not found.",
                Status = StatusCodes.Status404NotFound,
                Instance = HttpContext.Request.Path
            });
        }

        return Ok(batch);
    }

    /// <summary>
    /// Retrieves all funding batches for a specific subaccount.
    /// </summary>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <returns>List of batches for the subaccount</returns>
    /// <response code="200">Batches found (may be empty list)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("subaccount/{subaccountId}")]
    [ProducesResponseType(typeof(IEnumerable<FundingBatchResponse>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<FundingBatchResponse>>> GetBatchesBySubaccountId(string subaccountId)
    {
        _logger.LogInformation("Retrieving funding batches for subaccount {SubaccountId}", subaccountId);

        var batches = await _fundingBatchService.GetBySubaccountIdAsync(subaccountId);

        return Ok(batches);
    }

    /// <summary>
    /// Retrieves the currently open funding batch for a specific subaccount.
    /// </summary>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <returns>Open batch details (null if none)</returns>
    /// <response code="200">Open batch found (or null if none)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("subaccount/{subaccountId}/open")]
    [ProducesResponseType(typeof(FundingBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<FundingBatchResponse?>> GetOpenBatch(string subaccountId)
    {
        _logger.LogInformation("Retrieving open funding batch for subaccount {SubaccountId}", subaccountId);

        var batch = await _fundingBatchService.GetOpenBatchAsync(subaccountId);

        return Ok(batch);
    }
}
