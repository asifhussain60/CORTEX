using System;
using System.ComponentModel.Design;
using Microsoft.VisualStudio.Shell;
using CortexVSExtension.Services;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Command handler for CORTEX Code Sanitization operations.
    /// </summary>
    internal sealed class SanitizationCommands : CortexCommandBase
    {
        /// <summary>
        /// Command ID.
        /// </summary>
        public const int SanitizeCodeCommandId = 0x0500;

        /// <summary>
        /// Command menu group (command set GUID).
        /// </summary>
        public static readonly Guid CommandSet = new Guid("8b4f7b7d-2345-6789-abcd-ef0123456789");

        /// <summary>
        /// VS Package that provides this command, not null.
        /// </summary>
        private static AsyncPackage _package;

        /// <summary>
        /// Initializes a new instance of the <see cref="SanitizationCommands"/> class.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        /// <param name="commandService">Command service to add command to, not null.</param>
        private SanitizationCommands(AsyncPackage package, OleMenuCommandService commandService)
            : base(package)
        {
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, SanitizeCodeCommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        /// <summary>
        /// Gets the instance of the command.
        /// </summary>
        public static SanitizationCommands Instance { get; private set; }

        /// <summary>
        /// Initializes the singleton instance of the command.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            _package = package;
            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new SanitizationCommands(package, commandService);
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
        /// Executes the Sanitize Code command.
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

            // Confirm sanitization
            var confirmed = await ShowConfirmationAsync(
                "Start CORTEX Code Sanitization?\n\n" +
                "This will remove:\n" +
                "- Hardcoded secrets and credentials\n" +
                "- Company-specific information\n" +
                "- Personal data and PII\n" +
                "- Internal URLs and endpoints\n" +
                "- Comments with sensitive context\n\n" +
                "A backup will be created before sanitization.\n\n" +
                "Continue?",
                "Sanitize Code");

            if (!confirmed)
            {
                return;
            }

            // Get target directory
            var targetDir = await GetUserInputAsync(
                "Enter the directory to sanitize (relative to workspace root):",
                "Sanitize Code",
                "src");

            // Show progress message
            await WriteOutputAsync("Starting CORTEX code sanitization...");
            await WriteOutputAsync($"Workspace: {workspaceInfo.UserWorkspacePath ?? workspaceInfo.CortexPath}");
            await WriteOutputAsync($"Target: {targetDir}");
            await WriteOutputAsync("Creating backup and sanitizing...");

            // Execute CORTEX sanitization command
            var result = await PythonExecutor.ExecuteCommandAsync("sanitize", new[] { targetDir });

            if (result.Success)
            {
                await WriteOutputAsync("✅ Code sanitization completed successfully!");
                await WriteOutputAsync(result.Output);
                
                await ShowMessageAsync(
                    "Code sanitization completed!\n\n" +
                    "Changes:\n" +
                    "- Sensitive data removed\n" +
                    "- Generic placeholders added\n" +
                    "- Backup created\n\n" +
                    "Review the changes before committing.\n\n" +
                    "Check the Output window for details.",
                    "Sanitization Complete");
            }
            else
            {
                await WriteOutputAsync($"❌ Code sanitization failed: {result.ErrorMessage}");
                await ShowErrorAsync($"Code sanitization failed:\n\n{result.ErrorMessage}");
            }
        }
    }
}
