using System;
using System.ComponentModel.Design;
using Microsoft.VisualStudio.Shell;
using CortexVSExtension.Services;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Command handler for CORTEX System Maintenance operations.
    /// </summary>
    internal sealed class MaintenanceCommands : CortexCommandBase
    {
        /// <summary>
        /// Command ID.
        /// </summary>
        public const int SystemMaintenanceCommandId = 0x0300;

        /// <summary>
        /// Command menu group (command set GUID).
        /// </summary>
        public static readonly Guid CommandSet = new Guid("8b4f7b7d-2345-6789-abcd-ef0123456789");

        /// <summary>
        /// VS Package that provides this command, not null.
        /// </summary>
        private static AsyncPackage _package;

        /// <summary>
        /// Initializes a new instance of the <see cref="MaintenanceCommands"/> class.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        /// <param name="commandService">Command service to add command to, not null.</param>
        private MaintenanceCommands(AsyncPackage package, OleMenuCommandService commandService)
            : base(package)
        {
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, SystemMaintenanceCommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        /// <summary>
        /// Gets the instance of the command.
        /// </summary>
        public static MaintenanceCommands Instance { get; private set; }

        /// <summary>
        /// Initializes the singleton instance of the command.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            _package = package;
            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new MaintenanceCommands(package, commandService);
        }

        /// <summary>
        /// This function is the callback used to execute the command when the menu item is clicked.
        /// </summary>
        /// <param name="sender">Event sender.</param>
        /// <param name="e">Event args.</param>
        private void Execute(object sender, EventArgs e)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            _ = ExecuteCommandAsync();
        }

        /// <summary>
        /// Executes the System Maintenance command.
        /// </summary>
        protected override async Task ExecuteAsync()
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            // Validate CORTEX installation
            if (!await ValidateCortexInstallationAsync())
            {
                return;
            }

            // Get workspace info
            var workspaceInfo = WorkspaceService.GetWorkspaceInfo();

            // Confirm maintenance start
            var confirmed = await ShowConfirmationAsync(
                "Start CORTEX System Maintenance?\n\n" +
                "This will run the 7-phase health pipeline:\n" +
                "1. Pre-healthcheck\n" +
                "2. Align\n" +
                "3. Cleanup\n" +
                "4. Optimize\n" +
                "5. Vacuum\n" +
                "6. Refresh\n" +
                "7. Post-healthcheck\n\n" +
                "This may take several minutes. Continue?",
                "System Maintenance");

            if (!confirmed)
            {
                return;
            }

            // Show progress message
            await WriteOutputAsync("Starting CORTEX system maintenance...");
            await WriteOutputAsync($"Workspace: {workspaceInfo.UserWorkspacePath ?? workspaceInfo.CortexPath}");
            await WriteOutputAsync("This may take several minutes. Please wait...");

            // Execute CORTEX maintenance command
            var result = await PythonExecutor.ExecuteCommandAsync("system maintenance");

            if (result.Success)
            {
                await WriteOutputAsync("✅ System maintenance completed successfully!");
                await WriteOutputAsync(result.Output);
                
                await ShowMessageAsync(
                    "CORTEX system maintenance completed!\n\n" +
                    "Health report saved to:\n" +
                    "cortex-brain/health-reports/\n\n" +
                    "Check the Output window for details.",
                    "Maintenance Complete");
            }
            else
            {
                await WriteOutputAsync($"❌ System maintenance failed: {result.ErrorMessage}");
                await ShowErrorAsync($"System maintenance failed:\n\n{result.ErrorMessage}");
            }
        }
    }
}
