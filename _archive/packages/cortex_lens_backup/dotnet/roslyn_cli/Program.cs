/*
 * Phase 67 S1: Roslyn Semantic Model Extractor
 * 
 * Standalone C# CLI tool for extracting semantic information from .NET solutions.
 * Outputs JSON for Python consumption.
 * 
 * AC_START: AC-PHASE67-S1-ROSLYN-CLI-001
 */

using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.MSBuild;
using Microsoft.Build.Locator;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace CORTEX.RoslynAnalyzer
{
    class Program
    {
        static async Task<int> Main(string[] args)
        {
            // Register MSBuild instance before using MSBuildWorkspace
            if (!MSBuildLocator.IsRegistered)
            {
                MSBuildLocator.RegisterDefaults();
            }

            if (args.Length == 0)
            {
                Console.Error.WriteLine("Usage: RoslynAnalyzerCLI <solution_path> [--output <output_path>]");
                Console.Error.WriteLine("Example: RoslynAnalyzerCLI MySolution.sln --output output.json");
                return 1;
            }

            string solutionPath = args[0];
            string outputPath = args.Length >= 3 && args[1] == "--output" ? args[2] : null;

            if (!File.Exists(solutionPath))
            {
                Console.Error.WriteLine($"Error: Solution file not found: {solutionPath}");
                return 1;
            }

            try
            {
                var extractor = new SemanticExtractor();
                var result = await extractor.AnalyzeSolutionAsync(solutionPath);

                string jsonOutput = JsonConvert.SerializeObject(result, Formatting.Indented);

                if (outputPath != null)
                {
                    File.WriteAllText(outputPath, jsonOutput);
                    Console.WriteLine($"Analysis complete. Output written to: {outputPath}");
                }
                else
                {
                    Console.WriteLine(jsonOutput);
                }

                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error analyzing solution: {ex.Message}");
                Console.Error.WriteLine(ex.StackTrace);
                return 1;
            }
        }
    }

    public class SemanticExtractor
    {
        public async Task<SolutionAnalysisResult> AnalyzeSolutionAsync(string solutionPath)
        {
            var workspace = MSBuildWorkspace.Create();
            
            // Handle workspace diagnostics
            workspace.WorkspaceFailed += (sender, e) =>
            {
                if (e.Diagnostic.Kind == WorkspaceDiagnosticKind.Failure)
                {
                    Console.Error.WriteLine($"Workspace error: {e.Diagnostic.Message}");
                }
            };

            var solution = await workspace.OpenSolutionAsync(solutionPath);

            var result = new SolutionAnalysisResult
            {
                SolutionPath = solutionPath,
                SolutionName = Path.GetFileNameWithoutExtension(solutionPath),
                Projects = new List<ProjectAnalysisResult>()
            };

            foreach (var project in solution.Projects)
            {
                var projectResult = await AnalyzeProjectAsync(project);
                result.Projects.Add(projectResult);
            }

            return result;
        }

        private async Task<ProjectAnalysisResult> AnalyzeProjectAsync(Project project)
        {
            var compilation = await project.GetCompilationAsync();
            
            if (compilation == null)
            {
                return new ProjectAnalysisResult
                {
                    Name = project.Name,
                    Path = project.FilePath,
                    Error = "Failed to get compilation"
                };
            }

            var result = new ProjectAnalysisResult
            {
                Name = project.Name,
                Path = project.FilePath,
                TargetFramework = project.OutputFilePath != null 
                    ? Path.GetFileName(Path.GetDirectoryName(project.OutputFilePath)) 
                    : null,
                Types = new List<TypeInfo>()
            };

            // Extract type symbols
            var visitor = new TypeSymbolVisitor();
            visitor.Visit(compilation.GlobalNamespace);

            result.Types = visitor.Types;

            return result;
        }
    }

    public class TypeSymbolVisitor : SymbolVisitor
    {
        public List<TypeInfo> Types { get; } = new List<TypeInfo>();

        public override void VisitNamespace(INamespaceSymbol symbol)
        {
            foreach (var member in symbol.GetMembers())
            {
                member.Accept(this);
            }
        }

        public override void VisitNamedType(INamedTypeSymbol symbol)
        {
            // Skip compiler-generated types
            if (symbol.Name.StartsWith("<"))
                return;
            
            // Skip BCL types (System.*, Microsoft.* namespaces)
            // Only include user-defined types from solution projects
            string namespaceStr = symbol.ContainingNamespace?.ToDisplayString() ?? "";
            if (namespaceStr.StartsWith("System.") || 
                namespaceStr.StartsWith("Microsoft.") ||
                namespaceStr == "System" ||
                namespaceStr == "Microsoft")
                return;

            var typeInfo = new TypeInfo
            {
                Name = symbol.Name,
                FullName = symbol.ToDisplayString(),
                Namespace = symbol.ContainingNamespace?.ToDisplayString(),
                Kind = symbol.TypeKind.ToString(),
                IsAbstract = symbol.IsAbstract,
                IsSealed = symbol.IsSealed,
                IsStatic = symbol.IsStatic,
                BaseType = symbol.BaseType?.ToDisplayString(),
                Interfaces = symbol.Interfaces.Select(i => i.ToDisplayString()).ToList(),
                Methods = new List<MethodInfo>(),
                Properties = new List<PropertyInfo>()
            };

            // Extract methods
            foreach (var method in symbol.GetMembers().OfType<IMethodSymbol>())
            {
                // Skip special methods (constructors, property accessors, etc.)
                if (method.MethodKind != MethodKind.Ordinary)
                    continue;

                typeInfo.Methods.Add(new MethodInfo
                {
                    Name = method.Name,
                    ReturnType = method.ReturnType.ToDisplayString(),
                    Parameters = method.Parameters.Select(p => new ParameterInfo
                    {
                        Name = p.Name,
                        Type = p.Type.ToDisplayString()
                    }).ToList(),
                    IsPublic = method.DeclaredAccessibility == Accessibility.Public,
                    IsStatic = method.IsStatic,
                    IsAbstract = method.IsAbstract,
                    IsVirtual = method.IsVirtual
                });
            }

            // Extract properties
            foreach (var property in symbol.GetMembers().OfType<IPropertySymbol>())
            {
                typeInfo.Properties.Add(new PropertyInfo
                {
                    Name = property.Name,
                    Type = property.Type.ToDisplayString(),
                    IsPublic = property.DeclaredAccessibility == Accessibility.Public,
                    HasGetter = property.GetMethod != null,
                    HasSetter = property.SetMethod != null
                });
            }

            Types.Add(typeInfo);

            // Visit nested types
            foreach (var nestedType in symbol.GetTypeMembers())
            {
                nestedType.Accept(this);
            }
        }
    }

    // Data models for JSON serialization
    public class SolutionAnalysisResult
    {
        public string SolutionPath { get; set; }
        public string SolutionName { get; set; }
        public List<ProjectAnalysisResult> Projects { get; set; }
    }

    public class ProjectAnalysisResult
    {
        public string Name { get; set; }
        public string Path { get; set; }
        public string TargetFramework { get; set; }
        public string Error { get; set; }
        public List<TypeInfo> Types { get; set; }
    }

    public class TypeInfo
    {
        public string Name { get; set; }
        public string FullName { get; set; }
        public string Namespace { get; set; }
        public string Kind { get; set; }
        public bool IsAbstract { get; set; }
        public bool IsSealed { get; set; }
        public bool IsStatic { get; set; }
        public string BaseType { get; set; }
        public List<string> Interfaces { get; set; }
        public List<MethodInfo> Methods { get; set; }
        public List<PropertyInfo> Properties { get; set; }
    }

    public class MethodInfo
    {
        public string Name { get; set; }
        public string ReturnType { get; set; }
        public List<ParameterInfo> Parameters { get; set; }
        public bool IsPublic { get; set; }
        public bool IsStatic { get; set; }
        public bool IsAbstract { get; set; }
        public bool IsVirtual { get; set; }
    }

    public class ParameterInfo
    {
        public string Name { get; set; }
        public string Type { get; set; }
    }

    public class PropertyInfo
    {
        public string Name { get; set; }
        public string Type { get; set; }
        public bool IsPublic { get; set; }
        public bool HasGetter { get; set; }
        public bool HasSetter { get; set; }
    }
}

// AC_COMPLETE: AC-PHASE67-S1-ROSLYN-CLI-001 ✅ Roslyn CLI implementation complete
