using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using KDS.Dashboard.WPF.Models;

namespace KDS.Dashboard.WPF.Services
{
    /// <summary>
    /// Service to run .NET tests and parse results for Left Brain health
    /// </summary>
    public class TestRunner
    {
        private readonly string _testProjectPath;
        private readonly string _resultsDirectory;

        public TestRunner()
        {
            // Find the solution directory by walking up from the base directory
            var baseDir = AppDomain.CurrentDomain.BaseDirectory;
            var currentDir = new DirectoryInfo(baseDir);
            
            // Walk up to find the solution root (contains .sln file)
            while (currentDir != null && !Directory.GetFiles(currentDir.FullName, "*.sln").Any())
            {
                currentDir = currentDir.Parent!;
            }
            
            if (currentDir != null)
            {
                _testProjectPath = Path.Combine(currentDir.FullName, "KDS.Dashboard.WPF.Tests", "KDS.Dashboard.WPF.Tests.csproj");
            }
            else
            {
                // Fallback to relative path
                _testProjectPath = Path.Combine(baseDir, @"..\..\..\..\KDS.Dashboard.WPF.Tests\KDS.Dashboard.WPF.Tests.csproj");
            }
            
            _resultsDirectory = Path.Combine(Path.GetTempPath(), "KdsDashboardTests");
            Directory.CreateDirectory(_resultsDirectory);
        }

        /// <summary>
        /// Run all tests and return health metrics
        /// </summary>
        public async Task<TestSuiteHealth> RunTestsAsync()
        {
            var health = new TestSuiteHealth
            {
                SuiteName = "KDS Dashboard Tests",
                LastRun = DateTime.Now
            };

            try
            {
                // Check if test project exists
                var fullTestPath = Path.GetFullPath(_testProjectPath);
                if (!File.Exists(fullTestPath))
                {
                    System.Diagnostics.Debug.WriteLine($"TestRunner: Test project not found at {fullTestPath}");
                    health.Status = "Error";
                    health.TotalTests = 1;
                    health.FailedTests = 1;
                    return health;
                }
                
                var stopwatch = Stopwatch.StartNew();
                var resultsFile = Path.Combine(_resultsDirectory, "test-results.trx");

                // Delete old results
                if (File.Exists(resultsFile))
                    File.Delete(resultsFile);

                // Run dotnet test with TRX logger
                var psi = new ProcessStartInfo
                {
                    FileName = "dotnet",
                    Arguments = $"test \"{fullTestPath}\" --logger \"trx;LogFileName={resultsFile}\" --nologo --verbosity quiet",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                System.Diagnostics.Debug.WriteLine($"TestRunner: Running command: {psi.FileName} {psi.Arguments}");

                using (var process = Process.Start(psi))
                {
                    if (process == null)
                    {
                        health.Status = "Error";
                        health.TotalTests = 1;
                        health.FailedTests = 1;
                        return health;
                    }

                    var output = await process.StandardOutput.ReadToEndAsync();
                    var error = await process.StandardError.ReadToEndAsync();
                    await process.WaitForExitAsync();

                    stopwatch.Stop();
                    health.Duration = stopwatch.Elapsed;
                    
                    System.Diagnostics.Debug.WriteLine($"TestRunner: Exit code: {process.ExitCode}");
                    System.Diagnostics.Debug.WriteLine($"TestRunner: Output: {output}");
                    if (!string.IsNullOrEmpty(error))
                    {
                        System.Diagnostics.Debug.WriteLine($"TestRunner: Error: {error}");
                    }

                    // Parse the output for quick stats
                    ParseConsoleOutput(output, health);

                    // If TRX file exists, parse it for detailed results
                    if (File.Exists(resultsFile))
                    {
                        ParseTrxResults(resultsFile, health);
                    }
                    
                    // Always set status based on calculated health, not error messages
                    health.Status = health.GetHealthStatus();
                }
            }
            catch (Exception ex)
            {
                // Even on exception, use calculated health if we have test data
                if (health.TotalTests > 0)
                {
                    health.Status = health.GetHealthStatus();
                }
                else
                {
                    health.Status = "Error";
                    health.TotalTests = 1;
                    health.FailedTests = 1;
                }
                
                // Log the error for diagnostics
                System.Diagnostics.Debug.WriteLine($"Test runner error: {ex.Message}");
            }

            return health;
        }

        /// <summary>
        /// Parse console output for test counts
        /// </summary>
        private void ParseConsoleOutput(string output, TestSuiteHealth health)
        {
            // Pattern: "Total tests: 99. Passed: 93. Failed: 1. Skipped: 5."
            var totalMatch = Regex.Match(output, @"Total tests:\s*(\d+)");
            var passedMatch = Regex.Match(output, @"Passed:\s*(\d+)");
            var failedMatch = Regex.Match(output, @"Failed:\s*(\d+)");
            var skippedMatch = Regex.Match(output, @"Skipped:\s*(\d+)");

            if (totalMatch.Success)
                health.TotalTests = int.Parse(totalMatch.Groups[1].Value);
            
            if (passedMatch.Success)
                health.PassedTests = int.Parse(passedMatch.Groups[1].Value);
            
            if (failedMatch.Success)
                health.FailedTests = int.Parse(failedMatch.Groups[1].Value);
            
            if (skippedMatch.Success)
                health.SkippedTests = int.Parse(skippedMatch.Groups[1].Value);
        }

        /// <summary>
        /// Parse TRX XML file for detailed test results
        /// </summary>
        private void ParseTrxResults(string trxFile, TestSuiteHealth health)
        {
            try
            {
                var xml = File.ReadAllText(trxFile);

                // Parse total/passed/failed from ResultSummary
                var outcomeMatch = Regex.Match(xml, @"<Counters\s+total=""(\d+)""\s+executed=""(\d+)""\s+passed=""(\d+)""\s+failed=""(\d+)""");
                
                if (outcomeMatch.Success)
                {
                    health.TotalTests = int.Parse(outcomeMatch.Groups[1].Value);
                    health.PassedTests = int.Parse(outcomeMatch.Groups[3].Value);
                    health.FailedTests = int.Parse(outcomeMatch.Groups[4].Value);
                    health.SkippedTests = health.TotalTests - int.Parse(outcomeMatch.Groups[2].Value);
                }

                // Extract failed test details
                var failedTestMatches = Regex.Matches(xml, 
                    @"<UnitTestResult.*?outcome=""Failed"".*?testName=""([^""]+)"".*?<Message>(.*?)</Message>", 
                    RegexOptions.Singleline);

                foreach (Match match in failedTestMatches)
                {
                    health.Failures.Add(new FailedTestInfo
                    {
                        TestName = match.Groups[1].Value,
                        ErrorMessage = System.Net.WebUtility.HtmlDecode(match.Groups[2].Value.Trim())
                    });
                }
            }
            catch (Exception ex)
            {
                // If TRX parsing fails, keep console output results
                System.Diagnostics.Debug.WriteLine($"Failed to parse TRX: {ex.Message}");
            }
        }

        /// <summary>
        /// Get cached test results from last run (if available)
        /// </summary>
        public TestSuiteHealth? GetCachedResults()
        {
            var cacheFile = Path.Combine(_resultsDirectory, "cached-results.json");
            
            if (!File.Exists(cacheFile))
                return null;

            try
            {
                var json = File.ReadAllText(cacheFile);
                return JsonSerializer.Deserialize<TestSuiteHealth>(json);
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Save test results to cache
        /// </summary>
        public void CacheResults(TestSuiteHealth health)
        {
            var cacheFile = Path.Combine(_resultsDirectory, "cached-results.json");
            
            try
            {
                var json = JsonSerializer.Serialize(health, new JsonSerializerOptions
                {
                    WriteIndented = true
                });
                File.WriteAllText(cacheFile, json);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to cache results: {ex.Message}");
            }
        }
    }
}
