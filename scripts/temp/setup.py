"""
CORTEX Package Setup
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from setuptools import setup, find_packages
import os
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
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="cortex-ai",
    version="5.2.0",
    author="Asif Hussain",
    author_email="asif@cortexai.dev",
    description="AI enhancement system that gives GitHub Copilot long-term memory, context awareness, and strategic planning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asifhussain60/CORTEX",
    project_urls={
        "Bug Tracker": "https://github.com/asifhussain60/CORTEX/issues",
        "Documentation": "https://github.com/asifhussain60/CORTEX/docs",
        "Source Code": "https://github.com/asifhussain60/CORTEX",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
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
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
            "mkdocs-mermaid2-plugin>=1.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cortex=src.main:main",
            "cortex-setup=scripts.setup_cortex:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "*.yaml",
            "*.yml",
            "*.json",
            "*.md",
            "*.txt",
        ],
    },
    zip_safe=False,
    license="Proprietary",
    keywords="ai copilot memory context planning assistant cognitive-framework",
)
