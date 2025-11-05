using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using KDS.Dashboard.WPF.Helpers;
using KDS.Dashboard.WPF.Models;
using Xunit;

namespace KDS.Dashboard.WPF.Tests.Integration
{
    /// <summary>
    /// Integration tests validating that our models can deserialize actual brain files.
    /// These tests MUST pass before declaring dashboard functional.
    /// </summary>
    public class BrainFileIntegrationTests
    {
        [Fact]
        public void EventsJsonl_FileExists_AndIsReadable()
        {
            // Arrange
            var eventsPath = ConfigurationHelper.GetEventsPath();
            
            // Act & Assert
            Assert.True(File.Exists(eventsPath), 
                $"Brain events file not found at: {eventsPath}");
            
            var lines = File.ReadLines(eventsPath).ToList();
            Assert.True(lines.Count > 0, 
                "Events file exists but is empty");
        }

        [Fact]
        public void EventsJsonl_FirstEvent_DeserializesToBrainEvent()
        {
            // Arrange
            var eventsPath = ConfigurationHelper.GetEventsPath();
            var firstLine = File.ReadLines(eventsPath).First();
            
            // Act
            var result = JsonSerializer.Deserialize<BrainEvent>(firstLine, 
                new JsonSerializerOptions 
                { 
                    PropertyNameCaseInsensitive = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            
            // Assert
            Assert.NotNull(result);
            
            // Event property MUST exist
            Assert.NotNull(result.Event);
            Assert.False(string.IsNullOrEmpty(result.Event), "Event type must not be empty");
            
            // Agent is optional (not all events have an agent)
        }

        [Fact]
        public void EventsJsonl_AllEvents_CanBeDeserialized()
        {
            // Arrange
            var eventsPath = ConfigurationHelper.GetEventsPath();
            var lines = File.ReadLines(eventsPath).ToList();
            var errors = new List<string>();
            
            // Act
            for (int i = 0; i < lines.Count; i++)
            {
                try
                {
                    var evt = JsonSerializer.Deserialize<BrainEvent>(lines[i], 
                        new JsonSerializerOptions 
                        { 
                            PropertyNameCaseInsensitive = true,
                            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                        });
                    
                    if (evt == null)
                    {
                        errors.Add($"Line {i + 1}: Deserialized to null");
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Line {i + 1}: {ex.Message}");
                }
            }
            
            // Assert
            Assert.Empty(errors);
        }

        [Fact]
        public void EventsJsonl_SampleEvent_HasExpectedProperties()
        {
            // Arrange
            var eventsPath = ConfigurationHelper.GetEventsPath();
            var firstLine = File.ReadLines(eventsPath).First();
            
            // Deserialize as generic object to inspect actual structure
            var jsonDoc = JsonDocument.Parse(firstLine);
            var root = jsonDoc.RootElement;
            
            // Act & Assert - Document what properties actually exist
            Assert.True(root.TryGetProperty("timestamp", out _) || 
                       root.TryGetProperty("Timestamp", out _),
                "Event must have timestamp property");
            
            Assert.True(root.TryGetProperty("event", out _) || 
                       root.TryGetProperty("Event", out _),
                "Event must have event type property");
            
            // Agent is optional - not all events have it
            // This is expected for heterogeneous event streams
        }

        [Fact]
        public void ConversationHistoryJsonl_FileExists_AndIsReadable()
        {
            // Arrange
            var conversationsPath = ConfigurationHelper.GetConversationsPath();
            
            // Act & Assert
            Assert.True(File.Exists(conversationsPath), 
                $"Brain conversations file not found at: {conversationsPath}");
            
            var lines = File.ReadLines(conversationsPath).ToList();
            Assert.True(lines.Count > 0, 
                "Conversations file exists but is empty");
        }

        [Fact]
        public void ConversationHistoryJsonl_FirstConversation_DeserializesToConversation()
        {
            // Arrange
            var conversationsPath = ConfigurationHelper.GetConversationsPath();
            var firstLine = File.ReadLines(conversationsPath).First();
            
            // Act
            var result = JsonSerializer.Deserialize<Conversation>(firstLine, 
                new JsonSerializerOptions 
                { 
                    PropertyNameCaseInsensitive = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            
            // Assert
            Assert.NotNull(result);
            Assert.NotNull(result.Timestamp);
            Assert.NotNull(result.ConversationId);
        }

        [Fact]
        public void ConversationHistoryJsonl_AllConversations_CanBeDeserialized()
        {
            // Arrange
            var conversationsPath = ConfigurationHelper.GetConversationsPath();
            var lines = File.ReadLines(conversationsPath).ToList();
            var errors = new List<string>();
            
            // Act
            for (int i = 0; i < lines.Count; i++)
            {
                try
                {
                    var conv = JsonSerializer.Deserialize<Conversation>(lines[i], 
                        new JsonSerializerOptions 
                        { 
                            PropertyNameCaseInsensitive = true,
                            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                        });
                    
                    if (conv == null)
                    {
                        errors.Add($"Line {i + 1}: Deserialized to null");
                    }
                }
                catch (Exception ex)
                {
                    errors.Add($"Line {i + 1}: {ex.Message}");
                }
            }
            
            // Assert
            Assert.Empty(errors);
        }

        [Fact]
        public void DevelopmentContextYaml_FileExists_AndIsReadable()
        {
            // Arrange
            var metricsPath = ConfigurationHelper.GetMetricsPath();
            
            // Act & Assert
            Assert.True(File.Exists(metricsPath), 
                $"Brain metrics file not found at: {metricsPath}");
            
            var content = File.ReadAllText(metricsPath);
            Assert.True(content.Length > 0, 
                "Metrics file exists but is empty");
        }

        [Fact]
        public void KnowledgeGraphYaml_FileExists_AndIsReadable()
        {
            // Arrange
            var healthPath = ConfigurationHelper.GetHealthPath();
            
            // Act & Assert
            Assert.True(File.Exists(healthPath), 
                $"Brain health file not found at: {healthPath}");
            
            var content = File.ReadAllText(healthPath);
            Assert.True(content.Length > 0, 
                "Health file exists but is empty");
        }

        [Fact]
        public void BrainFiles_AllRequiredFiles_Exist()
        {
            // Arrange & Act
            var missingFiles = new List<string>();
            
            var eventsPath = ConfigurationHelper.GetEventsPath();
            if (!File.Exists(eventsPath))
                missingFiles.Add($"events.jsonl: {eventsPath}");
            
            var conversationsPath = ConfigurationHelper.GetConversationsPath();
            if (!File.Exists(conversationsPath))
                missingFiles.Add($"conversation-history.jsonl: {conversationsPath}");
            
            var metricsPath = ConfigurationHelper.GetMetricsPath();
            if (!File.Exists(metricsPath))
                missingFiles.Add($"development-context.yaml: {metricsPath}");
            
            var healthPath = ConfigurationHelper.GetHealthPath();
            if (!File.Exists(healthPath))
                missingFiles.Add($"knowledge-graph.yaml: {healthPath}");
            
            // Assert
            Assert.Empty(missingFiles);
        }
    }
}
