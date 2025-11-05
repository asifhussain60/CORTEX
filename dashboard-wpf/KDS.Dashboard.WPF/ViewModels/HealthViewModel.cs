using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Windows;
using KDS.Dashboard.WPF.Helpers;
using KDS.Dashboard.WPF.Models;

namespace KDS.Dashboard.WPF.ViewModels
{
    /// <summary>
    /// ViewModel for the Health tab showing brain health metrics
    /// Loads from multiple brain files with FileSystemWatcher for real-time updates
    /// </summary>
    public class HealthViewModel : ViewModelBase
    {
        private int _eventBacklog;
        private int _knowledgeEntries;
        private int _conversationCount;
        private DateTime _lastBrainUpdate;
        private string _healthStatus = string.Empty;
        private FileSystemWatcher? _eventsWatcher;
        private FileSystemWatcher? _knowledgeWatcher;
        private FileSystemWatcher? _conversationWatcher;

        public HealthViewModel()
        {
            try
            {
                LoadHealth();
                SetupFileWatchers();
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("HealthViewModel", 
                    "Error initializing HealthViewModel", ex);
            }
        }

        public int EventBacklog
        {
            get => _eventBacklog;
            set => SetProperty(ref _eventBacklog, value);
        }

        public int KnowledgeEntries
        {
            get => _knowledgeEntries;
            set => SetProperty(ref _knowledgeEntries, value);
        }

        public int ConversationCount
        {
            get => _conversationCount;
            set => SetProperty(ref _conversationCount, value);
        }

        public DateTime LastBrainUpdate
        {
            get => _lastBrainUpdate;
            set => SetProperty(ref _lastBrainUpdate, value);
        }

        public string HealthStatus
        {
            get => _healthStatus;
            set => SetProperty(ref _healthStatus, value);
        }

        private void SetupFileWatchers()
        {
            try
            {
                var brainPath = ConfigurationHelper.GetBrainPath();
                
                if (!Directory.Exists(brainPath))
                {
                    ErrorViewModel.Instance.LogError("HealthViewModel", 
                        $"Brain directory not found: {brainPath}");
                    return;
                }

                // Watch events.jsonl for backlog changes
                _eventsWatcher = new FileSystemWatcher(brainPath, "events.jsonl")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                _eventsWatcher.Changed += OnHealthFileChanged;

                // Watch knowledge-graph.yaml for pattern changes
                _knowledgeWatcher = new FileSystemWatcher(brainPath, "knowledge-graph.yaml")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                _knowledgeWatcher.Changed += OnHealthFileChanged;

                // Watch conversation-history.jsonl for count changes
                _conversationWatcher = new FileSystemWatcher(brainPath, "conversation-history.jsonl")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                _conversationWatcher.Changed += OnHealthFileChanged;
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("HealthViewModel", 
                    "Failed to setup file watchers for health monitoring", ex);
            }
        }

        private void OnHealthFileChanged(object sender, FileSystemEventArgs e)
        {
            // Reload health from files on UI thread
            Application.Current?.Dispatcher.Invoke(() =>
            {
                try
                {
                    LoadHealth();
                }
                catch (Exception ex)
                {
                    ErrorViewModel.Instance.LogError("HealthViewModel", 
                        "Failed to reload health after file change", ex);
                }
            });
        }

        private void LoadHealth()
        {
            try
            {
                // Event backlog
                var eventsPath = ConfigurationHelper.GetEventsPath();
                if (File.Exists(eventsPath))
                {
                    EventBacklog = File.ReadLines(eventsPath)
                        .Count(l => !string.IsNullOrWhiteSpace(l));
                }

                // Knowledge entries (count patterns in YAML)
                var knowledgePath = ConfigurationHelper.GetKnowledgeGraphPath();
                if (File.Exists(knowledgePath))
                {
                    var yaml = File.ReadAllText(knowledgePath);
                    KnowledgeEntries = Regex.Matches(yaml, @"pattern:|workflow:|insight:").Count;
                    LastBrainUpdate = File.GetLastWriteTime(knowledgePath);
                }

                // Conversation count
                var conversationPath = ConfigurationHelper.GetConversationHistoryPath();
                if (File.Exists(conversationPath))
                {
                    ConversationCount = File.ReadLines(conversationPath)
                        .Count(l => !string.IsNullOrWhiteSpace(l));
                }

                // Calculate health status
                HealthStatus = CalculateHealthStatus();
                
                // Don't log to events.jsonl - could trigger infinite loop since we're watching it
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("HealthViewModel", 
                    "Error loading health", ex);
            }
        }

        private string CalculateHealthStatus()
        {
            if (EventBacklog < 50 && KnowledgeEntries > 1000)
                return "Excellent";
            else if (EventBacklog < 100 && KnowledgeEntries > 500)
                return "Good";
            else if (EventBacklog < 200)
                return "Fair";
            else
                return "Needs Attention";
        }

        public void Dispose()
        {
            if (_eventsWatcher != null)
            {
                _eventsWatcher.EnableRaisingEvents = false;
                _eventsWatcher.Dispose();
            }
            if (_knowledgeWatcher != null)
            {
                _knowledgeWatcher.EnableRaisingEvents = false;
                _knowledgeWatcher.Dispose();
            }
            if (_conversationWatcher != null)
            {
                _conversationWatcher.EnableRaisingEvents = false;
                _conversationWatcher.Dispose();
            }
        }
    }
}
