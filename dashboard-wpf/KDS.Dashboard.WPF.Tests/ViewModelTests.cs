using Xunit;
using KDS.Dashboard.WPF.ViewModels;

namespace KDS.Dashboard.WPF.Tests
{
    /// <summary>
    /// Tests for ViewModels to ensure they can be instantiated
    /// Updated for Phase 1 - tests live data integration
    /// </summary>
    public class ViewModelTests
    {
        [Fact]
        public void ActivityViewModel_CanBeInstantiated()
        {
            // Arrange & Act
            var viewModel = new ActivityViewModel();

            // Assert
            Assert.NotNull(viewModel);
            Assert.NotNull(viewModel.Events);
            // Events may be empty if brain files don't exist
        }

        [Fact]
        public void ConversationsViewModel_CanBeInstantiated()
        {
            // Arrange & Act
            var viewModel = new ConversationsViewModel();

            // Assert
            Assert.NotNull(viewModel);
            Assert.NotNull(viewModel.Conversations);
            // Conversations may be empty if brain files don't exist
        }

        [Fact]
        public void MetricsViewModel_CanBeInstantiated()
        {
            // Arrange & Act
            var viewModel = new MetricsViewModel();

            // Assert
            Assert.NotNull(viewModel);
            // Metrics may be 0 if brain files don't exist
            Assert.True(viewModel.CommitsThisWeek >= 0);
            Assert.True(viewModel.LinesAddedThisWeek >= 0);
            Assert.True(viewModel.TestPassRate >= 0);
        }

        [Fact]
        public void HealthViewModel_CanBeInstantiated()
        {
            // Arrange & Act
            var viewModel = new HealthViewModel();

            // Assert
            Assert.NotNull(viewModel);
            Assert.True(viewModel.EventBacklog >= 0);
            Assert.True(viewModel.KnowledgeEntries >= 0);
            Assert.NotNull(viewModel.HealthStatus);
        }

        [Fact]
        public void FeaturesViewModel_CanBeInstantiated()
        {
            // Arrange & Act
            var viewModel = new FeaturesViewModel();

            // Assert
            Assert.NotNull(viewModel);
            Assert.NotNull(viewModel.Features);
            Assert.True(viewModel.ImplementedCount >= 0);
            Assert.True(viewModel.PartialCount >= 0);
            Assert.True(viewModel.DesignedCount >= 0);
        }
    }
}
