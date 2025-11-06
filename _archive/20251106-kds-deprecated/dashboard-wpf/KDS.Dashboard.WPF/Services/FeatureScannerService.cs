using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using KDS.Dashboard.WPF.Models;

namespace KDS.Dashboard.WPF.Services
{
    /// <summary>
    /// Scans the KDS directory structure to discover and validate features.
    /// Determines feature status by checking for code, tests, docs, and agent integration.
    /// </summary>
    public class FeatureScannerService
    {
        private readonly string _kdsRootPath;
        private readonly List<Feature> _cachedFeatures;
        private DateTime _lastScanTime;

        public FeatureScannerService(string kdsRootPath)
        {
            _kdsRootPath = kdsRootPath ?? throw new ArgumentNullException(nameof(kdsRootPath));
            _cachedFeatures = new List<Feature>();
            _lastScanTime = DateTime.MinValue;
        }

        /// <summary>
        /// Scans the KDS directory and returns all discovered features.
        /// Uses cache if scan was performed less than 5 minutes ago.
        /// </summary>
        public List<Feature> ScanFeatures(bool forceRefresh = false)
        {
            if (!forceRefresh && (DateTime.Now - _lastScanTime).TotalMinutes < 5)
            {
                return _cachedFeatures;
            }

            _cachedFeatures.Clear();

            try
            {
                // 1. Scan kds.md implementation status table
                var kdsDocFeatures = ScanKdsDocumentation();

                // 2. Scan prompts/ directory for agents
                var agentFeatures = ScanAgents();

                // 3. Scan scripts/ directory for PowerShell scripts
                var scriptFeatures = ScanScripts();

                // 4. Scan kds-brain/ for brain files
                var brainFeatures = ScanBrainFiles();

                // 5. Merge and deduplicate features
                var allFeatures = MergeFeatures(kdsDocFeatures, agentFeatures, scriptFeatures, brainFeatures);

                // 6. Validate each feature
                foreach (var feature in allFeatures)
                {
                    ValidateFeature(feature);
                }

                _cachedFeatures.AddRange(allFeatures);
                _lastScanTime = DateTime.Now;

                return _cachedFeatures;
            }
            catch (Exception ex)
            {
                ViewModels.ErrorViewModel.Instance.LogError("FeatureScannerService",
                    $"Error scanning features: {ex.Message}", ex);
                return _cachedFeatures;
            }
        }

        /// <summary>
        /// Scans kds.md for the Implementation Status table.
        /// </summary>
        private List<Feature> ScanKdsDocumentation()
        {
            var features = new List<Feature>();
            var kdsDocPath = Path.Combine(_kdsRootPath, "prompts", "user", "kds.md");

            if (!File.Exists(kdsDocPath))
            {
                return features;
            }

            try
            {
                var content = File.ReadAllText(kdsDocPath);
                
                // Extract implementation status table
                // Pattern: | **Feature Name** | Status | Notes |
                var tablePattern = @"\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|";
                var matches = Regex.Matches(content, tablePattern);

                foreach (Match match in matches)
                {
                    if (match.Groups.Count >= 4)
                    {
                        var featureName = match.Groups[1].Value.Trim();
                        var statusStr = match.Groups[2].Value.Trim();
                        var notes = match.Groups[3].Value.Trim();

                        // Skip header row
                        if (featureName == "Feature" || featureName.Contains("---"))
                            continue;

                        var feature = new Feature
                        {
                            Name = featureName,
                            Status = ParseFeatureStatus(statusStr),
                            Notes = notes,
                            DiscoveredFrom = "kds.md"
                        };

                        features.Add(feature);
                    }
                }
            }
            catch (Exception ex)
            {
                ViewModels.ErrorViewModel.Instance.LogError("FeatureScannerService",
                    $"Error scanning kds.md: {ex.Message}", ex);
            }

            return features;
        }

        /// <summary>
        /// Scans prompts/internal/ for agent files.
        /// </summary>
        private List<Feature> ScanAgents()
        {
            var features = new List<Feature>();
            var promptsPath = Path.Combine(_kdsRootPath, "prompts", "internal");

            if (!Directory.Exists(promptsPath))
            {
                return features;
            }

            try
            {
                var agentFiles = Directory.GetFiles(promptsPath, "*.md", SearchOption.TopDirectoryOnly);

                foreach (var agentFile in agentFiles)
                {
                    var agentName = Path.GetFileNameWithoutExtension(agentFile);
                    
                    // Convert filename to feature name (e.g., "intent-router.md" → "Intent Router")
                    var featureName = agentName.Replace("-", " ")
                        .Replace("_", " ")
                        .ToTitleCase();

                    var feature = new Feature
                    {
                        Name = $"Agent: {featureName}",
                        Status = FeatureStatus.Unknown, // Will be determined by validation
                        Files = new List<string> { agentFile },
                        DiscoveredFrom = "prompts/internal/"
                    };

                    features.Add(feature);
                }
            }
            catch (Exception ex)
            {
                ViewModels.ErrorViewModel.Instance.LogError("FeatureScannerService",
                    $"Error scanning agents: {ex.Message}", ex);
            }

            return features;
        }

        /// <summary>
        /// Scans scripts/ for PowerShell scripts.
        /// </summary>
        private List<Feature> ScanScripts()
        {
            var features = new List<Feature>();
            var scriptsPath = Path.Combine(_kdsRootPath, "scripts");

            if (!Directory.Exists(scriptsPath))
            {
                return features;
            }

            try
            {
                var scriptFiles = Directory.GetFiles(scriptsPath, "*.ps1", SearchOption.TopDirectoryOnly);

                foreach (var scriptFile in scriptFiles)
                {
                    var scriptName = Path.GetFileNameWithoutExtension(scriptFile);
                    
                    // Convert filename to feature name
                    var featureName = scriptName.Replace("-", " ")
                        .Replace("_", " ")
                        .ToTitleCase();

                    var feature = new Feature
                    {
                        Name = $"Script: {featureName}",
                        Status = FeatureStatus.Unknown,
                        Scripts = new List<string> { scriptFile },
                        DiscoveredFrom = "scripts/"
                    };

                    features.Add(feature);
                }
            }
            catch (Exception ex)
            {
                ViewModels.ErrorViewModel.Instance.LogError("FeatureScannerService",
                    $"Error scanning scripts: {ex.Message}", ex);
            }

            return features;
        }

        /// <summary>
        /// Scans kds-brain/ for brain data files.
        /// </summary>
        private List<Feature> ScanBrainFiles()
        {
            var features = new List<Feature>();
            var brainPath = Path.Combine(_kdsRootPath, "kds-brain");

            if (!Directory.Exists(brainPath))
            {
                return features;
            }

            try
            {
                // Key brain files
                var brainFiles = new Dictionary<string, string>
                {
                    { "conversation-history.jsonl", "Tier 1: Conversation History" },
                    { "conversation-context.jsonl", "Tier 1: Conversation Context" },
                    { "knowledge-graph.yaml", "Tier 2: Knowledge Graph" },
                    { "development-context.yaml", "Tier 3: Development Context" },
                    { "events.jsonl", "Tier 4: Event Stream" },
                    { "architectural-patterns.yaml", "Tier 2: Architectural Patterns" },
                    { "file-relationships.yaml", "Tier 2: File Relationships" }
                };

                foreach (var kvp in brainFiles)
                {
                    var filePath = Path.Combine(brainPath, kvp.Key);
                    if (File.Exists(filePath))
                    {
                        var feature = new Feature
                        {
                            Name = kvp.Value,
                            Status = FeatureStatus.FullyImplemented, // Brain files are operational
                            Files = new List<string> { filePath },
                            DiscoveredFrom = "kds-brain/"
                        };

                        features.Add(feature);
                    }
                }
            }
            catch (Exception ex)
            {
                ViewModels.ErrorViewModel.Instance.LogError("FeatureScannerService",
                    $"Error scanning brain files: {ex.Message}", ex);
            }

            return features;
        }

        /// <summary>
        /// Merges features from different sources, deduplicating by name.
        /// </summary>
        private List<Feature> MergeFeatures(params List<Feature>[] featureLists)
        {
            var merged = new Dictionary<string, Feature>();

            foreach (var featureList in featureLists)
            {
                foreach (var feature in featureList)
                {
                    if (merged.ContainsKey(feature.Name))
                    {
                        // Merge properties
                        var existing = merged[feature.Name];
                        existing.Files = existing.Files.Concat(feature.Files).Distinct().ToList();
                        existing.Scripts = existing.Scripts.Concat(feature.Scripts).Distinct().ToList();
                    }
                    else
                    {
                        merged[feature.Name] = feature;
                    }
                }
            }

            return merged.Values.ToList();
        }

        /// <summary>
        /// Validates a feature by checking for code, tests, docs, and agent integration.
        /// Updates the feature's Status and MissingComponents properties.
        /// </summary>
        private void ValidateFeature(Feature feature)
        {
            var hasCode = feature.Files.Count > 0 || feature.Scripts.Count > 0;
            var hasTests = CheckForTests(feature);
            var hasDocs = CheckForDocs(feature);
            var hasAgent = CheckForAgentIntegration(feature);

            // Update feature properties
            feature.HasCode = hasCode;
            feature.HasTests = hasTests;
            feature.HasDocs = hasDocs;
            feature.HasAgentIntegration = hasAgent;

            // Determine status
            if (hasCode && hasTests && hasDocs && hasAgent)
            {
                feature.Status = FeatureStatus.FullyImplemented;
                feature.Confidence = 0.98m;
            }
            else if (hasCode && hasTests)
            {
                feature.Status = FeatureStatus.PartiallyImplemented;
                feature.Confidence = 0.75m;
                feature.MissingComponents.AddRange(GetMissingComponents(feature));
            }
            else if (hasCode)
            {
                feature.Status = FeatureStatus.PartiallyImplemented;
                feature.Confidence = 0.50m;
                feature.MissingComponents.AddRange(GetMissingComponents(feature));
            }
            else if (hasDocs)
            {
                feature.Status = FeatureStatus.DesignedOnly;
                feature.Confidence = 0.20m;
                feature.MissingComponents.Add("Code implementation");
                feature.MissingComponents.Add("Tests");
            }
            else
            {
                feature.Status = FeatureStatus.Unknown;
                feature.Confidence = 0.0m;
            }
        }

        private bool CheckForTests(Feature feature)
        {
            var testsPath = Path.Combine(_kdsRootPath, "tests");
            if (!Directory.Exists(testsPath))
                return false;

            // Look for test files matching feature name
            var featureKeywords = feature.Name.ToLower()
                .Replace(":", "")
                .Replace("agent:", "")
                .Replace("script:", "")
                .Split(' ', StringSplitOptions.RemoveEmptyEntries);

            try
            {
                var testFiles = Directory.GetFiles(testsPath, "*.ps1", SearchOption.AllDirectories)
                    .Concat(Directory.GetFiles(testsPath, "*.cs", SearchOption.AllDirectories));

                foreach (var testFile in testFiles)
                {
                    var testFileName = Path.GetFileName(testFile).ToLower();
                    if (featureKeywords.Any(keyword => testFileName.Contains(keyword)))
                    {
                        feature.Tests.Add(testFile);
                    }
                }
            }
            catch
            {
                // Ignore errors
            }

            return feature.Tests.Count > 0;
        }

        private bool CheckForDocs(Feature feature)
        {
            var docsPath = Path.Combine(_kdsRootPath, "docs");
            if (!Directory.Exists(docsPath))
                return false;

            var featureKeywords = feature.Name.ToLower()
                .Replace(":", "")
                .Replace("agent:", "")
                .Replace("script:", "")
                .Split(' ', StringSplitOptions.RemoveEmptyEntries);

            try
            {
                var docFiles = Directory.GetFiles(docsPath, "*.md", SearchOption.AllDirectories);

                foreach (var docFile in docFiles)
                {
                    var content = File.ReadAllText(docFile).ToLower();
                    if (featureKeywords.Any(keyword => content.Contains(keyword)))
                    {
                        feature.Docs.Add(docFile);
                        return true;
                    }
                }
            }
            catch
            {
                // Ignore errors
            }

            return false;
        }

        private bool CheckForAgentIntegration(Feature feature)
        {
            // Check if feature is mentioned in intent-router.md
            var routerPath = Path.Combine(_kdsRootPath, "prompts", "internal", "intent-router.md");
            if (!File.Exists(routerPath))
                return false;

            try
            {
                var content = File.ReadAllText(routerPath).ToLower();
                var featureKeywords = feature.Name.ToLower()
                    .Replace(":", "")
                    .Replace("agent:", "")
                    .Replace("script:", "")
                    .Split(' ', StringSplitOptions.RemoveEmptyEntries);

                return featureKeywords.Any(keyword => content.Contains(keyword));
            }
            catch
            {
                return false;
            }
        }

        private List<string> GetMissingComponents(Feature feature)
        {
            var missing = new List<string>();

            if (!feature.HasTests)
                missing.Add("Tests");
            if (!feature.HasDocs)
                missing.Add("Documentation");
            if (!feature.HasAgentIntegration)
                missing.Add("Agent Integration");

            return missing;
        }

        private FeatureStatus ParseFeatureStatus(string statusStr)
        {
            if (statusStr.Contains("✅"))
                return FeatureStatus.FullyImplemented;
            if (statusStr.Contains("🟡"))
                return FeatureStatus.PartiallyImplemented;
            if (statusStr.Contains("🔄"))
                return FeatureStatus.InProgress;
            if (statusStr.Contains("📋"))
                return FeatureStatus.DesignedOnly;

            return FeatureStatus.Unknown;
        }
    }

    /// <summary>
    /// Extension method to convert string to Title Case.
    /// </summary>
    public static class StringExtensions
    {
        public static string ToTitleCase(this string str)
        {
            if (string.IsNullOrEmpty(str))
                return str;

            var words = str.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            for (int i = 0; i < words.Length; i++)
            {
                if (words[i].Length > 0)
                {
                    words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
                }
            }

            return string.Join(" ", words);
        }
    }
}
