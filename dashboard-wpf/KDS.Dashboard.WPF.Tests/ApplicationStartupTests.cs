using System.Windows;
using Xunit;

namespace KDS.Dashboard.WPF.Tests
{
    /// <summary>
    /// Tests to verify the WPF application can be instantiated and loaded
    /// </summary>
    public class ApplicationStartupTests
    {
        [WpfFact]
        public void App_CanBeInstantiated()
        {
            // Arrange & Act
            var app = new App();

            // Assert
            Assert.NotNull(app);
        }

        [WpfFact]
        public void MainWindow_CanBeInstantiated()
        {
            // Arrange & Act
            var mainWindow = new MainWindow();

            // Assert
            Assert.NotNull(mainWindow);
            Assert.Equal("KDS Brain Dashboard v8.0", mainWindow.Title);
        }

        [WpfFact]
        public void MainWindow_HasCorrectDimensions()
        {
            // Arrange & Act
            var mainWindow = new MainWindow();

            // Assert
            Assert.Equal(800, mainWindow.Height);
            Assert.Equal(1400, mainWindow.Width);
        }

        [WpfFact]
        public void App_InitializeComponent_DoesNotThrow()
        {
            // Arrange
            var app = new App();

            // Act & Assert - Should not throw
            app.InitializeComponent();
        }

        [WpfFact]
        public void MainWindow_InitializeComponent_DoesNotThrow()
        {
            // Arrange
            var mainWindow = new MainWindow();

            // Act & Assert - InitializeComponent is called in constructor
            // If we got here without exception, test passes
            Assert.NotNull(mainWindow.Content);
        }
    }

    /// <summary>
    /// Custom fact attribute for WPF tests that require STA thread
    /// </summary>
    public sealed class WpfFactAttribute : FactAttribute
    {
        public WpfFactAttribute()
        {
            if (Thread.CurrentThread.GetApartmentState() != ApartmentState.STA)
            {
                Skip = "WPF tests must run on STA thread";
            }
        }
    }
}
