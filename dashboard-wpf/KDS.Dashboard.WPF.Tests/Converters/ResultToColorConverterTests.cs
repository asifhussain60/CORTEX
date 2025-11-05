using Xunit;
using KDS.Dashboard.WPF.Converters;
using System.Globalization;
using System.Windows.Media;

namespace KDS.Dashboard.WPF.Tests.Converters
{
    /// <summary>
    /// TDD Tests for ResultToColorConverter
    /// Tests conversion of result strings to appropriate colors
    /// </summary>
    public class ResultToColorConverterTests
    {
        private readonly ResultToColorConverter _converter;

        public ResultToColorConverterTests()
        {
            _converter = new ResultToColorConverter();
        }

        [Fact]
        public void Convert_GreenResult_ReturnsGreenBrush()
        {
            // Arrange
            var result = "GREEN";
            var expectedColor = Color.FromRgb(46, 125, 50); // #2E7D32

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }

        [Fact]
        public void Convert_CompleteResult_ReturnsGreenBrush()
        {
            // Arrange
            var result = "COMPLETE";
            var expectedColor = Color.FromRgb(46, 125, 50); // #2E7D32

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }

        [Fact]
        public void Convert_ValidatedResult_ReturnsGreenBrush()
        {
            // Arrange
            var result = "VALIDATED";
            var expectedColor = Color.FromRgb(46, 125, 50); // #2E7D32

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }

        [Fact]
        public void Convert_RedResult_ReturnsRedBrush()
        {
            // Arrange
            var result = "RED";
            var expectedColor = Color.FromRgb(198, 40, 40); // #C62828

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }

        [Fact]
        public void Convert_FailedResult_ReturnsRedBrush()
        {
            // Arrange
            var result = "FAILED";
            var expectedColor = Color.FromRgb(198, 40, 40); // #C62828

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }

        [Fact]
        public void Convert_RefactorResult_ReturnsBlueBrush()
        {
            // Arrange
            var result = "REFACTOR";
            var expectedColor = Color.FromRgb(25, 118, 210); // #1976D2

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }

        [Fact]
        public void Convert_WarningResult_ReturnsOrangeBrush()
        {
            // Arrange
            var result = "WARNING";
            var expectedColor = Color.FromRgb(245, 124, 0); // #F57C00

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }

        [Fact]
        public void Convert_UnknownResult_ReturnsGrayBrush()
        {
            // Arrange
            var result = "UNKNOWN_STATUS";
            var expectedColor = Color.FromRgb(158, 158, 158); // #9E9E9E

            // Act
            var brush = _converter.Convert(result, typeof(Brush), null, CultureInfo.CurrentCulture) as SolidColorBrush;

            // Assert
            Assert.NotNull(brush);
            Assert.Equal(expectedColor, brush.Color);
        }
    }
}
