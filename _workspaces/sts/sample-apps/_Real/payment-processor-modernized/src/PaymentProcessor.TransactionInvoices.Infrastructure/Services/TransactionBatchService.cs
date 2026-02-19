using FluentValidation;
using Microsoft.Extensions.Logging;
using PaymentProcessor.TransactionInvoices.Core.Adapters;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Repositories;
using PaymentProcessor.TransactionInvoices.Core.Services;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Services;

/// <summary>
/// Implementation of transaction batch business logic service.
/// Extracts logic from XCloseTransactionBatch, XUpdateTransactionBatch, XReopenTransactionBatch.
/// </summary>
public class TransactionBatchService : ITransactionBatchService
{
    private readonly ITransactionBatchRepository _batchRepository;
    private readonly ITransactionInvoiceRepository _invoiceRepository;
    private readonly IAccountCategoryRepository _account_categoryRepository;
    private readonly ICashInOutRepository _cashInOutRepository;
    private readonly IPaymentPlanAdapter _paragonAdapter;
    private readonly IValidator<CloseTransactionBatchRequest> _closeValidator;
    private readonly IValidator<ReopenTransactionBatchRequest> _reopenValidator;
    private readonly IValidator<UpdateTransactionBatchRequest> _updateValidator;
    private readonly IValidator<CreateTransactionBatchRequest> _createValidator;
    private readonly ILogger<TransactionBatchService> _logger;

    public TransactionBatchService(
        ITransactionBatchRepository batchRepository,
        ITransactionInvoiceRepository invoiceRepository,
        IAccountCategoryRepository account_categoryRepository,
        ICashInOutRepository cashInOutRepository,
        IPaymentPlanAdapter paragonAdapter,
        IValidator<CloseTransactionBatchRequest> closeValidator,
        IValidator<ReopenTransactionBatchRequest> reopenValidator,
        IValidator<UpdateTransactionBatchRequest> updateValidator,
        IValidator<CreateTransactionBatchRequest> createValidator,
        ILogger<TransactionBatchService> logger)
    {
        _batchRepository = batchRepository;
        _invoiceRepository = invoiceRepository;
        _account_categoryRepository = account_categoryRepository;
        _cashInOutRepository = cashInOutRepository;
        _paragonAdapter = paragonAdapter;
        _closeValidator = closeValidator;
        _reopenValidator = reopenValidator;
        _updateValidator = updateValidator;
        _createValidator = createValidator;
        _logger = logger;
    }

    public async Task<CloseTransactionBatchResponse> CloseAsync(CloseTransactionBatchRequest request)
    {
        // Validate request
        var validationResult = await _closeValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Closing transaction batch {BatchId}, Excluded invoices: {ExcludedCount}", 
            request.BatchId, request.ExcludedInvoiceIds.Count);

        // Get the batch to close
        var batch = await _batchRepository.GetByIdAsync(request.BatchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Transaction batch not found: {request.BatchId}");
        }

        // Get account_category and payment plans
        var account_category = await _account_categoryRepository.GetByIdAsync(batch.AccountCategoryId);
        if (account_category == null)
        {
            throw new InvalidOperationException($"AccountCategory not found: {batch.AccountCategoryId}");
        }

        var plans = await _paragonAdapter.GetPaymentPlansAsync(batch.AccountCategoryId);
        if (!plans.Any())
        {
            throw new InvalidOperationException($"No payment plans found for account_category {batch.AccountCategoryId}");
        }

        var firstPlan = plans.First();

        // Handle status-specific logic
        if (batch.Status == "Open")
        {
            // Create new pending batch
            var newPendingBatch = new TransactionBatch
            {
                BatchId = Guid.NewGuid().ToString(),
                AccountCategoryId = batch.AccountCategoryId,
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
                var openBatch = openBatches.FirstOrDefault(b => b.AccountCategoryId == batch.AccountCategoryId);

                if (openBatch == null)
                {
                    openBatch = new TransactionBatch
                    {
                        BatchId = Guid.NewGuid().ToString(),
                        AccountCategoryId = batch.AccountCategoryId,
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
            throw new InvalidOperationException("PaymentProcessor Transaction invoices must be non-zero. Transaction Batch will be reopened.");
        }

        // Create replenishment CashInOut
        var cashInOut = new CashInOut
        {
            CashInOutId = Guid.NewGuid().ToString(),
            TransactionType = "PaymentProcessorTransaction",
            Amount = -batchTotal, // Negative for replenishment
            TransactionDate = DateTime.Today,
            Description = $"PaymentProcessor Replenishment for {firstPlan.PlanShortDescription}",
            CreatedBy = request.ClosedBy,
            CreatedDate = DateTime.UtcNow
        };

        await _cashInOutRepository.CreateAsync(cashInOut);
        _logger.LogInformation("Created replenishment CashInOut {CashInOutId} for {Amount:C}", 
            cashInOut.CashInOutId, cashInOut.Amount);

        // Update batch with CashInOut reference and mark as closed
        batch.TransactionCashInOutId = cashInOut.CashInOutId;
        batch.Status = "Closed";
        batch.ModifiedBy = request.ClosedBy;
        batch.ModifiedDate = DateTime.UtcNow;
        await _batchRepository.UpdateAsync(batch);

        // Process auto-debit if enabled
        var paymentAuths = await _paragonAdapter.GetPaymentAuthorizationsAsync(
            firstPlan.EmployerId,
            batch.AccountCategoryId,
            plans.Select(p => p.PaymentPlanId).ToList()
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

        var response = new CloseTransactionBatchResponse
        {
            Batch = MapBatchToResponse(batch, includedBatchInvoices.Count, batchTotal),
            CashInOutId = cashInOut.CashInOutId,
            CashInOutAmount = cashInOut.Amount,
            PaymentId = paymentId,
            AutoDebitProcessed = autoDebitProcessed
        };

        _logger.LogInformation("Successfully closed transaction batch {BatchId}", batch.BatchId);
        return response;
    }

    public async Task<TransactionBatchResponse> ReopenAsync(ReopenTransactionBatchRequest request)
    {
        // Validate request
        var validationResult = await _reopenValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Reopening transaction batch {BatchId}", request.BatchId);

        var batch = await _batchRepository.GetByIdAsync(request.BatchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Transaction batch not found: {request.BatchId}");
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

    public async Task<TransactionBatchResponse> UpdateAsync(UpdateTransactionBatchRequest request)
    {
        // Validate request
        var validationResult = await _updateValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Updating transaction batch {BatchId}", request.BatchId);

        var batch = await _batchRepository.GetByIdAsync(request.BatchId);
        if (batch == null)
        {
            throw new InvalidOperationException($"Transaction batch not found: {request.BatchId}");
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

        if (request.TransactionCashInOutRef != null)
        {
            batch.TransactionCashInOutId = request.TransactionCashInOutRef;
        }

        batch.ModifiedBy = request.ModifiedBy;
        batch.ModifiedDate = DateTime.UtcNow;

        await _batchRepository.UpdateAsync(batch);

        var invoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
        var totalAmount = invoices.Sum(inv => inv.Amount);

        _logger.LogInformation("Successfully updated batch {BatchId}", batch.BatchId);
        return MapBatchToResponse(batch, invoices.Count(), totalAmount);
    }

    public async Task<TransactionBatchResponse> CreateAsync(CreateTransactionBatchRequest request)
    {
        // Validate request
        var validationResult = await _createValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Creating transaction batch for AccountCategory={AccountCategoryId}, Status={Status}", 
            request.AccountCategoryId, request.Status);

        var batch = new TransactionBatch
        {
            BatchId = Guid.NewGuid().ToString(),
            AccountCategoryId = request.AccountCategoryId,
            Status = request.Status,
            Description = request.Description,
            CreatedBy = request.CreatedBy,
            CreatedDate = DateTime.UtcNow
        };

        await _batchRepository.CreateAsync(batch);

        _logger.LogInformation("Successfully created batch {BatchId}", batch.BatchId);
        return MapBatchToResponse(batch, 0, 0m);
    }

    public async Task<TransactionBatchResponse?> GetByIdAsync(string batchId)
    {
        var batch = await _batchRepository.GetByIdAsync(batchId);
        if (batch == null) return null;

        var invoices = await _invoiceRepository.GetByBatchIdAsync(batchId);
        var totalAmount = invoices.Sum(inv => inv.Amount);

        return MapBatchToResponse(batch, invoices.Count(), totalAmount);
    }

    public async Task<IEnumerable<TransactionBatchResponse>> GetByAccountCategoryIdAsync(string account_categoryId)
    {
        var batches = await _batchRepository.GetByAccountCategoryIdAsync(account_categoryId);
        var responses = new List<TransactionBatchResponse>();

        foreach (var batch in batches)
        {
            var invoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
            var totalAmount = invoices.Sum(inv => inv.Amount);
            responses.Add(MapBatchToResponse(batch, invoices.Count(), totalAmount));
        }

        return responses;
    }

    public async Task<TransactionBatchResponse?> GetOpenBatchAsync(string account_categoryId)
    {
        var openBatches = await _batchRepository.GetByStatusAsync("Open");
        var batch = openBatches.FirstOrDefault(b => b.AccountCategoryId == account_categoryId);

        if (batch == null) return null;

        var invoices = await _invoiceRepository.GetByBatchIdAsync(batch.BatchId);
        var totalAmount = invoices.Sum(inv => inv.Amount);

        return MapBatchToResponse(batch, invoices.Count(), totalAmount);
    }

    private TransactionBatchResponse MapBatchToResponse(TransactionBatch batch, int invoiceCount, decimal totalAmount)
    {
        return new TransactionBatchResponse
        {
            BatchId = batch.BatchId,
            AccountCategoryId = batch.AccountCategoryId,
            Status = batch.Status,
            Description = batch.Description,
            TransactionCashInOutId = batch.TransactionCashInOutId,
            CreatedDate = batch.CreatedDate,
            CreatedBy = batch.CreatedBy,
            ModifiedDate = batch.ModifiedDate,
            ModifiedBy = batch.ModifiedBy,
            InvoiceCount = invoiceCount,
            TotalAmount = totalAmount
        };
    }
}
