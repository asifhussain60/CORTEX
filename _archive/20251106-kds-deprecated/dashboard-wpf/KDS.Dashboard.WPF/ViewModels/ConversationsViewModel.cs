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
    /// ViewModel for the Conversations tab showing conversation history
    /// Loads from conversation-history.jsonl with FileSystemWatcher for real-time updates
    /// </summary>
    public class ConversationsViewModel : ViewModelBase
    {
        private ObservableCollection<Conversation> _conversations;
        private FileSystemWatcher? _conversationWatcher;

        public ConversationsViewModel()
        {
            _conversations = new ObservableCollection<Conversation>();
            
            try
            {
                LoadConversations();
                SetupFileWatcher();
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("ConversationsViewModel", 
                    "Error initializing ConversationsViewModel", ex);
            }
        }

        public ObservableCollection<Conversation> Conversations
        {
            get => _conversations;
            set => SetProperty(ref _conversations, value);
        }

        private void SetupFileWatcher()
        {
            try
            {
                var brainPath = ConfigurationHelper.GetBrainPath();
                
                if (!Directory.Exists(brainPath))
                {
                    ErrorViewModel.Instance.LogError("ConversationsViewModel", 
                        $"Brain directory not found: {brainPath}");
                    return;
                }

                _conversationWatcher = new FileSystemWatcher(brainPath, "conversation-history.jsonl")
                {
                    NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.Size,
                    EnableRaisingEvents = true
                };
                
                _conversationWatcher.Changed += OnConversationFileChanged;
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("ConversationsViewModel", 
                    "Failed to setup file watcher for conversation-history.jsonl", ex);
            }
        }

        private void OnConversationFileChanged(object sender, FileSystemEventArgs e)
        {
            // Reload conversations from file on UI thread
            Application.Current?.Dispatcher.Invoke(() =>
            {
                try
                {
                    LoadConversations();
                }
                catch (Exception ex)
                {
                    ErrorViewModel.Instance.LogError("ConversationsViewModel", 
                        "Failed to reload conversations after file change", ex);
                }
            });
        }

        private void LoadConversations()
        {
            try
            {
                var conversationPath = ConfigurationHelper.GetConversationHistoryPath();
                
                if (!File.Exists(conversationPath))
                {
                    ErrorViewModel.Instance.LogError("ConversationsViewModel", 
                        $"Conversation history not found: {conversationPath}");
                    Conversations = new ObservableCollection<Conversation>();
                    return;
                }

                var jsonOptions = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                };

                var lines = File.ReadLines(conversationPath)
                    .Where(l => !string.IsNullOrWhiteSpace(l));

                var conversations = lines
                    .Select(line =>
                    {
                        try
                        {
                            return JsonSerializer.Deserialize<Conversation>(line, jsonOptions);
                        }
                        catch (JsonException ex)
                        {
                            ErrorViewModel.Instance.LogError("ConversationsViewModel", 
                                "Error parsing conversation line", ex);
                            return null;
                        }
                    })
                    .Where(c => c != null)
                    .Select(c => c!)
                    .OrderByDescending(c => c.Timestamp)
                    .ToList();

                Conversations = new ObservableCollection<Conversation>(conversations);
                
                // Don't log to events.jsonl - could trigger watchers in other ViewModels
            }
            catch (Exception ex)
            {
                ErrorViewModel.Instance.LogError("ConversationsViewModel", 
                    "Error loading conversations", ex);
                Conversations = new ObservableCollection<Conversation>();
            }
        }

        public void Dispose()
        {
            if (_conversationWatcher != null)
            {
                _conversationWatcher.EnableRaisingEvents = false;
                _conversationWatcher.Dispose();
            }
        }
    }
}
