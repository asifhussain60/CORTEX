<#
.SYNOPSIS
    Unit tests for config-template-engine.ps1

.DESCRIPTION
    Tests the Expand-ConfigTemplate function and variable substitution logic.
    Covers basic substitution, default values, missing variables, and edge cases.

.NOTES
    Part of KDS Independence Project - Phase 3: Task 3.1
    Created: 2025-11-06
    Test Framework: Pester 5.x
#>

BeforeAll {
    # Import the template engine
    $scriptPath = Join-Path $PSScriptRoot "../../scripts/lib/config-template-engine.ps1"
    . $scriptPath
    
    # Create temp directory for test files
    $script:TestDir = Join-Path $TestDrive "config-tests"
    New-Item -ItemType Directory -Path $script:TestDir -Force | Out-Null
}

Describe "Expand-ConfigTemplate" {
    
    Context "Basic Variable Substitution" {
        
        It "Should expand single variable" {
            $template = "Hello {{NAME}}"
            $vars = @{ NAME = "World" }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be "Hello World"
        }
        
        It "Should expand multiple variables" {
            $template = "{{GREETING}} {{NAME}}, welcome to {{PLACE}}"
            $vars = @{ 
                GREETING = "Hello"
                NAME = "Alice"
                PLACE = "Wonderland"
            }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be "Hello Alice, welcome to Wonderland"
        }
        
        It "Should expand repeated variables" {
            $template = "{{NAME}} said: '{{NAME}} is the best!'"
            $vars = @{ NAME = "CORTEX" }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be "CORTEX said: 'CORTEX is the best!'"
        }
        
        It "Should preserve content without variables" {
            $template = "This is plain text with no variables"
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            $result | Should -Be $template
        }
    }
    
    Context "Default Values" {
        
        It "Should use default value when variable missing" {
            $template = "Environment: {{ENV:development}}"
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            $result | Should -Be "Environment: development"
        }
        
        It "Should override default when variable provided" {
            $template = "Environment: {{ENV:development}}"
            $vars = @{ ENV = "production" }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be "Environment: production"
        }
        
        It "Should handle empty default value" {
            $template = "Optional: {{OPTIONAL:}}"
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            $result | Should -Be "Optional: "
        }
        
        It "Should handle default with special characters" {
            $template = "Path: {{PATH:C:\Default\Path}}"
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            $result | Should -Be "Path: C:\Default\Path"
        }
    }
    
    Context "Error Handling" {
        
        It "Should throw when required variable missing" {
            $template = "Required: {{MISSING_VAR}}"
            
            { Expand-ConfigTemplate -TemplateContent $template } | Should -Throw "*Required variable not found: MISSING_VAR*"
        }
        
        It "Should throw when template file not found" {
            $invalidPath = Join-Path $TestDrive "nonexistent.template.json"
            
            { Expand-ConfigTemplate -TemplatePath $invalidPath } | Should -Throw "*Template file not found*"
        }
        
        It "Should provide helpful error message for missing variables" {
            $template = "{{VAR1}} and {{VAR2}}"
            $vars = @{ VAR1 = "Present" }
            
            { Expand-ConfigTemplate -TemplateContent $template -Variables $vars } | Should -Throw "*VAR2*"
        }
    }
    
    Context "Built-in Variables" {
        
        It "Should provide TIMESTAMP variable" {
            $template = "Generated: {{TIMESTAMP}}"
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            # Should match ISO 8601 format
            $result | Should -Match "Generated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
        }
        
        It "Should allow custom variables to override built-ins" {
            $template = "Timestamp: {{TIMESTAMP}}"
            $vars = @{ TIMESTAMP = "2025-01-01T00:00:00Z" }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be "Timestamp: 2025-01-01T00:00:00Z"
        }
    }
    
    Context "File-based Templates" {
        
        BeforeEach {
            $script:TemplatePath = Join-Path $TestDir "test.template.json"
        }
        
        It "Should expand template from file" {
            $templateContent = '{"name": "{{PROJECT_NAME:TestProject}}"}'
            Set-Content -Path $script:TemplatePath -Value $templateContent -NoNewline
            
            $result = Expand-ConfigTemplate -TemplatePath $script:TemplatePath
            
            $result | Should -Be '{"name": "TestProject"}'
        }
        
        It "Should write output to file" {
            $templateContent = '{"version": "{{VERSION}}"}'
            Set-Content -Path $script:TemplatePath -Value $templateContent -NoNewline
            
            $outputPath = Join-Path $TestDir "output.json"
            $vars = @{ VERSION = "1.0.0" }
            
            Expand-ConfigTemplate -TemplatePath $script:TemplatePath -Variables $vars -OutputPath $outputPath -Force
            
            $content = Get-Content -Path $outputPath -Raw
            $content | Should -Be '{"version": "1.0.0"}'
        }
        
        It "Should create output directory if missing" {
            $templateContent = "Test"
            Set-Content -Path $script:TemplatePath -Value $templateContent -NoNewline
            
            $outputPath = Join-Path $TestDir "nested/deeper/output.txt"
            
            Expand-ConfigTemplate -TemplatePath $script:TemplatePath -OutputPath $outputPath -Force
            
            Test-Path $outputPath | Should -Be $true
        }
    }
    
    Context "JSON Template Support" {
        
        It "Should expand JSON template" {
            $template = @"
{
  "project": "{{PROJECT_NAME}}",
  "version": "{{VERSION:1.0.0}}",
  "environment": "{{ENV}}",
  "paths": {
    "root": "{{PROJECT_ROOT}}",
    "logs": "{{PROJECT_ROOT}}/logs"
  }
}
"@
            $vars = @{
                PROJECT_NAME = "MyApp"
                ENV = "production"
                PROJECT_ROOT = "/app"
            }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            # Validate JSON is valid
            { $result | ConvertFrom-Json } | Should -Not -Throw
            
            $json = $result | ConvertFrom-Json
            $json.project | Should -Be "MyApp"
            $json.version | Should -Be "1.0.0"
            $json.environment | Should -Be "production"
            $json.paths.root | Should -Be "/app"
            $json.paths.logs | Should -Be "/app/logs"
        }
    }
    
    Context "YAML Template Support" {
        
        It "Should expand YAML template" {
            $template = @"
project: '{{PROJECT_NAME}}'
version: '{{VERSION:1.0.0}}'
environment: {{ENV}}
paths:
  root: '{{PROJECT_ROOT}}'
  config: '{{PROJECT_ROOT}}/config'
"@
            $vars = @{
                PROJECT_NAME = "MyService"
                ENV = "staging"
                PROJECT_ROOT = "/srv/myservice"
            }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Match "project: 'MyService'"
            $result | Should -Match "version: '1.0.0'"
            $result | Should -Match "environment: staging"
            $result | Should -Match "root: '/srv/myservice'"
        }
    }
    
    Context "Markdown Template Support" {
        
        It "Should expand Markdown template" {
            $template = @"
# {{PROJECT_NAME}}

**Version:** {{VERSION:1.0.0}}  
**Environment:** {{ENV}}

## Configuration

Project root: \`{{PROJECT_ROOT}}\`  
Generated: {{TIMESTAMP}}
"@
            $vars = @{
                PROJECT_NAME = "CORTEX"
                ENV = "development"
                PROJECT_ROOT = "/cortex"
            }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Match "# CORTEX"
            $result | Should -Match "\*\*Version:\*\* 1\.0\.0"
            $result | Should -Match "\*\*Environment:\*\* development"
            $result | Should -Match "Project root: /cortex"
        }
    }
    
    Context "Edge Cases" {
        
        It "Should handle empty template" {
            $template = ""
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            $result | Should -Be ""
        }
        
        It "Should handle template with only whitespace" {
            $template = "   `n  `n  "
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            $result | Should -Be $template
        }
        
        It "Should handle malformed variable syntax" {
            $template = "Bad: {NAME} or {{NAME or NAME}}"
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            # Should preserve malformed syntax unchanged
            $result | Should -Be $template
        }
        
        It "Should handle variable names with underscores" {
            $template = "{{MY_VAR_NAME}}"
            $vars = @{ MY_VAR_NAME = "test" }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be "test"
        }
        
        It "Should handle variable names with numbers" {
            $template = "{{VAR123}}"
            $vars = @{ VAR123 = "numeric" }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be "numeric"
        }
        
        It "Should ignore lowercase variable names" {
            $template = "{{lowercase}}"
            
            $result = Expand-ConfigTemplate -TemplateContent $template
            
            # Should not match lowercase - preserve as-is
            $result | Should -Be "{{lowercase}}"
        }
        
        It "Should handle special characters in values" {
            $template = "Path: {{PATH}}"
            $vars = @{ PATH = 'C:\Program Files\App (x86)\file.txt' }
            
            $result = Expand-ConfigTemplate -TemplateContent $template -Variables $vars
            
            $result | Should -Be 'Path: C:\Program Files\App (x86)\file.txt'
        }
    }
}

Describe "Test-TemplateVariables" {
    
    BeforeEach {
        $script:TemplatePath = Join-Path $TestDir "validate.template.json"
    }
    
    Context "Template Validation" {
        
        It "Should return true when all variables available" {
            $template = '{"name": "{{NAME}}", "version": "{{VERSION:1.0}}"}'
            Set-Content -Path $script:TemplatePath -Value $template -NoNewline
            
            $vars = @{ NAME = "Test" }
            
            $result = Test-TemplateVariables -TemplatePath $script:TemplatePath -Variables $vars
            
            $result | Should -Be $true
        }
        
        It "Should return false when required variables missing" {
            $template = '{"name": "{{NAME}}", "required": "{{REQUIRED}}"}'
            Set-Content -Path $script:TemplatePath -Value $template -NoNewline
            
            $vars = @{ NAME = "Test" }
            
            $result = Test-TemplateVariables -TemplatePath $script:TemplatePath -Variables $vars -WarningAction SilentlyContinue
            
            $result | Should -Be $false
        }
        
        It "Should accept templates with only defaults" {
            $template = '{"optional": "{{OPT:default}}"}'
            Set-Content -Path $script:TemplatePath -Value $template -NoNewline
            
            $result = Test-TemplateVariables -TemplatePath $script:TemplatePath
            
            $result | Should -Be $true
        }
    }
}

Describe "Get-BuiltInVariables" {
    
    It "Should return hashtable" {
        $vars = Get-BuiltInVariables
        
        $vars | Should -BeOfType [hashtable]
    }
    
    It "Should include TIMESTAMP" {
        $vars = Get-BuiltInVariables
        
        $vars.ContainsKey('TIMESTAMP') | Should -Be $true
        $vars['TIMESTAMP'] | Should -Match "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
    }
    
    It "Should not throw if git unavailable" {
        # This test just ensures graceful handling
        { Get-BuiltInVariables } | Should -Not -Throw
    }
}
