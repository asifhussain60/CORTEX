using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Windows;
using KDS.Dashboard.WPF.Models;
using KDS.Dashboard.WPF.Helpers;

namespace KDS.Dashboard.WPF.ViewModels
{
    /// <summary>
    /// ViewModel for the Activity tab showing real-time event stream
    /// Monitors events.jsonl with FileSystemWatcher for live updates
    /// </summary>
    public class ActivityViewModel : ViewModelBase
    {
        private ObservableCollection<BrainEvent> _events;
        private FileSystemWatcher? _eventWatcher;

        public ActivityViewModel()
        {
            _events = new ObservableCollection<BrainEvent>();
            
            try
            {
                LoadEvents();
                SetupFileWatcher();
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("ActivityViewModel", 
                    "Failed to initialize activity view", ex);
            }
        }

        public ObservableCollection<BrainEvent> Events
        {
            get => _events;
            set => SetProperty(ref _events, value);
        }

        private void SetupFileWatcher()
        {
            try
            {
                var eventsPath = ConfigurationHelper.GetEventsPath();
                var brainPath = ConfigurationHelper.GetBrainPath();
                
                if (!Directory.Exists(brainPath))
                {
                    ErrorViewModel.Instance.LogError("ActivityViewModel", 
                        $"Brain directory not found: {brainPath}");
                    return;
                }

                _eventWatcher = new FileSystemWatcher(brainPath, "events.jsonl")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                
                _eventWatcher.Changed += OnEventsFileChanged;
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("ActivityViewModel", 
                    "Failed to setup file watcher for events.jsonl", ex);
            }
        }

        private void OnEventsFileChanged(object sender, FileSystemEventArgs e)
        {
            // Reload events from file on UI thread
            Application.Current?.Dispatcher.Invoke(() =>
            {
                try
                {
                    LoadEvents();
                }
                catch (Exception ex)
                {
                    ErrorViewModel.Instance.LogError("ActivityViewModel", 
                        "Failed to reload events after file change", ex);
                }
            });
        }

        private void LoadEvents()
        {
            try
            {
                var eventsPath = ConfigurationHelper.GetEventsPath();
                
                if (!File.Exists(eventsPath))
                {
                    ErrorViewModel.Instance.LogError("ActivityViewModel", 
                        $"Events file not found: {eventsPath}");
                    Events = new ObservableCollection<BrainEvent>();
                    return;
                }

                // Read ALL events, filter out dashboard_error, then take last 50
                var lines = File.ReadLines(eventsPath)
                    .Where(l => !string.IsNullOrWhiteSpace(l));

                var events = lines
                    .Select(line =>
                    {
                        try
                        {
                            return JsonSerializer.Deserialize<BrainEvent>(line, 
                                new JsonSerializerOptions 
                                { 
                                    PropertyNameCaseInsensitive = true,
                                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                                });
                        }
                        catch (JsonException ex)
                        {
                            ErrorViewModel.Instance.LogError("ActivityViewModel", 
                                $"Failed to parse event line: {line}", ex);
                            return null;
                        }
                    })
                    .Where(e => e != null)
                    .Select(e => e!)
                    .Where(e => e.Event != "dashboard_error") // Filter out dashboard_error events
                    .OrderByDescending(e => e.Timestamp)
                    .Take(50) // Take last 50 AFTER filtering
                    .ToList();

                Events = new ObservableCollection<BrainEvent>(events);
                
                // Don't log here - it would trigger infinite loop since we're watching events.jsonl
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("ActivityViewModel", 
                    "Failed to load events from events.jsonl", ex);
                Events = new ObservableCollection<BrainEvent>();
            }
        }

        public void Dispose()
        {
            if (_eventWatcher != null)
            {
                _eventWatcher.EnableRaisingEvents = false;
                _eventWatcher.Dispose();
            }
        }
    }
}
