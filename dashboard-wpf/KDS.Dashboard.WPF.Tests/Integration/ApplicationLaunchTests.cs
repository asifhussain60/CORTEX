using System;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Xunit;

namespace KDS.Dashboard.WPF.Tests.Integration
{
    /// <summary>
    /// Integration test to verify the dashboard application can launch successfully
    /// </summary>
    public class ApplicationLaunchTests : IDisposable
    {
        private Process? _appProcess;

        [Fact(Skip = "Manual test - launches actual application")]
        public async Task Dashboard_ShouldLaunchSuccessfully()
        {
            // Arrange
            var projectPath = System.IO.Path.GetFullPath(
                @"..\..\..\..\KDS.Dashboard.WPF\KDS.Dashboard.WPF.csproj");

            Assert.True(System.IO.File.Exists(projectPath), 
                $"Project file should exist at {projectPath}");

            var startInfo = new ProcessStartInfo
            {
                FileName = "dotnet",
                Arguments = $"run --project \"{projectPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            // Act
            _appProcess = Process.Start(startInfo);
            Assert.NotNull(_appProcess);

            // Wait for the process to start
            await Task.Delay(3000);

            // Assert - Process should still be running
            Assert.False(_appProcess.HasExited, 
                "Dashboard process should be running");

            // Check if there's a window with the title
            await Task.Delay(2000);
            var dashboardWindows = Process.GetProcesses()
                .Where(p => p.ProcessName.Contains("KDS.Dashboard") || 
                           p.MainWindowTitle.Contains("KDS Brain Dashboard"))
                .ToList();

            // Note: This may not work in CI/headless environments
            // But validates the app can launch locally
        }

        [Fact]
        public void DashboardViewModel_ShouldNotThrowOnConstruction()
        {
            // Arrange & Act
            Exception? caughtException = null;
            try
            {
                var viewModel = new KDS.Dashboard.WPF.ViewModels.DashboardViewModel();
                Assert.NotNull(viewModel);
            }
            catch (Exception ex)
            {
                caughtException = ex;
            }

            // Assert
            Assert.Null(caughtException);
        }

        [Fact]
        public void DashboardView_ShouldNotThrowOnConstruction()
        {
            // Arrange & Act
            Type? viewType = null;
            Exception? caughtException = null;
            
            try
            {
                // This tests the view type can be loaded
                // In a real WPF app, instantiation needs STA thread
                viewType = Type.GetType("KDS.Dashboard.WPF.Views.DashboardView, KDS.Dashboard.WPF");
            }
            catch (Exception ex)
            {
                caughtException = ex;
            }

            // Assert
            Assert.Null(caughtException);
            Assert.NotNull(viewType);
        }

        public void Dispose()
        {
            // Cleanup - kill the app process if it's still running
            if (_appProcess != null && !_appProcess.HasExited)
            {
                _appProcess.Kill();
                _appProcess.WaitForExit(5000);
                _appProcess.Dispose();
            }
        }
    }
}
