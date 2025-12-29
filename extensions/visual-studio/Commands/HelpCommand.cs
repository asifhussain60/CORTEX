using System;
using System.ComponentModel.Design;
using System.Text;
using Microsoft.VisualStudio.Shell;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Command handler for CORTEX Help operations.
    /// </summary>
    internal sealed class HelpCommand : CortexCommandBase
    {
        /// <summary>
        /// Command ID.
        /// </summary>
        public const int HelpCommandId = 0x0700;

        /// <summary>
        /// Command menu group (command set GUID).
        /// </summary>
        public static readonly Guid CommandSet = new Guid("8b4f7b7d-2345-6789-abcd-ef0123456789");

        /// <summary>
        /// VS Package that provides this command, not null.
        /// </summary>
        private static AsyncPackage _package;

        /// <summary>
        /// Initializes a new instance of the <see cref="HelpCommand"/> class.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        /// <param name="commandService">Command service to add command to, not null.</param>
        private HelpCommand(AsyncPackage package, OleMenuCommandService commandService)
            : base(package)
        {
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, HelpCommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        /// <summary>
        /// Gets the instance of the command.
        /// </summary>
        public static HelpCommand Instance { get; private set; }

        /// <summary>
        /// Initializes the singleton instance of the command.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            _package = package;
            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new HelpCommand(package, commandService);
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
        /// Executes the Help command.
        /// </summary>
        protected override async Task ExecuteAsync()
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            // Get workspace info
            var workspaceInfo = WorkspaceService.GetWorkspaceInfo();

            // Build help message
            var helpMessage = new StringBuilder();
            helpMessage.AppendLine("🧠 CORTEX AI Assistant v4.0");
            helpMessage.AppendLine();
            helpMessage.AppendLine("AI Assistant with long-term memory, context awareness, and strategic planning.");
            helpMessage.AppendLine();
            helpMessage.AppendLine("WORKSPACE INFO:");
            helpMessage.AppendLine($"  CORTEX Path: {workspaceInfo.CortexPath ?? "Not found"}");
            helpMessage.AppendLine($"  User Workspace: {workspaceInfo.UserWorkspacePath ?? "N/A"}");
            helpMessage.AppendLine($"  Context: {(workspaceInfo.IsInCortexContext ? "CORTEX Repository" : "User Workspace")}");
            helpMessage.AppendLine();
            helpMessage.AppendLine("AVAILABLE COMMANDS:");
            helpMessage.AppendLine();
            helpMessage.AppendLine("📋 Planning System");
            helpMessage.AppendLine("  Create Plan - Start planning workflow with TDD integration");
            helpMessage.AppendLine();
            helpMessage.AppendLine("🧪 TDD Workflows");
            helpMessage.AppendLine("  Start TDD Workflow - Begin RED→GREEN→REFACTOR cycle");
            helpMessage.AppendLine();
            helpMessage.AppendLine("🔧 System Maintenance");
            helpMessage.AppendLine("  System Maintenance - Run 7-phase health pipeline");
            helpMessage.AppendLine();
            helpMessage.AppendLine("📊 Azure DevOps");
            helpMessage.AppendLine("  Create ADO Story - Create work items with DoR/DoD gates");
            helpMessage.AppendLine();
            helpMessage.AppendLine("🧹 Code Sanitization");
            helpMessage.AppendLine("  Sanitize Code - Remove sensitive data and company info");
            helpMessage.AppendLine();
            helpMessage.AppendLine("✨ System Refinement");
            helpMessage.AppendLine("  Refine System - 7-phase improvement process");
            helpMessage.AppendLine();
            helpMessage.AppendLine("🖥️ Tool Windows");
            helpMessage.AppendLine("  CORTEX Dashboard - System status and quick actions");
            helpMessage.AppendLine("  Planning Viewer - Interactive plan visualization");
            helpMessage.AppendLine();
            helpMessage.AppendLine("RESOURCES:");
            helpMessage.AppendLine("  Website: https://asifhussain60.github.io/CORTEX/");
            helpMessage.AppendLine("  Repository: https://github.com/asifhussain60/CORTEX");
            helpMessage.AppendLine("  Documentation: https://asifhussain60.github.io/CORTEX/docs/");
            helpMessage.AppendLine();
            helpMessage.AppendLine("For detailed help, check the Output window or visit the website.");

            // Write to output window
            await WriteOutputAsync("=== CORTEX HELP ===");
            await WriteOutputAsync(helpMessage.ToString());

            // Show help dialog
            await ShowMessageAsync(helpMessage.ToString(), "CORTEX Help");
        }
    }
}
