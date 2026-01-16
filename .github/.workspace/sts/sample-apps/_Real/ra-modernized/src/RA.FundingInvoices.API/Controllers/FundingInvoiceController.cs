using Microsoft.AspNetCore.Mvc;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Services;

namespace RA.FundingInvoices.API.Controllers;

/// <summary>
/// REST API controller for funding invoice operations.
/// Migrated from WCF transactions: XGenerateFundingInvoice, XAddFundingInvoice, Updater_CreateRAFundingInvoices.
/// </summary>
[ApiController]
[Route("api/v1/funding-invoices")]
[Produces("application/json")]
public class FundingInvoiceController : ControllerBase
{
    private readonly IFundingInvoiceService _fundingInvoiceService;
    private readonly ILogger<FundingInvoiceController> _logger;

    public FundingInvoiceController(
        IFundingInvoiceService fundingInvoiceService,
        ILogger<FundingInvoiceController> logger)
    {
        _fundingInvoiceService = fundingInvoiceService;
        _logger = logger;
    }

    /// <summary>
    /// Creates a payroll-based funding invoice.
    /// </summary>
    /// <param name="request">Invoice creation request with employer and employee funding amounts</param>
    /// <returns>Created funding invoice details</returns>
    /// <response code="201">Invoice created successfully</response>
    /// <response code="400">Validation errors (invalid amounts, missing fields, etc.)</response>
    /// <response code="404">Subaccount or employer not found</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/funding-invoices
    ///     {
    ///         "employerId": "EMP-001",
    ///         "subaccountId": "SA-001",
    ///         "reimbursementPlanId": "RP-001",
    ///         "employerFundingDefault": 500.00,
    ///         "employeeFundingDefault": 250.00,
    ///         "effectiveDate": "2025-12-15T00:00:00Z",
    ///         "invoiceDescription": "Payroll funding",
    ///         "isLSA": false,
    ///         "updateTemplate": true,
    ///         "createdBy": "system"
    ///     }
    ///     
    /// </remarks>
    [HttpPost]
    [ProducesResponseType(typeof(FundingInvoiceResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<FundingInvoiceResponse>> CreateInvoice([FromBody] CreateFundingInvoiceRequest request)
    {
        _logger.LogInformation("Creating funding invoice for Employer={EmployerId}, Subaccount={SubaccountId}",
            request.EmployerId, request.SubaccountId);

        var result = await _fundingInvoiceService.CreateAsync(request);

        _logger.LogInformation("Successfully created funding invoice {InvoiceId}", result.InvoiceId);

        return CreatedAtAction(
            nameof(GetInvoiceById),
            new { id = result.InvoiceId },
            result
        );
    }

    /// <summary>
    /// Generates an on-demand funding invoice based on peg amount logic.
    /// </summary>
    /// <param name="request">Invoice generation request with peg amount parameters</param>
    /// <returns>Generation result (invoice created or not needed)</returns>
    /// <response code="200">Invoice generation result (created or not needed)</response>
    /// <response code="400">Validation errors (invalid amount, past date, etc.)</response>
    /// <response code="404">Subaccount not found</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/funding-invoices/generate
    ///     {
    ///         "subaccountId": "SA-001",
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
    [ProducesResponseType(typeof(GenerateFundingInvoiceResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<GenerateFundingInvoiceResponse>> GenerateInvoice([FromBody] GenerateFundingInvoiceRequest request)
    {
        _logger.LogInformation("Generating on-demand funding invoice for Subaccount={SubaccountId}, Amount={Amount:C}",
            request.SubaccountId, request.InvoiceAmount);

        var result = await _fundingInvoiceService.GenerateAsync(request);

        _logger.LogInformation("Invoice generation result: {Result}", result.Result);

        return Ok(result);
    }

    /// <summary>
    /// Creates funding invoices for multiple subaccounts (batch processing).
    /// </summary>
    /// <param name="request">Batch creation request with optional employer filter</param>
    /// <returns>Batch processing results with success/failure counts</returns>
    /// <response code="200">Batch processing completed (check results for individual outcomes)</response>
    /// <response code="400">Validation errors</response>
    /// <response code="500">Internal server error</response>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /api/v1/funding-invoices/batch
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
    ///                 "subaccountId": "SA-001",
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
    [ProducesResponseType(typeof(BatchFundingInvoiceResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BatchFundingInvoiceResponse>> CreateBatchInvoices([FromBody] CreateBatchFundingInvoiceRequest request)
    {
        _logger.LogInformation("Creating batch funding invoices. Employer filter: {EmployerCount} employers",
            request.EmployerIds.Count);

        var result = await _fundingInvoiceService.CreateBatchAsync(request);

        _logger.LogInformation("Batch processing complete. Success: {Success}, Failed: {Failed}, Skipped: {Skipped}",
            result.SuccessCount, result.FailureCount, result.SkippedCount);

        return Ok(result);
    }

    /// <summary>
    /// Retrieves a funding invoice by ID.
    /// </summary>
    /// <param name="id">Invoice identifier</param>
    /// <returns>Funding invoice details</returns>
    /// <response code="200">Invoice found</response>
    /// <response code="404">Invoice not found</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(FundingInvoiceResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<FundingInvoiceResponse>> GetInvoiceById(string id)
    {
        _logger.LogInformation("Retrieving funding invoice {InvoiceId}", id);

        var invoice = await _fundingInvoiceService.GetByIdAsync(id);

        if (invoice == null)
        {
            _logger.LogWarning("Funding invoice {InvoiceId} not found", id);
            return NotFound(new ProblemDetails
            {
                Title = "Invoice Not Found",
                Detail = $"Funding invoice with ID '{id}' was not found.",
                Status = StatusCodes.Status404NotFound,
                Instance = HttpContext.Request.Path
            });
        }

        return Ok(invoice);
    }

    /// <summary>
    /// Retrieves all funding invoices for a specific batch.
    /// </summary>
    /// <param name="batchId">Batch identifier</param>
    /// <returns>List of funding invoices in the batch</returns>
    /// <response code="200">Invoices found (may be empty list)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("batch/{batchId}")]
    [ProducesResponseType(typeof(IEnumerable<FundingInvoiceResponse>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<FundingInvoiceResponse>>> GetInvoicesByBatchId(string batchId)
    {
        _logger.LogInformation("Retrieving funding invoices for batch {BatchId}", batchId);

        var invoices = await _fundingInvoiceService.GetByBatchIdAsync(batchId);

        return Ok(invoices);
    }

    /// <summary>
    /// Retrieves all funding invoices for a specific subaccount.
    /// </summary>
    /// <param name="subaccountId">Subaccount identifier</param>
    /// <returns>List of funding invoices for the subaccount</returns>
    /// <response code="200">Invoices found (may be empty list)</response>
    /// <response code="500">Internal server error</response>
    [HttpGet("subaccount/{subaccountId}")]
    [ProducesResponseType(typeof(IEnumerable<FundingInvoiceResponse>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<FundingInvoiceResponse>>> GetInvoicesBySubaccountId(string subaccountId)
    {
        _logger.LogInformation("Retrieving funding invoices for subaccount {SubaccountId}", subaccountId);

        var invoices = await _fundingInvoiceService.GetBySubaccountIdAsync(subaccountId);

        return Ok(invoices);
    }
}
