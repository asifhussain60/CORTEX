using System;
using System.ComponentModel.Design;
using Microsoft.VisualStudio.Shell;
using CortexVSExtension.Services;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Command handler for CORTEX System Refinement operations.
    /// </summary>
    internal sealed class RefinementCommands : CortexCommandBase
    {
        /// <summary>
        /// Command ID.
        /// </summary>
        public const int RefineSystemCommandId = 0x0600;

        /// <summary>
        /// Command menu group (command set GUID).
        /// </summary>
        public static readonly Guid CommandSet = new Guid("8b4f7b7d-2345-6789-abcd-ef0123456789");

        /// <summary>
        /// VS Package that provides this command, not null.
        /// </summary>
        private static AsyncPackage _package;

        /// <summary>
        /// Initializes a new instance of the <see cref="RefinementCommands"/> class.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        /// <param name="commandService">Command service to add command to, not null.</param>
        private RefinementCommands(AsyncPackage package, OleMenuCommandService commandService)
            : base(package)
        {
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, RefineSystemCommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        /// <summary>
        /// Gets the instance of the command.
        /// </summary>
        public static RefinementCommands Instance { get; private set; }

        /// <summary>
        /// Initializes the singleton instance of the command.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            _package = package;
            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new RefinementCommands(package, commandService);
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
        /// Executes the Refine System command.
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

            // Confirm refinement start
            var confirmed = await ShowConfirmationAsync(
                "Start CORTEX System Refinement?\n\n" +
                "This will run the 7-phase improvement process:\n" +
                "1. Discovery & Analysis\n" +
                "2. Architecture Review\n" +
                "3. Code Quality Analysis\n" +
                "4. SOLID Principles Enforcement\n" +
                "5. Performance Optimization\n" +
                "6. Test Coverage Improvement\n" +
                "7. Documentation Enhancement\n\n" +
                "This may take 10-15 minutes. Continue?",
                "System Refinement");

            if (!confirmed)
            {
                return;
            }

            // Show progress message
            await WriteOutputAsync("Starting CORTEX system refinement...");
            await WriteOutputAsync($"Workspace: {workspaceInfo.UserWorkspacePath ?? workspaceInfo.CortexPath}");
            await WriteOutputAsync("Running 7-phase improvement process...");
            await WriteOutputAsync("This may take 10-15 minutes. Please wait...");

            // Execute CORTEX refinement command
            var result = await PythonExecutor.ExecuteCommandAsync("refine");

            if (result.Success)
            {
                await WriteOutputAsync("✅ System refinement completed successfully!");
                await WriteOutputAsync(result.Output);
                
                await ShowMessageAsync(
                    "CORTEX system refinement completed!\n\n" +
                    "Improvements applied:\n" +
                    "- Architecture patterns\n" +
                    "- Code quality\n" +
                    "- SOLID principles\n" +
                    "- Performance\n" +
                    "- Test coverage\n" +
                    "- Documentation\n\n" +
                    "Refinement report saved to:\n" +
                    "cortex-brain/documents/reports/\n\n" +
                    "Check the Output window for details.",
                    "Refinement Complete");
            }
            else
            {
                await WriteOutputAsync($"❌ System refinement failed: {result.ErrorMessage}");
                await ShowErrorAsync($"System refinement failed:\n\n{result.ErrorMessage}");
            }
        }
    }
}
