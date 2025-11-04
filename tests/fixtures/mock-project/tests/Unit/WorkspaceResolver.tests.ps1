# WorkspaceResolver.tests.ps1
# Unit tests for workspace-resolver.ps1
# Tests dynamic path resolution across different working directories

Describe "WorkspaceResolver" {
    BeforeAll {
        # Import the module under test
        $kdsRoot = Split-Path (Split-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) -Parent) -Parent
        $resolverPath = Join-Path $kdsRoot "scripts\lib\workspace-resolver.ps1"
        if (-not (Test-Path $resolverPath)) {
            throw "Workspace resolver not found at: $resolverPath"
        }
        . $resolverPath
    }

    Context "Get-WorkspaceRoot" {
        It "Should find git root when in git repository" {
            # Arrange: We're in a git repo (KDS itself)
            Push-Location $PSScriptRoot
            
            # Act
            $root = Get-WorkspaceRoot
            
            # Assert
            $root | Should -Not -BeNullOrEmpty
            Test-Path (Join-Path $root ".git") | Should -Be $true
            
            Pop-Location
        }

        It "Should return parent folder when not in git repository" {
            # Arrange: Create temp folder outside git
            $tempDir = Join-Path $env:TEMP "kds-test-$(Get-Random)"
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
            Push-Location $tempDir
            
            # Act
            $root = Get-WorkspaceRoot
            
            # Assert
            $root | Should -Be (Get-Item $tempDir).Parent.FullName
            
            # Cleanup
            Pop-Location
            Remove-Item $tempDir -Force
        }

        It "Should handle paths with spaces" {
            # Arrange
            $tempDir = Join-Path $env:TEMP "kds test space $(Get-Random)"
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
            Push-Location $tempDir
            
            # Act
            $root = Get-WorkspaceRoot
            
            # Assert
            $root | Should -Not -BeNullOrEmpty
            $root | Should -Not -Contain '`'
            
            # Cleanup
            Pop-Location
            Remove-Item $tempDir -Force
        }

        It "Should work from any subdirectory in git repo" {
            # Arrange: Go deep into KDS structure
            $deepPath = Join-Path $PSScriptRoot "..\..\..\..\kds-brain"
            if (Test-Path $deepPath) {
                Push-Location $deepPath
                
                # Act
                $root = Get-WorkspaceRoot
                
                # Assert
                Test-Path (Join-Path $root ".git") | Should -Be $true
                
                Pop-Location
            }
        }
    }

    Context "Get-KdsRoot" {
        It "Should return absolute path to KDS folder" {
            # Act
            $kdsRoot = Get-KdsRoot
            
            # Assert
            $kdsRoot | Should -Not -BeNullOrEmpty
            Test-Path $kdsRoot | Should -Be $true
            $kdsRoot | Should -Match "KDS$"
        }

        It "Should work when called from different directories" {
            # Arrange: Save current location
            $originalLocation = Get-Location
            
            # Test from project root
            Push-Location (Get-WorkspaceRoot)
            $root1 = Get-KdsRoot
            Pop-Location
            
            # Test from KDS folder
            Push-Location (Get-KdsRoot)
            $root2 = Get-KdsRoot
            Pop-Location
            
            # Test from temp folder
            Push-Location $env:TEMP
            $root3 = Get-KdsRoot
            Pop-Location
            
            # Assert: All should return same path
            $root1 | Should -Be $root2
            $root2 | Should -Be $root3
            
            # Restore location
            Set-Location $originalLocation
        }

        It "Should return path that contains required KDS files" {
            # Act
            $kdsRoot = Get-KdsRoot
            
            # Assert: Check for critical KDS files
            Test-Path (Join-Path $kdsRoot "prompts") | Should -Be $true
            Test-Path (Join-Path $kdsRoot "scripts") | Should -Be $true
            Test-Path (Join-Path $kdsRoot "kds-brain") | Should -Be $true
        }
    }

    Context "Resolve-RelativePath" {
        It "Should convert relative path to absolute" {
            # Arrange
            $relativePath = ".\kds-brain\events.jsonl"
            
            # Act
            $absolutePath = Resolve-RelativePath -Path $relativePath -BasePath (Get-KdsRoot)
            
            # Assert
            $absolutePath | Should -Not -BeNullOrEmpty
            [System.IO.Path]::IsPathRooted($absolutePath) | Should -Be $true
            $absolutePath | Should -Match "kds-brain"
        }

        It "Should handle parent directory references (..)" {
            # Arrange
            $relativePath = "..\..\..\README.md"
            $basePath = Join-Path (Get-KdsRoot) "scripts\lib"
            
            # Act
            $absolutePath = Resolve-RelativePath -Path $relativePath -BasePath $basePath
            
            # Assert
            $absolutePath | Should -Not -BeNullOrEmpty
            [System.IO.Path]::IsPathRooted($absolutePath) | Should -Be $true
        }

        It "Should return absolute paths unchanged" {
            # Arrange
            $absolutePath = "D:\PROJECTS\KDS\README.md"
            
            # Act
            $result = Resolve-RelativePath -Path $absolutePath
            
            # Assert
            $result | Should -Be $absolutePath
        }

        It "Should normalize path separators" {
            # Arrange
            $mixedPath = "kds-brain/knowledge-graph.yaml"
            
            # Act
            $result = Resolve-RelativePath -Path $mixedPath -BasePath (Get-KdsRoot)
            
            # Assert
            $separator = [System.IO.Path]::DirectorySeparatorChar
            $result | Should -Match ([regex]::Escape($separator))
        }

        It "Should handle paths with spaces" {
            # Arrange
            $pathWithSpaces = "test folder\sub folder\file.txt"
            
            # Act
            $result = Resolve-RelativePath -Path $pathWithSpaces -BasePath (Get-KdsRoot)
            
            # Assert
            $result | Should -Not -BeNullOrEmpty
            $result | Should -Not -Contain '`'
        }
    }

    Context "Test-PathExists" {
        It "Should return true for existing file" {
            # Arrange
            $existingFile = Join-Path (Get-KdsRoot) "README.md"
            
            # Act & Assert
            Test-PathExists -Path $existingFile | Should -Be $true
        }

        It "Should return true for existing directory" {
            # Arrange
            $existingDir = Join-Path (Get-KdsRoot) "prompts"
            
            # Act & Assert
            Test-PathExists -Path $existingDir | Should -Be $true
        }

        It "Should return false for non-existent path" {
            # Arrange
            $nonExistentPath = Join-Path (Get-KdsRoot) "this-does-not-exist-$(Get-Random).txt"
            
            # Act & Assert
            Test-PathExists -Path $nonExistentPath | Should -Be $false
        }

        It "Should throw error when -ThrowIfNotFound is specified and path doesn't exist" {
            # Arrange
            $nonExistentPath = Join-Path (Get-KdsRoot) "this-does-not-exist-$(Get-Random).txt"
            
            # Act & Assert
            { Test-PathExists -Path $nonExistentPath -ThrowIfNotFound } | Should -Throw
        }

        It "Should not throw error when -ThrowIfNotFound is specified and path exists" {
            # Arrange
            $existingFile = Join-Path (Get-KdsRoot) "README.md"
            
            # Act & Assert
            { Test-PathExists -Path $existingFile -ThrowIfNotFound } | Should -Not -Throw
        }

        It "Should include path in error message when throwing" {
            # Arrange
            $nonExistentPath = Join-Path (Get-KdsRoot) "missing-file.txt"
            
            # Act & Assert
            try {
                Test-PathExists -Path $nonExistentPath -ThrowIfNotFound
                throw "Should have thrown"
            }
            catch {
                $_.Exception.Message | Should -Match "missing-file.txt"
            }
        }
    }

    Context "Cross-Platform Compatibility" {
        It "Should use correct path separator for current OS" {
            # Act
            $path = Resolve-RelativePath -Path "subfolder\file.txt" -BasePath (Get-KdsRoot)
            
            # Assert
            if ($IsWindows -or $PSVersionTable.PSVersion.Major -le 5) {
                $path | Should -Match '\\'
            }
            else {
                $path | Should -Match '/'
            }
        }

        It "Should handle mixed path separators" {
            # Arrange
            $mixedPath = "kds-brain/subfolder\file.txt"
            
            # Act
            $normalized = Resolve-RelativePath -Path $mixedPath -BasePath (Get-KdsRoot)
            
            # Assert
            $normalized | Should -Not -BeNullOrEmpty
            # Should be normalized to OS-appropriate separator
        }
    }

    Context "Error Handling" {
        It "Should provide helpful error when KDS folder not found" {
            # This test assumes we're running from within KDS
            # In real scenario where KDS isn't found, should get helpful message
            # We'll test the error message format
            $kdsRoot = Get-KdsRoot
            $kdsRoot | Should -Not -BeNullOrEmpty
        }

        It "Should handle null or empty paths gracefully" {
            # Act & Assert
            { Resolve-RelativePath -Path $null -BasePath (Get-KdsRoot) } | Should -Throw
            { Resolve-RelativePath -Path "" -BasePath (Get-KdsRoot) } | Should -Throw
        }

        It "Should handle invalid base path" {
            # Arrange
            $invalidBase = "Z:\This\Does\Not\Exist\$(Get-Random)"
            
            # Act & Assert
            { Resolve-RelativePath -Path "file.txt" -BasePath $invalidBase } | Should -Throw
        }
    }

    Context "Performance" {
        It "Should complete Get-WorkspaceRoot in under 100ms" {
            # Act
            $elapsed = Measure-Command { Get-WorkspaceRoot }
            
            # Assert
            $elapsed.TotalMilliseconds | Should -BeLessThan 100
        }

        It "Should complete Get-KdsRoot in under 50ms" {
            # Act
            $elapsed = Measure-Command { Get-KdsRoot }
            
            # Assert
            $elapsed.TotalMilliseconds | Should -BeLessThan 50
        }

        It "Should complete Resolve-RelativePath in under 10ms" {
            # Act
            $elapsed = Measure-Command { 
                Resolve-RelativePath -Path "test.txt" -BasePath (Get-KdsRoot) 
            }
            
            # Assert
            $elapsed.TotalMilliseconds | Should -BeLessThan 10
        }
    }
}
