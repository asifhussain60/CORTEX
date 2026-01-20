using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;
using Serilog;

namespace CortexLSPAdapter
{
    /// <summary>
    /// MCP Client for connecting to CORTEX hub.
    /// Fetches governance rules and violation information.
    /// </summary>
    public class MCPClient
    {
        private HttpClient? _client;
        private CortexConfig? _config;
        private Dictionary<string, List<GovernanceViolation>> _violationCache;

        public class CortexConfig
        {
            public string? RepoId { get; set; }
            public string? RepoName { get; set; }
            public string? MCP_Endpoint { get; set; }
            public string? Version { get; set; }
        }

        public class GovernanceViolation
        {
            public string? File { get; set; }
            public int Line { get; set; }
            public int Column { get; set; }
            public string? Severity { get; set; }
            public string? Message { get; set; }
            public string? Rule { get; set; }
            public string? QuickFix { get; set; }
        }

        public MCPClient()
        {
            _violationCache = new Dictionary<string, List<GovernanceViolation>>();
            _client = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
        }

        /// <summary>
        /// Initialize by loading cortex-config.yaml
        /// </summary>
        public async Task Initialize(string workspaceRoot)
        {
            try
            {
                var configPath = Path.Combine(workspaceRoot, "cortex-config.yaml");
                if (!File.Exists(configPath))
                {
                    Log.Warning("cortex-config.yaml not found at {Path}", configPath);
                    return;
                }

                var yaml = new DeserializerBuilder()
                    .WithNamingConvention(CamelCaseNamingConvention.Instance)
                    .Build();

                var configContent = File.ReadAllText(configPath);
                _config = yaml.Deserialize<CortexConfig>(configContent);

                Log.Information("CORTEX config loaded: RepoId={RepoId}, Endpoint={Endpoint}",
                    _config?.RepoId, _config?.MCP_Endpoint);

                // Test connectivity
                await ValidateConnectivity();
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Failed to initialize MCP client");
            }
        }

        /// <summary>
        /// Validate connection to MCP hub.
        /// </summary>
        private async Task ValidateConnectivity()
        {
            if (_config?.MCP_Endpoint == null)
                return;

            try
            {
                var response = await _client!.GetAsync($"{_config.MCP_Endpoint}/health");
                if (response.IsSuccessStatusCode)
                {
                    Log.Information("✓ Connected to MCP hub at {Endpoint}", _config.MCP_Endpoint);
                }
                else
                {
                    Log.Warning("⚠ MCP hub returned {StatusCode}", response.StatusCode);
                }
            }
            catch (Exception ex)
            {
                Log.Warning(ex, "Failed to connect to MCP hub - offline mode enabled");
            }
        }

        /// <summary>
        /// Fetch governance violations for a file.
        /// </summary>
        public async Task<List<GovernanceViolation>> GetViolations(string filePath)
        {
            if (_config?.MCP_Endpoint == null)
                return new List<GovernanceViolation>();

            // Check cache first
            if (_violationCache.TryGetValue(filePath, out var cached))
            {
                Log.Debug("Using cached violations for {File}", filePath);
                return cached;
            }

            try
            {
                var payload = new
                {
                    file = filePath,
                    repo_id = _config.RepoId
                };

                var json = JsonSerializer.Serialize(payload);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await _client!.PostAsync(
                    $"{_config.MCP_Endpoint}/governance/validate",
                    content);

                if (!response.IsSuccessStatusCode)
                {
                    Log.Warning("Governance validation failed: {StatusCode}", response.StatusCode);
                    return new List<GovernanceViolation>();
                }

                var responseContent = await response.Content.ReadAsStringAsync();
                var result = JsonSerializer.Deserialize<Dictionary<string, List<GovernanceViolation>>>(
                    responseContent);

                var violations = result?["violations"] ?? new List<GovernanceViolation>();
                _violationCache[filePath] = violations;

                Log.Debug("Found {Count} violations for {File}", violations.Count, filePath);
                return violations;
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Failed to get governance rules for {File}", filePath);
                return new List<GovernanceViolation>();
            }
        }

        /// <summary>
        /// Get audit trail entries.
        /// </summary>
        public async Task<List<object>> GetAuditTrail(int limit = 100)
        {
            if (_config?.MCP_Endpoint == null)
                return new List<object>();

            try
            {
                var response = await _client!.GetAsync(
                    $"{_config.MCP_Endpoint}/audit/trail?limit={limit}&repo_id={_config.RepoId}");

                if (!response.IsSuccessStatusCode)
                    return new List<object>();

                var content = await response.Content.ReadAsStringAsync();
                var entries = JsonSerializer.Deserialize<List<object>>(content);

                return entries ?? new List<object>();
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Failed to get audit trail");
                return new List<object>();
            }
        }

        /// <summary>
        /// Check if hub is connected.
        /// </summary>
        public bool IsConnected => _config?.MCP_Endpoint != null;
    }
}
