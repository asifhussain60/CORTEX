using System;
using System.Windows;
using System.Windows.Controls;
using CortexVSExtension.Services;
using Microsoft.VisualStudio.Shell;

namespace CortexVSExtension.ToolWindows
{
    /// <summary>
    /// Interaction logic for CortexDashboardControl.xaml
    /// </summary>
    public partial class CortexDashboardControl : UserControl
    {
        private readonly WorkspaceDetectionService _workspaceService;

        public CortexDashboardControl()
        {
            InitializeComponent();
            
            // Initialize workspace service
            var package = CortexVSExtensionPackage.Instance;
            if (package != null)
            {
                _workspaceService = new WorkspaceDetectionService(package);
            }
        }

        private void UserControl_Loaded(object sender, RoutedEventArgs e)
        {
            LoadWorkspaceInfo();
        }

        private void LoadWorkspaceInfo()
        {
            try
            {
                ThreadHelper.ThrowIfNotOnUIThread();

                if (_workspaceService == null)
                {
                    ContextText.Text = "Service unavailable";
                    return;
                }

                var workspaceInfo = _workspaceService.GetWorkspaceInfo();

                ContextText.Text = workspaceInfo.IsInCortexContext 
                    ? "CORTEX Repository" 
                    : "User Workspace";

                CortexPathText.Text = workspaceInfo.CortexPath ?? "Not found";
                WorkspacePathText.Text = workspaceInfo.UserWorkspacePath ?? "N/A";

                // Add activity entry
                AddActivity($"Dashboard loaded - Context: {ContextText.Text}");
            }
            catch (Exception ex)
            {
                ContextText.Text = $"Error: {ex.Message}";
            }
        }

        private void CreatePlanButton_Click(object sender, RoutedEventArgs e)
        {
            AddActivity("Create Plan command triggered");
            // Command will be executed through VS command system
        }

        private void StartTddButton_Click(object sender, RoutedEventArgs e)
        {
            AddActivity("Start TDD command triggered");
            // Command will be executed through VS command system
        }

        private void MaintenanceButton_Click(object sender, RoutedEventArgs e)
        {
            AddActivity("System Maintenance command triggered");
            // Command will be executed through VS command system
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            AddActivity("Refreshing dashboard...");
            LoadWorkspaceInfo();
        }

        private void AddActivity(string message)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var activityText = new TextBlock
            {
                Text = $"[{timestamp}] {message}",
                Margin = new Thickness(0, 2, 0, 2)
            };
            activityText.SetResourceReference(TextBlock.ForegroundProperty, "VsBrush.WindowText");

            // Remove "No recent activity" message if it exists
            if (ActivityPanel.Children.Count == 1 && 
                ActivityPanel.Children[0] is TextBlock tb && 
                tb.Text == "No recent activity")
            {
                ActivityPanel.Children.Clear();
            }

            ActivityPanel.Children.Insert(0, activityText);

            // Keep only last 20 activities
            while (ActivityPanel.Children.Count > 20)
            {
                ActivityPanel.Children.RemoveAt(ActivityPanel.Children.Count - 1);
            }
        }
    }
}
