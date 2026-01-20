using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Serilog;

namespace CortexLSPAdapter
{
    /// <summary>
    /// Validates Python environment compatibility.
    /// Checks Python version and required packages.
    /// </summary>
    public class PythonEnvironmentValidator
    {
        private Version? _pythonVersion;
        private List<string> _missingPackages = new();

        public class ValidationResult
        {
            public bool IsValid { get; set; }
            public Version? PythonVersion { get; set; }
            public string? ErrorMessage { get; set; }
            public List<string> MissingPackages { get; set; } = new();
        }

        /// <summary>
        /// Validate Python environment.
        /// </summary>
        public async Task<ValidationResult> Validate()
        {
            Log.Information("Validating Python environment");

            try
            {
                // Detect Python
                var pythonPath = DetectPython();
                if (pythonPath == null)
                {
                    return new ValidationResult
                    {
                        IsValid = false,
                        ErrorMessage = "Python not found on PATH"
                    };
                }

                // Get version
                _pythonVersion = await GetPythonVersion(pythonPath);
                if (_pythonVersion == null)
                {
                    return new ValidationResult
                    {
                        IsValid = false,
                        ErrorMessage = "Failed to determine Python version"
                    };
                }

                Log.Information("Python version: {Version}", _pythonVersion);

                // Validate version (>= 3.9 required)
                if (_pythonVersion.Major < 3 || (_pythonVersion.Major == 3 && _pythonVersion.Minor < 9))
                {
                    return new ValidationResult
                    {
                        IsValid = false,
                        ErrorMessage = $"Python {_pythonVersion} found, but 3.9+ required"
                    };
                }

                // Check required packages
                _missingPackages = await CheckRequiredPackages(pythonPath);

                if (_missingPackages.Count > 0)
                {
                    Log.Warning("Missing Python packages: {Packages}", 
                        string.Join(", ", _missingPackages));

                    return new ValidationResult
                    {
                        IsValid = false,
                        PythonVersion = _pythonVersion,
                        ErrorMessage = $"Missing packages: {string.Join(", ", _missingPackages)}",
                        MissingPackages = _missingPackages
                    };
                }

                Log.Information("✓ Python environment validated: {Version}", _pythonVersion);

                return new ValidationResult
                {
                    IsValid = true,
                    PythonVersion = _pythonVersion
                };
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Python validation failed");
                return new ValidationResult
                {
                    IsValid = false,
                    ErrorMessage = ex.Message
                };
            }
        }

        /// <summary>
        /// Detect Python executable on PATH.
        /// </summary>
        private string? DetectPython()
        {
            var pythonExe = GetOSPythonExecutable();
            
            // Check PATH
            var pathEnv = Environment.GetEnvironmentVariable("PATH") ?? "";
            var directories = pathEnv.Split(Path.PathSeparator);

            foreach (var dir in directories)
            {
                var pythonPath = Path.Combine(dir, pythonExe);
                if (File.Exists(pythonPath))
                {
                    Log.Information("Found Python at {Path}", pythonPath);
                    return pythonPath;
                }
            }

            return null;
        }

        /// <summary>
        /// Get OS-specific Python executable name.
        /// </summary>
        private static string GetOSPythonExecutable()
        {
            return System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(
                System.Runtime.InteropServices.OSPlatform.Windows) ? "python.exe" : "python3";
        }

        /// <summary>
        /// Get Python version.
        /// </summary>
        private async Task<Version?> GetPythonVersion(string pythonPath)
        {
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = "--version",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = Process.Start(psi);
                if (process == null)
                    return null;

                var output = await process.StandardOutput.ReadToEndAsync();
                var error = await process.StandardError.ReadToEndAsync();
                var versionString = (output + error).Trim();

                // Parse "Python 3.9.5" format
                var parts = versionString.Split(' ');
                if (parts.Length >= 2 && Version.TryParse(parts[1], out var version))
                {
                    return version;
                }

                return null;
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Failed to get Python version");
                return null;
            }
        }

        /// <summary>
        /// Check for required Python packages.
        /// </summary>
        private async Task<List<string>> CheckRequiredPackages(string pythonPath)
        {
            var required = new[] { "yaml", "requests" };
            var missing = new List<string>();

            foreach (var package in required)
            {
                var hasPackage = await CheckPackage(pythonPath, package);
                if (!hasPackage)
                    missing.Add(package);
            }

            return missing;
        }

        /// <summary>
        /// Check if a Python package is installed.
        /// </summary>
        private async Task<bool> CheckPackage(string pythonPath, string packageName)
        {
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"-c \"import {packageName}\"",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = Process.Start(psi);
                if (process == null)
                    return false;

                await process.WaitForExitAsync();
                return process.ExitCode == 0;
            }
            catch
            {
                return false;
            }
        }
    }
}
