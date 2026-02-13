using FluentValidation;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.Adapters;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Repositories;
using RA.FundingInvoices.Core.Services;

namespace RA.FundingInvoices.Infrastructure.Services;

/// <summary>
/// Implementation of funding batch business logic service.
/// Extracts logic from XCloseFundingBatch, XUpdateFundingBatch, XReopenFundingBatch.
/// </summary>
public class FundingBatchService : IFundingBatchService
{
    private readonly IFundingBatchRepository _batchRepository;
    private readonly IFundingInvoiceRepository _invoiceRepository;
    private readonly ISubaccountRepository _subaccountRepository;
    private readonly ICashInOutRepository _cashInOutRepository;
    private readonly IReimbursementPlanAdapter _paragonAdapter;
    private readonly IValidator<CloseFundingBatchRequest> _closeValidator;
    private readonly IValidator<ReopenFundingBatchRequest> _reopenValidator;
    private readonly IValidator<UpdateFundingBatchRequest> _updateValidator;
    private readonly IValidator<CreateFundingBatchRequest> _createValidator;
    private readonly ILogger<FundingBatchService> _logger;

    public FundingBatchService(
        IFundingBatchRepository batchRepository,
        IFundingInvoiceRepository invoiceRepository,
        ISubaccountRepository subaccountRepository,
        ICashInOutRepository cashInOutRepository,
        IReimbursementPlanAdapter paragonAdapter,
        IValidator<CloseFundingBatchRequest> closeValidator,
        IValidator<ReopenFundingBatchRequest> reopenValidator,
        IValidator<UpdateFundingBatchRequest> updateValidator,
        IValidator<CreateFundingBatchRequest> createValidator,
        ILogger<FundingBatchService> logger)
    {
        _batchRepository = batchRepository;
        _invoiceRepository = invoiceRepository;
        _subaccountRepository = subaccountRepository;
        _cashInOutRepository = cashInOutRepository;
        _paragonAdapter = paragonAdapter;
        _closeValidator = closeValidator;
        _reopenValidator = reopenValidator;
        _updateValidator = updateValidator;
        _createValidator = createValidator;
        _logger = logger;
    }

    public async Task<CloseFundingBatchResponse> CloseAsync(CloseFundingBatchRequest request)
    {
        // Validate request
        var validationResult = await _closeValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Closing funding batch {BatchId}, Excluded invoices: {ExcludedCount}", 
            request.BatchId, request.ExcludedInvoiceIds.Count);

        // Get the batch to close
        var batch = await _batchRepository.GetByIdAsync(request.BatchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Funding batch not found: {request.BatchId}");
        }

        // Get subaccount and reimbursement plans
        var subaccount = await _subaccountRepository.GetByIdAsync(batch.SubaccountId);
        if (subaccount == null)
        {
            throw new InvalidOperationException($"Subaccount not found: {batch.SubaccountId}");
        }

        var plans = await _paragonAdapter.GetReimbursementPlansAsync(batch.SubaccountId);
        if (!plans.Any())
        {
            throw new InvalidOperationException($"No reimbursement plans found for subaccount {batch.SubaccountId}");
        }

        var firstPlan = plans.First();

        // Handle status-specific logic
        if (batch.Status == "Open")
        {
            // Create new pending batch
            var newPendingBatch = new FundingBatch
            {
                BatchId = Guid.NewGuid().ToString(),
                SubaccountId = batch.SubaccountId,
                Status = "Pending",
                Description = $"Pending batch from {batch.BatchId}",
                CreatedBy = request.ClosedBy,
                CreatedDate = DateTime.UtcNow
            };

            await _batchRepository.CreateAsync(newPendingBatch);
            _logger.LogInformation("Created new pending batch {NewBatchId}", newPendingBatch.BatchId);

            // Move non-excluded invoices to new batch
            var batchInvoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
            var includedInvoices = batchInvoices.Where(inv => !request.ExcludedInvoiceIds.Contains(inv.InvoiceId)).ToList();
            
            foreach (var invoice in includedInvoices)
            {
                invoice.BatchId = newPendingBatch.BatchId;
                invoice.ModifiedBy = request.ClosedBy;
                invoice.ModifiedDate = DateTime.UtcNow;
                await _invoiceRepository.UpdateAsync(invoice);
            }

            _logger.LogInformation("Moved {Count} invoices to new pending batch", includedInvoices.Count);
            batch = newPendingBatch;
        }
        else if (batch.Status == "Reopened")
        {
            batch.Status = "Pending";
            
            // Move excluded items back to open batch if any exclusions
            if (request.ExcludedInvoiceIds.Any())
            {
                // Create or find open batch
                var openBatches = await _batchRepository.GetByStatusAsync("Open");
                var openBatch = openBatches.FirstOrDefault(b => b.SubaccountId == batch.SubaccountId);

                if (openBatch == null)
                {
                    openBatch = new FundingBatch
                    {
                        BatchId = Guid.NewGuid().ToString(),
                        SubaccountId = batch.SubaccountId,
                        Status = "Open",
                        Description = "Open batch for excluded items",
                        CreatedBy = request.ClosedBy,
                        CreatedDate = DateTime.UtcNow
                    };
                    await _batchRepository.CreateAsync(openBatch);
                }

                // Move excluded invoices to open batch
                foreach (var excludedId in request.ExcludedInvoiceIds)
                {
                    var invoice = await _invoiceRepository.GetByIdAsync(excludedId);
                    if (invoice != null)
                    {
                        invoice.BatchId = openBatch.BatchId;
                        invoice.ModifiedBy = request.ClosedBy;
                        invoice.ModifiedDate = DateTime.UtcNow;
                        await _invoiceRepository.UpdateAsync(invoice);
                    }
                }

                _logger.LogInformation("Moved {Count} excluded invoices to open batch {OpenBatchId}", 
                    request.ExcludedInvoiceIds.Count, openBatch.BatchId);
            }
        }

        // Calculate batch total (excluding excluded invoices)
        var allBatchInvoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
        var includedBatchInvoices = allBatchInvoices.Where(inv => !request.ExcludedInvoiceIds.Contains(inv.InvoiceId)).ToList();
        decimal batchTotal = includedBatchInvoices.Sum(inv => inv.Amount);

        _logger.LogInformation("Calculated batch total: {Total:C} from {Count} invoices", batchTotal, includedBatchInvoices.Count);

        // Validate non-zero amount
        if (batchTotal == 0)
        {
            _logger.LogWarning("Batch total is zero. Reopening batch {BatchId}", batch.BatchId);
            batch.Status = "Reopened";
            await _batchRepository.UpdateAsync(batch);
            throw new InvalidOperationException("RA Funding invoices must be non-zero. Funding Batch will be reopened.");
        }

        // Create replenishment CashInOut
        var cashInOut = new CashInOut
        {
            CashInOutId = Guid.NewGuid().ToString(),
            TransactionType = "RAFunding",
            Amount = -batchTotal, // Negative for replenishment
            TransactionDate = DateTime.Today,
            Description = $"RA Replenishment for {firstPlan.PlanShortDescription}",
            CreatedBy = request.ClosedBy,
            CreatedDate = DateTime.UtcNow
        };

        await _cashInOutRepository.CreateAsync(cashInOut);
        _logger.LogInformation("Created replenishment CashInOut {CashInOutId} for {Amount:C}", 
            cashInOut.CashInOutId, cashInOut.Amount);

        // Update batch with CashInOut reference and mark as closed
        batch.FundingCashInOutId = cashInOut.CashInOutId;
        batch.Status = "Closed";
        batch.ModifiedBy = request.ClosedBy;
        batch.ModifiedDate = DateTime.UtcNow;
        await _batchRepository.UpdateAsync(batch);

        // Process auto-debit if enabled
        var paymentAuths = await _paragonAdapter.GetPaymentAuthorizationsAsync(
            firstPlan.EmployerId,
            batch.SubaccountId,
            plans.Select(p => p.ReimbursementPlanId).ToList()
        );

        var autoDebitAuth = paymentAuths.FirstOrDefault(pa => pa.IsAutoDebit && !string.IsNullOrEmpty(pa.PaymentAuthorizationId));
        string? paymentId = null;
        bool autoDebitProcessed = false;

        if (autoDebitAuth != null && batchTotal > 0)
        {
            _logger.LogInformation("Auto-debit enabled for {Amount:C}. Payment authorization: {AuthId}", 
                batchTotal, autoDebitAuth.PaymentAuthorizationId);

            // Calculate effective date (2 business days from today or batch date, whichever is later)
            var effectiveDate = DateTime.Today.AddDays(2);
            if (cashInOut.TransactionDate > effectiveDate)
            {
                effectiveDate = cashInOut.TransactionDate;
            }

            // TODO: Phase 4 - Create Payment entity
            paymentId = $"PAYMENT-{Guid.NewGuid():N}";
            autoDebitProcessed = true;

            _logger.LogInformation("Created auto-debit payment {PaymentId} with effective date {EffectiveDate:yyyy-MM-dd}", 
                paymentId, effectiveDate);
        }
        else if (batchTotal <= 0)
        {
            _logger.LogWarning("Batch total {Total:C} is not positive. No payment created.", batchTotal);
        }

        var response = new CloseFundingBatchResponse
        {
            Batch = MapBatchToResponse(batch, includedBatchInvoices.Count, batchTotal),
            CashInOutId = cashInOut.CashInOutId,
            CashInOutAmount = cashInOut.Amount,
            PaymentId = paymentId,
            AutoDebitProcessed = autoDebitProcessed
        };

        _logger.LogInformation("Successfully closed funding batch {BatchId}", batch.BatchId);
        return response;
    }

    public async Task<FundingBatchResponse> ReopenAsync(ReopenFundingBatchRequest request)
    {
        // Validate request
        var validationResult = await _reopenValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Reopening funding batch {BatchId}", request.BatchId);

        var batch = await _batchRepository.GetByIdAsync(request.BatchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Funding batch not found: {request.BatchId}");
        }

        batch.Status = "Reopened";
        batch.ModifiedBy = request.ReopenedBy;
        batch.ModifiedDate = DateTime.UtcNow;

        await _batchRepository.UpdateAsync(batch);

        var invoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
        var totalAmount = invoices.Sum(inv => inv.Amount);

        _logger.LogInformation("Successfully reopened batch {BatchId}", batch.BatchId);
        return MapBatchToResponse(batch, invoices.Count(), totalAmount);
    }

    public async Task<FundingBatchResponse> UpdateAsync(UpdateFundingBatchRequest request)
    {
        // Validate request
        var validationResult = await _updateValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Updating funding batch {BatchId}", request.BatchId);

        var batch = await _batchRepository.GetByIdAsync(request.BatchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Funding batch not found: {request.BatchId}");
        }

        // Update fields
        if (request.Status != null)
        {
            batch.Status = request.Status;
        }

        if (request.Description != null)
        {
            batch.Description = request.Description;
        }

        if (request.FundingCashInOutRef != null)
        {
            batch.FundingCashInOutId = request.FundingCashInOutRef;
        }

        batch.ModifiedBy = request.ModifiedBy;
        batch.ModifiedDate = DateTime.UtcNow;

        await _batchRepository.UpdateAsync(batch);

        var invoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
        var totalAmount = invoices.Sum(inv => inv.Amount);

        _logger.LogInformation("Successfully updated batch {BatchId}", batch.BatchId);
        return MapBatchToResponse(batch, invoices.Count(), totalAmount);
    }

    public async Task<FundingBatchResponse> CreateAsync(CreateFundingBatchRequest request)
    {
        // Validate request
        var validationResult = await _createValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Creating funding batch for Subaccount={SubaccountId}, Status={Status}", 
            request.SubaccountId, request.Status);

        var batch = new FundingBatch
        {
            BatchId = Guid.NewGuid().ToString(),
            SubaccountId = request.SubaccountId,
            Status = request.Status,
            Description = request.Description,
            CreatedBy = request.CreatedBy,
            CreatedDate = DateTime.UtcNow
        };

        await _batchRepository.CreateAsync(batch);

        _logger.LogInformation("Successfully created batch {BatchId}", batch.BatchId);
        return MapBatchToResponse(batch, 0, 0m);
    }

    public async Task<FundingBatchResponse?> GetByIdAsync(string batchId)
    {
        var batch = await _batchRepository.GetByIdAsync(batchId);
        if (batch == null) return null;

        var invoices = await _invoiceRepository.GetByBatchIdAsync(batchId);
        var totalAmount = invoices.Sum(inv => inv.Amount);

        return MapBatchToResponse(batch, invoices.Count(), totalAmount);
    }

    public async Task<IEnumerable<FundingBatchResponse>> GetBySubaccountIdAsync(string subaccountId)
    {
        var batches = await _batchRepository.GetBySubaccountIdAsync(subaccountId);
        var responses = new List<FundingBatchResponse>();

        foreach (var batch in batches)
        {
            var invoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
            var totalAmount = invoices.Sum(inv => inv.Amount);
            responses.Add(MapBatchToResponse(batch, invoices.Count(), totalAmount));
        }

        return responses;
    }

    public async Task<FundingBatchResponse?> GetOpenBatchAsync(string subaccountId)
    {
        var openBatches = await _batchRepository.GetByStatusAsync("Open");
        var batch = openBatches.FirstOrDefault(b => b.SubaccountId == subaccountId);

        if (batch == null) return null;

        var invoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
        var totalAmount = invoices.Sum(inv => inv.Amount);

        return MapBatchToResponse(batch, invoices.Count(), totalAmount);
    }

    private FundingBatchResponse MapBatchToResponse(FundingBatch batch, int invoiceCount, decimal totalAmount)
    {
        return new FundingBatchResponse
        {
            BatchId = batch.BatchId,
            SubaccountId = batch.SubaccountId,
            Status = batch.Status,
            Description = batch.Description,
            FundingCashInOutId = batch.FundingCashInOutId,
            CreatedDate = batch.CreatedDate,
            CreatedBy = batch.CreatedBy,
            ModifiedDate = batch.ModifiedDate,
            ModifiedBy = batch.ModifiedBy,
            InvoiceCount = invoiceCount,
            TotalAmount = totalAmount
        };
    }
}
