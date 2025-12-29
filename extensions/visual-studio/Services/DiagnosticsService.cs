using System;
using System.Diagnostics;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;

namespace CortexVSExtension.Services
{
    /// <summary>
    /// Service for logging diagnostics and errors to the Output window.
    /// </summary>
    public class DiagnosticsService
    {
        private readonly IServiceProvider _serviceProvider;
        private IVsOutputWindowPane _outputPane;
        private readonly Guid _paneGuid = new Guid("8A3F6A6C-1234-5678-9ABC-DEF012345679");

        public DiagnosticsService(IServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
            InitializeOutputPane();
        }

        /// <summary>
        /// Initializes the CORTEX output pane.
        /// </summary>
        private void InitializeOutputPane()
        {
            try
            {
                ThreadHelper.ThrowIfNotOnUIThread();

                var outputWindow = _serviceProvider.GetService(typeof(SVsOutputWindow)) as IVsOutputWindow;
                if (outputWindow != null)
                {
                    outputWindow.GetPane(ref _paneGuid, out _outputPane);

                    if (_outputPane == null)
                    {
                        outputWindow.CreatePane(ref _paneGuid, "CORTEX Diagnostics", 1, 1);
                        outputWindow.GetPane(ref _paneGuid, out _outputPane);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Failed to initialize output pane: {ex.Message}");
            }
        }

        /// <summary>
        /// Logs an information message.
        /// </summary>
        public void LogInfo(string message)
        {
            Log($"[INFO] {message}");
        }

        /// <summary>
        /// Logs a warning message.
        /// </summary>
        public void LogWarning(string message)
        {
            Log($"[WARN] {message}");
        }

        /// <summary>
        /// Logs an error message.
        /// </summary>
        public void LogError(string message, Exception exception = null)
        {
            var errorMessage = exception != null
                ? $"[ERROR] {message}: {exception.Message}\n{exception.StackTrace}"
                : $"[ERROR] {message}";
            Log(errorMessage);
        }

        /// <summary>
        /// Logs a debug message (only in DEBUG builds).
        /// </summary>
        [Conditional("DEBUG")]
        public void LogDebug(string message)
        {
            Log($"[DEBUG] {message}");
            Debug.WriteLine($"CORTEX: {message}");
        }

        /// <summary>
        /// Logs a command execution.
        /// </summary>
        public void LogCommand(string commandName, string[] args = null)
        {
            var argsStr = args != null && args.Length > 0
                ? $" [{string.Join(", ", args)}]"
                : "";
            Log($"[CMD] Executing: {commandName}{argsStr}");
        }

        /// <summary>
        /// Logs a command result.
        /// </summary>
        public void LogCommandResult(string commandName, bool success, string message = null)
        {
            var status = success ? "SUCCESS" : "FAILED";
            var msg = message != null ? $": {message}" : "";
            Log($"[CMD] {commandName} - {status}{msg}");
        }

        /// <summary>
        /// Logs workspace detection.
        /// </summary>
        public void LogWorkspaceDetection(string cortexPath, string userWorkspace, bool isInCortexContext)
        {
            Log($"[WORKSPACE] Detected:");
            Log($"  CORTEX Path: {cortexPath ?? "Not found"}");
            Log($"  User Workspace: {userWorkspace ?? "N/A"}");
            Log($"  Context: {(isInCortexContext ? "CORTEX Repository" : "User Workspace")}");
        }

        /// <summary>
        /// Logs a separator line.
        /// </summary>
        public void LogSeparator()
        {
            Log("────────────────────────────────────────────────────────────────");
        }

        /// <summary>
        /// Writes a message to the output pane.
        /// </summary>
        private void Log(string message)
        {
            try
            {
                ThreadHelper.ThrowIfNotOnUIThread();

                var timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
                var formattedMessage = $"[{timestamp}] {message}\n";

                _outputPane?.OutputString(formattedMessage);
                _outputPane?.Activate(); // Bring output window to front on errors
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Failed to log message: {ex.Message}");
            }
        }

        /// <summary>
        /// Clears the output pane.
        /// </summary>
        public void Clear()
        {
            try
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                _outputPane?.Clear();
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Failed to clear output pane: {ex.Message}");
            }
        }
    }
}
