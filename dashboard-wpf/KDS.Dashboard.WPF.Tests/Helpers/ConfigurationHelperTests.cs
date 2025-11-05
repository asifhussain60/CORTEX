using System;
using System.IO;
using Xunit;
using KDS.Dashboard.WPF.Helpers;

namespace KDS.Dashboard.WPF.Tests.Helpers
{
    /// <summary>
    /// TDD Tests for ConfigurationHelper
    /// Tests KDS root and brain path discovery
    /// </summary>
    public class ConfigurationHelperTests
    {
        [Fact]
        public void GetKdsRoot_WhenConfigExists_ReturnsCorrectPath()
        {
            // Arrange - We expect KDS root to be found
            
            // Act
            var kdsRoot = ConfigurationHelper.GetKdsRoot();
            
            // Assert
            Assert.NotNull(kdsRoot);
            Assert.NotEmpty(kdsRoot);
            Assert.True(Directory.Exists(kdsRoot), $"KDS root directory should exist: {kdsRoot}");
        }

        [Fact]
        public void GetKdsRoot_WhenConfigExists_ContainsConfigFile()
        {
            // Arrange & Act
            var kdsRoot = ConfigurationHelper.GetKdsRoot();
            var configPath = Path.Combine(kdsRoot, "kds.config.json");
            
            // Assert
            Assert.True(File.Exists(configPath), $"kds.config.json should exist at: {configPath}");
        }

        [Fact]
        public void GetBrainPath_ReturnsKdsBrainDirectory()
        {
            // Arrange & Act
            var brainPath = ConfigurationHelper.GetBrainPath();
            
            // Assert
            Assert.NotNull(brainPath);
            Assert.NotEmpty(brainPath);
            Assert.EndsWith("kds-brain", brainPath);
        }

        [Fact]
        public void GetBrainPath_DirectoryExists()
        {
            // Arrange & Act
            var brainPath = ConfigurationHelper.GetBrainPath();
            
            // Assert
            Assert.True(Directory.Exists(brainPath), $"Brain directory should exist: {brainPath}");
        }

        [Fact]
        public void GetEventsPath_ReturnsEventsJsonlPath()
        {
            // Arrange & Act
            var eventsPath = ConfigurationHelper.GetEventsPath();
            
            // Assert
            Assert.NotNull(eventsPath);
            Assert.EndsWith("events.jsonl", eventsPath);
        }

        [Fact]
        public void GetConversationHistoryPath_ReturnsCorrectPath()
        {
            // Arrange & Act
            var conversationPath = ConfigurationHelper.GetConversationHistoryPath();
            
            // Assert
            Assert.NotNull(conversationPath);
            Assert.EndsWith("conversation-history.jsonl", conversationPath);
        }

        [Fact]
        public void GetDevelopmentContextPath_ReturnsCorrectPath()
        {
            // Arrange & Act
            var contextPath = ConfigurationHelper.GetDevelopmentContextPath();
            
            // Assert
            Assert.NotNull(contextPath);
            Assert.EndsWith("development-context.yaml", contextPath);
        }

        [Fact]
        public void GetKnowledgeGraphPath_ReturnsCorrectPath()
        {
            // Arrange & Act
            var knowledgePath = ConfigurationHelper.GetKnowledgeGraphPath();
            
            // Assert
            Assert.NotNull(knowledgePath);
            Assert.EndsWith("knowledge-graph.yaml", knowledgePath);
        }
    }
}
