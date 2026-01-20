using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using OmniSharp.Extensions.LanguageServer.Protocol.Models;
using OmniSharp.Extensions.LanguageServer.Protocol.Server;
using OmniSharp.Extensions.LanguageServer.Server;
using Serilog;

namespace CortexLSPAdapter
{
    /// <summary>
    /// LSP Server implementation for CORTEX governance integration.
    /// Implements Language Server Protocol with governance validation.
    /// </summary>
    public class LSPServer
    {
        private LanguageServer? _server;
        private MCPClient _mcpClient;
        private PythonEnvironmentValidator _pythonValidator;
        private Dictionary<string, List<MCPClient.GovernanceViolation>> _diagnosticsCache;

        public LSPServer()
        {
            _mcpClient = new MCPClient();
            _pythonValidator = new PythonEnvironmentValidator();
            _diagnosticsCache = new Dictionary<string, List<MCPClient.GovernanceViolation>>();
        }

        /// <summary>
        /// Start the LSP server.
        /// </summary>
        public async Task Start()
        {
            Log.Information("Starting LSP Server");

            try
            {
                // Validate environment
                var envValidation = await _pythonValidator.Validate();
                if (!envValidation.IsValid)
                {
                    Log.Warning("Python environment validation failed: {Error}", 
                        envValidation.ErrorMessage);
                    // Continue anyway - may work in degraded mode
                }

                // Build server
                var options = new LanguageServerOptions()
                    .WithLoggerFactory(new LoggerFactory())
                    .OnInitialize(OnInitialize)
                    .OnInitialized(OnInitialized)
                    .OnTextDocumentSync(OnTextDocumentSync)
                    .OnCodeLens(OnCodeLens)
                    .OnCodeAction(OnCodeAction);

                _server = await LanguageServer.From(options);
                
                Log.Information("LSP Server started successfully");

                // Keep running
                await _server.WaitForExit;
            }
            catch (Exception ex)
            {
                Log.Error(ex, "Failed to start LSP server");
                throw;
            }
        }

        /// <summary>
        /// Stop the LSP server.
        /// </summary>
        public async Task Stop()
        {
            if (_server != null)
            {
                Log.Information("Stopping LSP Server");
                await _server.Shutdown();
            }
        }

        /// <summary>
        /// Handle Initialize request.
        /// </summary>
        private Task OnInitialize(ILanguageServerFacade server, InitializeParams request, CancellationToken ct)
        {
            Log.Information("LSP Initialize called");

            // Initialize MCP client with workspace root
            var workspaceRoot = request.RootUri?.AbsolutePath ?? request.RootPath ?? ".";
            _ = _mcpClient.Initialize(workspaceRoot);

            return Task.CompletedTask;
        }

        /// <summary>
        /// Handle Initialized notification.
        /// </summary>
        private Task OnInitialized(ILanguageServerFacade server, InitializedParams request, CancellationToken ct)
        {
            Log.Information("LSP Initialized");
            return Task.CompletedTask;
        }

        /// <summary>
        /// Handle text document sync (open, change, close).
        /// </summary>
        private Task OnTextDocumentSync(ITextDocumentSyncHandler handler)
        {
            return Task.CompletedTask;
        }

        /// <summary>
        /// Handle code lens request.
        /// </summary>
        private async Task<CodeLensContainer?> OnCodeLens(
            CodeLensParams request,
            CancellationToken ct)
        {
            var filePath = request.TextDocument.Uri.AbsolutePath;
            Log.Debug("CodeLens requested for {File}", filePath);

            var violations = await _mcpClient.GetViolations(filePath);
            if (violations.Count == 0)
                return null;

            var codeLenses = new List<CodeLens>();

            foreach (var violation in violations)
            {
                var range = new Range(
                    new Position(Math.Max(0, violation.Line - 1), 
                        Math.Max(0, violation.Column - 1)),
                    new Position(Math.Max(0, violation.Line - 1), 
                        Math.Max(0, violation.Column))
                );

                var command = new Command
                {
                    Title = $"CORTEX: {violation.Rule} - {violation.Message}",
                    Name = "cortex.showRuleDetails",
                    Arguments = new object[] { violation.Rule }
                };

                codeLenses.Add(new CodeLens { Range = range, Command = command });
            }

            return new CodeLensContainer(codeLenses);
        }

        /// <summary>
        /// Handle code action request.
        /// </summary>
        private async Task<CommandOrCodeActionContainer?> OnCodeAction(
            CodeActionParams request,
            CancellationToken ct)
        {
            var filePath = request.TextDocument.Uri.AbsolutePath;
            Log.Debug("CodeAction requested for {File}", filePath);

            var violations = await _mcpClient.GetViolations(filePath);
            if (violations.Count == 0)
                return null;

            var actions = new List<CommandOrCodeAction>();

            foreach (var violation in violations)
            {
                if (!string.IsNullOrEmpty(violation.QuickFix))
                {
                    var action = new CodeAction
                    {
                        Title = $"CORTEX: Apply fix for {violation.Rule}",
                        Kind = CodeActionKind.QuickFix,
                        Command = new Command
                        {
                            Title = "Apply CORTEX fix",
                            Name = "cortex.applyQuickFix",
                            Arguments = new object[] { filePath, violation.Rule, violation.QuickFix }
                        }
                    };

                    actions.Add(action);
                }
            }

            return new CommandOrCodeActionContainer(actions);
        }

        /// <summary>
        /// Convert MCP violations to LSP diagnostics.
        /// </summary>
        private Diagnostic CreateDiagnostic(MCPClient.GovernanceViolation violation)
        {
            var severity = violation.Severity switch
            {
                "error" => DiagnosticSeverity.Error,
                "warning" => DiagnosticSeverity.Warning,
                "info" => DiagnosticSeverity.Information,
                _ => DiagnosticSeverity.Hint
            };

            return new Diagnostic
            {
                Range = new Range(
                    new Position(Math.Max(0, violation.Line - 1), 
                        Math.Max(0, violation.Column - 1)),
                    new Position(Math.Max(0, violation.Line - 1), 
                        Math.Max(0, violation.Column))
                ),
                Severity = severity,
                Code = violation.Rule,
                Source = "CORTEX",
                Message = violation.Message ?? "Governance violation",
                RelatedInformation = new Container<DiagnosticRelatedInformation>
                {
                    new DiagnosticRelatedInformation
                    {
                        Message = $"Rule: {violation.Rule}",
                        Location = new Location { Uri = new Uri(violation.File ?? "unknown") }
                    }
                }
            };
        }
    }

    /// <summary>
    /// Logger factory for LSP server.
    /// </summary>
    public class LoggerFactory : ILanguageServerFacade
    {
        // Minimal implementation for LSP integration
        public InitializeResult? InitializeResult { get; }
    }
}
