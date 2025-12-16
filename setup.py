"""
CORTEX Package Setup
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

Version: 3.9.0 (Planning System 3.0 - Production Package)
Status: Production Ready
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#") and "=" in line
        ]

setup(
    name="cortex-ai",
    version="3.9.0",
    author="Asif Hussain",
    author_email="asif@cortexai.dev",
    description="AI enhancement system that gives GitHub Copilot long-term memory, context awareness, and strategic planning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asifhussain60/CORTEX",
    project_urls={
        "Bug Tracker": "https://github.com/asifhussain60/CORTEX/issues",
        "Documentation": "https://github.com/asifhussain60/CORTEX",
        "Source Code": "https://github.com/asifhussain60/CORTEX",
    },
    packages=find_packages(
        where=".",
        include=["src*", "cortex_brain*"],
        exclude=["tests", "tests.*", "docs", "examples", "scripts.temp", "archive"]
    ),
    package_dir={
        "": ".",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "optional": [
            "tree-sitter>=0.20.0",
            "tree-sitter-python>=0.20.0",
            "scikit-learn>=1.3.0",
            "numpy>=1.24.0",
            "send2trash>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cortex=src.main:main",
            "cortex-plan=src.entry_point.planning_gate:plan_command",
            "cortex-approve=src.entry_point.planning_gate:approve_command",
            "cortex-reject=src.entry_point.planning_gate:reject_command",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "*.yaml",
            "*.yml",
            "*.json",
            "*.jsonl",
            "*.md",
            "*.txt",
            "*.prompt.md",
            "*.sql",
            "*.db",
        ],
        "cortex_brain": [
            "**/*.yaml",
            "**/*.yml",
            "**/*.json",
            "**/*.jsonl",
            "**/*.md",
            "**/*.txt",
            "**/*.sql",
            "**/*.db",
        ],
        "src": [
            "**/*.yaml",
            "**/*.yml",
            "**/*.json",
            "**/*.md",
        ],
    },
    zip_safe=False,
)
