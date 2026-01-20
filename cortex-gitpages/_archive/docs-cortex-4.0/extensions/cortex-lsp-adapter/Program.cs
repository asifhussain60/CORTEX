using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using OmniSharp.Extensions.LanguageServer.Server;
using OmniSharp.Extensions.LanguageServer.Protocol.Models;
using Serilog;

namespace CortexLSPAdapter
{
    /// <summary>
    /// CORTEX LSP Adapter - Main entry point
    /// 
    /// Implements LSP server for Visual Studio integration with CORTEX governance system.
    /// Connects to CORTEX MCP hub for governance validation, converts violations to LSP diagnostics.
    /// 
    /// AC-DEPLOY-ENHANCED-004-02
    /// </summary>
    class Program
    {
        static async Task Main(string[] args)
        {
            // Setup logging
            Log.Logger = new LoggerConfiguration()
                .MinimumLevel.Debug()
                .WriteTo.Console()
                .WriteTo.File("cortex-lsp-adapter.log", 
                    rollingInterval: RollingInterval.Day,
                    retainedFileCountLimit: 7)
                .CreateLogger();

            Log.Information("CORTEX LSP Adapter starting");
            Log.Information("Arguments: {Args}", string.Join(", ", args));

            try
            {
                // Determine connection mode
                string? mode = GetConnectionMode(args);
                await RunLSPServer(mode);
            }
            catch (Exception ex)
            {
                Log.Fatal(ex, "LSP adapter failed");
                Environment.Exit(1);
            }
            finally
            {
                Log.Information("CORTEX LSP Adapter shutting down");
                Log.CloseAndFlush();
            }
        }

        /// <summary>
        /// Determine if running in TCP, pipe, or stdio mode.
        /// </summary>
        static string? GetConnectionMode(string[] args)
        {
            // Default stdio for VS integration
            if (args.Length == 0)
                return "stdio";

            // Check for --tcp PORT
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--tcp" && i + 1 < args.Length)
                    return $"tcp:{args[i + 1]}";

                if (args[i] == "--pipe" && i + 1 < args.Length)
                    return $"pipe:{args[i + 1]}";
            }

            return "stdio";
        }

        /// <summary>
        /// Run the LSP server.
        /// </summary>
        static async Task RunLSPServer(string? mode)
        {
            Log.Information("Running in mode: {Mode}", mode ?? "stdio");

            var lspServer = new LSPServer();

            try
            {
                await lspServer.Start();
                Log.Information("LSP Server started successfully");

                // Keep the server running
                await Task.Delay(Timeout.Infinite);
            }
            finally
            {
                await lspServer.Stop();
            }
        }
    }
}
