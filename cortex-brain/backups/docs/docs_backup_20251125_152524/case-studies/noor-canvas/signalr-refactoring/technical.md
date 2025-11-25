# Technical Deep Dive: SignalR Architecture Evolution

[← Back to Success Metrics](metrics.md) | [Next: Lessons Learned →](lessons.md)

---

## 🏗️ Architecture Evolution

### Before: Monolithic Inline Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ HostControlPanel.razor (4,951 LOC)                          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ InitializeSignalRAsync() - 350 lines                    │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ hubConnection = new HubConnectionBuilder()          │ │ │
│ │ │     .WithUrl("/hub/session")                        │ │ │
│ │ │     .Build();                                       │ │ │
│ │ │                                                     │ │ │
│ │ │ hubConnection.On<object>("QuestionReceived",       │ │ │
│ │ │   (data) => {                                      │ │ │
│ │ │     // 80+ lines of JSON parsing               │ │ │
│ │ │     // UI updates                               │ │ │
│ │ │     // Error handling                           │ │ │
│ │ │   });                                              │ │ │
│ │ │                                                     │ │ │
│ │ │ // 4 more handlers × 50-80 lines each = 250 LOC    │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SessionCanvas.razor (4,056 LOC)                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ InitializeSignalRAsync() - ~300 lines                   │ │
│ │ // DUPLICATE CODE: Same pattern as HostControlPanel     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TranscriptCanvas.razor (4,871 LOC)                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ InitializeSignalRAsync() - ~300 lines                   │ │
│ │ // DUPLICATE CODE: Same pattern as HostControlPanel     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Problems:
❌ ~900 lines duplicated across 3 components
❌ Tight coupling (UI + JSON parsing + business logic)
❌ Untestable (Blazor infrastructure dependencies)
❌ Inconsistent error handling
❌ No health monitoring
❌ Connection issues hard to debug
```

### After: Service-Oriented Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Service Layer (Centralized)                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ IHostSignalREventHandler (5 methods, 287 LOC)           │ │
│ │ ├─ HandleQuestionReceivedAsync()                        │ │
│ │ ├─ HandleTranscriptUpdatedAsync()                       │ │
│ │ ├─ HandleVoteUpdateReceivedAsync()                      │ │
│ │ ├─ HandleHostQuestionUpdatedAsync()                     │ │
│ │ └─ HandleHostQuestionDeletedAsync()                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ISessionCanvasSignalRService (8 methods, 336 LOC)       │ │
│ │ ├─ HandleQuestionAddedAsync()                           │ │
│ │ ├─ HandleQuestionUpdatedAsync()                         │ │
│ │ ├─ HandleQuestionDeletedAsync()                         │ │
│ │ ├─ HandleVoteUpdatedAsync()                             │ │
│ │ ├─ HandleAssetSharedAsync()                             │ │
│ │ ├─ HandleTranscriptUpdatedAsync()                       │ │
│ │ ├─ HandleSessionEndedAsync()                            │ │
│ │ └─ HandleParticipantToastAsync()                        │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ DI Injection
                              │
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure Layer (Middleware)                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ SignalRMiddleware                                        │ │
│ │ ├─ GetOrCreateConnectionAsync()                         │ │
│ │ ├─ Health monitoring (30s interval)                     │ │
│ │ ├─ Exponential backoff (2s → 32s)                       │ │
│ │ └─ Diagnostic logging                                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ HubConnectionFactory                                     │ │
│ │ ├─ Absolute URL resolution (IHttpContextAccessor)       │ │
│ │ ├─ Configurable hub paths                               │ │
│ │ └─ Error handling & logging                             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ Uses
                              │
┌─────────────────────────────────────────────────────────────┐
│ Component Layer (Thin UI)                                    │
│ ┌───────────────┬───────────────┬──────────────────────────┐│
│ │ HostControl   │ SessionCanvas │ TranscriptCanvas         ││
│ │ Panel.razor   │ .razor        │ .razor                   ││
│ │ (4,636 LOC)   │ (3,740 LOC)   │ (3,982 LOC)              ││
│ │               │               │                          ││
│ │ @inject IHost │ @inject ISess │ @inject ISessionCanvas   ││
│ │ SignalREvent  │ ionCanvasSig  │ SignalRService           ││
│ │ Handler       │ nalRService   │                          ││
│ │               │               │                          ││
│ │ Only UI logic │ Only UI logic │ Only UI logic            ││
│ │ 35 LOC init   │ Delegated     │ Delegated                ││
│ └───────────────┴───────────────┴──────────────────────────┘│
└─────────────────────────────────────────────────────────────┘

Benefits:
✅ Single source of truth for SignalR logic
✅ Testable in isolation (33 unit tests)
✅ Consistent error handling & logging
✅ Centralized health monitoring
✅ Easy to debug (diagnostic logging throughout)
✅ 11% code reduction (1,520 lines eliminated)
```

---

## 🔧 Design Patterns Applied

### 1. Service Layer Pattern

**Purpose:** Separate business logic from UI components

**Implementation:**
```csharp
// Service Interface
public interface IHostSignalREventHandler
{
    Task HandleQuestionReceivedAsync(
        object data, 
        Func<QuestionData, Task>? callback = null);
        
    Task HandleTranscriptUpdatedAsync(
        string transcript, 
        Func<string, Task>? callback = null);
    
    // ... 3 more methods
}

// Service Implementation
public class HostSignalREventHandler : IHostSignalREventHandler
{
    private readonly ILogger<HostSignalREventHandler> _logger;
    
    public async Task HandleQuestionReceivedAsync(
        object data, 
        Func<QuestionData, Task>? callback = null)
    {
        try
        {
            var jsonString = JsonSerializer.Serialize(data);
            using var jsonDocument = JsonDocument.Parse(jsonString);
            var root = jsonDocument.RootElement;
            
            var questionData = new QuestionData
            {
                QuestionId = root.GetProperty("questionId").GetString(),
                Text = root.GetProperty("text").GetString(),
                UserName = root.GetProperty("userName").GetString(),
                // ... more properties
            };
            
            if (callback != null)
                await callback(questionData);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in HandleQuestionReceivedAsync");
            throw;
        }
    }
}
```

**Benefits:**
- ✅ Testable without Blazor infrastructure
- ✅ Reusable across multiple components
- ✅ Centralized error handling
- ✅ Type-safe callbacks

### 2. Dependency Injection Pattern

**Purpose:** Inversion of control for loose coupling

**Registration (Program.cs):**
```csharp
builder.Services.AddScoped<IHostSignalREventHandler, HostSignalREventHandler>();
builder.Services.AddScoped<ISessionCanvasSignalRService, SessionCanvasSignalRService>();
builder.Services.AddSingleton<SignalRMiddleware>();
builder.Services.AddSingleton<HubConnectionFactory>();
builder.Services.AddHttpContextAccessor(); // Phase 5 fix
```

**Component Injection:**
```csharp
@inject IHostSignalREventHandler SignalREventHandler
@inject ISessionCanvasSignalRService SessionCanvasService

@code {
    protected override async Task OnInitializedAsync()
    {
        // Services ready to use, no manual instantiation
        await SignalREventHandler.HandleQuestionReceivedAsync(data, OnQuestionReceived);
    }
}
```

### 3. Type Adapter Pattern

**Purpose:** Bridge incompatible nested class types

**Problem:**
```csharp
// SessionCanvas has this nested class
public class SessionCanvas
{
    public class QuestionData { ... }
}

// But service returns this type
public class TranscriptCanvas
{
    public class QuestionData { ... }
}

// Cannot directly assign: incompatible types
```

**Solution:**
```csharp
public async Task HandleQuestionAddedAsync(
    object data, 
    Func<SessionCanvas.QuestionData, Task>? callback = null)
{
    var serviceQuestion = ParseQuestionData(data);
    
    // Type Adapter: Convert service type → component type
    var componentQuestion = new SessionCanvas.QuestionData
    {
        QuestionId = serviceQuestion.QuestionId,
        Text = serviceQuestion.Text,
        UserName = serviceQuestion.UserName,
        Timestamp = serviceQuestion.Timestamp,
        Votes = serviceQuestion.Votes
    };
    
    await callback?.Invoke(componentQuestion);
}
```

### 4. Middleware Pattern

**Purpose:** Centralized connection lifecycle management

**Implementation:**
```csharp
public class SignalRMiddleware
{
    private readonly ConcurrentDictionary<string, HubConnection> _connections = new();
    private readonly HubConnectionFactory _factory;
    
    public async Task<HubConnection> GetOrCreateConnectionAsync(
        string hubUrl, 
        string connectionKey)
    {
        if (_connections.TryGetValue(connectionKey, out var existing))
        {
            if (existing.State == HubConnectionState.Connected)
                return existing;
                
            // Reconnect if disconnected
            await existing.StartAsync();
            return existing;
        }
        
        // Create new connection
        var connection = _factory.CreateConnection(hubUrl);
        
        // Configure reconnection
        connection.Closed += async (error) =>
        {
            await Task.Delay(TimeSpan.FromSeconds(2));
            await connection.StartAsync();
        };
        
        // Start connection
        await connection.StartAsync();
        
        // Store for reuse
        _connections.TryAdd(connectionKey, connection);
        
        // Health monitoring
        _ = MonitorConnectionHealthAsync(connection, connectionKey);
        
        return connection;
    }
    
    private async Task MonitorConnectionHealthAsync(
        HubConnection connection, 
        string connectionKey)
    {
        while (connection.State == HubConnectionState.Connected)
        {
            await Task.Delay(TimeSpan.FromSeconds(30));
            
            if (connection.State != HubConnectionState.Connected)
            {
                _logger.LogWarning("Connection {Key} lost", connectionKey);
                _connections.TryRemove(connectionKey, out _);
            }
        }
    }
}
```

### 5. Factory Pattern

**Purpose:** Encapsulate connection creation logic

**Phase 4 Implementation (BEFORE):**
```csharp
public class HubConnectionFactory
{
    public HubConnection CreateConnection(string hubUrl)
    {
        return new HubConnectionBuilder()
            .WithUrl(hubUrl) // PROBLEM: Relative URL "/hub/session"
            .Build();
    }
}
```

**Phase 5 Fix (AFTER):**
```csharp
public class HubConnectionFactory
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private readonly ILogger<HubConnectionFactory> _logger;
    
    public HubConnection CreateConnection(string hubUrl)
    {
        // Convert relative → absolute URL
        var absoluteUrl = hubUrl.StartsWith("http")
            ? hubUrl
            : GetAbsoluteUrl(hubUrl);
            
        _logger.LogDebug("Creating connection to: {AbsoluteUrl}", absoluteUrl);
        
        return new HubConnectionBuilder()
            .WithUrl(absoluteUrl) // FIX: Absolute URL
            .WithAutomaticReconnect(new[] {
                TimeSpan.FromSeconds(2),
                TimeSpan.FromSeconds(4),
                TimeSpan.FromSeconds(8),
                TimeSpan.FromSeconds(16),
                TimeSpan.FromSeconds(32)
            })
            .Build();
    }
    
    private string GetAbsoluteUrl(string relativeUrl)
    {
        var httpContext = _httpContextAccessor.HttpContext;
        if (httpContext == null)
            throw new InvalidOperationException("HttpContext not available");
            
        var request = httpContext.Request;
        return $"{request.Scheme}://{request.Host}{relativeUrl}";
    }
}
```

**Impact:** 0% → 100% participant connection success

---

## 🧪 Testing Architecture

### Unit Test Structure

**Test Hierarchy:**
```
Tests/Unit/NoorCanvas.Tests.Unit.csproj
├── Services/
│   ├── HostSignalREventHandlerTests.cs (21 tests)
│   │   ├── HandleQuestionReceivedAsync_WithValidData_InvokesCallback()
│   │   ├── HandleQuestionReceivedAsync_WithNullData_ThrowsException()
│   │   ├── HandleQuestionReceivedAsync_WithInvalidJson_LogsError()
│   │   ├── HandleTranscriptUpdatedAsync_WithValidData_InvokesCallback()
│   │   ├── HandleVoteUpdateReceivedAsync_WithStringId_ConvertsToInt()
│   │   ├── HandleHostQuestionUpdatedAsync_WithNestedProperties_ParsesCorrectly()
│   │   └── ... 15 more tests
│   │
│   └── SessionCanvasSignalRServiceTests.cs (12 tests)
│       ├── HandleQuestionAddedAsync_WithValidData_ConvertsTypeSuccessfully()
│       ├── HandleQuestionUpdatedAsync_WithCallback_InvokesWithAdaptedType()
│       ├── HandleVoteUpdatedAsync_WithStringId_ConvertsCorrectly()
│       └── ... 9 more tests
```

### Test Example: JSON Parsing

```csharp
[Fact]
public async Task HandleQuestionReceivedAsync_WithValidData_InvokesCallback()
{
    // Arrange
    var handler = new HostSignalREventHandler(_logger.Object);
    var callbackInvoked = false;
    QuestionData? capturedData = null;
    
    var testData = new
    {
        questionId = "q123",
        text = "What is SignalR?",
        userName = "Alice",
        timestamp = "2025-11-24T10:30:00",
        votes = 5
    };
    
    // Act
    await handler.HandleQuestionReceivedAsync(
        testData,
        async (data) => 
        {
            callbackInvoked = true;
            capturedData = data;
            await Task.CompletedTask;
        }
    );
    
    // Assert
    Assert.True(callbackInvoked);
    Assert.NotNull(capturedData);
    Assert.Equal("q123", capturedData.QuestionId);
    Assert.Equal("What is SignalR?", capturedData.Text);
    Assert.Equal("Alice", capturedData.UserName);
    Assert.Equal(5, capturedData.Votes);
}
```

### Test Coverage Strategy

**Coverage Goals:**
- ✅ Valid data scenarios (happy path)
- ✅ Null data handling (defensive programming)
- ✅ Invalid JSON handling (malformed payloads)
- ✅ Type conversion (string/int ID handling)
- ✅ Callback invocation (ensure callbacks fire)
- ✅ Error logging (exception scenarios)

**Result:** 100% coverage for service layer (33/33 tests passing)

---

## 🔍 Code Examples: Before vs After

### Example 1: Question Received Handler

**BEFORE (Inline, 80+ lines):**
```csharp
// Inside HostControlPanel.razor InitializeSignalRAsync()
hubConnection.On<object>("QuestionReceived", async (questionData) =>
{
    try
    {
        var jsonString = JsonSerializer.Serialize(questionData);
        using var jsonDocument = JsonDocument.Parse(jsonString);
        var root = jsonDocument.RootElement;
        
        var questionId = root.GetProperty("questionId").GetString();
        var text = root.GetProperty("text").GetString();
        var userName = root.GetProperty("userName").GetString();
        var timestampStr = root.GetProperty("timestamp").GetString();
        var timestamp = DateTime.Parse(timestampStr);
        var votes = root.GetProperty("votes").GetInt32();
        
        var question = new QuestionData
        {
            QuestionId = questionId,
            Text = text,
            UserName = userName,
            Timestamp = timestamp,
            Votes = votes
        };
        
        // Update UI state
        InvokeAsync(() =>
        {
            Questions.Add(question);
            StateHasChanged();
        });
        
        // Play notification sound
        await JS.InvokeVoidAsync("playNotificationSound");
        
        _logger.LogInformation(
            "Question received: {QuestionId} from {UserName}", 
            questionId, userName);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Error processing QuestionReceived");
        await JS.InvokeVoidAsync("showToast", "Error loading question", "error");
    }
});
```

**AFTER (Service Delegation, 12 lines):**
```csharp
// Inside HostControlPanel.razor InitializeSignalRAsync()
hubConnection.On<object>("QuestionReceived", async (data) =>
{
    await SignalREventHandler.HandleQuestionReceivedAsync(data, OnQuestionReceived);
});

// Callback method (component-specific UI logic)
private async Task OnQuestionReceived(QuestionData question)
{
    InvokeAsync(() =>
    {
        Questions.Add(question);
        StateHasChanged();
    });
    
    await JS.InvokeVoidAsync("playNotificationSound");
    _logger.LogInformation("Question received: {QuestionId}", question.QuestionId);
}
```

**Improvement:**
- 📉 80+ lines → 12 lines (85% reduction)
- ✅ Testable (service logic isolated)
- ✅ Reusable (other components use same service)
- ✅ Cleaner (separation of concerns)

### Example 2: Connection Establishment

**BEFORE (Phase 4, Inline HubConnectionBuilder):**
```csharp
private async Task InitializeSignalRAsync()
{
    try
    {
        hubConnection = new HubConnectionBuilder()
            .WithUrl(NavigationManager.ToAbsoluteUri("/hub/session"))
            .WithAutomaticReconnect()
            .Build();
        
        // Register 12+ event handlers (300 lines)
        hubConnection.On<object>("QuestionAdded", async (data) => { ... });
        hubConnection.On<object>("QuestionUpdated", async (data) => { ... });
        // ... 10 more handlers
        
        await hubConnection.StartAsync();
        _logger.LogInformation("SignalR connected: {ConnectionId}", hubConnection.ConnectionId);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "SignalR connection failed");
    }
}
```

**AFTER (Phase 4, Middleware):**
```csharp
private async Task InitializeSignalRAsync()
{
    try
    {
        hubConnection = await _signalRMiddleware.GetOrCreateConnectionAsync(
            "/hub/session",
            "SessionCanvas"
        );
        
        // Register handlers using service delegation (6 delegated + 6 inline)
        hubConnection.On<object>("QuestionAdded", async (data) =>
            await _sessionCanvasService.HandleQuestionAddedAsync(data, OnQuestionAdded));
            
        // ... 11 more handlers (mix of service + inline)
        
        _logger.LogInformation("SignalR ready: {ConnectionId}", hubConnection.ConnectionId);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "SignalR initialization failed");
    }
}
```

**Improvement:**
- ✅ Centralized connection management (health monitoring, reconnection)
- ✅ Reusable connection instance (middleware caches by key)
- ✅ Consistent error handling across all components
- ✅ Health monitoring (30-second checks)

### Example 3: Phase 5 Connection Fix

**BEFORE (Relative URL, Connection Failure):**
```csharp
public class HubConnectionFactory
{
    public HubConnection CreateConnection(string hubUrl)
    {
        // PROBLEM: Relative URL fails for scoped services
        return new HubConnectionBuilder()
            .WithUrl(hubUrl) // "/hub/session" → Connection failed
            .Build();
    }
}
```

**AFTER (Absolute URL, 100% Success):**
```csharp
public class HubConnectionFactory
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private readonly ILogger<HubConnectionFactory> _logger;
    
    public HubConnection CreateConnection(string hubUrl)
    {
        var absoluteUrl = hubUrl.StartsWith("http")
            ? hubUrl
            : GetAbsoluteUrl(hubUrl);
            
        _logger.LogDebug("Creating connection to: {AbsoluteUrl}", absoluteUrl);
        
        return new HubConnectionBuilder()
            .WithUrl(absoluteUrl) // "https://localhost:9091/hub/session" → Success
            .WithAutomaticReconnect(new[] {
                TimeSpan.FromSeconds(2),
                TimeSpan.FromSeconds(4),
                TimeSpan.FromSeconds(8),
                TimeSpan.FromSeconds(16),
                TimeSpan.FromSeconds(32)
            })
            .Build();
    }
    
    private string GetAbsoluteUrl(string relativeUrl)
    {
        var httpContext = _httpContextAccessor.HttpContext;
        if (httpContext == null)
            throw new InvalidOperationException("HttpContext not available");
            
        var request = httpContext.Request;
        return $"{request.Scheme}://{request.Host}{relativeUrl}";
    }
}
```

**Impact:**
- 🔗 Connection success: 0% → 100% for participants
- 📝 Diagnostic logging for troubleshooting
- 🔄 Exponential backoff reconnection strategy
- ⏱️ Time to fix: 45 minutes (15 lines changed)

---

## 📦 Deployment Considerations

### Rollout Strategy

**Phase-by-Phase Deployment:**

1. **Phase 1-2:** Service creation (zero risk)
   - Deploy services without component changes
   - Verify DI registration
   - Run unit tests in production

2. **Phase 3:** Component updates (medium risk)
   - Deploy SessionCanvas/TranscriptCanvas changes
   - Monitor for regressions
   - Rollback plan: Revert component files

3. **Phase 4:** Middleware migration (medium risk)
   - Deploy SessionCanvas middleware changes
   - Monitor connection health
   - Rollback plan: Revert to inline HubConnectionBuilder

4. **Phase 5:** Connection fix (low risk)
   - Deploy 3-file change
   - Immediate validation (100% success rate)
   - Rollback plan: Revert 3 files

**Result:** Zero production incidents, zero rollbacks needed

---

[← Back to Success Metrics](metrics.md) | [Next: Lessons Learned →](lessons.md)
