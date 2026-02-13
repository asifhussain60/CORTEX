using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using RA.FundingInvoices.API.Controllers;
using RA.FundingInvoices.Core.DTOs;
using RA.FundingInvoices.Core.Services;
using Xunit;

namespace RA.FundingInvoices.API.Tests.Controllers;

public class FundingInvoiceControllerTests
{
    private readonly Mock<IFundingInvoiceService> _mockService;
    private readonly Mock<ILogger<FundingInvoiceController>> _mockLogger;
    private readonly FundingInvoiceController _controller;

    public FundingInvoiceControllerTests()
    {
        _mockService = new Mock<IFundingInvoiceService>();
        _mockLogger = new Mock<ILogger<FundingInvoiceController>>();
        _controller = new FundingInvoiceController(_mockService.Object, _mockLogger.Object);

        // Set up HttpContext for CreatedAtAction
        _controller.ControllerContext = new ControllerContext
        {
            HttpContext = new DefaultHttpContext()
        };
    }

    [Fact]
    public async Task CreateInvoice_ValidRequest_ReturnsCreatedResult()
    {
        // Arrange
        var request = new CreateFundingInvoiceRequest
        {
            EmployerId = "EMP-001",
            SubaccountId = "SA-001",
            ReimbursementPlanId = "RP-001",
            EmployerFundingDefault = 500m,
            EmployeeFundingDefault = 250m,
            EffectiveDate = DateTime.UtcNow.AddDays(1),
            InvoiceDescription = "Test Invoice",
            IsLSA = false,
            UpdateTemplate = true,
            CreatedBy = "system"
        };

        var expectedResponse = new FundingInvoiceResponse
        {
            InvoiceId = "INV-001",
            EmployerId = request.EmployerId,
            SubaccountId = request.SubaccountId,
            TotalAmount = 750m,
            Status = "Pending",
            CreatedDate = DateTime.UtcNow,
            CreatedBy = request.CreatedBy
        };

        _mockService.Setup(s => s.CreateAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.CreateInvoice(request);

        // Assert
        result.Should().NotBeNull();
        var createdResult = result.Result as CreatedAtActionResult;
        createdResult.Should().NotBeNull();
        createdResult!.StatusCode.Should().Be(StatusCodes.Status201Created);
        createdResult.Value.Should().BeEquivalentTo(expectedResponse);
        createdResult.ActionName.Should().Be(nameof(FundingInvoiceController.GetInvoiceById));

        _mockService.Verify(s => s.CreateAsync(request), Times.Once);
    }

    [Fact]
    public async Task GenerateInvoice_InvoiceCreated_ReturnsOkResult()
    {
        // Arrange
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
            InvoiceAmount = 500m,
            InvoiceDate = DateTime.UtcNow.AddDays(1),
            CreatedBy = "system"
        };

        var expectedResponse = new GenerateFundingInvoiceResponse
        {
            Result = "invoice created",
            CashInOutId = "CIO-123",
            Invoice = new FundingInvoiceResponse
            {
                InvoiceId = "INV-001",
                TotalAmount = 500m
            },
            PaymentId = "PAY-456"
        };

        _mockService.Setup(s => s.GenerateAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.GenerateInvoice(request);

        // Assert
        result.Should().NotBeNull();
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.StatusCode.Should().Be(StatusCodes.Status200OK);
        okResult.Value.Should().BeEquivalentTo(expectedResponse);

        _mockService.Verify(s => s.GenerateAsync(request), Times.Once);
    }

    [Fact]
    public async Task GenerateInvoice_InvoiceNotNeeded_ReturnsOkResultWithNullInvoice()
    {
        // Arrange
        var request = new GenerateFundingInvoiceRequest
        {
            SubaccountId = "SA-001",
            InvoiceAmount = 100m,
            InvoiceDate = DateTime.UtcNow.AddDays(1),
            CreatedBy = "system"
        };

        var expectedResponse = new GenerateFundingInvoiceResponse
        {
            Result = "invoice not needed",
            CashInOutId = null,
            Invoice = null,
            PaymentId = null
        };

        _mockService.Setup(s => s.GenerateAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.GenerateInvoice(request);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        var response = okResult!.Value as GenerateFundingInvoiceResponse;
        response.Should().NotBeNull();
        response!.Result.Should().Be("invoice not needed");
        response.Invoice.Should().BeNull();

        _mockService.Verify(s => s.GenerateAsync(request), Times.Once);
    }

    [Fact]
    public async Task CreateBatchInvoices_ValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new CreateBatchFundingInvoiceRequest
        {
            EmployerIds = new List<string> { "EMP-001", "EMP-002" },
            CreatedBy = "system"
        };

        var expectedResponse = new BatchFundingInvoiceResponse
        {
            TotalProcessed = 10,
            SuccessCount = 8,
            FailureCount = 1,
            SkippedCount = 1,
            Results = new List<BatchFundingResult>
            {
                new BatchFundingResult
                {
                    SubaccountId = "SA-001",
                    EmployerId = "EMP-001",
                    Success = true,
                    CashInOutId = "CIO-123",
                    Amount = 500m
                }
            }
        };

        _mockService.Setup(s => s.CreateBatchAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.CreateBatchInvoices(request);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedResponse);

        _mockService.Verify(s => s.CreateBatchAsync(request), Times.Once);
    }

    [Fact]
    public async Task GetInvoiceById_InvoiceExists_ReturnsOkResult()
    {
        // Arrange
        var invoiceId = "INV-001";
        var expectedInvoice = new FundingInvoiceResponse
        {
            InvoiceId = invoiceId,
            TotalAmount = 750m,
            Status = "Pending"
        };

        _mockService.Setup(s => s.GetByIdAsync(invoiceId))
            .ReturnsAsync(expectedInvoice);

        // Act
        var result = await _controller.GetInvoiceById(invoiceId);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedInvoice);

        _mockService.Verify(s => s.GetByIdAsync(invoiceId), Times.Once);
    }

    [Fact]
    public async Task GetInvoiceById_InvoiceNotFound_ReturnsNotFoundResult()
    {
        // Arrange
        var invoiceId = "INV-999";
        _mockService.Setup(s => s.GetByIdAsync(invoiceId))
            .ReturnsAsync((FundingInvoiceResponse?)null);

        // Act
        var result = await _controller.GetInvoiceById(invoiceId);

        // Assert
        var notFoundResult = result.Result as NotFoundObjectResult;
        notFoundResult.Should().NotBeNull();
        notFoundResult!.StatusCode.Should().Be(StatusCodes.Status404NotFound);

        var problemDetails = notFoundResult.Value as ProblemDetails;
        problemDetails.Should().NotBeNull();
        problemDetails!.Title.Should().Be("Invoice Not Found");
        problemDetails.Detail.Should().Contain(invoiceId);

        _mockService.Verify(s => s.GetByIdAsync(invoiceId), Times.Once);
    }

    [Fact]
    public async Task GetInvoicesByBatchId_ReturnsOkResult()
    {
        // Arrange
        var batchId = "BATCH-001";
        var expectedInvoices = new List<FundingInvoiceResponse>
        {
            new FundingInvoiceResponse { InvoiceId = "INV-001", TotalAmount = 500m },
            new FundingInvoiceResponse { InvoiceId = "INV-002", TotalAmount = 300m }
        };

        _mockService.Setup(s => s.GetByBatchIdAsync(batchId))
            .ReturnsAsync(expectedInvoices);

        // Act
        var result = await _controller.GetInvoicesByBatchId(batchId);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedInvoices);

        _mockService.Verify(s => s.GetByBatchIdAsync(batchId), Times.Once);
    }

    [Fact]
    public async Task GetInvoicesBySubaccountId_ReturnsOkResult()
    {
        // Arrange
        var subaccountId = "SA-001";
        var expectedInvoices = new List<FundingInvoiceResponse>
        {
            new FundingInvoiceResponse { InvoiceId = "INV-001", SubaccountId = subaccountId },
            new FundingInvoiceResponse { InvoiceId = "INV-002", SubaccountId = subaccountId }
        };

        _mockService.Setup(s => s.GetBySubaccountIdAsync(subaccountId))
            .ReturnsAsync(expectedInvoices);

        // Act
        var result = await _controller.GetInvoicesBySubaccountId(subaccountId);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedInvoices);

        _mockService.Verify(s => s.GetBySubaccountIdAsync(subaccountId), Times.Once);
    }
}
