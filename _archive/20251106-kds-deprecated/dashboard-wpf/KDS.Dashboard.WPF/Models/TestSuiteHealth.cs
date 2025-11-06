using System;
using System.Collections.Generic;

namespace KDS.Dashboard.WPF.Models
{
    /// <summary>
    /// Represents the health status of a test suite
    /// </summary>
    public class TestSuiteHealth
    {
        public string SuiteName { get; set; } = string.Empty;
        public int TotalTests { get; set; }
        public int PassedTests { get; set; }
        public int FailedTests { get; set; }
        public int SkippedTests { get; set; }
        public double PassRate => TotalTests > 0 ? (double)PassedTests / TotalTests * 100 : 0;
        public string Status { get; set; } = "Unknown";
        public DateTime LastRun { get; set; }
        public TimeSpan Duration { get; set; }
        public List<FailedTestInfo> Failures { get; set; } = new List<FailedTestInfo>();

        /// <summary>
        /// Get health status based on pass rate
        /// </summary>
        public string GetHealthStatus()
        {
            if (PassRate >= 95) return "Excellent";
            if (PassRate >= 85) return "Good";
            if (PassRate >= 70) return "Fair";
            return "Poor";
        }
    }

    /// <summary>
    /// Information about a failed test
    /// </summary>
    public class FailedTestInfo
    {
        public string TestName { get; set; } = string.Empty;
        public string ErrorMessage { get; set; } = string.Empty;
        public string StackTrace { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
    }

    /// <summary>
    /// Combined brain health status
    /// </summary>
    public class BrainHealthStatus
    {
        // Left Brain - Test-Based
        public string LeftBrainHealth { get; set; } = "Unknown";
        public TestSuiteHealth? LeftBrainTests { get; set; }
        public bool IsLeftBrainLoading { get; set; }
        
        // Right Brain - Application Metrics
        public string RightBrainHealth { get; set; } = "Unknown";
        public List<HealthFactor> RightBrainMetrics { get; set; } = new List<HealthFactor>();
        
        // Combined
        public string OverallHealth { get; set; } = "Unknown";
        public DateTime LastUpdated { get; set; }
    }

    /// <summary>
    /// Individual health metric factor
    /// </summary>
    public class HealthFactor
    {
        public string Name { get; set; } = string.Empty;
        public int CurrentValue { get; set; }
        public int Threshold { get; set; }
        public string Status { get; set; } = "Unknown";
        public string Description { get; set; } = string.Empty;
        public bool IsHealthy { get; set; }
    }
}
