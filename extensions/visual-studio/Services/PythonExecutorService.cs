using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace CortexVSExtension.Services
{
    /// <summary>
    /// Service for executing Python scripts and CORTEX commands.
    /// Handles Python environment detection and command execution.
    /// </summary>
    public class PythonExecutorService
    {
        private readonly WorkspaceDetectionService _workspaceService;
        private string _cachedPythonPath;

        public PythonExecutorService(WorkspaceDetectionService workspaceService)
        {
            _workspaceService = workspaceService ?? throw new ArgumentNullException(nameof(workspaceService));
        }

        /// <summary>
        /// Executes a CORTEX command asynchronously.
        /// </summary>
        public async Task<ExecutionResult> ExecuteCommandAsync(string command, string[] args = null)
        {
            var cortexPath = _workspaceService.GetCortexPath();
            if (string.IsNullOrEmpty(cortexPath))
            {
                return new ExecutionResult
                {
                    Success = false,
                    ErrorMessage = "CORTEX installation not found. Please set CORTEX_HOME environment variable or open a solution near CORTEX."
                };
            }

            var pythonPath = await GetPythonPathAsync();
            if (string.IsNullOrEmpty(pythonPath))
            {
                return new ExecutionResult
                {
                    Success = false,
                    ErrorMessage = "Python interpreter not found. Please install Python 3.8+ and ensure it's in PATH."
                };
            }

            // Build command line
            var scriptPath = Path.Combine(cortexPath, "src", "main.py");
            var arguments = new StringBuilder();
            arguments.Append($"\"{scriptPath}\" {command}");

            if (args != null && args.Length > 0)
            {
                foreach (var arg in args)
                {
                    arguments.Append($" \"{arg}\"");
                }
            }

            // Execute command
            return await ExecutePythonScriptAsync(pythonPath, arguments.ToString(), cortexPath);
        }

        /// <summary>
        /// Executes a Python script directly.
        /// </summary>
        public async Task<ExecutionResult> ExecutePythonScriptAsync(string pythonPath, string arguments, string workingDirectory = null)
        {
            var result = new ExecutionResult();
            var outputBuilder = new StringBuilder();
            var errorBuilder = new StringBuilder();

            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = arguments,
                    WorkingDirectory = workingDirectory ?? Environment.CurrentDirectory,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = new Process { StartInfo = startInfo })
                {
                    process.OutputDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            outputBuilder.AppendLine(e.Data);
                        }
                    };

                    process.ErrorDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            errorBuilder.AppendLine(e.Data);
                        }
                    };

                    process.Start();
                    process.BeginOutputReadLine();
                    process.BeginErrorReadLine();

                    await Task.Run(() => process.WaitForExit());

                    result.ExitCode = process.ExitCode;
                    result.Output = outputBuilder.ToString();
                    result.ErrorMessage = errorBuilder.ToString();
                    result.Success = process.ExitCode == 0;
                }
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.ErrorMessage = $"Failed to execute Python script: {ex.Message}";
            }

            return result;
        }

        /// <summary>
        /// Gets the Python interpreter path.
        /// Searches in: python3, python, conda, venv.
        /// </summary>
        private async Task<string> GetPythonPathAsync()
        {
            if (!string.IsNullOrEmpty(_cachedPythonPath))
            {
                return _cachedPythonPath;
            }

            // Try common Python commands
            var pythonCommands = new[] { "python3", "python", "py" };

            foreach (var cmd in pythonCommands)
            {
                var result = await TestPythonCommandAsync(cmd);
                if (result)
                {
                    _cachedPythonPath = cmd;
                    return _cachedPythonPath;
                }
            }

            // Check CORTEX venv
            var cortexPath = _workspaceService.GetCortexPath();
            if (!string.IsNullOrEmpty(cortexPath))
            {
                var venvPath = Path.Combine(cortexPath, "venv", "Scripts", "python.exe");
                if (File.Exists(venvPath))
                {
                    _cachedPythonPath = venvPath;
                    return _cachedPythonPath;
                }
            }

            return null;
        }

        private async Task<bool> TestPythonCommandAsync(string command)
        {
            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = command,
                    Arguments = "--version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(startInfo))
                {
                    await Task.Run(() => process.WaitForExit(3000));
                    return process.ExitCode == 0;
                }
            }
            catch
            {
                return false;
            }
        }
    }

    /// <summary>
    /// Result of Python command execution.
    /// </summary>
    public class ExecutionResult
    {
        public bool Success { get; set; }
        public int ExitCode { get; set; }
        public string Output { get; set; }
        public string ErrorMessage { get; set; }
    }
}
