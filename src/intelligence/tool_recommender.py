"""
Tool Recommendation Engine
Recommends development tools based on detected languages

Features:
- Language-specific IDE extensions
- Linters and code analyzers
- Code formatters
- Testing frameworks
- Debuggers

Supported Languages:
- Python, JavaScript/TypeScript, C#, Ruby
- Go, Rust, PHP, Java, Swift, ColdFusion
"""

from pathlib import Path
from typing import Dict, List


class ToolRecommender:
    """Recommends development tools for detected languages."""
    
    # Tool recommendations database
    TOOL_RECOMMENDATIONS = {
        "python": [
            {
                "name": "pylint",
                "category": "linter",
                "description": "Python code analyzer",
                "install_command": "pip install pylint"
            },
            {
                "name": "flake8",
                "category": "linter",
                "description": "Python linter combining multiple tools",
                "install_command": "pip install flake8"
            },
            {
                "name": "mypy",
                "category": "linter",
                "description": "Static type checker for Python",
                "install_command": "pip install mypy"
            },
            {
                "name": "black",
                "category": "formatter",
                "description": "Uncompromising Python code formatter",
                "install_command": "pip install black"
            },
            {
                "name": "autopep8",
                "category": "formatter",
                "description": "Automatic Python code formatter",
                "install_command": "pip install autopep8"
            },
            {
                "name": "pytest",
                "category": "testing",
                "description": "Python testing framework",
                "install_command": "pip install pytest"
            },
            {
                "name": "unittest",
                "category": "testing",
                "description": "Built-in Python testing framework",
                "install_command": "Built-in (no installation required)"
            },
            {
                "name": "Python (VS Code)",
                "category": "ide",
                "description": "Official Python extension for VS Code",
                "install_command": "Install from VS Code marketplace: ms-python.python"
            },
            {
                "name": "Pylance",
                "category": "ide",
                "description": "Fast Python language server",
                "install_command": "Install from VS Code marketplace: ms-python.vscode-pylance"
            }
        ],
        "javascript": [
            {
                "name": "eslint",
                "category": "linter",
                "description": "JavaScript linter",
                "install_command": "npm install -g eslint"
            },
            {
                "name": "prettier",
                "category": "formatter",
                "description": "Opinionated code formatter",
                "install_command": "npm install -g prettier"
            },
            {
                "name": "jest",
                "category": "testing",
                "description": "JavaScript testing framework",
                "install_command": "npm install -g jest"
            },
            {
                "name": "ESLint (VS Code)",
                "category": "ide",
                "description": "VS Code ESLint extension",
                "install_command": "Install from VS Code marketplace: dbaeumer.vscode-eslint"
            }
        ],
        "typescript": [
            {
                "name": "typescript",
                "category": "linter",
                "description": "TypeScript compiler and type checker",
                "install_command": "npm install -g typescript"
            },
            {
                "name": "eslint",
                "category": "linter",
                "description": "JavaScript/TypeScript linter",
                "install_command": "npm install -g eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin"
            },
            {
                "name": "prettier",
                "category": "formatter",
                "description": "Opinionated code formatter",
                "install_command": "npm install -g prettier"
            },
            {
                "name": "jest",
                "category": "testing",
                "description": "TypeScript testing framework",
                "install_command": "npm install -g jest @types/jest ts-jest"
            }
        ],
        "csharp": [
            {
                "name": "OmniSharp",
                "category": "ide",
                "description": "C# language server for VS Code",
                "install_command": "Install from VS Code marketplace: ms-dotnettools.csharp"
            },
            {
                "name": "Roslyn",
                "category": "linter",
                "description": ".NET compiler platform with analyzers",
                "install_command": "Built into .NET SDK"
            },
            {
                "name": "dotnet format",
                "category": "formatter",
                "description": "Code formatter for .NET",
                "install_command": "dotnet tool install -g dotnet-format"
            },
            {
                "name": "xUnit",
                "category": "testing",
                "description": ".NET testing framework",
                "install_command": "dotnet add package xunit"
            }
        ],
        "ruby": [
            {
                "name": "rubocop",
                "category": "linter",
                "description": "Ruby code analyzer",
                "install_command": "gem install rubocop"
            },
            {
                "name": "ruby-beautify",
                "category": "formatter",
                "description": "Ruby code formatter",
                "install_command": "gem install ruby-beautify"
            },
            {
                "name": "rspec",
                "category": "testing",
                "description": "Ruby testing framework",
                "install_command": "gem install rspec"
            },
            {
                "name": "Ruby (VS Code)",
                "category": "ide",
                "description": "Ruby extension for VS Code",
                "install_command": "Install from VS Code marketplace: rebornix.ruby"
            }
        ],
        "go": [
            {
                "name": "golint",
                "category": "linter",
                "description": "Go linter",
                "install_command": "go install golang.org/x/lint/golint@latest"
            },
            {
                "name": "gofmt",
                "category": "formatter",
                "description": "Go code formatter (built-in)",
                "install_command": "Built into Go toolchain"
            },
            {
                "name": "go test",
                "category": "testing",
                "description": "Built-in Go testing",
                "install_command": "Built into Go toolchain"
            },
            {
                "name": "Go (VS Code)",
                "category": "ide",
                "description": "Go extension for VS Code",
                "install_command": "Install from VS Code marketplace: golang.go"
            }
        ],
        "rust": [
            {
                "name": "clippy",
                "category": "linter",
                "description": "Rust linter",
                "install_command": "rustup component add clippy"
            },
            {
                "name": "rustfmt",
                "category": "formatter",
                "description": "Rust code formatter",
                "install_command": "rustup component add rustfmt"
            },
            {
                "name": "cargo test",
                "category": "testing",
                "description": "Built-in Rust testing",
                "install_command": "Built into Cargo"
            },
            {
                "name": "rust-analyzer",
                "category": "ide",
                "description": "Rust language server",
                "install_command": "Install from VS Code marketplace: rust-lang.rust-analyzer"
            }
        ],
        "php": [
            {
                "name": "phpcs",
                "category": "linter",
                "description": "PHP Code Sniffer",
                "install_command": "composer global require squizlabs/php_codesniffer"
            },
            {
                "name": "php-cs-fixer",
                "category": "formatter",
                "description": "PHP coding standards fixer",
                "install_command": "composer global require friendsofphp/php-cs-fixer"
            },
            {
                "name": "phpunit",
                "category": "testing",
                "description": "PHP testing framework",
                "install_command": "composer require --dev phpunit/phpunit"
            }
        ],
        "java": [
            {
                "name": "checkstyle",
                "category": "linter",
                "description": "Java code analyzer",
                "install_command": "Add to Maven/Gradle build file"
            },
            {
                "name": "google-java-format",
                "category": "formatter",
                "description": "Google Java code formatter",
                "install_command": "Download from GitHub releases"
            },
            {
                "name": "junit",
                "category": "testing",
                "description": "Java testing framework",
                "install_command": "Add to Maven/Gradle dependencies"
            },
            {
                "name": "Java Extension Pack",
                "category": "ide",
                "description": "Java extensions for VS Code",
                "install_command": "Install from VS Code marketplace: vscjava.vscode-java-pack"
            }
        ],
        "swift": [
            {
                "name": "swiftlint",
                "category": "linter",
                "description": "Swift linter",
                "install_command": "brew install swiftlint (macOS)"
            },
            {
                "name": "swiftformat",
                "category": "formatter",
                "description": "Swift code formatter",
                "install_command": "brew install swiftformat (macOS)"
            },
            {
                "name": "XCTest",
                "category": "testing",
                "description": "Swift testing framework",
                "install_command": "Built into Swift"
            }
        ],
        "coldfusion": [
            {
                "name": "CFLint",
                "category": "linter",
                "description": "ColdFusion linter",
                "install_command": "Download from cflint.org"
            },
            {
                "name": "CFFormat",
                "category": "formatter",
                "description": "ColdFusion code formatter",
                "install_command": "Available as CommandBox module: box install cfformat"
            },
            {
                "name": "TestBox",
                "category": "testing",
                "description": "ColdFusion testing framework",
                "install_command": "box install testbox"
            },
            {
                "name": "CFML (VS Code)",
                "category": "ide",
                "description": "ColdFusion extension for VS Code",
                "install_command": "Install from VS Code marketplace: KamasamaK.vscode-cfml"
            }
        ]
    }
    
    def __init__(self, workspace_path: str):
        """
        Initialize recommender.
        
        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)
    
    def recommend(self, languages: List[str]) -> Dict[str, List[Dict]]:
        """
        Recommend tools for detected languages.
        
        Args:
            languages: List of language names (e.g., ["python", "javascript"])
        
        Returns:
            Dict mapping language names to tool recommendations
        """
        recommendations = {}
        
        for language in languages:
            # Normalize language name to lowercase
            normalized_lang = language.lower()
            
            # Get recommendations for this language
            if normalized_lang in self.TOOL_RECOMMENDATIONS:
                recommendations[normalized_lang] = self.TOOL_RECOMMENDATIONS[normalized_lang]
        
        return recommendations
