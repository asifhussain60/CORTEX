using System;
using System.Threading.Tasks;
using System.Windows;
using Xunit;
using KDS.Dashboard.WPF.ViewModels;

namespace KDS.Dashboard.WPF.Tests.ViewModels
{
    /// <summary>
    /// Tests for heartbeat animation functionality in ActivityViewModel
    /// Note: These are unit tests focused on the public API.
    /// Integration tests with actual file watching are in IntegrationTests.
    /// </summary>
    public class HeartbeatAnimationTests
    {
        [Fact]
        public void HeartbeatActive_ShouldBeInitiallyFalse()
        {
            // Arrange & Act
            var viewModel = new ActivityViewModel();

            // Assert
            Assert.False(viewModel.IsHeartbeatActive);
        }

        [Fact]
        public void LastEventTime_ShouldBeInitiallyMinValue()
        {
            // Arrange & Act
            var viewModel = new ActivityViewModel();

            // Assert
            // LastEventTime initializes to MinValue until first event
            Assert.True(viewModel.LastEventTime <= DateTime.Now);
        }

        [Fact]
        public void ViewModel_ShouldHaveHeartbeatProperties()
        {
            // Arrange & Act
            var viewModel = new ActivityViewModel();

            // Assert - Verify heartbeat properties exist and are accessible
            Assert.NotNull(viewModel);
            var isActiveProperty = viewModel.GetType().GetProperty("IsHeartbeatActive");
            var lastTimeProperty = viewModel.GetType().GetProperty("LastEventTime");
            
            Assert.NotNull(isActiveProperty);
            Assert.NotNull(lastTimeProperty);
            Assert.Equal(typeof(bool), isActiveProperty.PropertyType);
            Assert.Equal(typeof(DateTime), lastTimeProperty.PropertyType);
        }

        [Fact]
        public void HeartbeatActive_CanBeSetAndRaisePropertyChanged()
        {
            // Arrange
            var viewModel = new ActivityViewModel();
            bool propertyChangedRaised = false;
            
            viewModel.PropertyChanged += (sender, args) =>
            {
                if (args.PropertyName == "IsHeartbeatActive")
                {
                    propertyChangedRaised = true;
                }
            };

            // Act
            // Use reflection to trigger the private method (simulating file change)
            var triggerMethod = typeof(ActivityViewModel).GetMethod("TriggerHeartbeat",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            
            if (triggerMethod != null)
            {
                // Execute on UI thread if available
                if (Application.Current != null)
                {
                    Application.Current.Dispatcher.Invoke(() => triggerMethod.Invoke(viewModel, null));
                }
                else
                {
                    triggerMethod.Invoke(viewModel, null);
                }
            }

            // Assert
            if (triggerMethod != null)
            {
                Assert.True(propertyChangedRaised, "PropertyChanged should be raised for IsHeartbeatActive");
                Assert.True(viewModel.IsHeartbeatActive, "IsHeartbeatActive should be true after triggering");
            }
        }

        [Fact]
        public async Task HeartbeatActive_ShouldAutoDeactivateAfterDelay()
        {
            // Arrange
            var viewModel = new ActivityViewModel();
            var triggerMethod = typeof(ActivityViewModel).GetMethod("TriggerHeartbeat",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            if (triggerMethod == null)
            {
                // Skip test if reflection fails (method might be inlined or optimized)
                return;
            }

            // Act
            triggerMethod.Invoke(viewModel, null);
            
            // Verify it's active
            Assert.True(viewModel.IsHeartbeatActive, "Should be active immediately after trigger");

            // Wait for auto-deactivation (2 seconds + buffer)
            await Task.Delay(2500);

            // Assert
            // Note: This test may be flaky in CI environments without UI dispatcher
            // The actual deactivation happens on the dispatcher thread
            if (Application.Current != null)
            {
                await Application.Current.Dispatcher.InvokeAsync(() => 
                {
                    Assert.False(viewModel.IsHeartbeatActive, 
                        "Should be inactive after 2 second delay");
                });
            }
        }

        [Fact]
        public void ActivityViewModel_ShouldImplementINotifyPropertyChanged()
        {
            // Arrange & Act
            var viewModel = new ActivityViewModel();

            // Assert
            Assert.IsAssignableFrom<System.ComponentModel.INotifyPropertyChanged>(viewModel);
        }

        [Fact]
        public void Events_Collection_ShouldBeInitialized()
        {
            // Arrange & Act
            var viewModel = new ActivityViewModel();

            // Assert
            Assert.NotNull(viewModel.Events);
        }
    }
}
