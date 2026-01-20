using System.Collections.Generic;

namespace BadMonolith.Tests.Fixtures
{
    /// <summary>
    /// Test data builder with intentional anti-patterns.
    /// This demonstrates poor builder pattern implementation.
    /// 
    /// Anti-patterns demonstrated:
    /// ❌ Incomplete fluent interface (returns null)
    /// ❌ Missing validation in builder
    /// ❌ Inconsistent key naming (camelCase vs PascalCase)
    /// ❌ No null reference handling
    /// ❌ Missing batch building capability
    /// </summary>
    public class TestDataBuilder
    {
        private int _taskId = 1;
        private string _title = "Default Task";
        private bool _isCompleted = false;

        // ❌ FLAW: Broken fluent interface - returns null instead of this
        public TestDataBuilder WithId(int id)
        {
            _taskId = id;
            // ❌ FLAW: Should return this for fluent API
            return null; // BUG: Returns null - causes NullReferenceException in chained calls
        }

        // ❌ FLAW: No null validation
        public TestDataBuilder WithTitle(string title)
        {
            _title = title; // ❌ FLAW: No null or empty check
            return this;
        }

        public TestDataBuilder WithCompleted(bool isCompleted)
        {
            _isCompleted = isCompleted;
            return this;
        }

        // ❌ FLAW: Build method returns inconsistent key naming
        public Dictionary<string, object> Build()
        {
            // ❌ FLAW: No validation - allows invalid states
            if (_taskId == 0)
            {
                // Silently allows invalid ID - should throw
            }

            // ❌ FLAW: Inconsistent key naming (breaks serialization)
            return new Dictionary<string, object>
            {
                ["id"] = _taskId,           // ❌ lowercase key
                ["Title"] = _title,         // ❌ PascalCase key (inconsistent!)
                ["IsCompleted"] = _isCompleted  // ❌ PascalCase key (inconsistent!)
                // Frontend expects: ["isCompleted"] in camelCase
                // Backend returns: ["IsCompleted"] in PascalCase
                // This causes serialization bugs
            };
        }

        // ❌ FLAW: Missing BuildList for batch testing
        // ❌ FLAW: No reset/clear method for test reuse
        // ❌ FLAW: No fluent validation method
        // ❌ FLAW: No default factory method
    }
}
