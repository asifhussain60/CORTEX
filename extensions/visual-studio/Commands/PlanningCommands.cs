using System;
using System.ComponentModel.Design;
using Microsoft.VisualStudio.Shell;
using CortexVSExtension.Services;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Command handler for CORTEX Planning System operations.
    /// </summary>
    internal sealed class PlanningCommands : CortexCommandBase
    {
        /// <summary>
        /// Command ID.
        /// </summary>
        public const int CreatePlanCommandId = 0x0100;

        /// <summary>
        /// Command menu group (command set GUID).
        /// </summary>
        public static readonly Guid CommandSet = new Guid("8b4f7b7d-2345-6789-abcd-ef0123456789");

        /// <summary>
        /// VS Package that provides this command, not null.
        /// </summary>
        private static AsyncPackage _package;

        /// <summary>
        /// Initializes a new instance of the <see cref="PlanningCommands"/> class.
        /// Adds our command handlers for menu (commands must exist in the command table file)
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        /// <param name="commandService">Command service to add command to, not null.</param>
        private PlanningCommands(AsyncPackage package, OleMenuCommandService commandService)
            : base(package)
        {
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, CreatePlanCommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        /// <summary>
        /// Gets the instance of the command.
        /// </summary>
        public static PlanningCommands Instance { get; private set; }

        /// <summary>
        /// Initializes the singleton instance of the command.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            // Switch to the main thread - the call to AddCommand in PlanningCommands's constructor requires
            // the UI thread.
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            _package = package;
            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new PlanningCommands(package, commandService);
        }

        /// <summary>
        /// This function is the callback used to execute the command when the menu item is clicked.
        /// See the constructor to see how the menu item is associated with this function using
        /// OleMenuCommandService service and MenuCommand class.
        /// </summary>
        /// <param name="sender">Event sender.</param>
        /// <param name="e">Event args.</param>
        private void Execute(object sender, EventArgs e)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            _ = ExecuteCommandAsync();
        }

        /// <summary>
        /// Executes the Create Plan command.
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

            // Get plan name from user
            var planName = await GetUserInputAsync(
                "Enter the plan name (e.g., user-authentication, payment-integration):",
                "Create CORTEX Plan",
                "my-feature-plan");

            if (string.IsNullOrWhiteSpace(planName))
            {
                await ShowErrorAsync("Plan name cannot be empty.");
                return;
            }

            // Show progress message
            await WriteOutputAsync($"Creating CORTEX plan: {planName}");
            await WriteOutputAsync($"CORTEX Path: {workspaceInfo.CortexPath}");
            await WriteOutputAsync($"Workspace: {workspaceInfo.UserWorkspacePath ?? workspaceInfo.CortexPath}");

            // Execute CORTEX plan command
            var result = await PythonExecutor.ExecuteCommandAsync("plan", new[] { planName });

            if (result.Success)
            {
                await WriteOutputAsync($"✅ Plan created successfully!");
                await WriteOutputAsync(result.Output);
                
                await ShowMessageAsync(
                    $"CORTEX plan '{planName}' created successfully!\n\n" +
                    $"Location: cortex-brain/documents/planning/active/{planName}/\n\n" +
                    "Check the Output window for details.",
                    "Plan Created");
            }
            else
            {
                await WriteOutputAsync($"❌ Plan creation failed: {result.ErrorMessage}");
                await ShowErrorAsync($"Failed to create plan:\n\n{result.ErrorMessage}");
            }
        }
    }
}
