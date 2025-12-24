# Error Handling Patterns for CORTEX User Operations

**Version:** 1.0  
**Date:** December 8, 2025  
**Author:** Asif Hussain  
**Purpose:** Standardized error handling patterns for user-facing CORTEX operations

---

## Overview

This guide establishes error handling patterns for CORTEX user operations, addressing:
- Domain-specific exceptions vs generic framework exceptions
- Consistent error response formats
- Logging strategies for debugging
- User-friendly error messages
- Recovery mechanisms

**Addresses:** Cortex-Clean recommendation #2 (High Priority) and #3 (Medium Priority)

---

## Problem Statement (from Cortex-Clean Review)

**Issue:** Inconsistent error handling between handlers
- Using `KeyNotFoundException` (framework exception) for domain errors
- No domain-specific exceptions
- Inconsistent error messages
- Missing logging in handlers

**Example of Problem:**
```csharp
// ❌ BAD: Using framework exception for domain error
var task = await _repository.GetByIdAsync(request.Id, cancellationToken);
if (task == null)
    throw new KeyNotFoundException($"Task with ID {request.Id} not found.");
```

---

## Pattern 1: Domain-Specific Exceptions

### Principle
Domain errors should use domain exceptions, not framework exceptions. This provides:
- Type-safe error handling
- Meaningful error context
- Clear domain boundaries
- Testable error scenarios

### Implementation (.NET/C#)

#### Domain Exceptions

```csharp
// Domain/Exceptions/TaskNotFoundException.cs
namespace Cortex.Clean.Domain.Exceptions;

public class TaskNotFoundException : DomainException
{
    public Guid TaskId { get; }
    
    public TaskNotFoundException(Guid taskId) 
        : base($"Task with ID '{taskId}' was not found.")
    {
        TaskId = taskId;
    }
}

// Domain/Exceptions/DomainException.cs
public abstract class DomainException : Exception
{
    protected DomainException(string message) : base(message) { }
    
    protected DomainException(string message, Exception innerException) 
        : base(message, innerException) { }
}

// Domain/Exceptions/InvalidTaskException.cs
public class InvalidTaskException : DomainException
{
    public string ValidationError { get; }
    
    public InvalidTaskException(string validationError) 
        : base($"Invalid task: {validationError}")
    {
        ValidationError = validationError;
    }
}
```

#### Handler Usage

```csharp
// Application/Handlers/UpdateTaskCommandHandler.cs
public class UpdateTaskCommandHandler : IRequestHandler<UpdateTaskCommand, TaskDto>
{
    private readonly ITaskRepository _repository;
    private readonly IMapper _mapper;
    private readonly ILogger<UpdateTaskCommandHandler> _logger;

    public async Task<TaskDto> Handle(
        UpdateTaskCommand request, 
        CancellationToken cancellationToken)
    {
        _logger.LogInformation(
            "Updating task {TaskId} with title '{Title}'", 
            request.Id, 
            request.Title);

        try
        {
            var task = await _repository.GetByIdAsync(request.Id, cancellationToken);
            
            if (task == null)
            {
                _logger.LogWarning("Task {TaskId} not found", request.Id);
                throw new TaskNotFoundException(request.Id);  // ✅ Domain exception
            }
            
            task.UpdateTitle(request.Title);  // May throw InvalidTaskException
            
            await _repository.UpdateAsync(task, cancellationToken);
            await _repository.SaveChangesAsync(cancellationToken);
            
            _logger.LogInformation(
                "Successfully updated task {TaskId}", 
                request.Id);
            
            return _mapper.Map<TaskDto>(task);
        }
        catch (DomainException ex)
        {
            _logger.LogWarning(
                ex, 
                "Domain error updating task {TaskId}: {Message}", 
                request.Id, 
                ex.Message);
            throw;  // Re-throw for middleware to handle
        }
        catch (Exception ex)
        {
            _logger.LogError(
                ex, 
                "Unexpected error updating task {TaskId}", 
                request.Id);
            throw;
        }
    }
}
```

---

## Pattern 2: Centralized Exception Middleware

### Principle
Global exception handler translates exceptions into consistent HTTP responses with appropriate status codes.

### Implementation

#### Exception Middleware

```csharp
// API/Middleware/GlobalExceptionMiddleware.cs
public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;

    public GlobalExceptionMiddleware(
        RequestDelegate next, 
        ILogger<GlobalExceptionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var response = exception switch
        {
            TaskNotFoundException notFoundEx => new ErrorResponse
            {
                StatusCode = StatusCodes.Status404NotFound,
                ErrorCode = "TASK_NOT_FOUND",
                Message = notFoundEx.Message,
                Details = new { TaskId = notFoundEx.TaskId }
            },
            
            InvalidTaskException validationEx => new ErrorResponse
            {
                StatusCode = StatusCodes.Status400BadRequest,
                ErrorCode = "INVALID_TASK",
                Message = validationEx.Message,
                Details = new { ValidationError = validationEx.ValidationError }
            },
            
            FluentValidation.ValidationException fluentEx => new ErrorResponse
            {
                StatusCode = StatusCodes.Status400BadRequest,
                ErrorCode = "VALIDATION_FAILED",
                Message = "One or more validation errors occurred.",
                Details = fluentEx.Errors.Select(e => new 
                { 
                    Field = e.PropertyName, 
                    Error = e.ErrorMessage 
                })
            },
            
            DomainException domainEx => new ErrorResponse
            {
                StatusCode = StatusCodes.Status400BadRequest,
                ErrorCode = "DOMAIN_ERROR",
                Message = domainEx.Message
            },
            
            _ => new ErrorResponse
            {
                StatusCode = StatusCodes.Status500InternalServerError,
                ErrorCode = "INTERNAL_ERROR",
                Message = "An unexpected error occurred. Please try again later."
            }
        };

        // Log with appropriate level
        if (response.StatusCode >= 500)
        {
            _logger.LogError(
                exception, 
                "Internal server error: {Message}", 
                exception.Message);
        }
        else if (response.StatusCode >= 400)
        {
            _logger.LogWarning(
                exception, 
                "Client error {StatusCode}: {Message}", 
                response.StatusCode, 
                exception.Message);
        }

        context.Response.StatusCode = response.StatusCode;
        context.Response.ContentType = "application/json";
        
        await context.Response.WriteAsJsonAsync(response);
    }
}

// API/Models/ErrorResponse.cs
public record ErrorResponse
{
    public int StatusCode { get; init; }
    public string ErrorCode { get; init; } = string.Empty;
    public string Message { get; init; } = string.Empty;
    public object? Details { get; init; }
    public DateTime Timestamp { get; init; } = DateTime.UtcNow;
    public string TraceId { get; init; } = Activity.Current?.Id ?? Guid.NewGuid().ToString();
}
```

#### Registration

```csharp
// Program.cs
var app = builder.Build();

// Register exception middleware FIRST
app.UseMiddleware<GlobalExceptionMiddleware>();

app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
```

---

## Pattern 3: Result Pattern (Alternative to Exceptions)

### Principle
For expected failures (not exceptional conditions), use Result<T> pattern to avoid exception overhead and improve flow control.

### Implementation

#### Result Type

```csharp
// Application/Common/Result.cs
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }
    public string? ErrorCode { get; }

    private Result(bool isSuccess, T? value, string? error, string? errorCode)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
        ErrorCode = errorCode;
    }

    public static Result<T> Success(T value) 
        => new(true, value, null, null);

    public static Result<T> Failure(string error, string? errorCode = null) 
        => new(false, default, error, errorCode);

    public TResult Match<TResult>(
        Func<T, TResult> onSuccess,
        Func<string, TResult> onFailure)
    {
        return IsSuccess && Value != null 
            ? onSuccess(Value) 
            : onFailure(Error ?? "Unknown error");
    }
}
```

#### Handler with Result Pattern

```csharp
public class UpdateTaskCommandHandler : IRequestHandler<UpdateTaskCommand, Result<TaskDto>>
{
    public async Task<Result<TaskDto>> Handle(
        UpdateTaskCommand request, 
        CancellationToken cancellationToken)
    {
        _logger.LogInformation(
            "Updating task {TaskId}", 
            request.Id);

        var task = await _repository.GetByIdAsync(request.Id, cancellationToken);
        
        if (task == null)
        {
            _logger.LogWarning("Task {TaskId} not found", request.Id);
            return Result<TaskDto>.Failure(
                $"Task with ID '{request.Id}' was not found.", 
                "TASK_NOT_FOUND");
        }
        
        try
        {
            task.UpdateTitle(request.Title);
        }
        catch (InvalidTaskException ex)
        {
            _logger.LogWarning("Invalid task update: {Error}", ex.ValidationError);
            return Result<TaskDto>.Failure(ex.Message, "INVALID_TASK");
        }
        
        await _repository.UpdateAsync(task, cancellationToken);
        await _repository.SaveChangesAsync(cancellationToken);
        
        _logger.LogInformation("Successfully updated task {TaskId}", request.Id);
        
        var dto = _mapper.Map<TaskDto>(task);
        return Result<TaskDto>.Success(dto);
    }
}
```

#### Controller Usage

```csharp
[HttpPut("{id}")]
public async Task<IActionResult> UpdateTask(Guid id, UpdateTaskRequest request)
{
    var command = new UpdateTaskCommand(id, request.Title);
    var result = await _mediator.Send(command);
    
    return result.Match(
        onSuccess: task => Ok(task),
        onFailure: error => result.ErrorCode switch
        {
            "TASK_NOT_FOUND" => NotFound(new { message = error }),
            "INVALID_TASK" => BadRequest(new { message = error }),
            _ => StatusCode(500, new { message = "An unexpected error occurred." })
        }
    );
}
```

---

## Pattern 4: CORTEX Python Error Handling

### Principle
CORTEX operations use consistent error handling with OperationResult, logging, and graceful degradation.

### Implementation

#### Base Operation Result

```python
from dataclasses import dataclass
from typing import Optional, Any, Dict
from enum import Enum

class OperationStatus(Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    BLOCKED = "blocked"

@dataclass
class OperationResult:
    """Standard result format for CORTEX operations."""
    status: OperationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    
    @classmethod
    def success(cls, message: str, details: Optional[Dict[str, Any]] = None):
        return cls(OperationStatus.SUCCESS, message, details)
    
    @classmethod
    def warning(cls, message: str, details: Optional[Dict[str, Any]] = None):
        return cls(OperationStatus.WARNING, message, details)
    
    @classmethod
    def error(cls, message: str, error: Optional[Exception] = None, 
              details: Optional[Dict[str, Any]] = None):
        return cls(OperationStatus.ERROR, message, details, error)
    
    @classmethod
    def blocked(cls, message: str, details: Optional[Dict[str, Any]] = None):
        return cls(OperationStatus.BLOCKED, message, details)
    
    @property
    def is_success(self) -> bool:
        return self.status == OperationStatus.SUCCESS
    
    @property
    def is_warning(self) -> bool:
        return self.status == OperationStatus.WARNING
    
    @property
    def is_error(self) -> bool:
        return self.status == OperationStatus.ERROR
    
    @property
    def is_blocked(self) -> bool:
        return self.status == OperationStatus.BLOCKED
```

#### Agent with Error Handling

```python
from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
import logging

logger = logging.getLogger(__name__)

class PlanningAgent(BaseAgent):
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent in ["plan", "create_plan"]
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute planning with comprehensive error handling."""
        
        logger.info(f"Starting planning for: {request.user_message}")
        
        try:
            # Validate request
            validation_result = self._validate_request(request)
            if not validation_result.is_success:
                logger.warning(f"Validation failed: {validation_result.message}")
                return AgentResponse(
                    success=False,
                    message=validation_result.message,
                    result={"validation_errors": validation_result.details}
                )
            
            # Execute planning
            plan = self._create_plan(request)
            
            logger.info(f"Successfully created plan with {len(plan.phases)} phases")
            
            return AgentResponse(
                success=True,
                message="Plan created successfully",
                result={"plan": plan, "phases": len(plan.phases)}
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                message=f"Validation failed: {str(e)}",
                result={"error_type": "validation"}
            )
        
        except FileNotFoundError as e:
            logger.error(f"Required file not found: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                message=f"Required file not found: {str(e)}",
                result={"error_type": "file_not_found", "path": str(e)}
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in planning: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                message="An unexpected error occurred during planning",
                result={
                    "error_type": "unexpected",
                    "error_message": str(e)
                }
            )
    
    def _validate_request(self, request: AgentRequest) -> OperationResult:
        """Validate planning request."""
        if not request.context.get('feature_name'):
            return OperationResult.error(
                "Feature name is required",
                details={"missing_field": "feature_name"}
            )
        
        if not request.context.get('workspace_path'):
            return OperationResult.warning(
                "No workspace path provided, using default",
                details={"default_path": self.default_workspace}
            )
        
        return OperationResult.success("Validation passed")
```

#### Orchestrator with Checkpoint Error Handling

```python
class PlanningOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def execute_phase(self, phase: Dict) -> OperationResult:
        """Execute phase with checkpoint error handling."""
        
        self.logger.info(f"Executing phase: {phase['name']}")
        
        try:
            # Pre-execution checkpoint (non-blocking)
            checkpoint_result = self._create_checkpoint(phase)
            if not checkpoint_result.is_success:
                self.logger.warning(
                    f"Checkpoint failed (non-blocking): {checkpoint_result.message}"
                )
            
            # Execute phase steps
            for step in phase['steps']:
                step_result = self._execute_step(step)
                
                if step_result.is_blocked:
                    self.logger.error(f"Step blocked: {step_result.message}")
                    return OperationResult.blocked(
                        f"Phase blocked at step '{step['name']}'",
                        details={"step": step['name'], "reason": step_result.message}
                    )
                
                if step_result.is_error:
                    self.logger.error(f"Step failed: {step_result.message}")
                    return OperationResult.error(
                        f"Phase failed at step '{step['name']}'",
                        error=step_result.error,
                        details={"step": step['name']}
                    )
                
                if step_result.is_warning:
                    self.logger.warning(f"Step warning: {step_result.message}")
            
            self.logger.info(f"Phase '{phase['name']}' completed successfully")
            return OperationResult.success(
                f"Phase '{phase['name']}' completed",
                details={"steps_completed": len(phase['steps'])}
            )
            
        except Exception as e:
            self.logger.error(
                f"Unexpected error in phase '{phase['name']}': {e}", 
                exc_info=True
            )
            return OperationResult.error(
                f"Phase '{phase['name']}' failed with unexpected error",
                error=e
            )
    
    def _create_checkpoint(self, phase: Dict) -> OperationResult:
        """Create git checkpoint (non-blocking on failure)."""
        try:
            # Attempt checkpoint
            result = subprocess.run(
                ["git", "stash", "push", "-m", f"Checkpoint: {phase['name']}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return OperationResult.success("Checkpoint created")
            else:
                return OperationResult.warning(
                    "Checkpoint failed (continuing anyway)",
                    details={"stderr": result.stderr}
                )
        
        except subprocess.TimeoutExpired:
            self.logger.warning("Checkpoint timed out after 10s")
            return OperationResult.warning("Checkpoint timed out")
        
        except Exception as e:
            self.logger.warning(f"Checkpoint error: {e}", exc_info=True)
            return OperationResult.warning(f"Checkpoint error: {str(e)}")
```

---

## Pattern 5: Error Recovery & Retry Logic

### Implementation

```python
from functools import wraps
import time

def retry_on_transient_error(max_attempts=3, delay_seconds=1, backoff=2):
    """Decorator for retrying operations on transient errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay_seconds
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                
                except (ConnectionError, TimeoutError) as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
                
                except Exception as e:
                    # Non-transient error - don't retry
                    logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                    raise
            
        return wrapper
    return decorator

# Usage
class DatabaseOperation:
    @retry_on_transient_error(max_attempts=3, delay_seconds=2)
    def connect_to_database(self):
        """Connect with automatic retry on transient failures."""
        connection = create_connection()
        return connection
```

---

## Testing Error Handling

### Unit Tests

```csharp
[Fact]
public async Task UpdateTask_WhenTaskNotFound_ShouldThrowTaskNotFoundException()
{
    // Arrange
    var command = new UpdateTaskCommand(Guid.NewGuid(), "Updated Title");
    _mockRepository
        .Setup(r => r.GetByIdAsync(command.Id, It.IsAny<CancellationToken>()))
        .ReturnsAsync((TaskEntity?)null);

    // Act & Assert
    await Assert.ThrowsAsync<TaskNotFoundException>(
        () => _handler.Handle(command, CancellationToken.None)
    );
    
    _mockLogger.Verify(
        x => x.Log(
            LogLevel.Warning,
            It.IsAny<EventId>(),
            It.Is<It.IsAnyType>((o, t) => o.ToString()!.Contains("not found")),
            It.IsAny<Exception>(),
            It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
        Times.Once);
}

[Fact]
public async Task UpdateTask_WhenInvalidTitle_ShouldThrowInvalidTaskException()
{
    // Arrange
    var task = new TaskEntity("Original Title");
    var command = new UpdateTaskCommand(task.Id, "");  // Invalid: empty title
    
    _mockRepository
        .Setup(r => r.GetByIdAsync(command.Id, It.IsAny<CancellationToken>()))
        .ReturnsAsync(task);

    // Act & Assert
    var exception = await Assert.ThrowsAsync<InvalidTaskException>(
        () => _handler.Handle(command, CancellationToken.None)
    );
    
    Assert.Contains("title", exception.ValidationError, StringComparison.OrdinalIgnoreCase);
}
```

### Integration Tests

```csharp
[Fact]
public async Task UpdateTask_WhenNotFound_ShouldReturn404WithErrorResponse()
{
    // Arrange
    var taskId = Guid.NewGuid();
    var request = new { title = "Updated Title" };

    // Act
    var response = await _client.PutAsJsonAsync($"/api/tasks/{taskId}", request);

    // Assert
    response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    
    var error = await response.Content.ReadFromJsonAsync<ErrorResponse>();
    error.Should().NotBeNull();
    error!.ErrorCode.Should().Be("TASK_NOT_FOUND");
    error.Message.Should().Contain(taskId.ToString());
    error.TraceId.Should().NotBeNullOrEmpty();
}
```

---

## CORTEX Brain Protection Integration

Add to `brain-protection-rules.yaml`:

```yaml
- rule_id: DOMAIN_EXCEPTION_ENFORCEMENT
  name: Domain-Specific Exception Usage
  severity: warning
  description: "Domain errors MUST use domain exceptions, not framework exceptions (KeyNotFoundException, ArgumentException, etc.)"
  detection:
    combined_keywords:
      framework_exceptions:
      - "throw new KeyNotFoundException"
      - "throw new ArgumentException"
      - "throw new InvalidOperationException"
      domain_context:
      - "Repository"
      - "Handler"
      - "Service"
  alternatives:
  - "Create domain exception: TaskNotFoundException, InvalidTaskException"
  - "Throw from Domain layer, catch in Application layer"
  - "Log with context before throwing"
```

---

## Best Practices Summary

1. **Use domain exceptions** for domain errors, not framework exceptions
2. **Log at appropriate levels:** Error (500s), Warning (400s), Info (success)
3. **Include context** in log messages (IDs, operation names, user data)
4. **Centralize exception handling** in middleware for consistent responses
5. **Validate early** in handlers before executing business logic
6. **Use Result pattern** for expected failures (not exceptional conditions)
7. **Make checkpoints non-blocking** - warn on failure, continue execution
8. **Retry transient errors** (network, timeouts) with exponential backoff
9. **Test error scenarios** with unit and integration tests
10. **Provide trace IDs** for debugging production errors

---

## References

- Cortex-Clean CODE-QUALITY-REVIEW.md (Recommendations #2, #3)
- CORTEX checkpoint-failure-handling.md (450+ lines)
- Planning orchestrator error handling implementation
- BaseAgent standard response format

---

**Next Steps:**
1. Apply to Cortex-Clean sample app (create domain exceptions)
2. Add error handling examples to CleanSolidApp
3. Update planning DoR/DoD with error handling requirements
4. Create error handling checklist for code reviews
