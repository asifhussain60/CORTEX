using System;
using System.ComponentModel.Design;
using Microsoft.VisualStudio.Shell;
using CortexVSExtension.Services;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Command handler for CORTEX TDD Workflows.
    /// </summary>
    internal sealed class TddCommands : CortexCommandBase
    {
        /// <summary>
        /// Command ID.
        /// </summary>
        public const int StartTddCommandId = 0x0200;

        /// <summary>
        /// Command menu group (command set GUID).
        /// </summary>
        public static readonly Guid CommandSet = new Guid("8b4f7b7d-2345-6789-abcd-ef0123456789");

        /// <summary>
        /// VS Package that provides this command, not null.
        /// </summary>
        private static AsyncPackage _package;

        /// <summary>
        /// Initializes a new instance of the <see cref="TddCommands"/> class.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        /// <param name="commandService">Command service to add command to, not null.</param>
        private TddCommands(AsyncPackage package, OleMenuCommandService commandService)
            : base(package)
        {
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, StartTddCommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        /// <summary>
        /// Gets the instance of the command.
        /// </summary>
        public static TddCommands Instance { get; private set; }

        /// <summary>
        /// Initializes the singleton instance of the command.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            _package = package;
            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new TddCommands(package, commandService);
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
        /// Executes the Start TDD Workflow command.
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

            // Confirm TDD workflow start
            var confirmed = await ShowConfirmationAsync(
                "Start CORTEX TDD Workflow?\n\n" +
                "This will begin the RED→GREEN→REFACTOR cycle:\n" +
                "1. RED: Write failing tests\n" +
                "2. GREEN: Implement minimal code to pass\n" +
                "3. REFACTOR: Improve code quality\n\n" +
                "Continue?",
                "Start TDD Workflow");

            if (!confirmed)
            {
                return;
            }

            // Show progress message
            await WriteOutputAsync("Starting CORTEX TDD workflow...");
            await WriteOutputAsync($"Workspace: {workspaceInfo.UserWorkspacePath ?? workspaceInfo.CortexPath}");

            // Execute CORTEX TDD command
            var result = await PythonExecutor.ExecuteCommandAsync("start tdd");

            if (result.Success)
            {
                await WriteOutputAsync("✅ TDD workflow started successfully!");
                await WriteOutputAsync(result.Output);
                
                await ShowMessageAsync(
                    "CORTEX TDD workflow started!\n\n" +
                    "Follow the RED→GREEN→REFACTOR cycle in the Output window.\n\n" +
                    "Check the Output window for details.",
                    "TDD Started");
            }
            else
            {
                await WriteOutputAsync($"❌ TDD workflow failed: {result.ErrorMessage}");
                await ShowErrorAsync($"Failed to start TDD workflow:\n\n{result.ErrorMessage}");
            }
        }
    }
}
