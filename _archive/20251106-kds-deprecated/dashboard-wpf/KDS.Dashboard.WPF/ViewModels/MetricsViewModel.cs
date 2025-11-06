using System;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Input;
using KDS.Dashboard.WPF.Helpers;
using KDS.Dashboard.WPF.Models;

namespace KDS.Dashboard.WPF.ViewModels
{
    /// <summary>
    /// ViewModel for the Metrics tab showing development metrics
    /// Loads from development-context.yaml with FileSystemWatcher for real-time updates
    /// </summary>
    public class MetricsViewModel : ViewModelBase
    {
        private int _commitsThisWeek;
        private int _linesAddedThisWeek;
        private decimal _testPassRate;
        private FileSystemWatcher? _metricsWatcher;
        private ICommand? _refreshMetricsCommand;

        public MetricsViewModel()
        {
            try
            {
                LoadMetrics();
                SetupFileWatcher();
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("MetricsViewModel", 
                    "Error initializing MetricsViewModel", ex);
            }
        }

        public ICommand RefreshMetricsCommand
        {
            get
            {
                return _refreshMetricsCommand ??= new RelayCommand(
                    execute: _ => RefreshMetrics(),
                    canExecute: _ => true
                );
            }
        }

        public int CommitsThisWeek
        {
            get => _commitsThisWeek;
            set => SetProperty(ref _commitsThisWeek, value);
        }

        public int LinesAddedThisWeek
        {
            get => _linesAddedThisWeek;
            set => SetProperty(ref _linesAddedThisWeek, value);
        }

        public decimal TestPassRate
        {
            get => _testPassRate;
            set => SetProperty(ref _testPassRate, value);
        }

        private void SetupFileWatcher()
        {
            try
            {
                var brainPath = ConfigurationHelper.GetBrainPath();
                
                if (!Directory.Exists(brainPath))
                {
                    ErrorViewModel.Instance.LogError("MetricsViewModel", 
                        $"Brain directory not found: {brainPath}");
                    return;
                }

                _metricsWatcher = new FileSystemWatcher(brainPath, "development-context.yaml")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                
                _metricsWatcher.Changed += OnMetricsFileChanged;
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("MetricsViewModel", 
                    "Failed to setup file watcher for development-context.yaml", ex);
            }
        }

        private void OnMetricsFileChanged(object sender, FileSystemEventArgs e)
        {
            // Reload metrics from file on UI thread
            Application.Current?.Dispatcher.Invoke(() =>
            {
                try
                {
                    LoadMetrics();
                }
                catch (Exception ex)
                {
                    ErrorViewModel.Instance.LogError("MetricsViewModel", 
                        "Failed to reload metrics after file change", ex);
                }
            });
        }

        private void LoadMetrics()
        {
            try
            {
                var contextPath = ConfigurationHelper.GetDevelopmentContextPath();
                
                if (!File.Exists(contextPath))
                {
                    ErrorViewModel.Instance.LogError("MetricsViewModel", 
                        $"Development context not found: {contextPath}");
                    return;
                }

                var yaml = File.ReadAllText(contextPath);

                // Parse YAML using regex (robust to variations)
                // Commits: prefer commits_per_day_avg -> estimate commits per week
                var commitsPerDayMatch = Regex.Match(yaml, @"commits_per_day_avg:\s*([\d.]+)", RegexOptions.IgnoreCase);
                if (commitsPerDayMatch.Success && double.TryParse(commitsPerDayMatch.Groups[1].Value, out var commitsPerDay))
                {
                    CommitsThisWeek = (int)Math.Round(commitsPerDay * 7);
                }
                else
                {
                    // Fallback: total_commits under git_activity.last_30_days
                    var totalCommitsMatch = Regex.Match(yaml, @"total_commits:\s*(\d+)", RegexOptions.IgnoreCase);
                    if (totalCommitsMatch.Success && int.TryParse(totalCommitsMatch.Groups[1].Value, out var totalCommits))
                    {
                        // approximate commits this week as commits_per_day_avg*7 if available, else divide 30-day total by 4
                        CommitsThisWeek = totalCommits / 4;
                    }
                }

                // Lines added: look for code_changes.last_30_days.lines_added
                var linesMatch = Regex.Match(yaml, @"lines_added:\s*(\d+)", RegexOptions.IgnoreCase);
                if (linesMatch.Success && int.TryParse(linesMatch.Groups[1].Value, out var linesAdded))
                {
                    // If this is a 30-day total, approximate week by dividing by 4
                    LinesAddedThisWeek = linesAdded / 4;
                }

                // Test pass rate: prioritize testing_activity.last_30_days.test_pass_rate
                var testPassMatch = Regex.Match(yaml, @"test_pass_rate:\s*([\d.]+)", RegexOptions.IgnoreCase);
                if (testPassMatch.Success && decimal.TryParse(testPassMatch.Groups[1].Value, out var passRate))
                {
                    TestPassRate = passRate;
                }
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("MetricsViewModel", 
                    "Error loading metrics", ex);
            }
        }

        private void RefreshMetrics()
        {
            try
            {
                // Run the dev-context collection script
                var scriptPath = Path.Combine(ConfigurationHelper.GetKdsRoot(), "scripts", "collect-development-context.ps1");
                
                if (!File.Exists(scriptPath))
                {
                    ErrorViewModel.Instance.LogError("MetricsViewModel", 
                        $"Collection script not found: {scriptPath}");
                    return;
                }

                var startInfo = new ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = $"-NoProfile -ExecutionPolicy Bypass -File \"{scriptPath}\"",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                };

                using var process = Process.Start(startInfo);
                if (process != null)
                {
                    process.WaitForExit(30000); // 30 second timeout
                    
                    if (process.ExitCode == 0)
                    {
                        // Reload metrics after successful collection
                        LoadMetrics();
                    }
                    else
                    {
                        var error = process.StandardError.ReadToEnd();
                        ErrorViewModel.Instance.LogError("MetricsViewModel", 
                            $"Metrics collection failed: {error}");
                    }
                }
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("MetricsViewModel", 
                    "Failed to refresh metrics", ex);
            }
        }

        public void Dispose()
        {
            if (_metricsWatcher != null)
            {
                _metricsWatcher.EnableRaisingEvents = false;
                _metricsWatcher.Dispose();
            }
        }
    }
}
