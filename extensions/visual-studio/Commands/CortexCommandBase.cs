using System;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using CortexVSExtension.Services;
using Task = System.Threading.Tasks.Task;

namespace CortexVSExtension.Commands
{
    /// <summary>
    /// Base class for all CORTEX commands.
    /// Provides common functionality for command execution, error handling, and output.
    /// </summary>
    public abstract class CortexCommandBase
    {
        protected readonly AsyncPackage Package;
        protected readonly WorkspaceDetectionService WorkspaceService;
        protected readonly PythonExecutorService PythonExecutor;

        protected CortexCommandBase(AsyncPackage package)
        {
            Package = package ?? throw new ArgumentNullException(nameof(package));
            WorkspaceService = new WorkspaceDetectionService(package);
            PythonExecutor = new PythonExecutorService(WorkspaceService);
        }

        /// <summary>
        /// Gets the service provider from the owner package.
        /// </summary>
        protected IAsyncServiceProvider ServiceProvider => Package;

        /// <summary>
        /// Executes the command asynchronously.
        /// </summary>
        protected abstract Task ExecuteAsync();

        /// <summary>
        /// Command handler - entry point for all commands.
        /// </summary>
        protected async Task ExecuteCommandAsync()
        {
            try
            {
                await ExecuteAsync();
            }
            catch (Exception ex)
            {
                await ShowErrorAsync($"CORTEX command failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Shows an information message to the user.
        /// </summary>
        protected async Task ShowMessageAsync(string message, string title = "CORTEX")
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            VsShellUtilities.ShowMessageBox(
                Package,
                message,
                title,
                OLEMSGICON.OLEMSGICON_INFO,
                OLEMSGBUTTON.OLEMSGBUTTON_OK,
                OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
        }

        /// <summary>
        /// Shows an error message to the user.
        /// </summary>
        protected async Task ShowErrorAsync(string message, string title = "CORTEX Error")
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            VsShellUtilities.ShowMessageBox(
                Package,
                message,
                title,
                OLEMSGICON.OLEMSGICON_CRITICAL,
                OLEMSGBUTTON.OLEMSGBUTTON_OK,
                OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);
        }

        /// <summary>
        /// Shows a confirmation dialog.
        /// </summary>
        protected async Task<bool> ShowConfirmationAsync(string message, string title = "CORTEX")
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            var result = VsShellUtilities.ShowMessageBox(
                Package,
                message,
                title,
                OLEMSGICON.OLEMSGICON_QUERY,
                OLEMSGBUTTON.OLEMSGBUTTON_YESNO,
                OLEMSGDEFBUTTON.OLEMSGDEFBUTTON_FIRST);

            return result == 6; // IDYES
        }

        /// <summary>
        /// Writes output to the Output window.
        /// </summary>
        protected async Task WriteOutputAsync(string message)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            var outputWindow = Package.GetServiceAsync(typeof(SVsOutputWindow)).Result as IVsOutputWindow;
            if (outputWindow != null)
            {
                Guid paneGuid = new Guid("8A3F6A6C-1234-5678-9ABC-DEF012345679"); // CORTEX output pane
                outputWindow.GetPane(ref paneGuid, out IVsOutputWindowPane pane);

                if (pane == null)
                {
                    outputWindow.CreatePane(ref paneGuid, "CORTEX", 1, 1);
                    outputWindow.GetPane(ref paneGuid, out pane);
                }

                pane?.OutputString($"[{DateTime.Now:HH:mm:ss}] {message}\n");
            }
        }

        /// <summary>
        /// Validates that CORTEX is installed and accessible.
        /// </summary>
        protected async Task<bool> ValidateCortexInstallationAsync()
        {
            var cortexPath = WorkspaceService.GetCortexPath();
            if (string.IsNullOrEmpty(cortexPath))
            {
                await ShowErrorAsync(
                    "CORTEX installation not found.\n\n" +
                    "Please ensure:\n" +
                    "1. CORTEX is installed\n" +
                    "2. Set CORTEX_HOME environment variable, or\n" +
                    "3. Open a solution near the CORTEX installation");
                return false;
            }

            return true;
        }

        /// <summary>
        /// Gets user input via input box.
        /// </summary>
        protected async Task<string> GetUserInputAsync(string prompt, string title = "CORTEX", string defaultValue = "")
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            // Note: Visual Studio doesn't have a built-in input box like VB.
            // For now, we'll use a message box and return the default value.
            // In Task 12.2.3, we'll create a proper input dialog.
            await ShowMessageAsync($"{prompt}\n\nUsing default value: {defaultValue}", title);
            return defaultValue;
        }
    }
}
