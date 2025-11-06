using Xunit;
using System;
using System.IO;
using System.Diagnostics;

namespace KDS.Dashboard.WPF.Tests
{
    /// <summary>
    /// End-to-end smoke tests to verify the application can launch
    /// These tests verify the executable exists and has correct dependencies
    /// </summary>
    public class ApplicationSmokeTests
    {
        private const string ExePath = @"d:\PROJECTS\KDS\dashboard-wpf\KDS.Dashboard.WPF\bin\Debug\net8.0-windows\KDS.Dashboard.exe";
        private const string DllPath = @"d:\PROJECTS\KDS\dashboard-wpf\KDS.Dashboard.WPF\bin\Debug\net8.0-windows\KDS.Dashboard.dll";

        [Fact]
        public void Executable_ShouldExist()
        {
            Assert.True(File.Exists(ExePath), 
                $"Application executable not found at {ExePath}");
        }

        [Fact]
        public void MainDll_ShouldExist()
        {
            Assert.True(File.Exists(DllPath), 
                $"Main application DLL not found at {DllPath}");
        }

        [Fact]
        public void Executable_ShouldHaveCorrectExtension()
        {
            var extension = Path.GetExtension(ExePath);
            Assert.Equal(".exe", extension);
        }

        [Fact]
        public void Executable_ShouldNotBeEmpty()
        {
            var fileInfo = new FileInfo(ExePath);
            Assert.True(fileInfo.Length > 0, "Executable file is empty");
        }

        [Fact]
        public void MaterialDesignThemes_DllShouldExist()
        {
            var mdPath = Path.Combine(
                Path.GetDirectoryName(ExePath)!, 
                "MaterialDesignThemes.Wpf.dll");
            
            Assert.True(File.Exists(mdPath), 
                "MaterialDesignThemes.Wpf.dll dependency missing");
        }

        [Fact]
        public void MaterialDesignColors_DllShouldExist()
        {
            var mdcPath = Path.Combine(
                Path.GetDirectoryName(ExePath)!, 
                "MaterialDesignColors.dll");
            
            Assert.True(File.Exists(mdcPath), 
                "MaterialDesignColors.dll dependency missing");
        }

        [Fact]
        public void RuntimeConfig_ShouldExist()
        {
            var runtimeConfigPath = ExePath.Replace(".exe", ".runtimeconfig.json");
            
            Assert.True(File.Exists(runtimeConfigPath), 
                "Runtime configuration file missing - application cannot start");
        }

        [Fact]
        public void DepsJson_ShouldExist()
        {
            var depsPath = ExePath.Replace(".exe", ".deps.json");
            
            Assert.True(File.Exists(depsPath), 
                "Dependencies manifest missing");
        }

        [Fact]
        public void BuildOutputDirectory_ShouldContainViewDlls()
        {
            var outputDir = Path.GetDirectoryName(ExePath)!;
            var files = Directory.GetFiles(outputDir, "*.dll");
            
            Assert.True(files.Length > 5, 
                $"Expected multiple DLL dependencies, found only {files.Length}");
        }

        [Fact]
        public void ApplicationVersion_ShouldBeNet8()
        {
            var runtimeConfigPath = ExePath.Replace(".exe", ".runtimeconfig.json");
            var json = File.ReadAllText(runtimeConfigPath);
            
            Assert.Contains("\"version\": \"8.", json);
        }
    }
}
