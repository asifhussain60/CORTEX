namespace BadMonolith.Models
{
    /// <summary>
    /// Task model with intentional anti-patterns and missing validations.
    /// 
    /// Anti-patterns demonstrated:
    /// ❌ No data validation attributes
    /// ❌ No XML documentation
    /// ❌ Missing audit fields
    /// ❌ Same model for request and response (information leakage)
    /// ❌ No null reference handling
    /// </summary>
    public class Task
    {
        // ❌ FLAW: No required attribute
        // ❌ FLAW: No length validation
        public int Id { get; set; }
        
        // ❌ FLAW: No nullable reference warning suppression
        // ❌ FLAW: No validation
        public string Title { get; set; }
        
        // ❌ FLAW: No documentation
        public bool IsCompleted { get; set; }
        
        // ❌ FLAW: Missing enterprise audit fields:
        // - CreatedAt
        // - UpdatedAt
        // - CreatedBy
        // - Version (for optimistic concurrency)
        // - Timestamp
    }

    /// <summary>
    /// API Response model with anti-patterns.
    /// 
    /// ❌ FLAW: Generic response type - doesn't document response structure
    /// ❌ FLAW: Can return anything in data field
    /// ❌ FLAW: No typed error responses
    /// </summary>
    public class ApiResponse
    {
        // ❌ FLAW: Generic object type - loses type safety
        public object Data { get; set; }
        
        // ❌ FLAW: String message - no error codes
        public string Message { get; set; }
        
        // ❌ FLAW: No timestamp
        // ❌ FLAW: No correlation ID
    }
}
