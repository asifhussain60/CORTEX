using System;
using System.IO;
using System.Threading.Tasks;
using KDS.Dashboard.WPF.Services;
using Xunit;

namespace KDS.Dashboard.WPF.Tests.Services
{
    /// <summary>
    /// Tests for TestRunner service - ensures TDD enforcement works
    /// </summary>
    public class TestRunnerTests
    {
        [Fact]
        public void TestRunner_Constructor_ShouldSetTestProjectPath()
        {
            // Act
            var testRunner = new TestRunner();

            // Assert - TestRunner should be created without throwing
            Assert.NotNull(testRunner);
        }

        [Fact]
        public void TestRunner_ShouldFindTestProject()
        {
            // Arrange
            var testRunner = new TestRunner();
            var testProjectPath = Path.Combine(
                AppDomain.CurrentDomain.BaseDirectory,
                @"..\..\..\..\KDS.Dashboard.WPF.Tests\KDS.Dashboard.WPF.Tests.csproj");
            var fullPath = Path.GetFullPath(testProjectPath);

            // Act & Assert
            Assert.True(File.Exists(fullPath), $"Test project should exist at: {fullPath}");
        }

        [Fact]
        public async Task TestRunner_RunTestsAsync_ShouldReturnResults()
        {
            // Arrange
            var testRunner = new TestRunner();

            // Act
            var results = await testRunner.RunTestsAsync();

            // Assert
            Assert.NotNull(results);
            Assert.True(results.TotalTests > 0, "Should have at least one test");
            Assert.True(results.PassedTests > 0, "Should have at least one passing test");
            Assert.NotEqual("Error", results.Status);
        }

        [Fact]
        public async Task TestRunner_RunTestsAsync_ShouldCalculatePassRate()
        {
            // Arrange
            var testRunner = new TestRunner();

            // Act
            var results = await testRunner.RunTestsAsync();

            // Assert
            Assert.True(results.PassRate >= 0 && results.PassRate <= 100, 
                $"Pass rate should be between 0-100%, got {results.PassRate}%");
        }

        [Fact]
        public async Task TestRunner_RunTestsAsync_ShouldHaveHealthStatus()
        {
            // Arrange
            var testRunner = new TestRunner();

            // Act
            var results = await testRunner.RunTestsAsync();
            var status = results.GetHealthStatus();

            // Assert
            Assert.Contains(status, new[] { "Excellent", "Good", "Fair", "Poor" });
            Assert.NotEqual("Error", status);
        }

        [Fact]
        public async Task TestRunner_RunTestsAsync_ShouldNotTakeTooLong()
        {
            // Arrange
            var testRunner = new TestRunner();
            var startTime = DateTime.Now;

            // Act
            var results = await testRunner.RunTestsAsync();
            var elapsed = DateTime.Now - startTime;

            // Assert - Tests should complete in reasonable time (< 30 seconds)
            Assert.True(elapsed.TotalSeconds < 30, 
                $"Tests took {elapsed.TotalSeconds:F1}s, should be < 30s");
        }

        [Fact]
        public async Task TestRunner_GetCachedResults_ShouldReturnNullIfNoCacheExists()
        {
            // Arrange
            var testRunner = new TestRunner();
            var cacheFile = Path.Combine(Path.GetTempPath(), "KdsDashboardTests", "cached-results.json");
            
            // Delete cache if it exists
            if (File.Exists(cacheFile))
                File.Delete(cacheFile);

            // Act
            var cached = testRunner.GetCachedResults();

            // Assert
            Assert.Null(cached);
        }

        [Fact]
        public async Task TestRunner_CacheResults_ShouldSaveAndLoad()
        {
            // Arrange
            var testRunner = new TestRunner();

            // Act
            var results = await testRunner.RunTestsAsync();
            testRunner.CacheResults(results);
            var cached = testRunner.GetCachedResults();

            // Assert
            Assert.NotNull(cached);
            Assert.Equal(results.TotalTests, cached.TotalTests);
            Assert.Equal(results.PassedTests, cached.PassedTests);
        }
    }
}
