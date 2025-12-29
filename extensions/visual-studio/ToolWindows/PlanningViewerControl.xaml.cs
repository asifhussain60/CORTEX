using System;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using CortexVSExtension.Services;
using Microsoft.VisualStudio.Shell;

namespace CortexVSExtension.ToolWindows
{
    /// <summary>
    /// Interaction logic for PlanningViewerControl.xaml
    /// </summary>
    public partial class PlanningViewerControl : UserControl
    {
        private readonly WorkspaceDetectionService _workspaceService;

        public PlanningViewerControl()
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
            LoadPlans();
        }

        private void LoadPlans()
        {
            try
            {
                ThreadHelper.ThrowIfNotOnUIThread();

                PlansTreeView.Items.Clear();

                if (_workspaceService == null)
                {
                    AddEmptyMessage("Workspace service unavailable");
                    return;
                }

                var cortexPath = _workspaceService.GetCortexPath();
                if (string.IsNullOrEmpty(cortexPath))
                {
                    AddEmptyMessage("CORTEX installation not found");
                    return;
                }

                var planningPath = Path.Combine(cortexPath, "cortex-brain", "documents", "planning", "active");
                if (!Directory.Exists(planningPath))
                {
                    AddEmptyMessage("No planning directory found");
                    return;
                }

                var planDirectories = Directory.GetDirectories(planningPath);
                if (planDirectories.Length == 0)
                {
                    AddEmptyMessage("No active plans found");
                    PlanCountText.Text = "0 plans";
                    return;
                }

                // Load each plan
                foreach (var planDir in planDirectories.OrderByDescending(d => Directory.GetLastWriteTime(d)))
                {
                    var planName = Path.GetFileName(planDir);
                    var planNode = new TreeViewItem
                    {
                        Header = $"📋 {planName}",
                        Tag = planDir
                    };

                    // Add plan subfolders
                    AddPlanSubfolders(planNode, planDir);

                    PlansTreeView.Items.Add(planNode);
                }

                PlanCountText.Text = $"{planDirectories.Length} plan{(planDirectories.Length == 1 ? "" : "s")}";
            }
            catch (Exception ex)
            {
                AddEmptyMessage($"Error loading plans: {ex.Message}");
            }
        }

        private void AddPlanSubfolders(TreeViewItem parentNode, string planPath)
        {
            try
            {
                // Add master plan file
                var masterPlanPath = Path.Combine(planPath, "00-master-plan.md");
                if (File.Exists(masterPlanPath))
                {
                    var masterPlanNode = new TreeViewItem
                    {
                        Header = "📄 Master Plan",
                        Tag = masterPlanPath
                    };
                    parentNode.Items.Add(masterPlanNode);
                }

                // Add subfolders
                var subfolders = new[] { "context", "reports", "artifacts", "tracking" };
                foreach (var subfolder in subfolders)
                {
                    var subfolderPath = Path.Combine(planPath, subfolder);
                    if (Directory.Exists(subfolderPath))
                    {
                        var icon = subfolder switch
                        {
                            "context" => "📁",
                            "reports" => "📊",
                            "artifacts" => "📦",
                            "tracking" => "📈",
                            _ => "📁"
                        };

                        var fileCount = Directory.GetFiles(subfolderPath, "*", SearchOption.AllDirectories).Length;
                        var folderNode = new TreeViewItem
                        {
                            Header = $"{icon} {subfolder} ({fileCount} files)",
                            Tag = subfolderPath
                        };
                        parentNode.Items.Add(folderNode);
                    }
                }
            }
            catch
            {
                // Ignore errors loading subfolders
            }
        }

        private void AddEmptyMessage(string message)
        {
            var emptyNode = new TreeViewItem
            {
                Header = message,
                IsEnabled = false
            };
            PlansTreeView.Items.Add(emptyNode);
        }

        private void RefreshPlansButton_Click(object sender, RoutedEventArgs e)
        {
            LoadPlans();
        }

        private void CreateNewPlanButton_Click(object sender, RoutedEventArgs e)
        {
            // This will trigger the Create Plan command through VS command system
            MessageBox.Show(
                "Use 'Tools → CORTEX → Create Plan' to create a new plan.",
                "Create Plan",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }

        private void PlansTreeView_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
        {
            if (PlansTreeView.SelectedItem is TreeViewItem selectedItem && selectedItem.Tag is string path)
            {
                // Could open the file or folder in VS here
                // For now, just show a message
                if (File.Exists(path))
                {
                    // File selected - could open in editor
                }
                else if (Directory.Exists(path))
                {
                    // Directory selected - could show in solution explorer
                }
            }
        }
    }
}
