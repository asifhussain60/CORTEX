using Xunit;
using MaterialDesignThemes.Wpf;
using System;
using System.Collections.Generic;

namespace KDS.Dashboard.WPF.Tests
{
    /// <summary>
    /// TDD Test: Verify all Material Design icons used in XAML are valid
    /// This prevents runtime XamlParseException errors
    /// </summary>
    public class MaterialDesignIconTests
    {
        /// <summary>
        /// List of all PackIcon kinds used in the application XAML files
        /// These are extracted from grep search of Kind=" in all XAML files
        /// </summary>
        private static readonly List<string> UsedIconKinds = new()
        {
            // MainWindow.xaml
            "Brain",
            "Alert",
            "Flash",  // ✅ FIXED - was "Lightning" (invalid)
            "MessageText",
            "ChartLine",
            "Heart",
            "FormatListChecks",
            
            // ActivityView.xaml
            // "Flash" already listed
            
            // ConversationsView.xaml
            // "MessageText" already listed
            
            // MetricsView.xaml
            "SourceCommit",
            "CodeBraces",
            "CheckCircle",
            // "ChartLine" already listed
            
            // HealthView.xaml
            // "CheckCircle" already listed
            "FileDocumentMultiple",
            // "Brain" already listed
            // "MessageText" already listed
            "Update",
            
            // FeaturesView.xaml
            "File",
            "Script",
            "TestTube",
            "AlertCircle"
        };

        [Theory]
        [MemberData(nameof(GetAllUsedIcons))]
        public void AllUsedIcons_ShouldBeValidPackIconKinds(string iconKindString)
        {
            // Attempt to parse the string to PackIconKind enum
            bool isValid = Enum.TryParse<PackIconKind>(iconKindString, out var result);
            
            // Assert that the icon kind is valid
            Assert.True(isValid, 
                $"Icon kind '{iconKindString}' is not a valid PackIconKind. " +
                $"This will cause a runtime XamlParseException. " +
                $"Check Material Design Icons gallery for valid alternatives: " +
                $"https://materialdesignicons.com/");
        }

        [Fact]
        public void Lightning_IsNotAValidIcon_ShouldFail()
        {
            // This test documents the known issue
            bool isValid = Enum.TryParse<PackIconKind>("Lightning", out _);
            
            // We EXPECT this to fail - Lightning is not valid
            Assert.False(isValid, 
                "Lightning is not a valid PackIconKind. Use 'Flash' or 'FlashAuto' instead.");
        }

        [Fact]
        public void RecommendedAlternatives_ForLightning_ShouldBeValid()
        {
            // Flash is a valid alternative
            bool flashIsValid = Enum.TryParse<PackIconKind>("Flash", out _);
            Assert.True(flashIsValid, "Flash should be a valid icon");
            
            // FlashAuto is another alternative
            bool flashAutoIsValid = Enum.TryParse<PackIconKind>("FlashAuto", out _);
            Assert.True(flashAutoIsValid, "FlashAuto should be a valid icon");
        }

        public static IEnumerable<object[]> GetAllUsedIcons()
        {
            foreach (var icon in UsedIconKinds)
            {
                yield return new object[] { icon };
            }
        }

        [Fact]
        public void MainWindowIcons_ShouldAllBeValid()
        {
            var mainWindowIcons = new[] { "Brain", "Alert", "MessageText", "ChartLine", "Heart", "FormatListChecks" };
            
            foreach (var icon in mainWindowIcons)
            {
                bool isValid = Enum.TryParse<PackIconKind>(icon, out _);
                Assert.True(isValid, $"MainWindow icon '{icon}' is invalid");
            }
        }

        [Fact]
        public void ActivityViewIcons_Flash_ShouldBeValidAlternativeToLightning()
        {
            // When we fix Lightning → Flash, verify it works
            bool isValid = Enum.TryParse<PackIconKind>("Flash", out _);
            Assert.True(isValid, "Flash should be the correct icon for Activity tab");
        }

        [Fact]
        public void MetricsViewIcons_ShouldAllBeValid()
        {
            var metricsIcons = new[] { "SourceCommit", "CodeBraces", "CheckCircle", "ChartLine" };
            
            foreach (var icon in metricsIcons)
            {
                bool isValid = Enum.TryParse<PackIconKind>(icon, out _);
                Assert.True(isValid, $"MetricsView icon '{icon}' is invalid");
            }
        }

        [Fact]
        public void HealthViewIcons_ShouldAllBeValid()
        {
            var healthIcons = new[] { "CheckCircle", "FileDocumentMultiple", "Brain", "MessageText", "Update" };
            
            foreach (var icon in healthIcons)
            {
                bool isValid = Enum.TryParse<PackIconKind>(icon, out _);
                Assert.True(isValid, $"HealthView icon '{icon}' is invalid");
            }
        }

        [Fact]
        public void FeaturesViewIcons_ShouldAllBeValid()
        {
            var featuresIcons = new[] { "File", "Script", "TestTube", "AlertCircle" };
            
            foreach (var icon in featuresIcons)
            {
                bool isValid = Enum.TryParse<PackIconKind>(icon, out _);
                Assert.True(isValid, $"FeaturesView icon '{icon}' is invalid");
            }
        }
    }
}
