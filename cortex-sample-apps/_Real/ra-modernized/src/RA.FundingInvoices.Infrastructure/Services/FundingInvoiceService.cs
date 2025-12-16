using FluentValidation;
using Microsoft.Extensions.Logging;
using RA.FundingInvoices.Core.Adapters;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Repositories;
using RA.FundingInvoices.Core.Services;

namespace RA.FundingInvoices.Infrastructure.Services;

/// <summary>
/// Implementation of funding invoice business logic service.
/// Extracts logic from XGenerateFundingInvoice, XAddFundingInvoice, Updater_CreateRAFundingInvoices.
/// </summary>
public class FundingInvoiceService : IFundingInvoiceService
{
    private readonly IFundingInvoiceRepository _invoiceRepository;
    private readonly IFundingBatchRepository _batchRepository;
    private readonly ISubaccountRepository _subaccountRepository;
    private readonly ICashInOutRepository _cashInOutRepository;
    private readonly IReimbursementPlanAdapter _paragonAdapter;
    private readonly IValidator<CreateFundingInvoiceRequest> _createValidator;
    private readonly IValidator<GenerateFundingInvoiceRequest> _generateValidator;
    private readonly IValidator<CreateBatchFundingInvoiceRequest> _batchValidator;
    private readonly ILogger<FundingInvoiceService> _logger;

    public FundingInvoiceService(
        IFundingInvoiceRepository invoiceRepository,
        IFundingBatchRepository batchRepository,
        ISubaccountRepository subaccountRepository,
        ICashInOutRepository cashInOutRepository,
        IReimbursementPlanAdapter paragonAdapter,
        IValidator<CreateFundingInvoiceRequest> createValidator,
        IValidator<GenerateFundingInvoiceRequest> generateValidator,
        IValidator<CreateBatchFundingInvoiceRequest> batchValidator,
        ILogger<FundingInvoiceService> logger)
    {
        _invoiceRepository = invoiceRepository;
        _batchRepository = batchRepository;
        _subaccountRepository = subaccountRepository;
        _cashInOutRepository = cashInOutRepository;
        _paragonAdapter = paragonAdapter;
        _createValidator = createValidator;
        _generateValidator = generateValidator;
        _batchValidator = batchValidator;
        _logger = logger;
    }

    public async Task<FundingInvoiceResponse> CreateAsync(CreateFundingInvoiceRequest request)
    {
        // Validate request
        var validationResult = await _createValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Creating funding invoice for Employer={EmployerId}, Subaccount={SubaccountId}", 
            request.EmployerId, request.SubaccountId);

        // Verify subaccount exists
        var subaccount = await _subaccountRepository.GetByIdAsync(request.SubaccountId);
        if (subaccount == null)
        {
            throw new InvalidOperationException($"Subaccount not found: {request.SubaccountId}");
        }

        // Calculate total invoice amount
        decimal invoiceTotal = request.EmployerFundingDefault + request.EmployeeFundingDefault;

        // Create CashInOut entity
        var cashInOut = new CashInOut
        {
            CashInOutId = Guid.NewGuid().ToString(),
            TransactionType = "RAFunding",
            Amount = invoiceTotal,
            TransactionDate = request.EffectiveDate,
            Description = request.InvoiceDescription,
            CreatedBy = request.CreatedBy,
            CreatedDate = DateTime.UtcNow
        };

        await _cashInOutRepository.CreateAsync(cashInOut);
        _logger.LogInformation("Created CashInOut {CashInOutId} for amount {Amount:C}", cashInOut.CashInOutId, invoiceTotal);

        // Create funding invoice
        var invoice = new FundingInvoice
        {
            InvoiceId = Guid.NewGuid().ToString(),
            SubaccountId = request.SubaccountId,
            BatchId = string.Empty, // Will be set when added to a batch
            InvoiceNumber = GenerateInvoiceNumber(),
            Amount = invoiceTotal,
            Status = "Pending",
            Description = request.InvoiceDescription,
            InvoiceDate = request.EffectiveDate,
            DueDate = request.EffectiveDate.AddDays(30),
            CreatedBy = request.CreatedBy,
            CreatedDate = DateTime.UtcNow
        };

        await _invoiceRepository.CreateAsync(invoice);
        _logger.LogInformation("Created funding invoice {InvoiceId} with number {InvoiceNumber}", 
            invoice.InvoiceId, invoice.InvoiceNumber);

        return MapToResponse(invoice);
    }

    public async Task<GenerateFundingInvoiceResponse> GenerateAsync(GenerateFundingInvoiceRequest request)
    {
        // Validate request
        var validationResult = await _generateValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Generating on-demand funding invoice for Subaccount={SubaccountId}, Amount={Amount:C}", 
            request.SubaccountId, request.InvoiceAmount);

        var response = new GenerateFundingInvoiceResponse
        {
            Result = "invoice not needed"
        };

        // Verify subaccount exists
        var subaccount = await _subaccountRepository.GetByIdAsync(request.SubaccountId);
        if (subaccount == null)
        {
            throw new InvalidOperationException($"Subaccount not found: {request.SubaccountId}");
        }

        // Get reimbursement plans from Paragon
        var plans = await _paragonAdapter.GetReimbursementPlansAsync(request.SubaccountId);
        if (!plans.Any())
        {
            _logger.LogWarning("No reimbursement plans found for subaccount {SubaccountId}", request.SubaccountId);
            return response;
        }

        var firstPlan = plans.First();

        // Calculate pending amount (mock calculation - in real WCF this queries TransferLines)
        decimal pendingAmount = 0m; // TODO: Query actual pending transfers

        // Check if current balance + pending is below peg amount
        // Mock peg amount logic - in real WCF this comes from FundingFrequency
        decimal pegAmount = 1000m; // TODO: Get from FundingFrequency

        if (pegAmount > (subaccount.Balance + pendingAmount))
        {
            _logger.LogInformation("Balance ({Balance:C}) + Pending ({Pending:C}) is below peg amount ({PegAmount:C}). Creating invoice.", 
                subaccount.Balance, pendingAmount, pegAmount);

            // Create CashInOut
            var cashInOut = new CashInOut
            {
                CashInOutId = Guid.NewGuid().ToString(),
                TransactionType = "RAFunding",
                Amount = request.InvoiceAmount,
                TransactionDate = request.InvoiceDate,
                Description = $"RA Prefunding for {firstPlan.PlanShortDescription}",
                CreatedBy = request.CreatedBy,
                CreatedDate = DateTime.UtcNow
            };

            await _cashInOutRepository.CreateAsync(cashInOut);

            // Create funding invoice
            var invoice = new FundingInvoice
            {
                InvoiceId = Guid.NewGuid().ToString(),
                SubaccountId = request.SubaccountId,
                BatchId = string.Empty,
                InvoiceNumber = GenerateInvoiceNumber(),
                Amount = request.InvoiceAmount,
                Status = "Pending",
                Description = cashInOut.Description,
                InvoiceDate = request.InvoiceDate,
                DueDate = request.InvoiceDate.AddDays(30),
                CreatedBy = request.CreatedBy,
                CreatedDate = DateTime.UtcNow
            };

            await _invoiceRepository.CreateAsync(invoice);

            // Check for auto-debit payment authorization
            var paymentAuths = await _paragonAdapter.GetPaymentAuthorizationsAsync(
                firstPlan.EmployerId, 
                request.SubaccountId, 
                plans.Select(p => p.ReimbursementPlanId).ToList()
            );

            var autoDebitAuth = paymentAuths.FirstOrDefault(pa => pa.IsAutoDebit && !string.IsNullOrEmpty(pa.PaymentAuthorizationId));
            string? paymentId = null;

            if (autoDebitAuth != null)
            {
                _logger.LogInformation("Auto-debit enabled. Processing payment for {Amount:C}", request.InvoiceAmount);
                // TODO: Phase 4 - Create Payment entity and link to CashInOut
                paymentId = $"PAYMENT-{Guid.NewGuid():N}";
            }

            response.Result = "invoice created";
            response.CashInOutId = cashInOut.CashInOutId;
            response.Invoice = MapToResponse(invoice);
            response.PaymentId = paymentId;

            _logger.LogInformation("Successfully generated funding invoice {InvoiceId}", invoice.InvoiceId);
        }
        else
        {
            _logger.LogInformation("Peg amount check not met. Invoice not needed.");
        }

        return response;
    }

    public async Task<BatchFundingInvoiceResponse> CreateBatchAsync(CreateBatchFundingInvoiceRequest request)
    {
        // Validate request
        var validationResult = await _batchValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Creating batch funding invoices. Employer filter: {EmployerCount} employers", request.EmployerIds.Count);

        var response = new BatchFundingInvoiceResponse();

        // Get all PreFunding subaccounts
        var allSubaccounts = await _subaccountRepository.GetByAccountTypeAsync("PreFunding");
        
        // Filter by employer IDs if specified
        var subaccounts = request.EmployerIds.Any()
            ? allSubaccounts.Where(sa => request.EmployerIds.Contains(sa.AccountNumber)).ToList()
            : allSubaccounts.ToList();

        _logger.LogInformation("Found {Count} subaccounts to process", subaccounts.Count);
        response.TotalProcessed = subaccounts.Count;

        foreach (var subaccount in subaccounts)
        {
            try
            {
                // Check if invoice already created today
                var existingInvoices = await _invoiceRepository.GetBySubaccountIdAsync(subaccount.SubaccountId);
                if (existingInvoices.Any(inv => inv.InvoiceDate.Date == DateTime.Today))
                {
                    _logger.LogInformation("Invoice already created today for subaccount {SubaccountId}. Skipping.", subaccount.SubaccountId);
                    response.SkippedCount++;
                    response.Results.Add(new SubaccountProcessingResult
                    {
                        SubaccountId = subaccount.SubaccountId,
                        EmployerId = subaccount.AccountNumber,
                        Success = true,
                        ErrorMessage = "Already processed today"
                    });
                    continue;
                }

                // Find open funding batch
                var openBatch = await _batchRepository.GetByStatusAsync("Open");
                var subaccountBatch = openBatch.FirstOrDefault(b => b.SubaccountId == subaccount.SubaccountId);

                if (subaccountBatch == null)
                {
                    _logger.LogWarning("No open funding batch found for subaccount {SubaccountId}. Skipping.", subaccount.SubaccountId);
                    response.SkippedCount++;
                    response.Results.Add(new SubaccountProcessingResult
                    {
                        SubaccountId = subaccount.SubaccountId,
                        EmployerId = subaccount.AccountNumber,
                        Success = true,
                        ErrorMessage = "No open batch found"
                    });
                    continue;
                }

                // Close the batch (this creates the replenishment invoice)
                // TODO: Call IFundingBatchService.CloseAsync once implemented
                _logger.LogInformation("Processing batch closure for subaccount {SubaccountId}, Batch {BatchId}", 
                    subaccount.SubaccountId, subaccountBatch.BatchId);

                response.SuccessCount++;
                response.Results.Add(new SubaccountProcessingResult
                {
                    SubaccountId = subaccount.SubaccountId,
                    EmployerId = subaccount.AccountNumber,
                    Success = true,
                    CashInOutId = $"CIO-{Guid.NewGuid():N}", // Placeholder
                    Amount = 0m // Will be set by batch closure
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create funding invoice for subaccount {SubaccountId}", subaccount.SubaccountId);
                response.FailureCount++;
                response.Results.Add(new SubaccountProcessingResult
                {
                    SubaccountId = subaccount.SubaccountId,
                    EmployerId = subaccount.AccountNumber,
                    Success = false,
                    ErrorMessage = ex.Message
                });
            }
        }

        _logger.LogInformation("Batch processing complete. Success: {Success}, Failed: {Failed}, Skipped: {Skipped}", 
            response.SuccessCount, response.FailureCount, response.SkippedCount);

        return response;
    }

    public async Task<BatchInvoiceResultDto> CreateBatchInvoicesAsync(CreateBatchInvoicesDto dto)
    {
        _logger.LogInformation("Creating batch invoices for Employer={EmployerId}, SubaccountCount={Count}", 
            dto.EmployerId, dto.SubaccountIds.Count);

        var result = new BatchInvoiceResultDto
        {
            BatchId = Guid.NewGuid(),
            TotalInvoices = dto.SubaccountIds.Count
        };

        // Create funding batch first
        var batch = new FundingBatch
        {
            BatchId = result.BatchId.ToString(),
            EmployerId = dto.EmployerId,
            BatchNumber = GenerateBatchNumber(),
            Status = "Pending",
            TotalAmount = 0m,
            Description = dto.Description ?? $"Batch created {DateTime.UtcNow:yyyy-MM-dd}",
            CreatedDate = DateTime.UtcNow,
            CreatedBy = "System"
        };

        await _batchRepository.CreateAsync(batch);

        // Process each subaccount
        foreach (var subaccountId in dto.SubaccountIds)
        {
            try
            {
                // Get subaccount
                var subaccount = await _subaccountRepository.GetByIdAsync(subaccountId.ToString());
                if (subaccount == null)
                {
                    result.FailureCount++;
                    result.FailedSubaccounts.Add(new FailedInvoiceDto
                    {
                        SubaccountId = subaccountId,
                        Reason = "Subaccount not found",
                        ErrorType = "NotFound"
                    });
                    continue;
                }

                // Check for existing invoice with same effective date (duplicate prevention)
                var existingInvoices = await _invoiceRepository.GetBySubaccountIdAsync(subaccount.SubaccountId);
                if (existingInvoices.Any(i => i.InvoiceDate.Date == dto.EffectiveDate.Date))
                {
                    _logger.LogInformation("Skipping subaccount {SubaccountId} - invoice already exists for {Date}", 
                        subaccountId, dto.EffectiveDate);
                    result.FailureCount++;
                    result.FailedSubaccounts.Add(new FailedInvoiceDto
                    {
                        SubaccountId = subaccountId,
                        Reason = "Invoice already exists for this effective date",
                        ErrorType = "Duplicate"
                    });
                    continue;
                }

                // Get reimbursement plans to calculate peg amount
                var plans = await _paragonAdapter.GetReimbursementPlansAsync(subaccount.SubaccountId);
                if (!plans.Any())
                {
                    result.FailureCount++;
                    result.FailedSubaccounts.Add(new FailedInvoiceDto
                    {
                        SubaccountId = subaccountId,
                        Reason = "No reimbursement plans found",
                        ErrorType = "MissingData"
                    });
                    continue;
                }

                var plan = plans.First();

                // Calculate peg amount (invoice amount - current balance)
                // In production, InvoiceAmount would come from plan configuration
                decimal invoiceAmount = plan.Balance > 0 ? 1000m : 500m; // Mock logic
                decimal currentBalance = plan.Balance;
                decimal pegAmount = invoiceAmount - currentBalance;

                // Only create invoice if peg > 0 (balance below peg)
                if (pegAmount <= 0)
                {
                    _logger.LogInformation("Skipping subaccount {SubaccountId} - balance meets peg (Balance: {Balance:C}, Peg: {Peg:C})", 
                        subaccountId, currentBalance, pegAmount);
                    result.FailureCount++;
                    result.FailedSubaccounts.Add(new FailedInvoiceDto
                    {
                        SubaccountId = subaccountId,
                        Reason = "Balance meets peg requirement",
                        ErrorType = "NotNeeded"
                    });
                    continue;
                }

                // Create funding invoice
                var invoice = new FundingInvoice
                {
                    InvoiceId = Guid.NewGuid().ToString(),
                    SubaccountId = subaccount.SubaccountId,
                    BatchId = batch.BatchId,
                    InvoiceNumber = GenerateInvoiceNumber(),
                    Amount = pegAmount,
                    Status = "Pending",
                    Description = dto.Description ?? $"Batch invoice {batch.BatchNumber}",
                    InvoiceDate = dto.EffectiveDate,
                    DueDate = dto.EffectiveDate.AddDays(30),
                    CreatedBy = "System",
                    CreatedDate = DateTime.UtcNow
                };

                await _invoiceRepository.CreateAsync(invoice);
                result.SuccessCount++;
                batch.TotalAmount += pegAmount;

                _logger.LogInformation("Created invoice {InvoiceId} for subaccount {SubaccountId}, Amount: {Amount:C}", 
                    invoice.InvoiceId, subaccountId, pegAmount);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create invoice for subaccount {SubaccountId}", subaccountId);
                result.FailureCount++;
                result.FailedSubaccounts.Add(new FailedInvoiceDto
                {
                    SubaccountId = subaccountId,
                    Reason = ex.Message,
                    ErrorType = "Exception"
                });
            }
        }

        // Update batch with final total
        batch.TotalAmount = batch.TotalAmount;
        await _batchRepository.UpdateAsync(batch);

        _logger.LogInformation("Batch {BatchId} created. Total: {SuccessCount} invoices, {FailureCount} failures", 
            result.BatchId, result.SuccessCount, result.FailureCount);

        return result;
    }

    public async Task<GenerateFundingInvoiceResultDto> GenerateFundingInvoiceAsync(GenerateFundingInvoiceDto dto)
    {
        _logger.LogInformation("Generating funding invoice for Subaccount={SubaccountId}, Amount={Amount:C}", 
            dto.SubaccountId, dto.InvoiceAmount);

        var result = new GenerateFundingInvoiceResultDto
        {
            InvoiceCreated = false,
            Reason = "Balance meets peg requirement",
            PegAmount = 0m
        };

        // Verify subaccount exists
        var subaccount = await _subaccountRepository.GetByIdAsync(dto.SubaccountId.ToString());
        if (subaccount == null)
        {
            throw new InvalidOperationException($"Subaccount not found: {dto.SubaccountId}");
        }

        // Get reimbursement plans from Paragon
        var plans = await _paragonAdapter.GetReimbursementPlansAsync(subaccount.SubaccountId);
        if (!plans.Any())
        {
            _logger.LogWarning("No reimbursement plans found for subaccount {SubaccountId}", dto.SubaccountId);
            result.Reason = "No reimbursement plans found";
            return result;
        }

        var plan = plans.First();

        // Calculate peg amount: InvoiceAmount - CurrentBalance
        decimal currentBalance = plan.Balance;
        decimal pegAmount = dto.InvoiceAmount - currentBalance;

        result.PegAmount = pegAmount;

        // Only create invoice if peg > 0 (balance below peg)
        if (pegAmount <= 0)
        {
            _logger.LogInformation("Invoice not needed for subaccount {SubaccountId}. Balance {Balance:C} meets or exceeds invoice amount {Amount:C}", 
                dto.SubaccountId, currentBalance, dto.InvoiceAmount);
            result.Reason = "Balance meets peg requirement";
            return result;
        }

        // Create funding invoice with peg amount
        var invoice = new FundingInvoice
        {
            InvoiceId = Guid.NewGuid().ToString(),
            SubaccountId = subaccount.SubaccountId,
            BatchId = string.Empty, // Not part of a batch
            InvoiceNumber = GenerateInvoiceNumber(),
            Amount = pegAmount,
            Status = subaccount.AccountNumber.Contains("AutoDebit") ? "Pending" : "Open", // Mock auto-debit check
            Description = dto.Description ?? $"On-demand peg invoice - {DateTime.UtcNow:yyyy-MM-dd}",
            InvoiceDate = dto.EffectiveDate,
            DueDate = dto.EffectiveDate.AddDays(30),
            CreatedBy = "System",
            CreatedDate = DateTime.UtcNow
        };

        await _invoiceRepository.CreateAsync(invoice);

        // If auto-debit enabled, create payment record (effective date + 2 business days)
        if (subaccount.AccountNumber.Contains("AutoDebit")) // Mock auto-debit check
        {
            var paymentDate = AddBusinessDays(dto.EffectiveDate, 2);

            var payment = new CashInOut
            {
                CashInOutId = Guid.NewGuid().ToString(),
                TransactionType = "RAFundingPayment",
                Amount = pegAmount,
                TransactionDate = paymentDate,
                Description = $"Auto-debit payment for invoice {invoice.InvoiceNumber}",
                CreatedBy = "System",
                CreatedDate = DateTime.UtcNow
            };

            await _cashInOutRepository.CreateAsync(payment);

            _logger.LogInformation("Created auto-debit payment {PaymentId} for invoice {InvoiceId}, scheduled for {PaymentDate}", 
                payment.CashInOutId, invoice.InvoiceId, paymentDate);
        }

        result.InvoiceId = Guid.Parse(invoice.InvoiceId);
        result.InvoiceCreated = true;
        result.Reason = "Balance below peg amount";

        _logger.LogInformation("Created funding invoice {InvoiceId} for subaccount {SubaccountId}, Peg amount: {PegAmount:C}", 
            invoice.InvoiceId, dto.SubaccountId, pegAmount);

        return result;
    }

    public async Task<FundingInvoiceResponse?> GetByIdAsync(string invoiceId)
    {
        var invoice = await _invoiceRepository.GetByIdAsync(invoiceId);
        return invoice != null ? MapToResponse(invoice) : null;
    }

    public async Task<IEnumerable<FundingInvoiceResponse>> GetByBatchIdAsync(string batchId)
    {
        var invoices = await _invoiceRepository.GetByBatchIdAsync(batchId);
        return invoices.Select(MapToResponse);
    }

    public async Task<IEnumerable<FundingInvoiceResponse>> GetBySubaccountIdAsync(string subaccountId)
    {
        var invoices = await _invoiceRepository.GetBySubaccountIdAsync(subaccountId);
        return invoices.Select(MapToResponse);
    }

    private FundingInvoiceResponse MapToResponse(FundingInvoice invoice)
    {
        return new FundingInvoiceResponse
        {
            InvoiceId = invoice.InvoiceId,
            BatchId = invoice.BatchId,
            SubaccountId = invoice.SubaccountId,
            InvoiceNumber = invoice.InvoiceNumber,
            Amount = invoice.Amount,
            Status = invoice.Status,
            Description = invoice.Description,
            InvoiceDate = invoice.InvoiceDate,
            DueDate = invoice.DueDate,
            CreatedDate = invoice.CreatedDate,
            CreatedBy = invoice.CreatedBy
        };
    }

    private string GenerateInvoiceNumber()
    {
        // Generate invoice number: INV-YYYYMMDD-GUID
        return $"INV-{DateTime.UtcNow:yyyyMMdd}-{Guid.NewGuid():N[..8]}";
    }

    private string GenerateBatchNumber()
    {
        // Generate batch number: BATCH-YYYYMMDD-GUID
        return $"BATCH-{DateTime.UtcNow:yyyyMMdd}-{Guid.NewGuid():N[..8]}";
    }

    private DateTime AddBusinessDays(DateTime startDate, int businessDays)
    {
        var currentDate = startDate;
        var daysAdded = 0;

        while (daysAdded < businessDays)
        {
            currentDate = currentDate.AddDays(1);
            // Skip weekends (Saturday = 6, Sunday = 0)
            if (currentDate.DayOfWeek != DayOfWeek.Saturday && currentDate.DayOfWeek != DayOfWeek.Sunday)
            {
                daysAdded++;
            }
        }

        return currentDate;
    }
}
