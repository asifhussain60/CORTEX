using System;
using System.IO;
using System.Linq;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;

namespace CortexVSExtension.Services
{
    /// <summary>
    /// Service for detecting CORTEX workspace and user workspace paths.
    /// Implements the same multi-repo architecture logic as VS Code extension.
    /// </summary>
    public class WorkspaceDetectionService
    {
        private readonly IServiceProvider _serviceProvider;
        private string _cachedCortexPath;
        private string _cachedUserWorkspacePath;

        public WorkspaceDetectionService(IServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
        }

        /// <summary>
        /// Gets the CORTEX installation path.
        /// Searches in: Solution folder, parent folders, environment variable.
        /// </summary>
        public string GetCortexPath()
        {
            if (!string.IsNullOrEmpty(_cachedCortexPath))
            {
                return _cachedCortexPath;
            }

            ThreadHelper.ThrowIfNotOnUIThread();

            // Strategy 1: Check if current solution IS the CORTEX repo
            var solutionPath = GetSolutionPath();
            if (!string.IsNullOrEmpty(solutionPath) && IsCortexRepo(solutionPath))
            {
                _cachedCortexPath = solutionPath;
                return _cachedCortexPath;
            }

            // Strategy 2: Check parent directories
            if (!string.IsNullOrEmpty(solutionPath))
            {
                var currentDir = new DirectoryInfo(solutionPath);
                while (currentDir != null)
                {
                    if (IsCortexRepo(currentDir.FullName))
                    {
                        _cachedCortexPath = currentDir.FullName;
                        return _cachedCortexPath;
                    }
                    currentDir = currentDir.Parent;
                }
            }

            // Strategy 3: Check CORTEX_HOME environment variable
            var cortexHome = Environment.GetEnvironmentVariable("CORTEX_HOME");
            if (!string.IsNullOrEmpty(cortexHome) && IsCortexRepo(cortexHome))
            {
                _cachedCortexPath = cortexHome;
                return _cachedCortexPath;
            }

            // Strategy 4: Check common installation locations
            var commonPaths = new[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "PROJECTS", "CORTEX"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "CORTEX"),
                Path.Combine("C:", "CORTEX")
            };

            foreach (var path in commonPaths)
            {
                if (IsCortexRepo(path))
                {
                    _cachedCortexPath = path;
                    return _cachedCortexPath;
                }
            }

            return null;
        }

        /// <summary>
        /// Gets the user workspace path (current solution/project folder).
        /// </summary>
        public string GetUserWorkspacePath()
        {
            if (!string.IsNullOrEmpty(_cachedUserWorkspacePath))
            {
                return _cachedUserWorkspacePath;
            }

            ThreadHelper.ThrowIfNotOnUIThread();

            var solutionPath = GetSolutionPath();
            if (!string.IsNullOrEmpty(solutionPath) && !IsCortexRepo(solutionPath))
            {
                _cachedUserWorkspacePath = solutionPath;
                return _cachedUserWorkspacePath;
            }

            return null;
        }

        /// <summary>
        /// Checks if the extension is running in CORTEX context vs user workspace.
        /// </summary>
        public bool IsInCortexContext()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var solutionPath = GetSolutionPath();
            return !string.IsNullOrEmpty(solutionPath) && IsCortexRepo(solutionPath);
        }

        /// <summary>
        /// Gets workspace info for display in UI.
        /// </summary>
        public WorkspaceInfo GetWorkspaceInfo()
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            return new WorkspaceInfo
            {
                CortexPath = GetCortexPath(),
                UserWorkspacePath = GetUserWorkspacePath(),
                IsInCortexContext = IsInCortexContext(),
                SolutionName = GetSolutionName()
            };
        }

        /// <summary>
        /// Clears cached paths (use when solution changes).
        /// </summary>
        public void ClearCache()
        {
            _cachedCortexPath = null;
            _cachedUserWorkspacePath = null;
        }

        #region Private Helper Methods

        private string GetSolutionPath()
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            var solution = _serviceProvider.GetService(typeof(SVsSolution)) as IVsSolution;
            if (solution == null)
            {
                return null;
            }

            solution.GetProperty((int)__VSPROPID.VSPROPID_SolutionDirectory, out object solutionDirObj);
            return solutionDirObj as string;
        }

        private string GetSolutionName()
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            var solution = _serviceProvider.GetService(typeof(SVsSolution)) as IVsSolution;
            if (solution == null)
            {
                return null;
            }

            solution.GetProperty((int)__VSPROPID.VSPROPID_SolutionFileName, out object solutionFileObj);
            var solutionFile = solutionFileObj as string;
            return string.IsNullOrEmpty(solutionFile) ? null : Path.GetFileNameWithoutExtension(solutionFile);
        }

        private bool IsCortexRepo(string path)
        {
            if (string.IsNullOrEmpty(path) || !Directory.Exists(path))
            {
                return false;
            }

            // Check for CORTEX signature files/folders
            var cortexSignatures = new[]
            {
                Path.Combine(path, "cortex-brain"),
                Path.Combine(path, "cortex-brain", "admin"),
                Path.Combine(path, "cortex.config.json"),
                Path.Combine(path, ".github", "prompts", "CORTEX.prompt.md")
            };

            return cortexSignatures.Any(signature => Directory.Exists(signature) || File.Exists(signature));
        }

        #endregion
    }

    /// <summary>
    /// Workspace information model.
    /// </summary>
    public class WorkspaceInfo
    {
        public string CortexPath { get; set; }
        public string UserWorkspacePath { get; set; }
        public bool IsInCortexContext { get; set; }
        public string SolutionName { get; set; }

        public bool IsCortexInstalled => !string.IsNullOrEmpty(CortexPath);
        public bool HasUserWorkspace => !string.IsNullOrEmpty(UserWorkspacePath);
    }
}
