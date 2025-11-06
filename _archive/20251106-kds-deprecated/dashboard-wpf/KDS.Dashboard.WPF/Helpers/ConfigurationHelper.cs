using System;
using System.IO;

namespace KDS.Dashboard.WPF.Helpers
{
    /// <summary>
    /// Helper class to locate KDS root directory and brain files
    /// Searches upward from current directory for kds.config.json
    /// </summary>
    public static class ConfigurationHelper
    {
        private static string? _kdsRoot;
        
        /// <summary>
        /// Gets the KDS root directory by searching for kds.config.json
        /// </summary>
        public static string GetKdsRoot()
        {
            if (_kdsRoot != null)
                return _kdsRoot;
            
            // Start from current directory and search upward
            var searchPath = Directory.GetCurrentDirectory();
            
            while (searchPath != null)
            {
                var configPath = Path.Combine(searchPath, "kds.config.json");
                if (File.Exists(configPath))
                {
                    _kdsRoot = searchPath;
                    return _kdsRoot;
                }
                
                var parentDir = Directory.GetParent(searchPath);
                searchPath = parentDir?.FullName;
            }
            
            // Fallback: Check common locations
            var fallbackPaths = new[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "source", "repos", "KDS"),
                @"D:\PROJECTS\KDS",
                @"C:\Projects\KDS"
            };
            
            foreach (var fallbackPath in fallbackPaths)
            {
                if (Directory.Exists(fallbackPath) && File.Exists(Path.Combine(fallbackPath, "kds.config.json")))
                {
                    _kdsRoot = fallbackPath;
                    return _kdsRoot;
                }
            }
            
            throw new DirectoryNotFoundException(
                "Could not find KDS root. Ensure kds.config.json exists in the KDS directory."
            );
        }
        
        /// <summary>
        /// Gets the kds-brain directory path
        /// </summary>
        public static string GetBrainPath()
        {
            var kdsRoot = GetKdsRoot();
            return Path.Combine(kdsRoot, "kds-brain");
        }
        
        /// <summary>
        /// Gets the events.jsonl file path
        /// </summary>
        public static string GetEventsPath()
        {
            return Path.Combine(GetBrainPath(), "events.jsonl");
        }
        
        /// <summary>
        /// Gets the conversation-history.jsonl file path
        /// </summary>
        public static string GetConversationHistoryPath()
        {
            return Path.Combine(GetBrainPath(), "conversation-history.jsonl");
        }
        
        /// <summary>
        /// Gets the development-context.yaml file path
        /// </summary>
        public static string GetDevelopmentContextPath()
        {
            return Path.Combine(GetBrainPath(), "development-context.yaml");
        }
        
        /// <summary>
        /// Gets the knowledge-graph.yaml file path
        /// </summary>
        public static string GetKnowledgeGraphPath()
        {
            return Path.Combine(GetBrainPath(), "knowledge-graph.yaml");
        }
        
        // Alias methods for integration tests
        
        /// <summary>
        /// Alias for GetConversationHistoryPath()
        /// </summary>
        public static string GetConversationsPath() => GetConversationHistoryPath();
        
        /// <summary>
        /// Alias for GetDevelopmentContextPath()
        /// </summary>
        public static string GetMetricsPath() => GetDevelopmentContextPath();
        
        /// <summary>
        /// Alias for GetKnowledgeGraphPath()
        /// </summary>
        public static string GetHealthPath() => GetKnowledgeGraphPath();
    }
}
