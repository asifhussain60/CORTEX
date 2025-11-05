using Xunit;
using KDS.Dashboard.WPF.Converters;
using MaterialDesignThemes.Wpf;
using System.Globalization;

namespace KDS.Dashboard.WPF.Tests.Converters
{
    /// <summary>
    /// TDD Tests for ResultToIconConverter
    /// Tests conversion of result strings to Material Design icons
    /// </summary>
    public class ResultToIconConverterTests
    {
        private readonly ResultToIconConverter _converter;

        public ResultToIconConverterTests()
        {
            _converter = new ResultToIconConverter();
        }

        [Fact]
        public void Convert_GreenResult_ReturnsCheckCircleIcon()
        {
            // Arrange
            var result = "GREEN";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.CheckCircle, icon);
        }

        [Fact]
        public void Convert_CompleteResult_ReturnsCheckIcon()
        {
            // Arrange
            var result = "COMPLETE";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.Check, icon);
        }

        [Fact]
        public void Convert_ValidatedResult_ReturnsShieldCheckIcon()
        {
            // Arrange
            var result = "VALIDATED";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.ShieldCheck, icon);
        }

        [Fact]
        public void Convert_RedResult_ReturnsAlertCircleIcon()
        {
            // Arrange
            var result = "RED";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.AlertCircle, icon);
        }

        [Fact]
        public void Convert_FailedResult_ReturnsCloseCircleIcon()
        {
            // Arrange
            var result = "FAILED";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.CloseCircle, icon);
        }

        [Fact]
        public void Convert_RefactorResult_ReturnsAutoFixIcon()
        {
            // Arrange
            var result = "REFACTOR";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.AutoFix, icon);
        }

        [Fact]
        public void Convert_InProgressResult_ReturnsProgressClockIcon()
        {
            // Arrange
            var result = "IN_PROGRESS";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.ProgressClock, icon);
        }

        [Fact]
        public void Convert_WarningResult_ReturnsAlertIcon()
        {
            // Arrange
            var result = "WARNING";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.Alert, icon);
        }

        [Fact]
        public void Convert_UnknownResult_ReturnsHelpCircleIcon()
        {
            // Arrange
            var result = "UNKNOWN_STATUS";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.HelpCircle, icon);
        }

        [Fact]
        public void Convert_NullResult_ReturnsHelpCircleIcon()
        {
            // Arrange
            object? result = null;

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.HelpCircle, icon);
        }

        [Fact]
        public void Convert_EmptyStringResult_ReturnsHelpCircleIcon()
        {
            // Arrange
            var result = string.Empty;

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.HelpCircle, icon);
        }

        [Fact]
        public void Convert_LowercaseResult_HandlesCorrectly()
        {
            // Arrange - Test case insensitivity
            var result = "green";

            // Act
            var icon = _converter.Convert(result, typeof(PackIconKind), null, CultureInfo.CurrentCulture);

            // Assert
            Assert.Equal(PackIconKind.CheckCircle, icon);
        }

        [Fact]
        public void ConvertBack_NotImplemented_ThrowsNotImplementedException()
        {
            // Act & Assert
            Assert.Throws<NotImplementedException>(() => 
                _converter.ConvertBack(PackIconKind.Check, typeof(string), null, CultureInfo.CurrentCulture)
            );
        }
    }
}
