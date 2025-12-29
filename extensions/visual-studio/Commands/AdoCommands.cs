using System;
using System.ComponentModel.Design;
using Microsoft.VisualStudio.Shell;
using CortexVSExtension.Services;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Command handler for CORTEX Azure DevOps operations.
    /// </summary>
    internal sealed class AdoCommands : CortexCommandBase
    {
        /// <summary>
        /// Command ID.
        /// </summary>
        public const int CreateAdoStoryCommandId = 0x0400;

        /// <summary>
        /// Command menu group (command set GUID).
        /// </summary>
        public static readonly Guid CommandSet = new Guid("8b4f7b7d-2345-6789-abcd-ef0123456789");

        /// <summary>
        /// VS Package that provides this command, not null.
        /// </summary>
        private static AsyncPackage _package;

        /// <summary>
        /// Initializes a new instance of the <see cref="AdoCommands"/> class.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        /// <param name="commandService">Command service to add command to, not null.</param>
        private AdoCommands(AsyncPackage package, OleMenuCommandService commandService)
            : base(package)
        {
            commandService = commandService ?? throw new ArgumentNullException(nameof(commandService));

            var menuCommandID = new CommandID(CommandSet, CreateAdoStoryCommandId);
            var menuItem = new MenuCommand(this.Execute, menuCommandID);
            commandService.AddCommand(menuItem);
        }

        /// <summary>
        /// Gets the instance of the command.
        /// </summary>
        public static AdoCommands Instance { get; private set; }

        /// <summary>
        /// Initializes the singleton instance of the command.
        /// </summary>
        /// <param name="package">Owner package, not null.</param>
        public static async Task InitializeAsync(AsyncPackage package)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            _package = package;
            OleMenuCommandService commandService = await package.GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            Instance = new AdoCommands(package, commandService);
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
        /// Executes the Create ADO Story command.
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

            // Get story title from user
            var storyTitle = await GetUserInputAsync(
                "Enter the Azure DevOps story title:",
                "Create ADO Story",
                "Implement user authentication");

            if (string.IsNullOrWhiteSpace(storyTitle))
            {
                await ShowErrorAsync("Story title cannot be empty.");
                return;
            }

            // Show progress message
            await WriteOutputAsync($"Creating Azure DevOps story: {storyTitle}");
            await WriteOutputAsync($"Workspace: {workspaceInfo.UserWorkspacePath ?? workspaceInfo.CortexPath}");

            // Execute CORTEX ADO command
            var result = await PythonExecutor.ExecuteCommandAsync("ado story", new[] { storyTitle });

            if (result.Success)
            {
                await WriteOutputAsync("✅ ADO story created successfully!");
                await WriteOutputAsync(result.Output);
                
                await ShowMessageAsync(
                    $"Azure DevOps story created successfully!\n\n" +
                    $"Title: {storyTitle}\n\n" +
                    "Story includes:\n" +
                    "- DoR/DoD quality gates\n" +
                    "- Acceptance criteria\n" +
                    "- Task breakdown\n\n" +
                    "Check the Output window for details.",
                    "ADO Story Created");
            }
            else
            {
                await WriteOutputAsync($"❌ ADO story creation failed: {result.ErrorMessage}");
                await ShowErrorAsync($"Failed to create ADO story:\n\n{result.ErrorMessage}");
            }
        }
    }
}
