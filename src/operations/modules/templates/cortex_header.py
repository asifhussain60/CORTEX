"""
CORTEX Header Template Generator

Provides standardized branding header for all planning documents,
reports, and generated markdown files.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from typing import Optional, Dict
from datetime import datetime


CORTEX_ASCII_LOGO = """<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->"""


def generate_cortex_header(
    document_title: str,
    document_type: str,
    status: str = "🟡 In Progress",
    version: Optional[str] = None,
    additional_metadata: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate standardized CORTEX header for markdown documents.
    
    Args:
        document_title: Title of the document (H1 level)
        document_type: Type classification (Master Plan, Sub-Plan, Report, etc.)
        status: Document status with emoji
        version: Version number (optional)
        additional_metadata: Extra metadata fields (optional)
    
    Returns:
        Formatted markdown header with CORTEX branding
    
    Example:
        >>> header = generate_cortex_header(
        ...     document_title="CORTEX Evolution v3.9",
        ...     document_type="Tier 4 Complex Plan",
        ...     status="🟡 In Progress",
        ...     version="3.9.0"
        ... )
    """
    created_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Build metadata section
    metadata = [
        f"**Type:** {document_type}",
        f"**Status:** {status}",
        f"**Created:** {created_date}"
    ]
    
    if version:
        metadata.append(f"**Version:** {version}")
    
    if additional_metadata:
        for key, value in additional_metadata.items():
            metadata.append(f"**{key}:** {value}")
    
    # Assemble header
    header_parts = [
        CORTEX_ASCII_LOGO,
        "",
        f"# {document_title}",
        "",
        "\n".join(metadata),
        "",
        "---",
        ""
    ]
    
    return "\n".join(header_parts)


def generate_sub_plan_header(
    phase_id: str,
    phase_name: str,
    master_plan_path: str,
    status: str = "⏳ Pending",
    version: Optional[str] = None
) -> str:
    """
    Generate header specifically for sub-plan documents.
    
    Args:
        phase_id: Phase identifier (e.g., "04")
        phase_name: Human-readable phase name
        master_plan_path: Relative path to master plan
        status: Phase status
        version: Version number (optional)
    
    Returns:
        Formatted sub-plan header with breadcrumb navigation
    """
    created_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Build metadata
    metadata = [
        f"**🔗 Breadcrumb:** [← Back to Master Plan]({master_plan_path})",
        "",
        f"**Status:** {status}",
        f"**Phase ID:** {phase_id}",
        f"**Created:** {created_date}"
    ]
    
    if version:
        metadata.append(f"**Version:** {version}")
    
    # Assemble header
    header_parts = [
        CORTEX_ASCII_LOGO,
        "",
        f"# {phase_name}",
        "",
        "\n".join(metadata),
        "",
        "---",
        ""
    ]
    
    return "\n".join(header_parts)


def generate_report_header(
    report_title: str,
    report_type: str,
    project_name: Optional[str] = None
) -> str:
    """
    Generate header for analysis reports and summaries.
    
    Args:
        report_title: Title of the report
        report_type: Type of report (Analysis, Summary, Investigation, etc.)
        project_name: Name of project being analyzed (optional)
    
    Returns:
        Formatted report header
    """
    generated_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Build metadata
    metadata = [
        f"**Type:** {report_type}",
        f"**Generated:** {generated_date}"
    ]
    
    if project_name:
        metadata.append(f"**Project:** {project_name}")
    
    # Assemble header
    header_parts = [
        CORTEX_ASCII_LOGO,
        "",
        f"# {report_title}",
        "",
        "\n".join(metadata),
        "",
        "---",
        ""
    ]
    
    return "\n".join(header_parts)


def generate_ado_header(
    feature_title: str,
    feature_type: str = "Feature",
    priority: str = "Medium",
    area_path: Optional[str] = None
) -> str:
    """
    Generate header for Azure DevOps formatted documents.
    
    Args:
        feature_title: Title of the feature/story
        feature_type: ADO work item type (Feature, User Story, Task, etc.)
        priority: Priority level
        area_path: Area path in ADO (optional)
    
    Returns:
        Formatted ADO document header
    """
    created_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Build metadata
    metadata = [
        f"**Type:** {feature_type}",
        f"**Priority:** {priority}",
        f"**Created:** {created_date}"
    ]
    
    if area_path:
        metadata.append(f"**Area Path:** {area_path}")
    
    # Assemble header
    header_parts = [
        CORTEX_ASCII_LOGO,
        "",
        f"# {feature_title}",
        "",
        "\n".join(metadata),
        "",
        "---",
        ""
    ]
    
    return "\n".join(header_parts)


def extract_document_title(content: str) -> Optional[str]:
    """
    Extract document title (H1) from markdown content.
    
    Args:
        content: Markdown document content
    
    Returns:
        Document title or None if not found
    """
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None


def has_cortex_header(content: str) -> bool:
    """
    Check if content already has CORTEX header.
    
    Args:
        content: Document content
    
    Returns:
        True if CORTEX header present
    """
    return 'CORTEX' in content and '██████╗' in content and 'AI-Powered Development Intelligence System' in content


def inject_cortex_header(
    content: str,
    header_type: str = "document",
    **kwargs
) -> str:
    """
    Inject CORTEX header into existing markdown document.
    
    Args:
        content: Existing document content
        header_type: Type of header to generate (document, sub_plan, report, ado)
        **kwargs: Arguments passed to specific header generator
    
    Returns:
        Document with CORTEX header prepended
    """
    # Check if header already exists
    if has_cortex_header(content):
        return content
    
    # Extract existing title
    title = extract_document_title(content)
    
    # Generate appropriate header
    if header_type == "document":
        header = generate_cortex_header(
            document_title=kwargs.get('document_title', title or 'Untitled Document'),
            document_type=kwargs.get('document_type', 'Document'),
            status=kwargs.get('status', '🟡 In Progress'),
            version=kwargs.get('version'),
            additional_metadata=kwargs.get('additional_metadata')
        )
    elif header_type == "sub_plan":
        header = generate_sub_plan_header(
            phase_id=kwargs.get('phase_id', '00'),
            phase_name=kwargs.get('phase_name', title or 'Phase'),
            master_plan_path=kwargs.get('master_plan_path', 'master.md'),
            status=kwargs.get('status', '⏳ Pending'),
            version=kwargs.get('version')
        )
    elif header_type == "report":
        header = generate_report_header(
            report_title=kwargs.get('report_title', title or 'Report'),
            report_type=kwargs.get('report_type', 'Analysis Report'),
            project_name=kwargs.get('project_name')
        )
    elif header_type == "ado":
        header = generate_ado_header(
            feature_title=kwargs.get('feature_title', title or 'Feature'),
            feature_type=kwargs.get('feature_type', 'Feature'),
            priority=kwargs.get('priority', 'Medium'),
            area_path=kwargs.get('area_path')
        )
    else:
        raise ValueError(f"Unknown header type: {header_type}")
    
    # Remove existing H1 title if present
    if title:
        content = content.replace(f'# {title}\n', '', 1)
    
    # Prepend header
    return header + "\n" + content.lstrip()
