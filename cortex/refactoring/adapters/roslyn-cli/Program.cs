/*
 * CortexRoslynCli - C# Refactoring CLI Tool
 * 
 * JSON-RPC style CLI for C# semantic refactoring using Roslyn compiler services.
 * 
 * AC_START: AC-PHASE24.2.2-002
 * Description: Roslyn CLI entry point
 * Authority: Phase 24.2.2 - Type-Safe Operations
 * Author: Asif Hussain
 * Created: 2026-02-07
 */

using System;
using System.Text.Json;
using System.Threading.Tasks;

namespace CortexRoslynCli;

/// <summary>
/// Entry point for CORTEX Roslyn CLI tool.
/// </summary>
public class Program
{
    /// <summary>
    /// Main entry point.
    /// </summary>
    public static async Task<int> Main(string[] args)
    {
        try
        {
            // Handle command-line arguments
            if (args.Length > 0)
            {
                return HandleCommandLineArgs(args);
            }

            // Default: JSON-RPC mode via stdin
            return await RunJsonRpcModeAsync();
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Fatal error: {ex.Message}");
            return 1;
        }
    }

    /// <summary>
    /// Handle command-line arguments (--version, --help, etc.).
    /// </summary>
    private static int HandleCommandLineArgs(string[] args)
    {
        switch (args[0].ToLower())
        {
            case "--version":
            case "-v":
                Console.WriteLine("CortexRoslynCli v1.0.0");
                Console.WriteLine("Roslyn API: 4.8.0");
                Console.WriteLine(".NET Runtime: " + Environment.Version);
                return 0;

            case "--help":
            case "-h":
                PrintHelp();
                return 0;

            case "refactor":
                // Read JSON from stdin for refactor command
                return Task.Run(async () => await ProcessRefactorCommandAsync()).Result;

            default:
                Console.Error.WriteLine($"Unknown command: {args[0]}");
                Console.Error.WriteLine("Use --help for usage information.");
                return 1;
        }
    }

    /// <summary>
    /// Print help information.
    /// </summary>
    private static void PrintHelp()
    {
        Console.WriteLine("CortexRoslynCli - C# Refactoring Tool");
        Console.WriteLine();
        Console.WriteLine("USAGE:");
        Console.WriteLine("  dotnet CortexRoslynCli.dll [OPTIONS] [COMMAND]");
        Console.WriteLine();
        Console.WriteLine("OPTIONS:");
        Console.WriteLine("  --version, -v     Show version information");
        Console.WriteLine("  --help, -h        Show this help message");
        Console.WriteLine();
        Console.WriteLine("COMMANDS:");
        Console.WriteLine("  refactor          Execute refactoring (reads JSON from stdin)");
        Console.WriteLine();
        Console.WriteLine("SUPPORTED REFACTORINGS:");
        Console.WriteLine("  - extract_method       Extract code into new method");
        Console.WriteLine("  - rename               Rename symbols (variables, methods, classes)");
        Console.WriteLine("  - inline_method        Inline method calls");
        Console.WriteLine("  - encapsulate_field    Generate getter/setter for field");
        Console.WriteLine("  - move_to_new_file     Move type to new file");
        Console.WriteLine("  - introduce_parameter  Convert local to parameter");
        Console.WriteLine("  - extract_interface    Extract interface from class");
        Console.WriteLine("  - change_signature     Modify method signature");
        Console.WriteLine();
        Console.WriteLine("EXAMPLE:");
        Console.WriteLine("  echo '{\"action\":\"refactor\",\"operation\":\"rename\",...}' | dotnet CortexRoslynCli.dll refactor");
    }

    /// <summary>
    /// Run in JSON-RPC mode (read commands from stdin, write responses to stdout).
    /// </summary>
    private static async Task<int> RunJsonRpcModeAsync()
    {
        var service = new RefactoringService();

        while (true)
        {
            try
            {
                // Read JSON command from stdin
                var inputLine = await Console.In.ReadLineAsync();
                if (string.IsNullOrWhiteSpace(inputLine))
                {
                    break; // EOF or empty input
                }

                // Parse JSON command
                var command = JsonSerializer.Deserialize<RefactorCommand>(inputLine);
                if (command == null)
                {
                    WriteErrorResponse("Invalid JSON command");
                    continue;
                }

                // Execute refactoring
                var response = await service.ExecuteRefactoringAsync(command);

                // Write JSON response to stdout
                var responseJson = JsonSerializer.Serialize(response, new JsonSerializerOptions
                {
                    WriteIndented = false
                });
                Console.WriteLine(responseJson);
            }
            catch (JsonException ex)
            {
                WriteErrorResponse($"JSON parsing error: {ex.Message}");
            }
            catch (Exception ex)
            {
                WriteErrorResponse($"Unexpected error: {ex.Message}");
            }
        }

        return 0;
    }

    /// <summary>
    /// Process refactor command (read JSON from stdin once).
    /// </summary>
    private static async Task<int> ProcessRefactorCommandAsync()
    {
        try
        {
            // Read entire stdin
            var input = await Console.In.ReadToEndAsync();
            if (string.IsNullOrWhiteSpace(input))
            {
                WriteErrorResponse("No input provided");
                return 1;
            }

            // Parse JSON
            var command = JsonSerializer.Deserialize<RefactorCommand>(input);
            if (command == null)
            {
                WriteErrorResponse("Invalid JSON command");
                return 1;
            }

            // Execute refactoring
            var service = new RefactoringService();
            var response = await service.ExecuteRefactoringAsync(command);

            // Write response
            var responseJson = JsonSerializer.Serialize(response, new JsonSerializerOptions
            {
                WriteIndented = false
            });
            Console.WriteLine(responseJson);

            return response.Success ? 0 : 1;
        }
        catch (JsonException ex)
        {
            WriteErrorResponse($"JSON error: {ex.Message}");
            return 1;
        }
        catch (Exception ex)
        {
            WriteErrorResponse($"Error: {ex.Message}");
            return 1;
        }
    }

    /// <summary>
    /// Write error response to stdout.
    /// </summary>
    private static void WriteErrorResponse(string errorMessage)
    {
        var errorResponse = new RefactorResponse
        {
            Success = false,
            Error = errorMessage
        };

        var json = JsonSerializer.Serialize(errorResponse);
        Console.WriteLine(json);
    }
}

/// <summary>
/// Refactor command model (matches Python side with snake_case JSON).
/// </summary>
public class RefactorCommand
{
    [System.Text.Json.Serialization.JsonPropertyName("action")]
    public string Action { get; set; } = "";
    
    [System.Text.Json.Serialization.JsonPropertyName("operation")]
    public string Operation { get; set; } = "";
    
    [System.Text.Json.Serialization.JsonPropertyName("file_path")]
    public string FilePath { get; set; } = "";
    
    [System.Text.Json.Serialization.JsonPropertyName("parameters")]
    public Dictionary<string, object> Parameters { get; set; } = new();
}

/// <summary>
/// Refactor response model (matches Python side with snake_case JSON).
/// </summary>
public class RefactorResponse
{
    [System.Text.Json.Serialization.JsonPropertyName("success")]
    public bool Success { get; set; }
    
    [System.Text.Json.Serialization.JsonPropertyName("modified_files")]
    public List<string> ModifiedFiles { get; set; } = new();
    
    [System.Text.Json.Serialization.JsonPropertyName("description")]
    public string Description { get; set; } = "";
    
    [System.Text.Json.Serialization.JsonPropertyName("warnings")]
    public List<string> Warnings { get; set; } = new();
    
    [System.Text.Json.Serialization.JsonPropertyName("error")]
    public string? Error { get; set; }
    
    [System.Text.Json.Serialization.JsonPropertyName("metadata")]
    public Dictionary<string, object> Metadata { get; set; } = new();
}

// AC_COMPLETE: AC-PHASE24.2.2-002 ✅ Roslyn CLI Program entry point
