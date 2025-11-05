using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Windows;
using KDS.Dashboard.WPF.Helpers;
using KDS.Dashboard.WPF.Models;

namespace KDS.Dashboard.WPF.ViewModels
{
    /// <summary>
    /// Dashboard ViewModel showing brain health and activity metrics with visual charts
    /// </summary>
    public class DashboardViewModel : ViewModelBase
    {
        private FileSystemWatcher? _eventsWatcher;
        private FileSystemWatcher? _conversationWatcher;
        private FileSystemWatcher? _knowledgeWatcher;
        
        private int _totalEvents;
        private int _eventsTodayCount;
        private int _conversationsCount;
        private int _knowledgePatternsCount;
        private string _brainHealth;
        private ObservableCollection<EventTypeMetric> _eventTypeDistribution;
        private ObservableCollection<ConversationTrend> _conversationTimeline;
        private ObservableCollection<BrainMetric> _brainMetrics;

        public DashboardViewModel()
        {
            _eventTypeDistribution = new ObservableCollection<EventTypeMetric>();
            _conversationTimeline = new ObservableCollection<ConversationTrend>();
            _brainMetrics = new ObservableCollection<BrainMetric>();
            _brainHealth = "Unknown";
            
            try
            {
                LoadDashboardData();
                SetupFileWatchers();
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("DashboardViewModel", 
                    "Error initializing dashboard", ex);
            }
        }

        public int TotalEvents
        {
            get => _totalEvents;
            set => SetProperty(ref _totalEvents, value);
        }

        public int EventsTodayCount
        {
            get => _eventsTodayCount;
            set => SetProperty(ref _eventsTodayCount, value);
        }

        public int ConversationsCount
        {
            get => _conversationsCount;
            set => SetProperty(ref _conversationsCount, value);
        }

        public int KnowledgePatternsCount
        {
            get => _knowledgePatternsCount;
            set => SetProperty(ref _knowledgePatternsCount, value);
        }

        public string BrainHealth
        {
            get => _brainHealth;
            set => SetProperty(ref _brainHealth, value);
        }

        public ObservableCollection<EventTypeMetric> EventTypeDistribution
        {
            get => _eventTypeDistribution;
            set => SetProperty(ref _eventTypeDistribution, value);
        }

        public ObservableCollection<ConversationTrend> ConversationTimeline
        {
            get => _conversationTimeline;
            set => SetProperty(ref _conversationTimeline, value);
        }

        public ObservableCollection<BrainMetric> BrainMetrics
        {
            get => _brainMetrics;
            set => SetProperty(ref _brainMetrics, value);
        }

        private void SetupFileWatchers()
        {
            try
            {
                var brainPath = ConfigurationHelper.GetBrainPath();
                
                if (!Directory.Exists(brainPath))
                    return;

                // Watch events.jsonl
                _eventsWatcher = new FileSystemWatcher(brainPath, "events.jsonl")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                _eventsWatcher.Changed += OnDataFileChanged;

                // Watch conversation-history.jsonl
                _conversationWatcher = new FileSystemWatcher(brainPath, "conversation-history.jsonl")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                _conversationWatcher.Changed += OnDataFileChanged;

                // Watch knowledge-graph.yaml
                _knowledgeWatcher = new FileSystemWatcher(brainPath, "knowledge-graph.yaml")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                _knowledgeWatcher.Changed += OnDataFileChanged;
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("DashboardViewModel", 
                    "Failed to setup file watchers", ex);
            }
        }

        private void OnDataFileChanged(object sender, FileSystemEventArgs e)
        {
            Application.Current?.Dispatcher.Invoke(() =>
            {
                try
                {
                    LoadDashboardData();
                }
                catch (Exception ex)
                {
                    ErrorViewModel.Instance.LogError("DashboardViewModel", 
                        "Failed to reload dashboard after file change", ex);
                }
            });
        }

        private void LoadDashboardData()
        {
            try
            {
                LoadEventMetrics();
                LoadConversationMetrics();
                LoadBrainHealthMetrics();
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("DashboardViewModel", 
                    "Error loading dashboard data", ex);
            }
        }

        private void LoadEventMetrics()
        {
            try
            {
                var eventsPath = ConfigurationHelper.GetEventsPath();
                
                if (!File.Exists(eventsPath))
                    return;

                var jsonOptions = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                };

                var events = File.ReadLines(eventsPath)
                    .Where(l => !string.IsNullOrWhiteSpace(l))
                    .Select(line =>
                    {
                        try
                        {
                            return JsonSerializer.Deserialize<BrainEvent>(line, jsonOptions);
                        }
                        catch
                        {
                            return null;
                        }
                    })
                    .Where(e => e != null && e.Event != "dashboard_error")
                    .Select(e => e!)
                    .ToList();

                TotalEvents = events.Count;
                
                // Events today
                var today = DateTime.Today;
                EventsTodayCount = events.Count(e => e.Timestamp.Date == today);

                // Event type distribution
                var distribution = events
                    .GroupBy(e => e.Event)
                    .Select(g => new EventTypeMetric
                    {
                        EventType = g.Key,
                        Count = g.Count(),
                        Percentage = (double)g.Count() / TotalEvents * 100
                    })
                    .OrderByDescending(m => m.Count)
                    .Take(10)
                    .ToList();

                EventTypeDistribution.Clear();
                foreach (var metric in distribution)
                {
                    EventTypeDistribution.Add(metric);
                }
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("DashboardViewModel", 
                    "Error loading event metrics", ex);
            }
        }

        private void LoadConversationMetrics()
        {
            try
            {
                var conversationPath = ConfigurationHelper.GetConversationHistoryPath();
                
                if (!File.Exists(conversationPath))
                    return;

                var jsonOptions = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                };

                var conversations = File.ReadLines(conversationPath)
                    .Where(l => !string.IsNullOrWhiteSpace(l))
                    .Select(line =>
                    {
                        try
                        {
                            return JsonSerializer.Deserialize<Conversation>(line, jsonOptions);
                        }
                        catch
                        {
                            return null;
                        }
                    })
                    .Where(c => c != null)
                    .Select(c => c!)
                    .ToList();

                ConversationsCount = conversations.Count;

                // Conversation timeline (last 7 days)
                var timeline = conversations
                    .Where(c => c.Started >= DateTime.Now.AddDays(-7))
                    .GroupBy(c => c.Started.Date)
                    .Select(g => new ConversationTrend
                    {
                        Date = g.Key,
                        Count = g.Count(),
                        TotalMessages = g.Sum(c => c.MessageCount)
                    })
                    .OrderBy(t => t.Date)
                    .ToList();

                ConversationTimeline.Clear();
                foreach (var trend in timeline)
                {
                    ConversationTimeline.Add(trend);
                }
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("DashboardViewModel", 
                    "Error loading conversation metrics", ex);
            }
        }

        private void LoadBrainHealthMetrics()
        {
            try
            {
                var knowledgePath = ConfigurationHelper.GetKnowledgeGraphPath();
                
                if (!File.Exists(knowledgePath))
                    return;

                var yaml = File.ReadAllText(knowledgePath);
                
                // Count patterns in knowledge graph
                var patternMatches = System.Text.RegularExpressions.Regex.Matches(
                    yaml, @"^\s*-\s+", System.Text.RegularExpressions.RegexOptions.Multiline);
                KnowledgePatternsCount = patternMatches.Count;

                // Calculate brain health
                var eventBacklog = TotalEvents;
                var conversationUtilization = (ConversationsCount / 20.0) * 100; // 20 is FIFO capacity
                
                if (eventBacklog < 50 && KnowledgePatternsCount > 1000 && conversationUtilization < 80)
                    BrainHealth = "Excellent";
                else if (eventBacklog < 100 && KnowledgePatternsCount > 500)
                    BrainHealth = "Good";
                else if (eventBacklog < 200)
                    BrainHealth = "Fair";
                else
                    BrainHealth = "Needs Attention";

                // Brain metrics cards
                BrainMetrics.Clear();
                BrainMetrics.Add(new BrainMetric
                {
                    Name = "Event Backlog",
                    Value = eventBacklog,
                    Status = eventBacklog < 50 ? "Healthy" : "Warning",
                    Icon = "Flash"
                });
                BrainMetrics.Add(new BrainMetric
                {
                    Name = "Knowledge Patterns",
                    Value = KnowledgePatternsCount,
                    Status = KnowledgePatternsCount > 500 ? "Healthy" : "Low",
                    Icon = "Brain"
                });
                BrainMetrics.Add(new BrainMetric
                {
                    Name = "Conversation Capacity",
                    Value = (int)conversationUtilization,
                    Status = conversationUtilization < 80 ? "Healthy" : "High",
                    Icon = "MessageText"
                });
                BrainMetrics.Add(new BrainMetric
                {
                    Name = "Events Today",
                    Value = EventsTodayCount,
                    Status = EventsTodayCount > 0 ? "Active" : "Idle",
                    Icon = "ChartLine"
                });
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("DashboardViewModel", 
                    "Error loading brain health metrics", ex);
            }
        }

        public void Dispose()
        {
            _eventsWatcher?.Dispose();
            _conversationWatcher?.Dispose();
            _knowledgeWatcher?.Dispose();
        }
    }

    public class EventTypeMetric
    {
        public string EventType { get; set; } = string.Empty;
        public int Count { get; set; }
        public double Percentage { get; set; }
    }

    public class ConversationTrend
    {
        public DateTime Date { get; set; }
        public int Count { get; set; }
        public int TotalMessages { get; set; }
    }

    public class BrainMetric
    {
        public string Name { get; set; } = string.Empty;
        public int Value { get; set; }
        public string Status { get; set; } = string.Empty;
        public string Icon { get; set; } = string.Empty;
    }
}
