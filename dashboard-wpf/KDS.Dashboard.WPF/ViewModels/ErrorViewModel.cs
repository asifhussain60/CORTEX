using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using System.Windows;
using KDS.Dashboard.WPF.Helpers;

namespace KDS.Dashboard.WPF.ViewModels
{
    /// <summary>
    /// Centralized error logging and display for the dashboard.
    /// Replaces silent Debug.WriteLine failures with visible errors.
    /// Logs errors to both UI and events.jsonl for brain tracking.
    /// </summary>
    public class ErrorViewModel : ViewModelBase
    {
        private ObservableCollection<ErrorEntry> _errors;
        private ErrorEntry? _latestError;
        private static ErrorViewModel? _instance;

        private ErrorViewModel()
        {
            _errors = new ObservableCollection<ErrorEntry>();
        }

        /// <summary>
        /// Singleton instance for application-wide error tracking
        /// </summary>
        public static ErrorViewModel Instance => _instance ??= new ErrorViewModel();

        public ObservableCollection<ErrorEntry> Errors
        {
            get => _errors;
            set => SetProperty(ref _errors, value);
        }

        public ErrorEntry? LatestError
        {
            get => _latestError;
            set => SetProperty(ref _latestError, value);
        }

        public bool HasErrors => _errors.Count > 0;

        public string LatestErrorMessage => _latestError?.Message ?? string.Empty;

        /// <summary>
        /// Log an error to both UI and events.jsonl
        /// </summary>
        public void LogError(string source, string message, Exception? exception = null)
        {
            var entry = new ErrorEntry
            {
                Timestamp = DateTime.Now,
                Source = source,
                Message = message,
                Exception = exception?.ToString(),
                Severity = exception != null ? ErrorSeverity.Critical : ErrorSeverity.Warning
            };

            // Add to UI on dispatcher thread
            Application.Current?.Dispatcher.Invoke(() =>
            {
                Errors.Insert(0, entry);
                LatestError = entry;
                OnPropertyChanged(nameof(HasErrors));
                OnPropertyChanged(nameof(LatestErrorMessage));

                // Keep last 100 errors in UI
                while (Errors.Count > 100)
                {
                    Errors.RemoveAt(Errors.Count - 1);
                }
            });

            // Log to events.jsonl asynchronously
            LogToEventsFile(entry);
        }

        /// <summary>
        /// Log an informational message (not shown as error, just logged to brain)
        /// </summary>
        public void LogInfo(string source, string message)
        {
            var entry = new ErrorEntry
            {
                Timestamp = DateTime.Now,
                Source = source,
                Message = message,
                Severity = ErrorSeverity.Info
            };

            LogToEventsFile(entry);
        }

        private void LogToEventsFile(ErrorEntry entry)
        {
            try
            {
                var eventsPath = ConfigurationHelper.GetEventsPath();
                var logEntry = new
                {
                    timestamp = entry.Timestamp.ToString("o"),
                    @event = "dashboard_error",
                    source = entry.Source,
                    message = entry.Message,
                    severity = entry.Severity.ToString().ToLower(),
                    exception = entry.Exception
                };

                var json = JsonSerializer.Serialize(logEntry);
                File.AppendAllText(eventsPath, json + Environment.NewLine);
            }
            catch
            {
                // If we can't log to events.jsonl, don't crash
                // This can happen during initialization or if brain files unavailable
            }
        }

        public void ClearErrors()
        {
            Application.Current?.Dispatcher.Invoke(() =>
            {
                Errors.Clear();
                LatestError = null;
                OnPropertyChanged(nameof(HasErrors));
                OnPropertyChanged(nameof(LatestErrorMessage));
            });
        }
    }

    public class ErrorEntry
    {
        public DateTime Timestamp { get; set; }
        public string Source { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
        public string? Exception { get; set; }
        public ErrorSeverity Severity { get; set; }

        public string SeverityIcon => Severity switch
        {
            ErrorSeverity.Info => "Information",
            ErrorSeverity.Warning => "Alert",
            ErrorSeverity.Error => "AlertCircle",
            ErrorSeverity.Critical => "AlertOctagon",
            _ => "Help"
        };

        public string SeverityColor => Severity switch
        {
            ErrorSeverity.Info => "#3498DB",
            ErrorSeverity.Warning => "#F39C12",
            ErrorSeverity.Error => "#E67E22",
            ErrorSeverity.Critical => "#E74C3C",
            _ => "#95A5A6"
        };
    }

    public enum ErrorSeverity
    {
        Info,
        Warning,
        Error,
        Critical
    }
}
