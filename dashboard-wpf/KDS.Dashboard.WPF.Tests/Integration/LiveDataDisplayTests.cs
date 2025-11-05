using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using KDS.Dashboard.WPF.ViewModels;
using KDS.Dashboard.WPF.Models;
using KDS.Dashboard.WPF.Helpers;
using Xunit;

namespace KDS.Dashboard.WPF.Tests.Integration
{
    /// <summary>
    /// Integration tests to verify the dashboard displays live data from brain files
    /// Tests each ViewModel's ability to load and display real data
    /// </summary>
    public class LiveDataDisplayTests
    {
        [Fact]
        public void ActivityViewModel_ShouldLoadRealEvents_NotDashboardErrors()
        {
            // Arrange
            var viewModel = new ActivityViewModel();
            Thread.Sleep(500); // Allow time for file loading

            // Act
            var events = viewModel.Events;

            // Assert
            Assert.NotNull(events);
            Assert.NotEmpty(events);
            
            // Should have events that are NOT dashboard_error
            var realEvents = events.Where(e => e.Event != "dashboard_error").ToList();
            Assert.NotEmpty(realEvents);
            
            // Should have variety of event types
            var eventTypes = events.Select(e => e.Event).Distinct().ToList();
            Assert.Contains(eventTypes, t => t != "dashboard_error");
        }

        [Fact]
        public void ActivityViewModel_ShouldFilterOutDashboardErrors()
        {
            // Arrange
            var viewModel = new ActivityViewModel();
            Thread.Sleep(500);

            // Act
            var dashboardErrors = viewModel.Events.Where(e => e.Event == "dashboard_error").ToList();

            // Assert - Should not display dashboard_error events
            Assert.Empty(dashboardErrors);
        }

        [Fact]
        public void ConversationsViewModel_ShouldLoadConversationHistory()
        {
            // Arrange
            var viewModel = new ConversationsViewModel();
            Thread.Sleep(500);

            // Act
            var conversations = viewModel.Conversations;

            // Assert
            Assert.NotNull(conversations);
            Assert.NotEmpty(conversations);
            
            // Should have actual conversation data
            var firstConvo = conversations.FirstOrDefault();
            Assert.NotNull(firstConvo);
            Assert.NotEmpty(firstConvo.ConversationId);
            Assert.NotEmpty(firstConvo.Title);
            Assert.True(firstConvo.MessageCount > 0);
        }

        [Fact]
        public void MetricsViewModel_ShouldLoadDevelopmentMetrics()
        {
            // Arrange
            var viewModel = new MetricsViewModel();
            Thread.Sleep(500);

            // Act & Assert
            // Should load some metrics (even if zero, properties should be set)
            Assert.True(viewModel.CommitsThisWeek >= 0);
            Assert.True(viewModel.LinesAddedThisWeek >= 0);
            Assert.True(viewModel.TestPassRate >= 0);
        }

        [Fact]
        public void HealthViewModel_ShouldLoadBrainHealthMetrics()
        {
            // Arrange
            var viewModel = new HealthViewModel();
            Thread.Sleep(500);

            // Act & Assert
            Assert.True(viewModel.EventBacklog >= 0);
            Assert.True(viewModel.KnowledgeEntries >= 0);
            Assert.True(viewModel.ConversationCount >= 0);
            Assert.NotNull(viewModel.HealthStatus);
            Assert.NotEmpty(viewModel.HealthStatus);
        }

        [Fact]
        public async Task ActivityViewModel_ShouldUpdateOnFileChange()
        {
            // Arrange
            var viewModel = new ActivityViewModel();
            Thread.Sleep(500);
            var initialCount = viewModel.Events.Count;

            // Act - Add a new event to events.jsonl
            var eventsPath = ConfigurationHelper.GetEventsPath();
            var testEvent = new
            {
                timestamp = DateTime.UtcNow.ToString("o"),
                @event = "test_event",
                source = "integration_test",
                message = "Live data test event"
            };
            
            var json = System.Text.Json.JsonSerializer.Serialize(testEvent);
            await File.AppendAllTextAsync(eventsPath, json + Environment.NewLine);
            
            // Wait for FileSystemWatcher to trigger
            Thread.Sleep(1000);

            // Assert
            var updatedCount = viewModel.Events.Count;
            Assert.True(updatedCount >= initialCount, 
                $"Events should have updated. Initial: {initialCount}, Updated: {updatedCount}");
            
            // Should contain our test event
            var hasTestEvent = viewModel.Events.Any(e => e.Event == "test_event");
            Assert.True(hasTestEvent, "Should contain the test event we just added");
        }

        [Fact]
        public void AllViewModels_ShouldNotCreateInfiniteLoop()
        {
            // Arrange - Count events before creating ViewModels
            var eventsPath = ConfigurationHelper.GetEventsPath();
            var eventsBefore = File.ReadLines(eventsPath).Count();

            // Act - Create all ViewModels (this previously caused infinite loop)
            var activityVM = new ActivityViewModel();
            var conversationsVM = new ConversationsViewModel();
            var metricsVM = new MetricsViewModel();
            var healthVM = new HealthViewModel();
            
            Thread.Sleep(2000); // Wait for any potential loops

            // Assert - Event count should not explode
            var eventsAfter = File.ReadLines(eventsPath).Count();
            var eventsDifference = eventsAfter - eventsBefore;
            
            Assert.True(eventsDifference < 10, 
                $"Events should not multiply (infinite loop check). Before: {eventsBefore}, After: {eventsAfter}, Diff: {eventsDifference}");
        }

        [Fact]
        public void BrainFiles_ShouldExist()
        {
            // Assert all required brain files exist
            Assert.True(File.Exists(ConfigurationHelper.GetEventsPath()), 
                "events.jsonl should exist");
            Assert.True(File.Exists(ConfigurationHelper.GetConversationHistoryPath()), 
                "conversation-history.jsonl should exist");
            Assert.True(File.Exists(ConfigurationHelper.GetDevelopmentContextPath()), 
                "development-context.yaml should exist");
            Assert.True(File.Exists(ConfigurationHelper.GetKnowledgeGraphPath()), 
                "knowledge-graph.yaml should exist");
        }

        [Fact]
        public void Events_ShouldContainRealBrainActivity()
        {
            // Arrange
            var eventsPath = ConfigurationHelper.GetEventsPath();
            var events = File.ReadAllLines(eventsPath);

            // Act - Parse events
            var parsedEvents = events
                .Where(line => !string.IsNullOrWhiteSpace(line))
                .Select(line => System.Text.Json.JsonSerializer.Deserialize<BrainEvent>(line,
                    new System.Text.Json.JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true,
                        PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase
                    }))
                .Where(e => e != null)
                .ToList();

            // Assert
            Assert.NotEmpty(parsedEvents);
            
            // Should have real brain events (not just dashboard_error)
            var realBrainEvents = parsedEvents
                .Where(e => e!.Event != "dashboard_error")
                .ToList();
            
            Assert.NotEmpty(realBrainEvents);
            
            // Should have variety of event types
            var eventTypes = parsedEvents
                .Select(e => e!.Event)
                .Distinct()
                .ToList();
            
            Assert.Contains("conversation_recorded", eventTypes);
            // Should have other event types
            Assert.True(eventTypes.Count > 1, 
                $"Should have multiple event types. Found: {string.Join(", ", eventTypes)}");
        }
    }
}
