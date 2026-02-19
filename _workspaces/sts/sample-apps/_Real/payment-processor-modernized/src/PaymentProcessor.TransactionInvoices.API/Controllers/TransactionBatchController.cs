using Microsoft.AspNetCore.Mvc;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Services;

namespace PaymentProcessor.TransactionInvoices.API.Controllers;

/// <summary>
/// REST API controller for transaction batch operations.
/// Migrated from WCF transactions: XCloseTransactionBatch, XUpdateTransactionBatch.
/// </summary>
[ApiController]
[Route("api/v1/transaction-batches")]
[Produces("application/json")]
public class TransactionBatchController : ControllerBase
{
    private readonly ITransactionBatchService _transactionBatchService;
    private readonly ILogger<TransactionBatchController> _logger;

    public TransactionBatchController(
        ITransactionBatchService transactionBatchService,
        ILogger<TransactionBatchController> logger)
    {
        _transactionBatchService = transactionBatchService;
        _logger = logger;
    }

    /// <summary>
    /// Creates a new transaction batch.
    /// </summary>
    /// <param name="request">Batch creation request</param>
    /// <returns>Created batch details</returns>
    /// <response code="201">Batch created successfully</response>
    /// <response code="400">Validation errors</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/transaction-batches
    ///     {
    ///         "description": "December 2025 Payroll Batch",
    ///         "employerId": "EMP-001",
    ///         "createdBy": "system"
    ///     }
    ///     
    /// </remarks>
    [HttpPost]
    [ProducesResponseType(typeof(TransactionBatchResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<TransactionBatchResponse>> CreateBatch([FromBody] CreateTransactionBatchRequest request)
    {
        _logger.LogInformation("Creating transaction batch for Employer={EmployerId}", request.EmployerId);

        var result = await _transactionBatchService.CreateAsync(request);

        _logger.LogInformation("Successfully created transaction batch {BatchId}", result.BatchId);

        return CreatedAtAction(
            nameof(GetBatchById),
            new { id = result.BatchId },
            result
        );
    }

    /// <summary>
    /// Closes a transaction batch with state transition validation and auto-debit processing.
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
    ///     POST /api/v1/transaction-batches/close
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
    [ProducesResponseType(typeof(CloseTransactionBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<CloseTransactionBatchResponse>> CloseBatch([FromBody] CloseTransactionBatchRequest request)
    {
        _logger.LogInformation("Closing transaction batch {BatchId}", request.BatchId);

        var result = await _transactionBatchService.CloseAsync(request);

        _logger.LogInformation("Successfully closed batch {BatchId}. Status: {Status}, Payment: {PaymentId}",
            request.BatchId, result.Batch.Status, result.PaymentId);

        return Ok(result);
    }

    /// <summary>
    /// Reopens a closed transaction batch.
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
    ///     POST /api/v1/transaction-batches/reopen
    ///     {
    ///         "batchId": "BATCH-001",
    ///         "description": "Reopened for corrections",
    ///         "updatedBy": "admin"
    ///     }
    ///     
    /// </remarks>
    [HttpPost("reopen")]
    [ProducesResponseType(typeof(TransactionBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<TransactionBatchResponse>> ReopenBatch([FromBody] ReopenTransactionBatchRequest request)
    {
        _logger.LogInformation("Reopening transaction batch {BatchId}", request.BatchId);

        var result = await _transactionBatchService.ReopenAsync(request);

        _logger.LogInformation("Successfully reopened batch {BatchId}. New status: {Status}",
            request.BatchId, result.Status);

        return Ok(result);
    }

    /// <summary>
    /// Updates transaction batch metadata (description, employer).
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
    ///     PUT /api/v1/transaction-batches/BATCH-001
    ///     {
    ///         "description": "Updated batch description",
    ///         "employerId": "EMP-002",
    ///         "updatedBy": "admin"
    ///     }
    ///     
    /// </remarks>
    [HttpPut("{id}")]
    [ProducesResponseType(typeof(TransactionBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<TransactionBatchResponse>> UpdateBatch(string id, [FromBody] UpdateTransactionBatchRequest request)
    {
        _logger.LogInformation("Updating transaction batch {BatchId}", id);

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

        var result = await _transactionBatchService.UpdateAsync(request);

        _logger.LogInformation("Successfully updated batch {BatchId}", id);

        return Ok(result);
    }

    /// <summary>
    /// Retrieves a transaction batch by ID.
    /// </summary>
    /// <param name="id">Batch identifier</param>
    /// <returns>Batch details</returns>
    /// <response code="200">Batch found</response>
    /// <response code="404">Batch not found</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(TransactionBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<TransactionBatchResponse>> GetBatchById(string id)
    {
        _logger.LogInformation("Retrieving transaction batch {BatchId}", id);

        var batch = await _transactionBatchService.GetByIdAsync(id);

        if (batch == null)
        {
            _logger.LogWarning("Transaction batch {BatchId} not found", id);
            return NotFound(new ProblemDetails
            {
                Title = "Batch Not Found",
                Detail = $"Transaction batch with ID '{id}' was not found.",
                Status = StatusCodes.Status404NotFound,
                Instance = HttpContext.Request.Path
            });
        }

        return Ok(batch);
    }

    /// <summary>
    /// Retrieves all transaction batches for a specific account_category.
    /// </summary>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <returns>List of batches for the account_category</returns>
    /// <response code="200">Batches found (may be empty list)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("account_category/{account_categoryId}")]
    [ProducesResponseType(typeof(IEnumerable<TransactionBatchResponse>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<TransactionBatchResponse>>> GetBatchesByAccountCategoryId(string account_categoryId)
    {
        _logger.LogInformation("Retrieving transaction batches for account_category {AccountCategoryId}", account_categoryId);

        var batches = await _transactionBatchService.GetByAccountCategoryIdAsync(account_categoryId);

        return Ok(batches);
    }

    /// <summary>
    /// Retrieves the currently open transaction batch for a specific account_category.
    /// </summary>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <returns>Open batch details (null if none)</returns>
    /// <response code="200">Open batch found (or null if none)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("account_category/{account_categoryId}/open")]
    [ProducesResponseType(typeof(TransactionBatchResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<TransactionBatchResponse?>> GetOpenBatch(string account_categoryId)
    {
        _logger.LogInformation("Retrieving open transaction batch for account_category {AccountCategoryId}", account_categoryId);

        var batch = await _transactionBatchService.GetOpenBatchAsync(account_categoryId);

        return Ok(batch);
    }
}
