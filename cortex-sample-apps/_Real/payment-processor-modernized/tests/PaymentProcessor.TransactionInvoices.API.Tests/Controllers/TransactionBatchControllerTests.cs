using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using PaymentProcessor.TransactionInvoices.API.Controllers;
using PaymentProcessor.TransactionInvoices.Core.DTOs;
using PaymentProcessor.TransactionInvoices.Core.Services;
using Xunit;

namespace PaymentProcessor.TransactionInvoices.API.Tests.Controllers;

public class TransactionBatchControllerTests
{
    private readonly Mock<ITransactionBatchService> _mockService;
    private readonly Mock<ILogger<TransactionBatchController>> _mockLogger;
    private readonly TransactionBatchController _controller;

    public TransactionBatchControllerTests()
    {
        _mockService = new Mock<ITransactionBatchService>();
        _mockLogger = new Mock<ILogger<TransactionBatchController>>();
        _controller = new TransactionBatchController(_mockService.Object, _mockLogger.Object);

        // Set up HttpContext for CreatedAtAction
        _controller.ControllerContext = new ControllerContext
        {
            HttpContext = new DefaultHttpContext()
        };
    }

    [Fact]
    public async Task CreateBatch_ValidRequest_ReturnsCreatedResult()
    {
        // Arrange
        var request = new CreateTransactionBatchRequest
        {
            Description = "December 2025 Batch",
            EmployerId = "EMP-001",
            CreatedBy = "system"
        };

        var expectedResponse = new TransactionBatchResponse
        {
            BatchId = "BATCH-001",
            Description = request.Description,
            EmployerId = request.EmployerId,
            Status = "Open",
            CreatedDate = DateTime.UtcNow,
            CreatedBy = request.CreatedBy
        };

        _mockService.Setup(s => s.CreateAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.CreateBatch(request);

        // Assert
        var createdResult = result.Result as CreatedAtActionResult;
        createdResult.Should().NotBeNull();
        createdResult!.StatusCode.Should().Be(StatusCodes.Status201Created);
        createdResult.Value.Should().BeEquivalentTo(expectedResponse);

        _mockService.Verify(s => s.CreateAsync(request), Times.Once);
    }

    [Fact]
    public async Task CloseBatch_ValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new CloseTransactionBatchRequest
        {
            BatchId = "BATCH-001",
            Description = "December Batch",
            ExcludedInvoiceIds = new List<string> { "INV-999" },
            ClosedBy = "system"
        };

        var expectedResponse = new CloseTransactionBatchResponse
        {
            Result = "batch closed",
            CashInOutId = "CIO-123",
            PaymentId = "PAY-456",
            Batch = new TransactionBatchResponse
            {
                BatchId = request.BatchId,
                Status = "Pending",
                TotalAmount = 5000m
            }
        };

        _mockService.Setup(s => s.CloseAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.CloseBatch(request);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedResponse);

        _mockService.Verify(s => s.CloseAsync(request), Times.Once);
    }

    [Fact]
    public async Task ReopenBatch_ValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new ReopenTransactionBatchRequest
        {
            BatchId = "BATCH-001",
            Description = "Reopened for corrections",
            UpdatedBy = "admin"
        };

        var expectedResponse = new TransactionBatchResponse
        {
            BatchId = request.BatchId,
            Status = "Reopened",
            Description = request.Description
        };

        _mockService.Setup(s => s.ReopenAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.ReopenBatch(request);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedResponse);

        _mockService.Verify(s => s.ReopenAsync(request), Times.Once);
    }

    [Fact]
    public async Task UpdateBatch_ValidRequest_ReturnsOkResult()
    {
        // Arrange
        var batchId = "BATCH-001";
        var request = new UpdateTransactionBatchRequest
        {
            BatchId = batchId,
            Description = "Updated description",
            EmployerId = "EMP-002",
            UpdatedBy = "admin"
        };

        var expectedResponse = new TransactionBatchResponse
        {
            BatchId = batchId,
            Description = request.Description,
            EmployerId = request.EmployerId
        };

        _mockService.Setup(s => s.UpdateAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.UpdateBatch(batchId, request);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedResponse);

        _mockService.Verify(s => s.UpdateAsync(request), Times.Once);
    }

    [Fact]
    public async Task UpdateBatch_IdMismatch_ReturnsBadRequest()
    {
        // Arrange
        var routeId = "BATCH-001";
        var request = new UpdateTransactionBatchRequest
        {
            BatchId = "BATCH-999",  // Mismatch!
            Description = "Test",
            UpdatedBy = "admin"
        };

        // Act
        var result = await _controller.UpdateBatch(routeId, request);

        // Assert
        var badRequestResult = result.Result as BadRequestObjectResult;
        badRequestResult.Should().NotBeNull();

        var problemDetails = badRequestResult!.Value as ProblemDetails;
        problemDetails.Should().NotBeNull();
        problemDetails!.Title.Should().Be("ID Mismatch");

        _mockService.Verify(s => s.UpdateAsync(It.IsAny<UpdateTransactionBatchRequest>()), Times.Never);
    }

    [Fact]
    public async Task GetBatchById_BatchExists_ReturnsOkResult()
    {
        // Arrange
        var batchId = "BATCH-001";
        var expectedBatch = new TransactionBatchResponse
        {
            BatchId = batchId,
            Status = "Open",
            TotalAmount = 5000m
        };

        _mockService.Setup(s => s.GetByIdAsync(batchId))
            .ReturnsAsync(expectedBatch);

        // Act
        var result = await _controller.GetBatchById(batchId);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedBatch);

        _mockService.Verify(s => s.GetByIdAsync(batchId), Times.Once);
    }

    [Fact]
    public async Task GetBatchById_BatchNotFound_ReturnsNotFoundResult()
    {
        // Arrange
        var batchId = "BATCH-999";
        _mockService.Setup(s => s.GetByIdAsync(batchId))
            .ReturnsAsync((TransactionBatchResponse?)null);

        // Act
        var result = await _controller.GetBatchById(batchId);

        // Assert
        var notFoundResult = result.Result as NotFoundObjectResult;
        notFoundResult.Should().NotBeNull();

        var problemDetails = notFoundResult!.Value as ProblemDetails;
        problemDetails.Should().NotBeNull();
        problemDetails!.Title.Should().Be("Batch Not Found");

        _mockService.Verify(s => s.GetByIdAsync(batchId), Times.Once);
    }

    [Fact]
    public async Task GetBatchesByAccountCategoryId_ReturnsOkResult()
    {
        // Arrange
        var account_categoryId = "SA-001";
        var expectedBatches = new List<TransactionBatchResponse>
        {
            new TransactionBatchResponse { BatchId = "BATCH-001", Status = "Open" },
            new TransactionBatchResponse { BatchId = "BATCH-002", Status = "Closed" }
        };

        _mockService.Setup(s => s.GetByAccountCategoryIdAsync(account_categoryId))
            .ReturnsAsync(expectedBatches);

        // Act
        var result = await _controller.GetBatchesByAccountCategoryId(account_categoryId);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedBatches);

        _mockService.Verify(s => s.GetByAccountCategoryIdAsync(account_categoryId), Times.Once);
    }

    [Fact]
    public async Task GetOpenBatch_OpenBatchExists_ReturnsOkResult()
    {
        // Arrange
        var account_categoryId = "SA-001";
        var expectedBatch = new TransactionBatchResponse
        {
            BatchId = "BATCH-001",
            Status = "Open"
        };

        _mockService.Setup(s => s.GetOpenBatchAsync(account_categoryId))
            .ReturnsAsync(expectedBatch);

        // Act
        var result = await _controller.GetOpenBatch(account_categoryId);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeEquivalentTo(expectedBatch);

        _mockService.Verify(s => s.GetOpenBatchAsync(account_categoryId), Times.Once);
    }

    [Fact]
    public async Task GetOpenBatch_NoOpenBatch_ReturnsOkWithNull()
    {
        // Arrange
        var account_categoryId = "SA-001";
        _mockService.Setup(s => s.GetOpenBatchAsync(account_categoryId))
            .ReturnsAsync((TransactionBatchResponse?)null);

        // Act
        var result = await _controller.GetOpenBatch(account_categoryId);

        // Assert
        var okResult = result.Result as OkObjectResult;
        okResult.Should().NotBeNull();
        okResult!.Value.Should().BeNull();

        _mockService.Verify(s => s.GetOpenBatchAsync(account_categoryId), Times.Once);
    }
}
