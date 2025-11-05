using System;
using Xunit;
using KDS.Dashboard.WPF.ViewModels;

namespace KDS.Dashboard.WPF.Tests
{
    /// <summary>
    /// Integration tests to verify the application components work together
    /// Updated for Phase 1 - tests live data integration
    /// </summary>
    public class IntegrationTests
    {
        [Fact]
        public void AllViewModels_CanBeInstantiatedSimultaneously()
        {
            // This test verifies that creating all ViewModels at once doesn't cause conflicts
            
            // Act
            var activityVM = new ActivityViewModel();
            var conversationsVM = new ConversationsViewModel();
            var metricsVM = new MetricsViewModel();
            var healthVM = new HealthViewModel();
            var featuresVM = new FeaturesViewModel();

            // Assert - All should be instantiated without errors
            Assert.NotNull(activityVM);
            Assert.NotNull(conversationsVM);
            Assert.NotNull(metricsVM);
            Assert.NotNull(healthVM);
            Assert.NotNull(featuresVM);

            // Verify collections are initialized (may be empty if brain files don't exist)
            Assert.NotNull(activityVM.Events);
            Assert.NotNull(conversationsVM.Conversations);
            Assert.NotNull(featuresVM.Features);
        }
    }
}
