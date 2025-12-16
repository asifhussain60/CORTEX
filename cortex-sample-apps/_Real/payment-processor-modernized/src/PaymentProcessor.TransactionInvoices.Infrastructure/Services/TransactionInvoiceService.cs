using FluentValidation;
using Microsoft.Extensions.Logging;
using PaymentProcessor.TransactionInvoices.Core.Adapters;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Repositories;
using PaymentProcessor.TransactionInvoices.Core.Services;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Services;

/// <summary>
/// Implementation of transaction invoice business logic service.
/// Extracts logic from XGenerateTransactionInvoice, XAddTransactionInvoice, Updater_CreatePaymentTransactionInvoices.
/// </summary>
public class TransactionInvoiceService : ITransactionInvoiceService
{
    private readonly ITransactionInvoiceRepository _invoiceRepository;
    private readonly ITransactionBatchRepository _batchRepository;
    private readonly IAccountCategoryRepository _account_categoryRepository;
    private readonly ICashInOutRepository _cashInOutRepository;
    private readonly IPaymentPlanAdapter _paragonAdapter;
    private readonly IValidator<CreateTransactionInvoiceRequest> _createValidator;
    private readonly IValidator<GenerateTransactionInvoiceRequest> _generateValidator;
    private readonly IValidator<CreateBatchTransactionInvoiceRequest> _batchValidator;
    private readonly ILogger<TransactionInvoiceService> _logger;

    public TransactionInvoiceService(
        ITransactionInvoiceRepository invoiceRepository,
        ITransactionBatchRepository batchRepository,
        IAccountCategoryRepository account_categoryRepository,
        ICashInOutRepository cashInOutRepository,
        IPaymentPlanAdapter paragonAdapter,
        IValidator<CreateTransactionInvoiceRequest> createValidator,
        IValidator<GenerateTransactionInvoiceRequest> generateValidator,
        IValidator<CreateBatchTransactionInvoiceRequest> batchValidator,
        ILogger<TransactionInvoiceService> logger)
    {
        _invoiceRepository = invoiceRepository;
        _batchRepository = batchRepository;
        _account_categoryRepository = account_categoryRepository;
        _cashInOutRepository = cashInOutRepository;
        _paragonAdapter = paragonAdapter;
        _createValidator = createValidator;
        _generateValidator = generateValidator;
        _batchValidator = batchValidator;
        _logger = logger;
    }

    public async Task<TransactionInvoiceResponse> CreateAsync(CreateTransactionInvoiceRequest request)
    {
        // Validate request
        var validationResult = await _createValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Creating transaction invoice for Employer={EmployerId}, AccountCategory={AccountCategoryId}", 
            request.EmployerId, request.AccountCategoryId);

        // Verify account_category exists
        var account_category = await _account_categoryRepository.GetByIdAsync(request.AccountCategoryId);
        if (account_category == null)
        {
            throw new InvalidOperationException($"AccountCategory not found: {request.AccountCategoryId}");
        }

        // Calculate total invoice amount
        decimal invoiceTotal = request.EmployerTransactionDefault + request.EmployeeTransactionDefault;

        // Create CashInOut entity
        var cashInOut = new CashInOut
        {
            CashInOutId = Guid.NewGuid().ToString(),
            TransactionType = "PaymentProcessorTransaction",
            Amount = invoiceTotal,
            TransactionDate = request.EffectiveDate,
            Description = request.InvoiceDescription,
            CreatedBy = request.CreatedBy,
            CreatedDate = DateTime.UtcNow
        };

        await _cashInOutRepository.CreateAsync(cashInOut);
        _logger.LogInformation("Created CashInOut {CashInOutId} for amount {Amount:C}", cashInOut.CashInOutId, invoiceTotal);

        // Create transaction invoice
        var invoice = new TransactionInvoice
        {
            InvoiceId = Guid.NewGuid().ToString(),
            AccountCategoryId = request.AccountCategoryId,
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
        _logger.LogInformation("Created transaction invoice {InvoiceId} with number {InvoiceNumber}", 
            invoice.InvoiceId, invoice.InvoiceNumber);

        return MapToResponse(invoice);
    }

    public async Task<GenerateTransactionInvoiceResponse> GenerateAsync(GenerateTransactionInvoiceRequest request)
    {
        // Validate request
        var validationResult = await _generateValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Generating on-demand transaction invoice for AccountCategory={AccountCategoryId}, Amount={Amount:C}", 
            request.AccountCategoryId, request.InvoiceAmount);

        var response = new GenerateTransactionInvoiceResponse
        {
            Result = "invoice not needed"
        };

        // Verify account_category exists
        var account_category = await _account_categoryRepository.GetByIdAsync(request.AccountCategoryId);
        if (account_category == null)
        {
            throw new InvalidOperationException($"AccountCategory not found: {request.AccountCategoryId}");
        }

        // Get payment plans from Paragon
        var plans = await _paragonAdapter.GetPaymentPlansAsync(request.AccountCategoryId);
        if (!plans.Any())
        {
            _logger.LogWarning("No payment plans found for account_category {AccountCategoryId}", request.AccountCategoryId);
            return response;
        }

        var firstPlan = plans.First();

        // Calculate pending amount (mock calculation - in real WCF this queries TransferLines)
        decimal pendingAmount = 0m; // TODO: Query actual pending transfers

        // Check if current balance + pending is below peg amount
        // Mock peg amount logic - in real WCF this comes from TransactionFrequency
        decimal pegAmount = 1000m; // TODO: Get from TransactionFrequency

        if (pegAmount > (account_category.Balance + pendingAmount))
        {
            _logger.LogInformation("Balance ({Balance:C}) + Pending ({Pending:C}) is below peg amount ({PegAmount:C}). Creating invoice.", 
                account_category.Balance, pendingAmount, pegAmount);

            // Create CashInOut
            var cashInOut = new CashInOut
            {
                CashInOutId = Guid.NewGuid().ToString(),
                TransactionType = "PaymentProcessorTransaction",
                Amount = request.InvoiceAmount,
                TransactionDate = request.InvoiceDate,
                Description = $"PaymentProcessor Pretransaction for {firstPlan.PlanShortDescription}",
                CreatedBy = request.CreatedBy,
                CreatedDate = DateTime.UtcNow
            };

            await _cashInOutRepository.CreateAsync(cashInOut);

            // Create transaction invoice
            var invoice = new TransactionInvoice
            {
                InvoiceId = Guid.NewGuid().ToString(),
                AccountCategoryId = request.AccountCategoryId,
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
                request.AccountCategoryId, 
                plans.Select(p => p.PaymentPlanId).ToList()
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

            _logger.LogInformation("Successfully generated transaction invoice {InvoiceId}", invoice.InvoiceId);
        }
        else
        {
            _logger.LogInformation("Peg amount check not met. Invoice not needed.");
        }

        return response;
    }

    public async Task<BatchTransactionInvoiceResponse> CreateBatchAsync(CreateBatchTransactionInvoiceRequest request)
    {
        // Validate request
        var validationResult = await _batchValidator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errors = string.Join(", ", validationResult.Errors.Select(e => e.ErrorMessage));
            throw new ValidationException($"Validation failed: {errors}");
        }

        _logger.LogInformation("Creating batch transaction invoices. Employer filter: {EmployerCount} employers", request.EmployerIds.Count);

        var response = new BatchTransactionInvoiceResponse();

        // Get all PreTransaction account_categorys
        var allAccountCategorys = await _account_categoryRepository.GetByAccountTypeAsync("PreTransaction");
        
        // Filter by employer IDs if specified
        var account_categorys = request.EmployerIds.Any()
            ? allAccountCategorys.Where(sa => request.EmployerIds.Contains(sa.AccountNumber)).ToList()
            : allAccountCategorys.ToList();

        _logger.LogInformation("Found {Count} account_categorys to process", account_categorys.Count);
        response.TotalProcessed = account_categorys.Count;

        foreach (var account_category in account_categorys)
        {
            try
            {
                // Check if invoice already created today
                var existingInvoices = await _invoiceRepository.GetByAccountCategoryIdAsync(account_category.AccountCategoryId);
                if (existingInvoices.Any(inv => inv.InvoiceDate.Date == DateTime.Today))
                {
                    _logger.LogInformation("Invoice already created today for account_category {AccountCategoryId}. Skipping.", account_category.AccountCategoryId);
                    response.SkippedCount++;
                    response.Results.Add(new AccountCategoryProcessingResult
                    {
                        AccountCategoryId = account_category.AccountCategoryId,
                        EmployerId = account_category.AccountNumber,
                        Success = true,
                        ErrorMessage = "Already processed today"
                    });
                    continue;
                }

                // Find open transaction batch
                var openBatch = await _batchRepository.GetByStatusAsync("Open");
                var account_categoryBatch = openBatch.FirstOrDefault(b => b.AccountCategoryId == account_category.AccountCategoryId);

                if (account_categoryBatch == null)
                {
                    _logger.LogWarning("No open transaction batch found for account_category {AccountCategoryId}. Skipping.", account_category.AccountCategoryId);
                    response.SkippedCount++;
                    response.Results.Add(new AccountCategoryProcessingResult
                    {
                        AccountCategoryId = account_category.AccountCategoryId,
                        EmployerId = account_category.AccountNumber,
                        Success = true,
                        ErrorMessage = "No open batch found"
                    });
                    continue;
                }

                // Close the batch (this creates the replenishment invoice)
                // TODO: Call ITransactionBatchService.CloseAsync once implemented
                _logger.LogInformation("Processing batch closure for account_category {AccountCategoryId}, Batch {BatchId}", 
                    account_category.AccountCategoryId, account_categoryBatch.BatchId);

                response.SuccessCount++;
                response.Results.Add(new AccountCategoryProcessingResult
                {
                    AccountCategoryId = account_category.AccountCategoryId,
                    EmployerId = account_category.AccountNumber,
                    Success = true,
                    CashInOutId = $"CIO-{Guid.NewGuid():N}", // Placeholder
                    Amount = 0m // Will be set by batch closure
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create transaction invoice for account_category {AccountCategoryId}", account_category.AccountCategoryId);
                response.FailureCount++;
                response.Results.Add(new AccountCategoryProcessingResult
                {
                    AccountCategoryId = account_category.AccountCategoryId,
                    EmployerId = account_category.AccountNumber,
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
        _logger.LogInformation("Creating batch invoices for Employer={EmployerId}, AccountCategoryCount={Count}", 
            dto.EmployerId, dto.AccountCategoryIds.Count);

        var result = new BatchInvoiceResultDto
        {
            BatchId = Guid.NewGuid(),
            TotalInvoices = dto.AccountCategoryIds.Count
        };

        // Create transaction batch first
        var batch = new TransactionBatch
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

        // Process each account_category
        foreach (var account_categoryId in dto.AccountCategoryIds)
        {
            try
            {
                // Get account_category
                var account_category = await _account_categoryRepository.GetByIdAsync(account_categoryId.ToString());
                if (account_category == null)
                {
                    result.FailureCount++;
                    result.FailedAccountCategorys.Add(new FailedInvoiceDto
                    {
                        AccountCategoryId = account_categoryId,
                        Reason = "AccountCategory not found",
                        ErrorType = "NotFound"
                    });
                    continue;
                }

                // Check for existing invoice with same effective date (duplicate prevention)
                var existingInvoices = await _invoiceRepository.GetByAccountCategoryIdAsync(account_category.AccountCategoryId);
                if (existingInvoices.Any(i => i.InvoiceDate.Date == dto.EffectiveDate.Date))
                {
                    _logger.LogInformation("Skipping account_category {AccountCategoryId} - invoice already exists for {Date}", 
                        account_categoryId, dto.EffectiveDate);
                    result.FailureCount++;
                    result.FailedAccountCategorys.Add(new FailedInvoiceDto
                    {
                        AccountCategoryId = account_categoryId,
                        Reason = "Invoice already exists for this effective date",
                        ErrorType = "Duplicate"
                    });
                    continue;
                }

                // Get payment plans to calculate peg amount
                var plans = await _paragonAdapter.GetPaymentPlansAsync(account_category.AccountCategoryId);
                if (!plans.Any())
                {
                    result.FailureCount++;
                    result.FailedAccountCategorys.Add(new FailedInvoiceDto
                    {
                        AccountCategoryId = account_categoryId,
                        Reason = "No payment plans found",
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
                    _logger.LogInformation("Skipping account_category {AccountCategoryId} - balance meets peg (Balance: {Balance:C}, Peg: {Peg:C})", 
                        account_categoryId, currentBalance, pegAmount);
                    result.FailureCount++;
                    result.FailedAccountCategorys.Add(new FailedInvoiceDto
                    {
                        AccountCategoryId = account_categoryId,
                        Reason = "Balance meets peg requirement",
                        ErrorType = "NotNeeded"
                    });
                    continue;
                }

                // Create transaction invoice
                var invoice = new TransactionInvoice
                {
                    InvoiceId = Guid.NewGuid().ToString(),
                    AccountCategoryId = account_category.AccountCategoryId,
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

                _logger.LogInformation("Created invoice {InvoiceId} for account_category {AccountCategoryId}, Amount: {Amount:C}", 
                    invoice.InvoiceId, account_categoryId, pegAmount);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create invoice for account_category {AccountCategoryId}", account_categoryId);
                result.FailureCount++;
                result.FailedAccountCategorys.Add(new FailedInvoiceDto
                {
                    AccountCategoryId = account_categoryId,
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

    public async Task<GenerateTransactionInvoiceResultDto> GenerateTransactionInvoiceAsync(GenerateTransactionInvoiceDto dto)
    {
        _logger.LogInformation("Generating transaction invoice for AccountCategory={AccountCategoryId}, Amount={Amount:C}", 
            dto.AccountCategoryId, dto.InvoiceAmount);

        var result = new GenerateTransactionInvoiceResultDto
        {
            InvoiceCreated = false,
            Reason = "Balance meets peg requirement",
            PegAmount = 0m
        };

        // Verify account_category exists
        var account_category = await _account_categoryRepository.GetByIdAsync(dto.AccountCategoryId.ToString());
        if (account_category == null)
        {
            throw new InvalidOperationException($"AccountCategory not found: {dto.AccountCategoryId}");
        }

        // Get payment plans from Paragon
        var plans = await _paragonAdapter.GetPaymentPlansAsync(account_category.AccountCategoryId);
        if (!plans.Any())
        {
            _logger.LogWarning("No payment plans found for account_category {AccountCategoryId}", dto.AccountCategoryId);
            result.Reason = "No payment plans found";
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
            _logger.LogInformation("Invoice not needed for account_category {AccountCategoryId}. Balance {Balance:C} meets or exceeds invoice amount {Amount:C}", 
                dto.AccountCategoryId, currentBalance, dto.InvoiceAmount);
            result.Reason = "Balance meets peg requirement";
            return result;
        }

        // Create transaction invoice with peg amount
        var invoice = new TransactionInvoice
        {
            InvoiceId = Guid.NewGuid().ToString(),
            AccountCategoryId = account_category.AccountCategoryId,
            BatchId = string.Empty, // Not part of a batch
            InvoiceNumber = GenerateInvoiceNumber(),
            Amount = pegAmount,
            Status = account_category.AccountNumber.Contains("AutoDebit") ? "Pending" : "Open", // Mock auto-debit check
            Description = dto.Description ?? $"On-demand peg invoice - {DateTime.UtcNow:yyyy-MM-dd}",
            InvoiceDate = dto.EffectiveDate,
            DueDate = dto.EffectiveDate.AddDays(30),
            CreatedBy = "System",
            CreatedDate = DateTime.UtcNow
        };

        await _invoiceRepository.CreateAsync(invoice);

        // If auto-debit enabled, create payment record (effective date + 2 business days)
        if (account_category.AccountNumber.Contains("AutoDebit")) // Mock auto-debit check
        {
            var paymentDate = AddBusinessDays(dto.EffectiveDate, 2);

            var payment = new CashInOut
            {
                CashInOutId = Guid.NewGuid().ToString(),
                TransactionType = "PaymentProcessorTransactionPayment",
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

        _logger.LogInformation("Created transaction invoice {InvoiceId} for account_category {AccountCategoryId}, Peg amount: {PegAmount:C}", 
            invoice.InvoiceId, dto.AccountCategoryId, pegAmount);

        return result;
    }

    public async Task<TransactionInvoiceResponse?> GetByIdAsync(string invoiceId)
    {
        var invoice = await _invoiceRepository.GetByIdAsync(invoiceId);
        return invoice != null ? MapToResponse(invoice) : null;
    }

    public async Task<IEnumerable<TransactionInvoiceResponse>> GetByBatchIdAsync(string batchId)
    {
        var invoices = await _invoiceRepository.GetByBatchIdAsync(batchId);
        return invoices.Select(MapToResponse);
    }

    public async Task<IEnumerable<TransactionInvoiceResponse>> GetByAccountCategoryIdAsync(string account_categoryId)
    {
        var invoices = await _invoiceRepository.GetByAccountCategoryIdAsync(account_categoryId);
        return invoices.Select(MapToResponse);
    }

    private TransactionInvoiceResponse MapToResponse(TransactionInvoice invoice)
    {
        return new TransactionInvoiceResponse
        {
            InvoiceId = invoice.InvoiceId,
            BatchId = invoice.BatchId,
            AccountCategoryId = invoice.AccountCategoryId,
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
