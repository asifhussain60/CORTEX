using Microsoft.AspNetCore.Mvc;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Services;

namespace PaymentProcessor.TransactionInvoices.API.Controllers;

/// <summary>
/// REST API controller for transaction invoice operations.
/// Migrated from WCF transactions: XGenerateTransactionInvoice, XAddTransactionInvoice, Updater_CreatePaymentTransactionInvoices.
/// </summary>
[ApiController]
[Route("api/v1/transaction-invoices")]
[Produces("application/json")]
public class TransactionInvoiceController : ControllerBase
{
    private readonly ITransactionInvoiceService _transactionInvoiceService;
    private readonly ILogger<TransactionInvoiceController> _logger;

    public TransactionInvoiceController(
        ITransactionInvoiceService transactionInvoiceService,
        ILogger<TransactionInvoiceController> logger)
    {
        _transactionInvoiceService = transactionInvoiceService;
        _logger = logger;
    }

    /// <summary>
    /// Creates a payroll-based transaction invoice.
    /// </summary>
    /// <param name="request">Invoice creation request with employer and employee transaction amounts</param>
    /// <returns>Created transaction invoice details</returns>
    /// <response code="201">Invoice created successfully</response>
    /// <response code="400">Validation errors (invalid amounts, missing fields, etc.)</response>
    /// <response code="404">AccountCategory or employer not found</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/transaction-invoices
    ///     {
    ///         "employerId": "EMP-001",
    ///         "account_categoryId": "SA-001",
    ///         "paymentPlanId": "RP-001",
    ///         "employerTransactionDefault": 500.00,
    ///         "employeeTransactionDefault": 250.00,
    ///         "effectiveDate": "2025-12-15T00:00:00Z",
    ///         "invoiceDescription": "Payroll transaction",
    ///         "isLSA": false,
    ///         "updateTemplate": true,
    ///         "createdBy": "system"
    ///     }
    ///     
    /// </remarks>
    [HttpPost]
    [ProducesResponseType(typeof(TransactionInvoiceResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<TransactionInvoiceResponse>> CreateInvoice([FromBody] CreateTransactionInvoiceRequest request)
    {
        _logger.LogInformation("Creating transaction invoice for Employer={EmployerId}, AccountCategory={AccountCategoryId}",
            request.EmployerId, request.AccountCategoryId);

        var result = await _transactionInvoiceService.CreateAsync(request);

        _logger.LogInformation("Successfully created transaction invoice {InvoiceId}", result.InvoiceId);

        return CreatedAtAction(
            nameof(GetInvoiceById),
            new { id = result.InvoiceId },
            result
        );
    }

    /// <summary>
    /// Generates an on-demand transaction invoice based on peg amount logic.
    /// </summary>
    /// <param name="request">Invoice generation request with peg amount parameters</param>
    /// <returns>Generation result (invoice created or not needed)</returns>
    /// <response code="200">Invoice generation result (created or not needed)</response>
    /// <response code="400">Validation errors (invalid amount, past date, etc.)</response>
    /// <response code="404">AccountCategory not found</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/transaction-invoices/generate
    ///     {
    ///         "account_categoryId": "SA-001",
    ///         "invoiceAmount": 500.00,
    ///         "invoiceDate": "2025-12-15T00:00:00Z",
    ///         "createdBy": "system"
    ///     }
    ///     
    /// Sample response (invoice created):
    /// 
    ///     {
    ///         "result": "invoice created",
    ///         "cashInOutId": "CIO-123",
    ///         "invoice": { /* invoice details */ },
    ///         "paymentId": "PAY-456"
    ///     }
    ///     
    /// Sample response (not needed):
    /// 
    ///     {
    ///         "result": "invoice not needed",
    ///         "cashInOutId": null,
    ///         "invoice": null,
    ///         "paymentId": null
    ///     }
    ///     
    /// </remarks>
    [HttpPost("generate")]
    [ProducesResponseType(typeof(GenerateTransactionInvoiceResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<GenerateTransactionInvoiceResponse>> GenerateInvoice([FromBody] GenerateTransactionInvoiceRequest request)
    {
        _logger.LogInformation("Generating on-demand transaction invoice for AccountCategory={AccountCategoryId}, Amount={Amount:C}",
            request.AccountCategoryId, request.InvoiceAmount);

        var result = await _transactionInvoiceService.GenerateAsync(request);

        _logger.LogInformation("Invoice generation result: {Result}", result.Result);

        return Ok(result);
    }

    /// <summary>
    /// Creates transaction invoices for multiple account_categorys (batch processing).
    /// </summary>
    /// <param name="request">Batch creation request with optional employer filter</param>
    /// <returns>Batch processing results with success/failure counts</returns>
    /// <response code="200">Batch processing completed (check results for individual outcomes)</response>
    /// <response code="400">Validation errors</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/transaction-invoices/batch
    ///     {
    ///         "employerIds": ["EMP-001", "EMP-002"],
    ///         "createdBy": "system"
    ///     }
    ///     
    /// Sample response:
    /// 
    ///     {
    ///         "totalProcessed": 10,
    ///         "successCount": 8,
    ///         "failureCount": 1,
    ///         "skippedCount": 1,
    ///         "results": [
    ///             {
    ///                 "account_categoryId": "SA-001",
    ///                 "employerId": "EMP-001",
    ///                 "success": true,
    ///                 "cashInOutId": "CIO-123",
    ///                 "amount": 500.00
    ///             }
    ///         ]
    ///     }
    ///     
    /// </remarks>
    [HttpPost("batch")]
    [ProducesResponseType(typeof(BatchTransactionInvoiceResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BatchTransactionInvoiceResponse>> CreateBatchInvoices([FromBody] CreateBatchTransactionInvoiceRequest request)
    {
        _logger.LogInformation("Creating batch transaction invoices. Employer filter: {EmployerCount} employers",
            request.EmployerIds.Count);

        var result = await _transactionInvoiceService.CreateBatchAsync(request);

        _logger.LogInformation("Batch processing complete. Success: {Success}, Failed: {Failed}, Skipped: {Skipped}",
            result.SuccessCount, result.FailureCount, result.SkippedCount);

        return Ok(result);
    }

    /// <summary>
    /// Retrieves a transaction invoice by ID.
    /// </summary>
    /// <param name="id">Invoice identifier</param>
    /// <returns>Transaction invoice details</returns>
    /// <response code="200">Invoice found</response>
    /// <response code="404">Invoice not found</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(TransactionInvoiceResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<TransactionInvoiceResponse>> GetInvoiceById(string id)
    {
        _logger.LogInformation("Retrieving transaction invoice {InvoiceId}", id);

        var invoice = await _transactionInvoiceService.GetByIdAsync(id);

        if (invoice == null)
        {
            _logger.LogWarning("Transaction invoice {InvoiceId} not found", id);
            return NotFound(new ProblemDetails
            {
                Title = "Invoice Not Found",
                Detail = $"Transaction invoice with ID '{id}' was not found.",
                Status = StatusCodes.Status404NotFound,
                Instance = HttpContext.Request.Path
            });
        }

        return Ok(invoice);
    }

    /// <summary>
    /// Retrieves all transaction invoices for a specific batch.
    /// </summary>
    /// <param name="batchId">Batch identifier</param>
    /// <returns>List of transaction invoices in the batch</returns>
    /// <response code="200">Invoices found (may be empty list)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("batch/{batchId}")]
    [ProducesResponseType(typeof(IEnumerable<TransactionInvoiceResponse>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<TransactionInvoiceResponse>>> GetInvoicesByBatchId(string batchId)
    {
        _logger.LogInformation("Retrieving transaction invoices for batch {BatchId}", batchId);

        var invoices = await _transactionInvoiceService.GetByBatchIdAsync(batchId);

        return Ok(invoices);
    }

    /// <summary>
    /// Retrieves all transaction invoices for a specific account_category.
    /// </summary>
    /// <param name="account_categoryId">AccountCategory identifier</param>
    /// <returns>List of transaction invoices for the account_category</returns>
    /// <response code="200">Invoices found (may be empty list)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("account_category/{account_categoryId}")]
    [ProducesResponseType(typeof(IEnumerable<TransactionInvoiceResponse>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<TransactionInvoiceResponse>>> GetInvoicesByAccountCategoryId(string account_categoryId)
    {
        _logger.LogInformation("Retrieving transaction invoices for account_category {AccountCategoryId}", account_categoryId);

        var invoices = await _transactionInvoiceService.GetByAccountCategoryIdAsync(account_categoryId);

        return Ok(invoices);
    }
}
