using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace KDS.Dashboard.WPF.Models
{
    /// <summary>
    /// Represents a single brain event from events.jsonl
    /// Actual schema: heterogeneous events with varying properties
    /// Common fields: timestamp, event, plus event-specific properties
    /// </summary>
    public class BrainEvent
    {
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
        
        [JsonPropertyName("event")]
        public string Event { get; set; } = string.Empty;
        
        [JsonPropertyName("agent")]
        public string? Agent { get; set; }
        
        [JsonPropertyName("type")]
        public string? Type { get; set; }
        
        [JsonPropertyName("workflow")]
        public string? Workflow { get; set; }
        
        [JsonPropertyName("category")]
        public string? Category { get; set; }
        
        [JsonPropertyName("context")]
        public string? Context { get; set; }
        
        [JsonPropertyName("hemisphere")]
        public string? Hemisphere { get; set; }
        
        [JsonPropertyName("feature")]
        public string? Feature { get; set; }
        
        [JsonPropertyName("confidence")]
        public decimal? Confidence { get; set; }
        
        [JsonPropertyName("impact")]
        public string? Impact { get; set; }
        
        [JsonPropertyName("issue")]
        public string? Issue { get; set; }
        
        [JsonPropertyName("insight")]
        public string? Insight { get; set; }
        
        [JsonPropertyName("recommendation")]
        public string? Recommendation { get; set; }
        
        [JsonPropertyName("outcome")]
        public string? Outcome { get; set; }
        
        // Extension data for unknown properties
        [JsonExtensionData]
        public Dictionary<string, JsonElement>? ExtensionData { get; set; }
        
        // Computed properties for display
        public string DisplayTitle => !string.IsNullOrEmpty(Feature) ? Feature :
                                     !string.IsNullOrEmpty(Workflow) ? Workflow :
                                     !string.IsNullOrEmpty(Type) ? Type :
                                     Event;
        
        public string DisplayStatus => Outcome ?? Impact ?? "active";
    }

    /// <summary>
    /// Represents a conversation from conversation-history.jsonl
    /// Actual schema: conversation_id, title, started, ended, message_count, active, messages, outcome
    /// </summary>
    public class Conversation
    {
        [JsonPropertyName("conversation_id")]
        public string ConversationId { get; set; } = string.Empty;
        
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;
        
        [JsonPropertyName("started")]
        public DateTime Started { get; set; }
        
        [JsonPropertyName("ended")]
        public DateTime? Ended { get; set; }
        
        [JsonPropertyName("message_count")]
        public int MessageCount { get; set; }
        
        [JsonPropertyName("active")]
        public bool Active { get; set; }
        
        [JsonPropertyName("outcome")]
        public string? Outcome { get; set; }
        
        [JsonPropertyName("note")]
        public string? Note { get; set; }
        
        [JsonPropertyName("files_modified")]
        [JsonConverter(typeof(StringOrArrayConverter))]
        public List<string>? FilesModified { get; set; }
        
        [JsonPropertyName("entities_discussed")]
        [JsonConverter(typeof(StringOrArrayConverter))]
        public List<string>? EntitiesDiscussed { get; set; }
        
        [JsonPropertyName("messages")]
        public List<ConversationMessage>? Messages { get; set; }
        
        [JsonPropertyName("associated_commits")]
        public List<GitCommit>? AssociatedCommits { get; set; }
        
        // Extension data for unknown properties
        [JsonExtensionData]
        public Dictionary<string, JsonElement>? ExtensionData { get; set; }
        
        // Computed properties
        public DateTime Timestamp => Started;
        public string Status => Active ? "Active" : (Outcome ?? "Completed");
        public int Duration => Ended.HasValue ? (int)(Ended.Value - Started).TotalSeconds : 0;

        /// <summary>
        /// A short, user-focused snippet extracted from messages.
        /// Filters to useful intents and returns the first non-empty text found.
        /// </summary>
        public string DisplaySnippet
        {
            get
            {
                try
                {
                    if (Messages == null || Messages.Count == 0)
                        return string.Empty;

                    // Prefer user messages with meaningful intent
                    var useful = Messages
                        .Where(m => !string.IsNullOrWhiteSpace(m.Text) &&
                                    (string.IsNullOrEmpty(m.Intent) || m.Intent.Equals("PLAN", StringComparison.OrdinalIgnoreCase) || m.Intent.Equals("EXECUTE", StringComparison.OrdinalIgnoreCase) || m.Intent.Equals("TEST", StringComparison.OrdinalIgnoreCase)))
                        .Select(m => m.Text!.Trim())
                        .ToList();

                    var first = useful.FirstOrDefault() ?? Messages.Select(m => m.Text).FirstOrDefault(t => !string.IsNullOrWhiteSpace(t)) ?? string.Empty;
                    if (first.Length > 140) return first.Substring(0, 137) + "...";
                    return first;
                }
                catch
                {
                    return string.Empty;
                }
            }
        }
    }
    
    /// <summary>
    /// Represents a message within a conversation
    /// </summary>
    public class ConversationMessage
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;
        
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
        
        [JsonPropertyName("user")]
        public string User { get; set; } = string.Empty;
        
        [JsonPropertyName("intent")]
        public string? Intent { get; set; }
        
        [JsonPropertyName("text")]
        public string? Text { get; set; }
        
        [JsonPropertyName("context_ref")]
        public string? ContextRef { get; set; }
        
        [JsonPropertyName("entities")]
        public List<string>? Entities { get; set; }
    }

    /// <summary>
    /// Represents a git commit associated with a conversation
    /// Tracks code changes resulting from conversation discussions
    /// </summary>
    public class GitCommit
    {
        [JsonPropertyName("sha")]
        public string Sha { get; set; } = string.Empty;
        
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
        
        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;
        
        [JsonPropertyName("author")]
        public string Author { get; set; } = string.Empty;
        
        [JsonPropertyName("files_changed")]
        public List<string> FilesChanged { get; set; } = new();
        
        [JsonPropertyName("additions")]
        public int Additions { get; set; }
        
        [JsonPropertyName("deletions")]
        public int Deletions { get; set; }
        
        // Computed properties for display
        public string ShortSha => Sha.Length > 8 ? Sha.Substring(0, 8) : Sha;
        public string ShortMessage => Message.Length > 100 ? Message.Substring(0, 97) + "..." : Message;
        public string StatsDisplay => $"{FilesChanged.Count} files • +{Additions} -{Deletions}";
    }

    /// <summary>
    /// Represents development metrics from development-context.yaml
    /// </summary>
    public class MetricsData
    {
        public int CommitsThisWeek { get; set; }
        public int LinesAddedThisWeek { get; set; }
        public decimal TestPassRate { get; set; }
        public int[] VelocityTrend { get; set; } = Array.Empty<int>();
        public Dictionary<string, int> TopFiles { get; set; } = new();
    }

    /// <summary>
    /// Represents brain health metrics
    /// </summary>
    public class HealthData
    {
        public int EventBacklog { get; set; }
        public int KnowledgeEntries { get; set; }
        public int ConversationCount { get; set; }
        public DateTime LastBrainUpdate { get; set; }
        public string HealthStatus { get; set; } = string.Empty;
        public decimal ConfidenceAverage { get; set; }
    }

    /// <summary>
    /// Represents a KDS feature from feature inventory
    /// </summary>
    public class Feature
    {
        public string Name { get; set; } = string.Empty;
        public FeatureStatus Status { get; set; }
        public string Notes { get; set; } = string.Empty;
        public string DiscoveredFrom { get; set; } = string.Empty;
        
        // Component lists
        public List<string> Files { get; set; } = new List<string>();
        public List<string> Scripts { get; set; } = new List<string>();
        public List<string> Tests { get; set; } = new List<string>();
        public List<string> Docs { get; set; } = new List<string>();
        public List<GitCommit> GitCommits { get; set; } = new List<GitCommit>();
        
        // Validation flags
        public bool HasCode { get; set; }
        public bool HasTests { get; set; }
        public bool HasDocs { get; set; }
        public bool HasAgentIntegration { get; set; }
        
        // Metadata
        public decimal Confidence { get; set; }
        public List<string> MissingComponents { get; set; } = new List<string>();
        public string Version { get; set; } = string.Empty;
        public DateTime? DateAdded { get; set; }
        public DateTime? DateModified { get; set; }
        
        // Display properties
        public string StatusBadge => Status switch
        {
            FeatureStatus.FullyImplemented => "✅",
            FeatureStatus.PartiallyImplemented => "🟡",
            FeatureStatus.InProgress => "🔄",
            FeatureStatus.DesignedOnly => "📋",
            FeatureStatus.Deprecated => "❌",
            _ => "❓"
        };
        
        public string StatusText => Status switch
        {
            FeatureStatus.FullyImplemented => "Fully Implemented",
            FeatureStatus.PartiallyImplemented => "Partially Implemented",
            FeatureStatus.InProgress => "In Progress",
            FeatureStatus.DesignedOnly => "Designed Only",
            FeatureStatus.Deprecated => "Deprecated",
            _ => "Unknown"
        };
        
        public int FileCount => Files.Count;
        public int ScriptCount => Scripts.Count;
        public int TestCount => Tests.Count;
        public int DocCount => Docs.Count;
        public int CommitCount => GitCommits.Count;
        
        public string ComponentSummary => 
            $"{FileCount} files, {ScriptCount} scripts, {TestCount} tests";
        
        public string MissingComponentsText =>
            MissingComponents.Count > 0 
                ? string.Join(", ", MissingComponents) 
                : "None";
    }

    public enum FeatureStatus
    {
        FullyImplemented,
        PartiallyImplemented,
        InProgress,
        DesignedOnly,
        Deprecated,
        Unknown
    }
}
