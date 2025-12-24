# Pagination Patterns for CORTEX Features

**Version:** 1.0  
**Date:** December 8, 2025  
**Author:** Asif Hussain  
**Purpose:** Reusable pagination patterns for CORTEX features and sample applications

---

## Overview

Pagination is essential for handling large datasets efficiently. This guide provides patterns for implementing pagination in:
- REST APIs (offset-based, cursor-based)
- Database queries (SQLite, EF Core)
- UI components (Angular, React)
- CORTEX brain tier queries

**Addresses:** Cortex-Clean recommendation #5 (Medium Priority)

---

## Pattern 1: Offset-Based Pagination (Simple)

### Use Case
- Small to medium datasets (< 100K records)
- User needs to jump to specific pages
- Stable result ordering

### Implementation

#### Backend (.NET/C#)

```csharp
// Request DTO
public record PagedRequest(int PageNumber = 1, int PageSize = 20);

// Response DTO
public record PagedResult<T>(
    IEnumerable<T> Items,
    int TotalCount,
    int PageNumber,
    int PageSize
)
{
    public int TotalPages => (int)Math.Ceiling(TotalCount / (double)PageSize);
    public bool HasPrevious => PageNumber > 1;
    public bool HasNext => PageNumber < TotalPages;
};

// Repository Extension
public static class QueryableExtensions
{
    public static async Task<PagedResult<T>> ToPagedResultAsync<T>(
        this IQueryable<T> query,
        int pageNumber,
        int pageSize,
        CancellationToken cancellationToken = default)
    {
        var totalCount = await query.CountAsync(cancellationToken);
        var items = await query
            .Skip((pageNumber - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync(cancellationToken);
        
        return new PagedResult<T>(items, totalCount, pageNumber, pageSize);
    }
}

// Handler Example (CQRS)
public record GetTasksQuery(int PageNumber = 1, int PageSize = 20) 
    : IRequest<PagedResult<TaskDto>>;

public class GetTasksQueryHandler : IRequestHandler<GetTasksQuery, PagedResult<TaskDto>>
{
    private readonly IApplicationDbContext _context;
    private readonly IMapper _mapper;

    public async Task<PagedResult<TaskDto>> Handle(
        GetTasksQuery request, 
        CancellationToken cancellationToken)
    {
        var pagedTasks = await _context.Tasks
            .AsNoTracking()
            .OrderByDescending(t => t.CreatedAt)
            .ToPagedResultAsync(request.PageNumber, request.PageSize, cancellationToken);
        
        var dtos = _mapper.Map<IEnumerable<TaskDto>>(pagedTasks.Items);
        
        return new PagedResult<TaskDto>(
            dtos, 
            pagedTasks.TotalCount, 
            pagedTasks.PageNumber, 
            pagedTasks.PageSize);
    }
}
```

#### API Controller

```csharp
[HttpGet]
public async Task<ActionResult<PagedResult<TaskDto>>> GetTasks(
    [FromQuery] int pageNumber = 1,
    [FromQuery] int pageSize = 20)
{
    if (pageSize > 100)
        return BadRequest("Page size cannot exceed 100");
    
    var query = new GetTasksQuery(pageNumber, pageSize);
    var result = await _mediator.Send(query);
    
    return Ok(result);
}
```

#### Frontend (Angular)

```typescript
// Service
export interface PagedResult<T> {
  items: T[];
  totalCount: number;
  pageNumber: number;
  pageSize: number;
  totalPages: number;
  hasPrevious: boolean;
  hasNext: boolean;
}

getTasks(pageNumber: number = 1, pageSize: number = 20): Observable<PagedResult<Task>> {
  return this.http.get<PagedResult<Task>>(
    `${this.apiUrl}/tasks?pageNumber=${pageNumber}&pageSize=${pageSize}`
  );
}

// Component
export class TaskListComponent {
  tasks: Task[] = [];
  currentPage = 1;
  pageSize = 20;
  totalPages = 1;
  hasNext = false;
  hasPrevious = false;

  loadTasks() {
    this.taskService.getTasks(this.currentPage, this.pageSize)
      .subscribe(result => {
        this.tasks = result.items;
        this.totalPages = result.totalPages;
        this.hasNext = result.hasNext;
        this.hasPrevious = result.hasPrevious;
      });
  }

  nextPage() {
    if (this.hasNext) {
      this.currentPage++;
      this.loadTasks();
    }
  }

  previousPage() {
    if (this.hasPrevious) {
      this.currentPage--;
      this.loadTasks();
    }
  }
}
```

---

## Pattern 2: Cursor-Based Pagination (High Performance)

### Use Case
- Large datasets (> 100K records)
- Real-time data with frequent inserts
- Infinite scroll UIs
- No need to jump to specific pages

### Implementation

#### Backend

```csharp
// Request DTO
public record CursorPagedRequest(
    string? Cursor = null,  // Last item's ID from previous page
    int PageSize = 20
);

// Response DTO
public record CursorPagedResult<T>(
    IEnumerable<T> Items,
    string? NextCursor,  // ID to fetch next page
    bool HasMore
);

// Handler
public record GetTasksCursorQuery(string? Cursor, int PageSize = 20) 
    : IRequest<CursorPagedResult<TaskDto>>;

public class GetTasksCursorQueryHandler 
    : IRequestHandler<GetTasksCursorQuery, CursorPagedResult<TaskDto>>
{
    private readonly IApplicationDbContext _context;
    private readonly IMapper _mapper;

    public async Task<CursorPagedResult<TaskDto>> Handle(
        GetTasksCursorQuery request, 
        CancellationToken cancellationToken)
    {
        var query = _context.Tasks.AsNoTracking();
        
        // Apply cursor filter (fetch records AFTER cursor)
        if (!string.IsNullOrEmpty(request.Cursor) && Guid.TryParse(request.Cursor, out var cursorId))
        {
            var cursorTask = await _context.Tasks.FindAsync(cursorId);
            if (cursorTask != null)
            {
                query = query.Where(t => t.CreatedAt < cursorTask.CreatedAt || 
                    (t.CreatedAt == cursorTask.CreatedAt && t.Id.CompareTo(cursorId) < 0));
            }
        }
        
        // Fetch PageSize + 1 to determine if there are more records
        var tasks = await query
            .OrderByDescending(t => t.CreatedAt)
            .ThenByDescending(t => t.Id)
            .Take(request.PageSize + 1)
            .ToListAsync(cancellationToken);
        
        var hasMore = tasks.Count > request.PageSize;
        var items = hasMore ? tasks.Take(request.PageSize) : tasks;
        var nextCursor = hasMore ? tasks[request.PageSize - 1].Id.ToString() : null;
        
        var dtos = _mapper.Map<IEnumerable<TaskDto>>(items);
        
        return new CursorPagedResult<TaskDto>(dtos, nextCursor, hasMore);
    }
}
```

#### Frontend (Infinite Scroll)

```typescript
export class InfiniteScrollTaskListComponent implements OnInit {
  tasks: Task[] = [];
  cursor: string | null = null;
  loading = false;
  hasMore = true;

  ngOnInit() {
    this.loadMore();
  }

  @HostListener('window:scroll', ['$event'])
  onScroll() {
    const scrollPosition = window.innerHeight + window.scrollY;
    const threshold = document.body.offsetHeight - 100;
    
    if (scrollPosition >= threshold && !this.loading && this.hasMore) {
      this.loadMore();
    }
  }

  loadMore() {
    if (!this.hasMore || this.loading) return;
    
    this.loading = true;
    this.taskService.getTasksCursor(this.cursor, 20)
      .subscribe(result => {
        this.tasks = [...this.tasks, ...result.items];
        this.cursor = result.nextCursor;
        this.hasMore = result.hasMore;
        this.loading = false;
      });
  }
}
```

---

## Pattern 3: CORTEX Brain Tier Pagination

### Use Case
- Paginating conversation history (Tier 1)
- Paginating knowledge graph results (Tier 2)
- Paginating code metrics (Tier 3)

### Implementation

#### Tier 1 Working Memory (SQLite)

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PagedResult:
    items: List[dict]
    total_count: int
    page_number: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        return (self.total_count + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        return self.page_number < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        return self.page_number > 1

class WorkingMemory:
    def get_conversation_history_paged(
        self, 
        page_number: int = 1, 
        page_size: int = 20,
        filter_intent: Optional[str] = None
    ) -> PagedResult:
        """Get paginated conversation history."""
        
        # Build query
        query = "SELECT * FROM conversations"
        count_query = "SELECT COUNT(*) FROM conversations"
        params = []
        
        if filter_intent:
            where_clause = " WHERE intent = ?"
            query += where_clause
            count_query += where_clause
            params.append(filter_intent)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        
        # Get total count
        cursor = self.conn.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get page items
        offset = (page_number - 1) * page_size
        params.extend([page_size, offset])
        cursor = self.conn.execute(query, params)
        
        items = [dict(row) for row in cursor.fetchall()]
        
        return PagedResult(
            items=items,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size
        )
```

---

## Pattern 4: Keyset Pagination (Optimal for SQLite)

### Use Case
- Very large CORTEX brain tier queries
- Need consistent performance regardless of page depth
- Results sorted by indexed columns

### Implementation

```python
from typing import Optional, Tuple

class Tier2KnowledgeGraph:
    def get_patterns_keyset(
        self,
        page_size: int = 20,
        last_id: Optional[int] = None,
        last_score: Optional[float] = None
    ) -> Tuple[List[dict], bool]:
        """
        Keyset pagination for patterns sorted by score DESC, id DESC.
        Returns (items, has_more).
        """
        
        query = """
        SELECT id, pattern, score, frequency 
        FROM patterns 
        WHERE (score, id) < (?, ?)
        ORDER BY score DESC, id DESC 
        LIMIT ?
        """
        
        # First page: use maximum values
        if last_id is None or last_score is None:
            last_score = float('inf')
            last_id = 2**63 - 1  # Max int64
        
        # Fetch page_size + 1 to check for more records
        cursor = self.conn.execute(query, (last_score, last_id, page_size + 1))
        items = [dict(row) for row in cursor.fetchall()]
        
        has_more = len(items) > page_size
        if has_more:
            items = items[:page_size]
        
        return items, has_more

# Usage
patterns, has_more = kg.get_patterns_keyset(page_size=20)
if has_more:
    last_item = patterns[-1]
    next_patterns, has_more = kg.get_patterns_keyset(
        page_size=20,
        last_id=last_item['id'],
        last_score=last_item['score']
    )
```

---

## Performance Comparison

| Pattern | Dataset Size | Page Jump | Performance | Use Case |
|---------|--------------|-----------|-------------|----------|
| **Offset-Based** | < 100K | ✅ Yes | O(n) degrades with page | Simple pagination, page numbers |
| **Cursor-Based** | > 100K | ❌ No | O(1) consistent | Infinite scroll, real-time data |
| **Keyset** | Any | ⚠️ Limited | O(log n) indexed | Large CORTEX queries, optimal SQLite |

---

## Testing Strategy

### Unit Tests

```csharp
[Fact]
public async Task GetTasks_ShouldReturnPagedResult()
{
    // Arrange
    var handler = new GetTasksQueryHandler(_context, _mapper);
    var query = new GetTasksQuery(PageNumber: 1, PageSize: 10);
    
    // Act
    var result = await handler.Handle(query, CancellationToken.None);
    
    // Assert
    result.PageNumber.Should().Be(1);
    result.PageSize.Should().Be(10);
    result.Items.Should().HaveCountLessOrEqualTo(10);
    result.TotalCount.Should().BeGreaterOrEqualTo(result.Items.Count());
}

[Fact]
public async Task GetTasks_WithInvalidPageSize_ShouldThrowValidationException()
{
    // Arrange
    var query = new GetTasksQuery(PageNumber: 1, PageSize: 1000);
    
    // Act & Assert
    await Assert.ThrowsAsync<ValidationException>(
        () => handler.Handle(query, CancellationToken.None)
    );
}
```

### Integration Tests

```csharp
[Fact]
public async Task PaginationAPI_ShouldReturnConsistentResults()
{
    // Arrange: Create 50 test tasks
    for (int i = 0; i < 50; i++)
    {
        await _client.PostAsync("/api/tasks", CreateTaskContent($"Task {i}"));
    }
    
    // Act: Fetch all pages
    var allTasks = new List<TaskDto>();
    var pageNumber = 1;
    PagedResult<TaskDto>? result;
    
    do
    {
        var response = await _client.GetAsync($"/api/tasks?pageNumber={pageNumber}&pageSize=10");
        result = await response.Content.ReadFromJsonAsync<PagedResult<TaskDto>>();
        allTasks.AddRange(result!.Items);
        pageNumber++;
    } while (result.HasNext);
    
    // Assert
    allTasks.Should().HaveCount(50);
    allTasks.Select(t => t.Id).Should().OnlyHaveUniqueItems();
}
```

---

## CORTEX Integration

### Brain Protector Validation

Add to `brain-protection-rules.yaml`:

```yaml
- rule_id: PAGINATION_ENFORCEMENT
  name: Pagination Required for Large Datasets
  severity: warning
  description: "Queries returning >100 records MUST implement pagination"
  detection:
    combined_keywords:
      query_patterns:
      - "ToListAsync()"
      - ".ToList()"
      - "GetAll"
      missing_pagination:
      - "no Take()"
      - "no Skip()"
      - "no pagination"
  alternatives:
  - "Use ToPagedResultAsync() extension method"
  - "Implement cursor-based pagination for infinite scroll"
  - "Add PageSize validation (max 100)"
```

### Planning DoR/DoD Integration

**Definition of Ready (DoR):**
- [ ] Pagination requirements specified (offset/cursor/keyset)
- [ ] Maximum page size defined
- [ ] UI pattern selected (page numbers/infinite scroll)

**Definition of Done (DoD):**
- [ ] Pagination implemented with PagedResult<T>
- [ ] Maximum page size enforced (≤100)
- [ ] Unit tests verify page boundaries
- [ ] Integration tests validate consistency

---

## Migration Guide: Adding Pagination to Existing Features

### Step 1: Update Query DTOs

```csharp
// Before
public record GetTasksQuery : IRequest<IEnumerable<TaskDto>>;

// After
public record GetTasksQuery(int PageNumber = 1, int PageSize = 20) 
    : IRequest<PagedResult<TaskDto>>;
```

### Step 2: Update Handler

```csharp
// Before
var tasks = await _context.Tasks.ToListAsync(cancellationToken);

// After
var pagedTasks = await _context.Tasks
    .ToPagedResultAsync(request.PageNumber, request.PageSize, cancellationToken);
```

### Step 3: Update API Contract

```csharp
// Before
[HttpGet]
public async Task<ActionResult<IEnumerable<TaskDto>>> GetTasks()

// After
[HttpGet]
public async Task<ActionResult<PagedResult<TaskDto>>> GetTasks(
    [FromQuery] int pageNumber = 1,
    [FromQuery] int pageSize = 20)
```

### Step 4: Update Frontend

```typescript
// Before
tasks$: Observable<Task[]> = this.taskService.getTasks();

// After
loadTasks(page: number = 1) {
  this.taskService.getTasks(page, this.pageSize)
    .subscribe(result => {
      this.tasks = result.items;
      this.totalPages = result.totalPages;
    });
}
```

---

## Best Practices

1. **Always set maximum page size** (e.g., 100) to prevent abuse
2. **Include total count** in offset pagination for UI page indicators
3. **Use indexed columns** for cursor/keyset pagination (CreatedAt, Id)
4. **Validate page number ≥ 1** to prevent negative offsets
5. **Return empty array** for out-of-bounds pages, not 404
6. **Cache total count** if expensive to calculate (invalidate on writes)
7. **Document pagination** in API contracts (OpenAPI/Swagger)
8. **Test edge cases:** empty results, single page, last page

---

## References

- Cortex-Clean CODE-QUALITY-REVIEW.md (Recommendation #5)
- CORTEX brain-protection-rules.yaml (PAGINATION_ENFORCEMENT)
- Clean Architecture patterns (CQRS + pagination)
- SQLite optimization guide (keyset pagination)

---

**Next Steps:**
1. Apply to Cortex-Clean sample app
2. Create pagination templates for CleanSolidApp
3. Add pagination examples to CORTEX dashboard
4. Update planning orchestrator DoR/DoD with pagination requirements
