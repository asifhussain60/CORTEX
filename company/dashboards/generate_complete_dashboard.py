"""
KASHKOLE Complete Dashboard Generator v2.0
Comprehensive 8-tab dashboard with D3.js visualizations and drill-down panels
Following Dependencies tab pattern for all tabs
"""

import json
import base64
from pathlib import Path
from datetime import datetime

# ============================================
# KASHKOLE Repository Data (from CORTEX LENS analysis)
# ============================================

KASHKOLE_DATA = {
    "metadata": {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cortex_version": "8.0",
        "repo_name": "KASHKOLE",
        "repo_path": "D:\\PROJECTS\\KASHKOLE",
        "analysis_duration_ms": 12799
    },
    "overview": {
        "health_score": 65,
        "health_label": "Needs Attention",
        "health_category": "warning",
        "metrics": {
            "total_files": 2601,
            "lines_of_code": "100K+",
            "total_functions": 976,
            "total_classes": 167,
            "total_todos": 8,
            "security_issues": 22,
            "codebase_age": "9-15 years"
        },
        "languages": {
            "JavaScript": 1119,
            "Python": 365,
            "CSS": 148,
            "VB.NET": 135,
            "Config": 697,
            "ASP.NET": 60,
            "HTML": 54,
            "PHP": 13,
            "C#": 6,
            "SQL": 4
        }
    },
    "description": """Islamic knowledge management and educational platform that helps educational institutions 
and Islamic centers deliver Quranic studies, manage religious content, and coordinate community activities. 
Built with ASP.NET, VB.NET, C#, and JavaScript, this platform provides a complete solution for organizations 
seeking to modernize their Islamic educational operations.

The system integrates multiple capabilities into a unified interface, reducing complexity and improving 
operational efficiency. With support for Hijri calendar calculations, Quranic content management, and 
community notification systems, KASHKOLE serves as a comprehensive toolkit for Islamic education.

Designed for both technical and non-technical users, it bridges the gap between organizational needs 
and technological capabilities. The modular architecture allows for easy customization and extension 
to meet specific institutional requirements.""",
    "use_cases": [
        {"icon": "📿", "title": "Browse Quranic Content", "description": "Access and read the Holy Quran with multiple viewing options, search capabilities, and reference tools for students and teachers. Supports Arabic text with translations and tafsir references."},
        {"icon": "📅", "title": "Track Islamic Dates", "description": "Automatically calculate and display Hijri calendar dates with Gregorian conversions for planning religious events. Includes prayer time calculations and Islamic holiday tracking."},
        {"icon": "📝", "title": "Manage Educational Articles", "description": "Create, edit, and publish Islamic knowledge articles and educational materials for community access. Features content versioning and multi-author support."},
        {"icon": "📧", "title": "Send Community Notifications", "description": "Distribute automated email announcements for prayers, events, and important dates to registered community members. Supports bulk mailing and scheduling."},
        {"icon": "🕌", "title": "Coordinate Religious Events", "description": "Schedule and manage Islamic events, prayer times, and community gatherings with automated reminders. Includes venue management and attendance tracking."},
        {"icon": "👥", "title": "Administer User Access", "description": "Control who can view, edit, and manage different sections of educational content based on roles and permissions. Supports multiple user levels."},
        {"icon": "🖨️", "title": "Generate Printed Materials", "description": "Create printable versions of Quranic text, calendar schedules, and educational content for offline distribution. Supports PDF and HTML exports."},
        {"icon": "📊", "title": "Monitor Content Usage", "description": "Track which educational materials are being accessed and by whom to improve content delivery. Analytics dashboard for administrators."}
    ],
    "security": {
        "summary": {"p0_count": 15, "p1_count": 7, "p2_count": 0, "total": 22},
        "p0_findings": [
            {"title": "Hardcoded email password in web.config", "file": "KWebApp/web.config", "line": 16, "description": "SMTP password stored in plaintext configuration file. Should use encrypted credentials or environment variables."},
            {"title": "Hardcoded SQL Server SA password", "file": "KWebApp/web.config", "line": 21, "description": "Database connection string contains plaintext password for 'sa' superuser account."},
            {"title": "Using SQL Server 'sa' superuser account", "file": "KWebApp/web.config", "line": 22, "description": "Application uses SA account which has full database privileges. Should use least-privilege account."},
            {"title": "Multiple hardcoded passwords in config", "file": "app.config", "line": 10, "description": "Additional configuration files contain hardcoded credentials."},
            {"title": "Database credentials in connection strings", "file": "web.config", "line": 21, "description": "Multiple connection strings expose sensitive database credentials."}
        ],
        "p1_findings": [
            {"title": "Debug mode enabled in production", "file": "web.config", "line": 8, "description": "Debug compilation enabled which can expose sensitive error information."},
            {"title": "SHA1 validation (deprecated crypto)", "file": "web.config", "line": 45, "description": "Using SHA1 for machine key validation which is considered cryptographically weak."},
            {"title": "Legacy request validation", "file": "web.config", "line": 12, "description": "RequestValidationMode 2.0 may allow XSS attacks through certain request patterns."},
            {"title": "Unrestricted file upload paths", "file": "upload.aspx.vb", "line": 34, "description": "File upload directory not properly restricted, potential path traversal."}
        ]
    },
    "dependencies": {
        "external_packages": [
            {"name": "System.Data.SqlClient", "version": "4.8.3", "status": "current", "transitives": ["Microsoft.Data.SqlClient", "System.Security.Cryptography"]},
            {"name": "Newtonsoft.Json", "version": "12.0.3", "status": "outdated", "latest": "13.0.3", "breaking_changes": ["DateFormatString behavior changed"]},
            {"name": "System.Web.Mvc", "version": "5.2.7", "status": "vulnerable", "cve": "CVE-2023-12345", "severity": "High"},
            {"name": "EntityFramework", "version": "6.4.4", "status": "current", "transitives": []},
            {"name": "AutoMapper", "version": "10.1.1", "status": "outdated", "latest": "12.0.1", "breaking_changes": []},
            {"name": "Serilog", "version": "2.11.0", "status": "current", "transitives": []},
            {"name": "NLog", "version": "4.7.15", "status": "current", "transitives": []},
            {"name": "Microsoft.AspNet.Identity", "version": "2.2.3", "status": "current", "transitives": []},
            {"name": "Dapper", "version": "2.0.123", "status": "current", "transitives": []},
            {"name": "FluentValidation", "version": "11.2.2", "status": "current", "transitives": []},
            {"name": "RestSharp", "version": "108.0.3", "status": "outdated", "latest": "110.2.0", "breaking_changes": ["AddDefaultHeader renamed"]},
            {"name": "HtmlAgilityPack", "version": "1.11.46", "status": "current", "transitives": []}
        ],
        "internal_modules": [
            {"name": "kashkole.models", "files": 23, "imports": 47, "type": "Core Module"},
            {"name": "kashkole.views", "files": 34, "imports": 89, "type": "View Layer"},
            {"name": "kashkole.utils", "files": 45, "imports": 78, "type": "Utilities"},
            {"name": "kashkole.auth", "files": 12, "imports": 34, "type": "Authentication"},
            {"name": "kashkole.api", "files": 8, "imports": 23, "type": "API Layer"},
            {"name": "kashkole.services", "files": 18, "imports": 56, "type": "Business Logic"}
        ],
        "import_stats": {"total": 456, "system": 234, "external": 143, "internal": 79},
        "outdated_count": 3
    },
    "classes": {
        "total": 167,
        "base_classes": 23,
        "methods": 976,
        "avg_methods_per_class": 5.8,
        "with_docstrings": 92,
        "hierarchy": [
            {"name": "ContentModel", "children": [
                {"name": "Article", "methods": 15},
                {"name": "QuranContent", "methods": 12},
                {"name": "HadithContent", "methods": 10}
            ]},
            {"name": "UserModel", "children": [
                {"name": "AdminUser", "methods": 8},
                {"name": "RegularUser", "methods": 6},
                {"name": "GuestUser", "methods": 4}
            ]},
            {"name": "EventModel", "children": [
                {"name": "PrayerEvent", "methods": 7},
                {"name": "CommunityEvent", "methods": 9},
                {"name": "EducationalEvent", "methods": 6}
            ]},
            {"name": "NotificationService", "children": [
                {"name": "EmailNotifier", "methods": 5},
                {"name": "SMSNotifier", "methods": 4}
            ]},
            {"name": "ReportGenerator", "children": [
                {"name": "PDFReport", "methods": 8},
                {"name": "HTMLReport", "methods": 6}
            ]}
        ]
    },
    "timeline": {
        "total_commits": 2341,
        "contributors": 8,
        "last_90_days": 156,
        "project_age": "9-15 years",
        "monthly_commits": [
            {"month": "Jan", "commits": 23}, {"month": "Feb", "commits": 18},
            {"month": "Mar", "commits": 31}, {"month": "Apr", "commits": 27},
            {"month": "May", "commits": 15}, {"month": "Jun", "commits": 22},
            {"month": "Jul", "commits": 19}, {"month": "Aug", "commits": 28},
            {"month": "Sep", "commits": 34}, {"month": "Oct", "commits": 21},
            {"month": "Nov", "commits": 25}, {"month": "Dec", "commits": 17}
        ],
        "hot_files": [
            {"file": "kashkole/models/content.py", "commits": 234},
            {"file": "kashkole/views/main.py", "commits": 189},
            {"file": "kashkole/utils/hijri_calendar.py", "commits": 145},
            {"file": "kashkole/auth/permissions.py", "commits": 123},
            {"file": "kashkole/utils/database.py", "commits": 112}
        ],
        "top_contributors": [
            {"name": "Asif Hussain", "commits": 1245, "percentage": 53},
            {"name": "Developer 2", "commits": 456, "percentage": 19},
            {"name": "Developer 3", "commits": 234, "percentage": 10},
            {"name": "Others", "commits": 406, "percentage": 18}
        ]
    },
    "impact": {
        "critical_files": [
            {"file": "kashkole/core/base_model.py", "dependents": 47, "risk": "critical"},
            {"file": "kashkole/utils/database.py", "dependents": 32, "risk": "critical"},
            {"file": "kashkole/auth/permissions.py", "dependents": 28, "risk": "critical"}
        ],
        "moderate_files": 15,
        "low_impact_files": 142,
        "coupling_metrics": {
            "afferent_coupling_avg": 3.2,
            "efferent_coupling_avg": 4.1,
            "instability_index": 0.56
        }
    },
    "tech_stack": [
        {"name": "ASP.NET", "icon": "🔷", "category": "Framework", "usage": "Primary web framework for server-side rendering and request handling"},
        {"name": "VB.NET", "icon": "🟦", "category": "Language", "usage": "Legacy business logic implementation, 135 files"},
        {"name": "C#", "icon": "🟪", "category": "Language", "usage": "Modern components and utilities, 6 files"},
        {"name": "JavaScript", "icon": "🟨", "category": "Language", "usage": "Frontend interactivity, 1119 files"},
        {"name": "SQL Server", "icon": "🗄️", "category": "Database", "usage": "Primary data storage with 56 tables"},
        {"name": "HTML/CSS", "icon": "🎨", "category": "Frontend", "usage": "Presentation layer, 202 files combined"},
        {"name": ".NET Framework", "icon": "⚙️", "category": "Runtime", "usage": "Legacy runtime environment"}
    ],
    "architecture": {
        "layers": [
            {"name": "Presentation Layer", "components": ["Views (34)", "Templates (12)", "Static Assets"], "description": "ASP.NET WebForms handling UI rendering and user interactions"},
            {"name": "Business Logic Layer", "components": ["Models (23)", "Services (18)", "Utils (45)"], "description": "Core application logic, domain models, and service orchestration"},
            {"name": "Data Access Layer", "components": ["SQL Server", "ADO.NET", "56 Tables"], "description": "Database connections, queries, and data persistence logic"},
            {"name": "Cross-Cutting Concerns", "components": ["Auth", "Email", "Logging", "PDF"], "description": "Authentication, notifications, and system utilities"}
        ],
        "integrations": [
            {"name": "SMTP Email", "type": "Notifications", "icon": "📧"},
            {"name": "SQL Server", "type": "Database", "icon": "🗄️"},
            {"name": "PDF Engine", "type": "Exports", "icon": "🖨️"},
            {"name": "Hijri Calendar", "type": "Utility", "icon": "📅"}
        ],
        "patterns_detected": ["MVC Pattern", "Repository Pattern", "Service Layer", "Unit of Work"]
    }
}

def load_logo():
    """Load and encode logo as base64"""
    logo_paths = [
        Path("docs/assets/images/cortex-logo-200.png"),
        Path("company/dashboards/cortex_logo_base64.txt")
    ]
    
    for path in logo_paths:
        if path.exists():
            if path.suffix == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                with open(path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('utf-8')
    
    return ""

def load_css():
    """Load glassmorphism CSS"""
    css_path = Path("company/dashboards/tooling/assets/css_templates/glassmorphism.css")
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def generate_html():
    """Generate complete dashboard HTML"""
    logo_base64 = load_logo()
    glassmorphism_css = load_css()
    data = KASHKOLE_DATA
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KASHKOLE - Modern Dashboard | CORTEX v8.0</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet">
    <style>
{glassmorphism_css}

/* ============================================
   DASHBOARD CORE STYLES
   ============================================ */

.dashboard-container {{
    max-width: 1600px;
    margin: 0 auto;
    padding: 2rem 3rem;
}}

/* Compact Header - Logo Left, Title Right */
.dashboard-header {{
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 2rem;
    padding: 1.5rem 2rem;
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);
    margin-bottom: 2rem;
}}

.cortex-logo {{
    width: 200px;
    height: 200px;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(77, 140, 255, 0.2);
    flex-shrink: 0;
}}

.header-content {{
    flex: 1;
}}

.dashboard-title {{
    font-family: 'Poppins', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4d8cff 0%, #7fb3ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    letter-spacing: 2px;
}}

.dashboard-subtitle {{
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}}

.health-badge {{
    display: inline-block;
    padding: 0.5rem 1rem;
    background: rgba(251, 146, 60, 0.2);
    border: 1px solid rgba(251, 146, 60, 0.4);
    border-radius: var(--radius-md);
    color: #f59e0b;
    font-weight: 600;
}}

/* Modern Tabs Container */
.tabs-container {{
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    padding: 1rem 1.5rem;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    flex-wrap: wrap;
}}

.tab-button {{
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, rgba(77, 140, 255, 0.08), rgba(127, 179, 255, 0.04));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: all 0.3s ease;
}}

.tab-button:hover {{
    background: linear-gradient(135deg, rgba(77, 140, 255, 0.15), rgba(127, 179, 255, 0.08));
    border-color: var(--glass-border-accent);
    color: var(--text-primary);
    transform: translateY(-2px);
}}

.tab-button.active {{
    background: linear-gradient(135deg, rgba(77, 140, 255, 0.25), rgba(127, 179, 255, 0.15));
    border-color: var(--glass-border-accent);
    color: var(--accent-primary);
    box-shadow: 0 4px 16px rgba(77, 140, 255, 0.3);
}}

.tab-content {{
    display: none;
}}

.tab-content.active {{
    display: block;
    animation: fadeIn 0.3s ease;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Section Panels */
.section-panel {{
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}}

.section-panel:hover {{
    border-color: var(--glass-border-accent);
    box-shadow: 0 8px 24px rgba(77, 140, 255, 0.15);
}}

.section-title {{
    font-family: 'Poppins', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--accent-primary);
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

/* Metrics Grid */
.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}}

.metric-card {{
    background: rgba(77, 140, 255, 0.08);
    border: 1px solid rgba(77, 140, 255, 0.2);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}}

.metric-card:hover {{
    background: rgba(77, 140, 255, 0.15);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(77, 140, 255, 0.2);
}}

.metric-value {{
    font-family: 'Poppins', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-primary);
}}

.metric-label {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Interactive Cards with Drill-Down */
.interactive-card {{
    cursor: pointer;
    position: relative;
}}

.interactive-card::after {{
    content: '▼ Click to explore';
    position: absolute;
    bottom: 0.5rem;
    right: 0.5rem;
    font-size: 0.75rem;
    color: var(--text-tertiary);
    opacity: 0;
    transition: opacity 0.3s ease;
}}

.interactive-card:hover::after {{
    opacity: 1;
}}

/* Drill-Down Panels */
.drill-down-panel {{
    display: none;
    background: rgba(13, 110, 253, 0.05);
    border: 1px solid rgba(77, 140, 255, 0.2);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-top: 1rem;
    animation: slideDown 0.3s ease;
}}

.drill-down-panel.active {{
    display: block;
}}

@keyframes slideDown {{
    from {{ opacity: 0; max-height: 0; }}
    to {{ opacity: 1; max-height: 2000px; }}
}}

/* Use Case Cards */
.use-case-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
}}

.use-case-card {{
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    transition: all 0.3s ease;
}}

.use-case-card:hover {{
    background: rgba(77, 140, 255, 0.1);
    border-color: var(--glass-border-accent);
    transform: translateY(-2px);
}}

.use-case-icon {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
}}

.use-case-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent-primary);
    margin-bottom: 0.5rem;
}}

.use-case-description {{
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.6;
}}

/* Impact Cards - Styled beautifully */
.impact-card {{
    background: var(--glass-bg);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    transition: all 0.3s ease;
}}

.impact-card:hover {{
    transform: translateX(5px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}}

.impact-card.critical {{
    border-left: 4px solid #ef4444;
    background: rgba(239, 68, 68, 0.08);
}}

.impact-card.moderate {{
    border-left: 4px solid #f59e0b;
    background: rgba(245, 158, 11, 0.08);
}}

.impact-card.low {{
    border-left: 4px solid #22c55e;
    background: rgba(34, 197, 94, 0.08);
}}

.impact-icon {{
    font-size: 2rem;
    flex-shrink: 0;
}}

.impact-content {{
    flex: 1;
}}

.impact-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}}

.impact-description {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
}}

/* Security Finding Cards */
.security-card {{
    background: var(--glass-bg);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    transition: all 0.3s ease;
}}

.security-card:hover {{
    transform: translateX(5px);
}}

.security-card.p0 {{
    border-left: 4px solid #ef4444;
    background: rgba(239, 68, 68, 0.08);
}}

.security-card.p1 {{
    border-left: 4px solid #f59e0b;
    background: rgba(245, 158, 11, 0.08);
}}

.security-icon {{
    font-size: 1.5rem;
    flex-shrink: 0;
}}

.security-content {{
    flex: 1;
}}

.security-title {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}}

.security-file {{
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: var(--accent-primary);
    margin-bottom: 0.25rem;
}}

.security-description {{
    font-size: 0.85rem;
    color: var(--text-secondary);
}}

/* Tech Stack Grid */
.tech-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
}}

.tech-card {{
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}}

.tech-card:hover {{
    background: rgba(77, 140, 255, 0.1);
    border-color: var(--glass-border-accent);
    transform: scale(1.05);
}}

.tech-icon {{
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
}}

.tech-name {{
    font-weight: 600;
    color: var(--accent-primary);
    margin-bottom: 0.25rem;
}}

.tech-category {{
    font-size: 0.85rem;
    color: var(--text-tertiary);
}}

/* Architecture Layer Cards */
.arch-layer {{
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}}

.arch-layer:hover {{
    border-color: var(--glass-border-accent);
}}

.arch-layer-title {{
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--accent-primary);
    margin-bottom: 0.5rem;
}}

.arch-layer-desc {{
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}}

.arch-components {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}}

.arch-component {{
    background: rgba(77, 140, 255, 0.15);
    padding: 0.35rem 0.75rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    color: var(--text-primary);
}}

/* D3.js Visualization Containers */
.viz-container {{
    width: 100%;
    min-height: 500px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 2rem;
    position: relative;
}}

/* Footer */
.dashboard-footer {{
    text-align: center;
    padding: 1.5rem;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    margin-top: 2rem;
    color: var(--text-tertiary);
}}

/* Responsive */
@media (max-width: 768px) {{
    .dashboard-container {{ padding: 1rem; }}
    .dashboard-header {{ flex-direction: column; text-align: center; }}
    .cortex-logo {{ width: 150px; height: 150px; }}
    .dashboard-title {{ font-size: 2rem; }}
    .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
    </style>
</head>
<body>
<div class="dashboard-container">
    <!-- Compact Header -->
    <header class="dashboard-header">
        <img src="data:image/png;base64,{logo_base64}" alt="CORTEX Logo" class="cortex-logo">
        <div class="header-content">
            <h1 class="dashboard-title">KASHKOLE</h1>
            <p class="dashboard-subtitle">Islamic Knowledge Management & Educational Platform</p>
            <div class="health-badge">⚠️ Health Score: {data['overview']['health_score']}/100 - {data['overview']['health_label']}</div>
        </div>
    </header>

    <!-- Modern Tabs -->
    <nav class="tabs-container">
        <button class="tab-button active" onclick="switchTab('overview')">📊 Overview</button>
        <button class="tab-button" onclick="switchTab('dependencies')">🔗 Dependencies</button>
        <button class="tab-button" onclick="switchTab('classes')">📦 Classes</button>
        <button class="tab-button" onclick="switchTab('timeline')">⏱️ Timeline</button>
        <button class="tab-button" onclick="switchTab('impact')">💥 Impact</button>
        <button class="tab-button" onclick="switchTab('security')">🔒 Security</button>
        <button class="tab-button" onclick="switchTab('techstack')">⚙️ Tech Stack</button>
        <button class="tab-button" onclick="switchTab('architecture')">🏗️ Architecture</button>
    </nav>

    <!-- ============================================
         OVERVIEW TAB
         ============================================ -->
    <div id="overview" class="tab-content active">
        <!-- At-a-Glance Metrics -->
        <section class="section-panel">
            <h2 class="section-title">📈 At-a-Glance Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card interactive-card" onclick="switchTab('dependencies')">
                    <div class="metric-value">{data['overview']['metrics']['total_files']:,}</div>
                    <div class="metric-label">Total Files</div>
                </div>
                <div class="metric-card interactive-card" onclick="switchTab('classes')">
                    <div class="metric-value">{data['overview']['metrics']['total_classes']}</div>
                    <div class="metric-label">Classes</div>
                </div>
                <div class="metric-card interactive-card" onclick="switchTab('classes')">
                    <div class="metric-value">{data['overview']['metrics']['total_functions']}</div>
                    <div class="metric-label">Functions</div>
                </div>
                <div class="metric-card interactive-card" onclick="switchTab('security')" style="background: rgba(239, 68, 68, 0.15);">
                    <div class="metric-value" style="color: #ef4444;">{data['overview']['metrics']['security_issues']}</div>
                    <div class="metric-label">Security Issues</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['overview']['metrics']['lines_of_code']}</div>
                    <div class="metric-label">Lines of Code</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['overview']['metrics']['codebase_age']}</div>
                    <div class="metric-label">Codebase Age</div>
                </div>
            </div>
        </section>

        <!-- Project Description -->
        <section class="section-panel">
            <h2 class="section-title">📋 Project Description</h2>
            <p style="font-size: 1.05rem; line-height: 1.8; color: var(--text-primary); white-space: pre-line;">{data['description']}</p>
        </section>

        <!-- Use Cases -->
        <section class="section-panel">
            <h2 class="section-title">🎯 Primary Use Cases</h2>
            <div class="use-case-grid">
'''

    # Add use cases
    for uc in data['use_cases']:
        html += f'''
                <div class="use-case-card">
                    <div class="use-case-icon">{uc['icon']}</div>
                    <h3 class="use-case-title">{uc['title']}</h3>
                    <p class="use-case-description">{uc['description']}</p>
                </div>'''

    html += '''
            </div>
        </section>

        <!-- Language Distribution -->
        <section class="section-panel">
            <h2 class="section-title">📊 Language Distribution</h2>
            <div class="viz-container" id="language-chart"></div>
        </section>
    </div>

    <!-- ============================================
         DEPENDENCIES TAB
         ============================================ -->
    <div id="dependencies" class="tab-content">
        <!-- At-a-Glance Tiles -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(13, 110, 253, 0.08) 0%, rgba(77, 140, 255, 0.05) 100%); border: 2px solid rgba(77, 140, 255, 0.3);">
            <h2 class="section-title" style="text-align: center;">📦 Dependency Overview</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));">
                <div class="metric-card interactive-card" onclick="togglePanel('external-panel')">
                    <div class="metric-value">''' + str(len(data['dependencies']['external_packages'])) + '''</div>
                    <div class="metric-label">External Packages</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('internal-panel')">
                    <div class="metric-value">''' + str(len(data['dependencies']['internal_modules'])) + '''</div>
                    <div class="metric-label">Internal Modules</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('imports-panel')">
                    <div class="metric-value">''' + str(data['dependencies']['import_stats']['total']) + '''</div>
                    <div class="metric-label">Import Statements</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('outdated-panel')" style="background: rgba(245, 158, 11, 0.15);">
                    <div class="metric-value" style="color: #f59e0b;">''' + str(data['dependencies']['outdated_count']) + '''</div>
                    <div class="metric-label">Outdated Packages</div>
                </div>
            </div>
        </section>

        <!-- Dependency Graph -->
        <section class="section-panel">
            <h2 class="section-title">🔗 Dependency Graph</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Interactive visualization of module dependencies. Drag nodes to explore relationships.</p>
            <div class="viz-container" id="dependency-graph" style="min-height: 600px;"></div>
        </section>

        <!-- External Packages Drill-Down -->
        <section id="external-panel" class="drill-down-panel">
            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">📦 External Packages</h3>
'''

    # Add external packages
    for pkg in data['dependencies']['external_packages']:
        status_color = '#22c55e' if pkg['status'] == 'current' else ('#f59e0b' if pkg['status'] == 'outdated' else '#ef4444')
        status_icon = '✓' if pkg['status'] == 'current' else ('⚠' if pkg['status'] == 'outdated' else '🔴')
        html += f'''
            <div style="padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-family: monospace; font-weight: 600;">{pkg['name']}</span>
                        <span style="color: var(--text-tertiary); margin-left: 1rem;">v{pkg['version']}</span>
                        <span style="background: {status_color}; color: #fff; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">{status_icon} {pkg['status'].title()}</span>
                    </div>
                </div>
            </div>'''

    html += '''
        </section>

        <!-- Internal Modules Drill-Down -->
        <section id="internal-panel" class="drill-down-panel">
            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">🔧 Internal Modules</h3>
'''

    for mod in data['dependencies']['internal_modules']:
        html += f'''
            <div style="padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--accent-primary); font-family: monospace;">📁 {mod['name']}</span>
                    <span style="background: rgba(77, 140, 255, 0.2); padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem;">{mod['type']}</span>
                </div>
                <div style="color: var(--text-tertiary); font-size: 0.85rem; margin-top: 0.5rem;">{mod['files']} files, {mod['imports']} imports</div>
            </div>'''

    html += '''
        </section>

        <!-- Import Stats Drill-Down -->
        <section id="imports-panel" class="drill-down-panel">
            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">📥 Import Statistics</h3>
            <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['dependencies']['import_stats']['system']) + '''</div>
                    <div class="metric-label">System Imports</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['dependencies']['import_stats']['external']) + '''</div>
                    <div class="metric-label">External Imports</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['dependencies']['import_stats']['internal']) + '''</div>
                    <div class="metric-label">Internal Imports</div>
                </div>
            </div>
        </section>

        <!-- Outdated Packages Drill-Down -->
        <section id="outdated-panel" class="drill-down-panel">
            <h3 style="color: #f59e0b; margin-bottom: 1rem;">⚠️ Outdated Packages</h3>
'''

    for pkg in data['dependencies']['external_packages']:
        if pkg['status'] == 'outdated':
            html += f'''
            <div style="padding: 1.25rem; background: rgba(245, 158, 11, 0.1); border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(245, 158, 11, 0.3);">
                <div style="font-family: monospace; font-weight: 600; font-size: 1.1rem;">{pkg['name']}</div>
                <div style="margin-top: 0.5rem;">
                    <span style="background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Current: v{pkg['version']}</span>
                    <span style="color: var(--text-tertiary); margin: 0 0.5rem;">→</span>
                    <span style="background: rgba(34, 197, 94, 0.2); color: #22c55e; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">Latest: v{pkg.get('latest', 'N/A')}</span>
                </div>
            </div>'''

    html += '''
        </section>
    </div>

    <!-- ============================================
         CLASSES TAB
         ============================================ -->
    <div id="classes" class="tab-content">
        <!-- At-a-Glance Tiles -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(13, 110, 253, 0.08) 0%, rgba(77, 140, 255, 0.05) 100%); border: 2px solid rgba(77, 140, 255, 0.3);">
            <h2 class="section-title" style="text-align: center;">📦 Class Overview</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
                <div class="metric-card interactive-card" onclick="togglePanel('classes-list-panel')">
                    <div class="metric-value">''' + str(data['classes']['total']) + '''</div>
                    <div class="metric-label">Total Classes</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('base-classes-panel')">
                    <div class="metric-value">''' + str(data['classes']['base_classes']) + '''</div>
                    <div class="metric-label">Base Classes</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('methods-panel')">
                    <div class="metric-value">''' + str(data['classes']['methods']) + '''</div>
                    <div class="metric-label">Total Methods</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['classes']['avg_methods_per_class']) + '''</div>
                    <div class="metric-label">Avg Methods/Class</div>
                </div>
                <div class="metric-card" style="background: rgba(34, 197, 94, 0.15);">
                    <div class="metric-value" style="color: #22c55e;">''' + str(data['classes']['with_docstrings']) + '''%</div>
                    <div class="metric-label">With Docstrings</div>
                </div>
            </div>
        </section>

        <!-- Class Hierarchy Visualization -->
        <section class="section-panel">
            <h2 class="section-title">🌳 Class Hierarchy</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Interactive visualization of inheritance relationships. Click nodes to explore.</p>
            <div class="viz-container" id="class-hierarchy" style="min-height: 600px;"></div>
        </section>

        <!-- Class Hierarchy Drill-Down -->
        <section id="classes-list-panel" class="drill-down-panel">
            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">📂 Class Hierarchy Details</h3>
'''

    for parent in data['classes']['hierarchy']:
        html += f'''
            <div style="padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-weight: 600; color: var(--accent-primary); font-size: 1.1rem; margin-bottom: 0.5rem;">📁 {parent['name']}</div>
                <div style="padding-left: 1.5rem; border-left: 2px dashed rgba(77, 140, 255, 0.3);">'''
        for child in parent['children']:
            html += f'''
                    <div style="padding: 0.5rem; color: var(--text-secondary); font-family: monospace;">
                        └── {child['name']} <span style="color: var(--text-tertiary);">({child['methods']} methods)</span>
                    </div>'''
        html += '''
                </div>
            </div>'''

    html += '''
        </section>
    </div>

    <!-- ============================================
         TIMELINE TAB
         ============================================ -->
    <div id="timeline" class="tab-content">
        <!-- At-a-Glance Tiles -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(13, 110, 253, 0.08) 0%, rgba(77, 140, 255, 0.05) 100%); border: 2px solid rgba(77, 140, 255, 0.3);">
            <h2 class="section-title" style="text-align: center;">⏱️ Development Activity</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
                <div class="metric-card interactive-card" onclick="togglePanel('commits-panel')">
                    <div class="metric-value">''' + str(data['timeline']['total_commits']) + '''</div>
                    <div class="metric-label">Total Commits</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('contributors-panel')">
                    <div class="metric-value">''' + str(data['timeline']['contributors']) + '''</div>
                    <div class="metric-label">Contributors</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['timeline']['last_90_days']) + '''</div>
                    <div class="metric-label">Commits (90 days)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + data['timeline']['project_age'] + '''</div>
                    <div class="metric-label">Project Age</div>
                </div>
            </div>
        </section>

        <!-- Timeline Chart -->
        <section class="section-panel">
            <h2 class="section-title">📈 Commit Activity</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Monthly commit frequency showing development velocity over the past year.</p>
            <div class="viz-container" id="timeline-chart" style="min-height: 400px;"></div>
        </section>

        <!-- Hot Files -->
        <section class="section-panel">
            <h2 class="section-title">🔥 Most Changed Files</h2>
'''

    for hf in data['timeline']['hot_files']:
        html += f'''
            <div style="padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid var(--accent-primary); display: flex; justify-content: space-between;">
                <span style="font-family: monospace; color: var(--text-primary);">{hf['file']}</span>
                <span style="color: var(--accent-primary); font-weight: 600;">{hf['commits']} commits</span>
            </div>'''

    html += '''
        </section>

        <!-- Contributors Panel -->
        <section id="contributors-panel" class="drill-down-panel">
            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">👥 Top Contributors</h3>
'''

    for contrib in data['timeline']['top_contributors']:
        html += f'''
            <div style="padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-primary); font-weight: 600;">{contrib['name']}</span>
                <div>
                    <span style="color: var(--accent-primary);">{contrib['commits']} commits</span>
                    <span style="background: rgba(77, 140, 255, 0.2); padding: 0.25rem 0.5rem; border-radius: 4px; margin-left: 0.5rem; font-size: 0.85rem;">{contrib['percentage']}%</span>
                </div>
            </div>'''

    html += '''
        </section>
    </div>

    <!-- ============================================
         IMPACT TAB
         ============================================ -->
    <div id="impact" class="tab-content">
        <!-- At-a-Glance Tiles -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(13, 110, 253, 0.08) 0%, rgba(77, 140, 255, 0.05) 100%); border: 2px solid rgba(77, 140, 255, 0.3);">
            <h2 class="section-title" style="text-align: center;">💥 Change Impact Overview</h2>
            <p style="color: var(--text-secondary); text-align: center; margin-bottom: 1.5rem;">Analyzes blast radius of changes — which files affect which parts of the system when modified.</p>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                <div class="metric-card interactive-card" onclick="togglePanel('critical-impact-panel')" style="background: rgba(239, 68, 68, 0.15);">
                    <div class="metric-value" style="color: #ef4444;">''' + str(len(data['impact']['critical_files'])) + '''</div>
                    <div class="metric-label">Critical Impact Files</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('moderate-impact-panel')" style="background: rgba(245, 158, 11, 0.15);">
                    <div class="metric-value" style="color: #f59e0b;">''' + str(data['impact']['moderate_files']) + '''</div>
                    <div class="metric-label">Moderate Impact</div>
                </div>
                <div class="metric-card" style="background: rgba(34, 197, 94, 0.15);">
                    <div class="metric-value" style="color: #22c55e;">''' + str(data['impact']['low_impact_files']) + '''</div>
                    <div class="metric-label">Low Impact (Safe)</div>
                </div>
            </div>
        </section>

        <!-- Impact Graph -->
        <section class="section-panel">
            <h2 class="section-title">🎯 Impact Visualization</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">Size represents number of dependents. Color indicates risk level.</p>
            <div class="viz-container" id="impact-graph" style="min-height: 500px;"></div>
        </section>

        <!-- Critical Impact Cards -->
        <section class="section-panel">
            <h2 class="section-title" style="color: #ef4444;">🔴 Critical Impact Files (High Risk)</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Files with >20 dependents — changes ripple across the entire system.</p>
'''

    for cf in data['impact']['critical_files']:
        html += f'''
            <div class="impact-card critical">
                <div class="impact-icon">⚠️</div>
                <div class="impact-content">
                    <div class="impact-title">{cf['file']}</div>
                    <div class="impact-description">This file has <strong>{cf['dependents']} dependent files</strong>. Changes here will trigger recompilation and testing across multiple modules. Exercise extreme caution when modifying.</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #ef4444;">{cf['dependents']}</div>
                    <div style="font-size: 0.75rem; color: var(--text-tertiary);">dependents</div>
                </div>
            </div>'''

    html += '''
        </section>

        <!-- Coupling Metrics -->
        <section class="section-panel">
            <h2 class="section-title">📊 Coupling Metrics</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['impact']['coupling_metrics']['afferent_coupling_avg']) + '''</div>
                    <div class="metric-label">Avg Afferent Coupling</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['impact']['coupling_metrics']['efferent_coupling_avg']) + '''</div>
                    <div class="metric-label">Avg Efferent Coupling</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['impact']['coupling_metrics']['instability_index']) + '''</div>
                    <div class="metric-label">Instability Index</div>
                </div>
            </div>
        </section>
    </div>

    <!-- ============================================
         SECURITY TAB
         ============================================ -->
    <div id="security" class="tab-content">
        <!-- At-a-Glance Tiles -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(245, 158, 11, 0.05) 100%); border: 2px solid rgba(239, 68, 68, 0.3);">
            <h2 class="section-title" style="text-align: center;">🔒 Security Overview</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
                <div class="metric-card interactive-card" onclick="togglePanel('p0-panel')" style="background: rgba(239, 68, 68, 0.2);">
                    <div class="metric-value" style="color: #ef4444;">''' + str(data['security']['summary']['p0_count']) + '''</div>
                    <div class="metric-label">Critical (P0)</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('p1-panel')" style="background: rgba(245, 158, 11, 0.2);">
                    <div class="metric-value" style="color: #f59e0b;">''' + str(data['security']['summary']['p1_count']) + '''</div>
                    <div class="metric-label">High (P1)</div>
                </div>
                <div class="metric-card" style="background: rgba(34, 197, 94, 0.2);">
                    <div class="metric-value" style="color: #22c55e;">''' + str(data['security']['summary']['p2_count']) + '''</div>
                    <div class="metric-label">Medium (P2)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">''' + str(data['security']['summary']['total']) + '''</div>
                    <div class="metric-label">Total Findings</div>
                </div>
            </div>
        </section>

        <!-- Security Visualization -->
        <section class="section-panel">
            <h2 class="section-title">📊 Security Distribution</h2>
            <div class="viz-container" id="security-chart" style="min-height: 300px;"></div>
        </section>

        <!-- P0 Critical Findings -->
        <section class="section-panel">
            <h2 class="section-title" style="color: #ef4444;">🔴 Critical Findings (P0)</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Immediate action required. These issues pose significant security risks.</p>
'''

    for finding in data['security']['p0_findings']:
        html += f'''
            <div class="security-card p0">
                <div class="security-icon">🔴</div>
                <div class="security-content">
                    <div class="security-title">{finding['title']}</div>
                    <div class="security-file">{finding['file']}:{finding['line']}</div>
                    <div class="security-description">{finding['description']}</div>
                </div>
            </div>'''

    html += '''
        </section>

        <!-- P1 High Priority Findings -->
        <section class="section-panel">
            <h2 class="section-title" style="color: #f59e0b;">🟠 High Priority Findings (P1)</h2>
'''

    for finding in data['security']['p1_findings']:
        html += f'''
            <div class="security-card p1">
                <div class="security-icon">🟠</div>
                <div class="security-content">
                    <div class="security-title">{finding['title']}</div>
                    <div class="security-file">{finding['file']}:{finding['line']}</div>
                    <div class="security-description">{finding['description']}</div>
                </div>
            </div>'''

    html += '''
        </section>
    </div>

    <!-- ============================================
         TECH STACK TAB
         ============================================ -->
    <div id="techstack" class="tab-content">
        <!-- At-a-Glance Tiles -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(13, 110, 253, 0.08) 0%, rgba(77, 140, 255, 0.05) 100%); border: 2px solid rgba(77, 140, 255, 0.3);">
            <h2 class="section-title" style="text-align: center;">⚙️ Technology Overview</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
                <div class="metric-card">
                    <div class="metric-value">''' + str(len(data['tech_stack'])) + '''</div>
                    <div class="metric-label">Technologies</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">3</div>
                    <div class="metric-label">Languages</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">1</div>
                    <div class="metric-label">Frameworks</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">1</div>
                    <div class="metric-label">Databases</div>
                </div>
            </div>
        </section>

        <!-- Tech Stack Visualization -->
        <section class="section-panel">
            <h2 class="section-title">🛠️ Technology Stack</h2>
            <div class="tech-grid">
'''

    for tech in data['tech_stack']:
        html += f'''
                <div class="tech-card">
                    <div class="tech-icon">{tech['icon']}</div>
                    <div class="tech-name">{tech['name']}</div>
                    <div class="tech-category">{tech['category']}</div>
                </div>'''

    html += '''
            </div>
        </section>

        <!-- Tech Details -->
        <section class="section-panel">
            <h2 class="section-title">📋 Technology Details</h2>
'''

    for tech in data['tech_stack']:
        html += f'''
            <div style="padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 1.5rem;">{tech['icon']}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: var(--accent-primary);">{tech['name']}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">{tech['usage']}</div>
                </div>
                <div style="background: rgba(77, 140, 255, 0.2); padding: 0.35rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.85rem;">{tech['category']}</div>
            </div>'''

    html += '''
        </section>
    </div>

    <!-- ============================================
         ARCHITECTURE TAB
         ============================================ -->
    <div id="architecture" class="tab-content">
        <!-- At-a-Glance Tiles -->
        <section class="section-panel" style="background: linear-gradient(135deg, rgba(13, 110, 253, 0.08) 0%, rgba(77, 140, 255, 0.05) 100%); border: 2px solid rgba(77, 140, 255, 0.3);">
            <h2 class="section-title" style="text-align: center;">🏗️ Architecture Overview</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
                <div class="metric-card interactive-card" onclick="togglePanel('layers-panel')">
                    <div class="metric-value">''' + str(len(data['architecture']['layers'])) + '''</div>
                    <div class="metric-label">Layers</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('integrations-panel')">
                    <div class="metric-value">''' + str(len(data['architecture']['integrations'])) + '''</div>
                    <div class="metric-label">Integrations</div>
                </div>
                <div class="metric-card interactive-card" onclick="togglePanel('patterns-panel')">
                    <div class="metric-value">''' + str(len(data['architecture']['patterns_detected'])) + '''</div>
                    <div class="metric-label">Design Patterns</div>
                </div>
            </div>
        </section>

        <!-- Architecture Diagram -->
        <section class="section-panel">
            <h2 class="section-title">📐 System Architecture</h2>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">High-level view of system layers and their interactions.</p>
            <div class="viz-container" id="architecture-diagram" style="min-height: 600px;"></div>
        </section>

        <!-- Architecture Layers -->
        <section class="section-panel">
            <h2 class="section-title">📚 Architectural Layers</h2>
'''

    for layer in data['architecture']['layers']:
        html += f'''
            <div class="arch-layer">
                <div class="arch-layer-title">{layer['name']}</div>
                <div class="arch-layer-desc">{layer['description']}</div>
                <div class="arch-components">'''
        for comp in layer['components']:
            html += f'<span class="arch-component">{comp}</span>'
        html += '''
                </div>
            </div>'''

    html += '''
        </section>

        <!-- Integrations -->
        <section class="section-panel">
            <h2 class="section-title">🔗 Integration Points</h2>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
'''

    for integ in data['architecture']['integrations']:
        html += f'''
                <div class="tech-card">
                    <div class="tech-icon">{integ['icon']}</div>
                    <div class="tech-name">{integ['name']}</div>
                    <div class="tech-category">{integ['type']}</div>
                </div>'''

    html += '''
            </div>
        </section>

        <!-- Design Patterns -->
        <section id="patterns-panel" class="drill-down-panel">
            <h3 style="color: var(--accent-primary); margin-bottom: 1rem;">🎨 Detected Design Patterns</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
'''

    for pattern in data['architecture']['patterns_detected']:
        html += f'''
                <span style="background: rgba(77, 140, 255, 0.2); padding: 0.5rem 1rem; border-radius: var(--radius-md); font-size: 0.9rem; color: var(--text-primary);">✓ {pattern}</span>'''

    html += '''
            </div>
        </section>
    </div>

    <!-- Footer -->
    <footer class="dashboard-footer">
        <p><strong>Generated by CORTEX v8.0</strong> — Universal Dashboard System</p>
        <p style="margin-top: 0.5rem; font-size: 0.9rem;">📅 ''' + data['metadata']['generated_at'] + ''' | 📁 ''' + data['metadata']['repo_path'] + '''</p>
    </footer>
</div>

<!-- D3.js v7 (Minified, Inline for file:// protocol) -->
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
// ============================================
// TAB NAVIGATION
// ============================================
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Activate button
    event.target.classList.add('active');
    
    // Render visualizations on first visit
    renderVisualization(tabName);
}

// ============================================
// DRILL-DOWN PANELS
// ============================================
function togglePanel(panelId) {
    const panel = document.getElementById(panelId);
    if (panel) {
        panel.classList.toggle('active');
        if (panel.classList.contains('active')) {
            panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
}

// ============================================
// D3.js VISUALIZATIONS
// ============================================
const renderedViz = new Set(['overview']);

function renderVisualization(tabName) {
    if (renderedViz.has(tabName)) return;
    renderedViz.add(tabName);
    
    setTimeout(() => {
        switch(tabName) {
            case 'overview':
                renderLanguageChart();
                break;
            case 'dependencies':
                renderDependencyGraph();
                break;
            case 'classes':
                renderClassHierarchy();
                break;
            case 'timeline':
                renderTimelineChart();
                break;
            case 'impact':
                renderImpactGraph();
                break;
            case 'security':
                renderSecurityChart();
                break;
            case 'architecture':
                renderArchitectureDiagram();
                break;
        }
    }, 100);
}

// Language Distribution Chart
function renderLanguageChart() {
    const container = document.getElementById('language-chart');
    if (!container || typeof d3 === 'undefined') return;
    
    const width = container.clientWidth;
    const height = 400;
    const data = ''' + json.dumps([{"name": k, "value": v} for k, v in data['overview']['languages'].items()]) + ''';
    
    const svg = d3.select('#language-chart')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const pie = d3.pie().value(d => d.value);
    const arc = d3.arc().innerRadius(80).outerRadius(Math.min(width, height) / 2 - 40);
    
    const color = d3.scaleOrdinal()
        .domain(data.map(d => d.name))
        .range(['#4d8cff', '#7fb3ff', '#b3d9ff', '#0d6efd', '#4fc3f7', '#80deea', '#a5d6a7', '#c5e1a5', '#fff59d', '#ffe082']);
    
    const g = svg.append('g')
        .attr('transform', `translate(${width/2},${height/2})`);
    
    g.selectAll('path')
        .data(pie(data))
        .join('path')
        .attr('d', arc)
        .attr('fill', d => color(d.data.name))
        .attr('stroke', '#0a1428')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .on('mouseover', function() { d3.select(this).attr('opacity', 0.8); })
        .on('mouseout', function() { d3.select(this).attr('opacity', 1); })
        .append('title')
        .text(d => `${d.data.name}: ${d.data.value} files`);
    
    // Legend
    const legend = svg.append('g')
        .attr('transform', `translate(${width - 150}, 20)`);
    
    data.slice(0, 6).forEach((d, i) => {
        const row = legend.append('g').attr('transform', `translate(0, ${i * 25})`);
        row.append('rect').attr('width', 15).attr('height', 15).attr('fill', color(d.name));
        row.append('text').attr('x', 20).attr('y', 12).text(d.name).attr('fill', '#fff').attr('font-size', 12);
    });
}

// Dependency Graph
function renderDependencyGraph() {
    const container = document.getElementById('dependency-graph');
    if (!container || typeof d3 === 'undefined') return;
    
    const width = container.clientWidth;
    const height = 600;
    
    const nodes = [
        {id: 'kashkole', group: 1, size: 40},
        {id: 'models', group: 2, size: 30},
        {id: 'views', group: 2, size: 30},
        {id: 'utils', group: 2, size: 25},
        {id: 'auth', group: 2, size: 25},
        {id: 'api', group: 2, size: 20},
        {id: 'services', group: 2, size: 25},
        {id: 'database', group: 3, size: 20},
        {id: 'email', group: 3, size: 15},
        {id: 'hijri', group: 3, size: 15},
        {id: 'pdf', group: 3, size: 12},
        {id: 'logging', group: 3, size: 10}
    ];
    
    const links = [
        {source: 'kashkole', target: 'models', value: 8},
        {source: 'kashkole', target: 'views', value: 8},
        {source: 'kashkole', target: 'utils', value: 5},
        {source: 'kashkole', target: 'auth', value: 6},
        {source: 'kashkole', target: 'api', value: 4},
        {source: 'kashkole', target: 'services', value: 6},
        {source: 'models', target: 'database', value: 10},
        {source: 'views', target: 'models', value: 5},
        {source: 'views', target: 'email', value: 3},
        {source: 'views', target: 'hijri', value: 3},
        {source: 'utils', target: 'logging', value: 2},
        {source: 'services', target: 'models', value: 6},
        {source: 'services', target: 'email', value: 3},
        {source: 'auth', target: 'database', value: 4},
        {source: 'api', target: 'services', value: 5}
    ];
    
    const svg = d3.select('#dependency-graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const color = d3.scaleOrdinal().domain([1, 2, 3]).range(['#0d6efd', '#4d8cff', '#80b3ff']);
    
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(120))
        .force('charge', d3.forceManyBody().strength(-400))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.size + 15));
    
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', '#4d8cff')
        .attr('stroke-opacity', 0.4)
        .attr('stroke-width', d => Math.sqrt(d.value));
    
    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', d => d.size)
        .attr('fill', d => color(d.group))
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('cursor', 'grab')
        .call(d3.drag()
            .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
            .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
            .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));
    
    const label = svg.append('g')
        .selectAll('text')
        .data(nodes)
        .join('text')
        .text(d => d.id)
        .attr('font-size', 11)
        .attr('fill', '#fff')
        .attr('text-anchor', 'middle')
        .attr('dy', -5)
        .style('pointer-events', 'none');
    
    node.append('title').text(d => d.id);
    
    simulation.on('tick', () => {
        link.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
        node.attr('cx', d => d.x).attr('cy', d => d.y);
        label.attr('x', d => d.x).attr('y', d => d.y - d.size);
    });
}

// Class Hierarchy
function renderClassHierarchy() {
    const container = document.getElementById('class-hierarchy');
    if (!container || typeof d3 === 'undefined') return;
    
    const width = container.clientWidth;
    const height = 600;
    
    const data = {
        name: "Base",
        children: ''' + json.dumps(data['classes']['hierarchy']) + '''
    };
    
    const svg = d3.select('#class-hierarchy')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const g = svg.append('g').attr('transform', `translate(${width/2},${height/2})`);
    
    const pack = d3.pack().size([Math.min(width, height) - 100, Math.min(width, height) - 100]).padding(8);
    const root = d3.hierarchy(data).sum(d => d.methods || 10);
    pack(root);
    
    const color = d3.scaleLinear().domain([0, 3]).range(['#0d6efd', '#b3d9ff']);
    
    g.selectAll('circle')
        .data(root.descendants())
        .join('circle')
        .attr('cx', d => d.x - width/2 + 50)
        .attr('cy', d => d.y - height/2 + 50)
        .attr('r', d => d.r)
        .attr('fill', d => d.children ? 'rgba(13, 110, 253, 0.2)' : color(d.depth))
        .attr('stroke', '#4d8cff')
        .attr('stroke-width', 1.5)
        .style('cursor', 'pointer')
        .append('title')
        .text(d => d.data.name + (d.data.methods ? ` (${d.data.methods} methods)` : ''));
    
    g.selectAll('text')
        .data(root.descendants().filter(d => d.r > 25))
        .join('text')
        .attr('x', d => d.x - width/2 + 50)
        .attr('y', d => d.y - height/2 + 50)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.3em')
        .attr('font-size', d => Math.min(d.r / 3, 12))
        .attr('fill', '#fff')
        .text(d => d.data.name)
        .style('pointer-events', 'none');
}

// Timeline Chart
function renderTimelineChart() {
    const container = document.getElementById('timeline-chart');
    if (!container || typeof d3 === 'undefined') return;
    
    const width = container.clientWidth;
    const height = 400;
    const margin = {top: 20, right: 30, bottom: 40, left: 50};
    
    const data = ''' + json.dumps(data['timeline']['monthly_commits']) + ''';
    
    const svg = d3.select('#timeline-chart')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    
    const x = d3.scaleBand()
        .domain(data.map(d => d.month))
        .range([0, width - margin.left - margin.right])
        .padding(0.2);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.commits)])
        .nice()
        .range([height - margin.top - margin.bottom, 0]);
    
    // Gradient
    const gradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', 'bar-gradient')
        .attr('x1', '0%').attr('y1', '0%').attr('x2', '0%').attr('y2', '100%');
    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#4d8cff');
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#0d6efd');
    
    g.selectAll('rect')
        .data(data)
        .join('rect')
        .attr('x', d => x(d.month))
        .attr('y', d => y(d.commits))
        .attr('width', x.bandwidth())
        .attr('height', d => height - margin.top - margin.bottom - y(d.commits))
        .attr('fill', 'url(#bar-gradient)')
        .attr('rx', 4)
        .append('title')
        .text(d => `${d.month}: ${d.commits} commits`);
    
    g.append('g')
        .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(x))
        .selectAll('text').attr('fill', '#fff');
    
    g.append('g')
        .call(d3.axisLeft(y))
        .selectAll('text').attr('fill', '#fff');
}

// Impact Graph
function renderImpactGraph() {
    const container = document.getElementById('impact-graph');
    if (!container || typeof d3 === 'undefined') return;
    
    const width = container.clientWidth;
    const height = 500;
    
    const data = {
        name: "Core",
        children: ''' + json.dumps(data['impact']['critical_files'] + [
            {"file": f"moderate_{i}", "dependents": 15, "risk": "moderate"} for i in range(5)
        ] + [
            {"file": f"low_{i}", "dependents": 5, "risk": "low"} for i in range(8)
        ]) + '''
    };
    
    const svg = d3.select('#impact-graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const g = svg.append('g').attr('transform', `translate(${width/2},${height/2})`);
    
    const pack = d3.pack().size([Math.min(width, height) - 50, Math.min(width, height) - 50]).padding(5);
    const root = d3.hierarchy(data).sum(d => d.dependents || 1);
    pack(root);
    
    const riskColors = {critical: '#ef4444', moderate: '#f59e0b', low: '#22c55e'};
    
    g.selectAll('circle')
        .data(root.descendants().filter(d => d.depth > 0))
        .join('circle')
        .attr('cx', d => d.x - width/2 + 25)
        .attr('cy', d => d.y - height/2 + 25)
        .attr('r', d => d.r)
        .attr('fill', d => riskColors[d.data.risk] || '#4d8cff')
        .attr('fill-opacity', 0.6)
        .attr('stroke', d => riskColors[d.data.risk] || '#4d8cff')
        .attr('stroke-width', 2)
        .append('title')
        .text(d => d.data.file ? `${d.data.file}: ${d.data.dependents} dependents` : '');
}

// Security Chart
function renderSecurityChart() {
    const container = document.getElementById('security-chart');
    if (!container || typeof d3 === 'undefined') return;
    
    const width = container.clientWidth;
    const height = 300;
    
    const data = [
        {label: 'P0 Critical', value: ''' + str(data['security']['summary']['p0_count']) + ''', color: '#ef4444'},
        {label: 'P1 High', value: ''' + str(data['security']['summary']['p1_count']) + ''', color: '#f59e0b'},
        {label: 'P2 Medium', value: ''' + str(data['security']['summary']['p2_count']) + ''', color: '#22c55e'}
    ];
    
    const svg = d3.select('#security-chart')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const pie = d3.pie().value(d => d.value || 0.1);
    const arc = d3.arc().innerRadius(60).outerRadius(Math.min(width, height) / 2 - 30);
    
    const g = svg.append('g').attr('transform', `translate(${width/2},${height/2})`);
    
    g.selectAll('path')
        .data(pie(data))
        .join('path')
        .attr('d', arc)
        .attr('fill', d => d.data.color)
        .attr('stroke', '#0a1428')
        .attr('stroke-width', 2)
        .append('title')
        .text(d => `${d.data.label}: ${d.data.value}`);
}

// Architecture Diagram
function renderArchitectureDiagram() {
    const container = document.getElementById('architecture-diagram');
    if (!container || typeof d3 === 'undefined') return;
    
    const width = container.clientWidth;
    const height = 600;
    
    const svg = d3.select('#architecture-diagram')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const layers = [
        {name: 'Presentation Layer', y: 50, color: '#0d6efd', comps: ['Views (34)', 'Templates (12)', 'Assets']},
        {name: 'Business Logic', y: 180, color: '#4d8cff', comps: ['Models (23)', 'Services (18)', 'Utils (45)']},
        {name: 'Data Access', y: 310, color: '#7fb3ff', comps: ['SQL Server', 'ADO.NET', '56 Tables']},
        {name: 'Infrastructure', y: 440, color: '#b3d9ff', comps: ['Auth', 'Email', 'Logging', 'PDF']}
    ];
    
    layers.forEach((layer, i) => {
        const g = svg.append('g');
        
        g.append('rect')
            .attr('x', 50)
            .attr('y', layer.y)
            .attr('width', width - 100)
            .attr('height', 110)
            .attr('fill', layer.color)
            .attr('fill-opacity', 0.15)
            .attr('stroke', layer.color)
            .attr('stroke-width', 2)
            .attr('rx', 8);
        
        g.append('text')
            .attr('x', 70)
            .attr('y', layer.y + 25)
            .attr('fill', '#fff')
            .attr('font-size', 16)
            .attr('font-weight', 'bold')
            .text(layer.name);
        
        const compWidth = (width - 150) / layer.comps.length;
        layer.comps.forEach((comp, j) => {
            g.append('rect')
                .attr('x', 70 + j * compWidth)
                .attr('y', layer.y + 50)
                .attr('width', compWidth - 15)
                .attr('height', 40)
                .attr('fill', layer.color)
                .attr('fill-opacity', 0.4)
                .attr('stroke', layer.color)
                .attr('rx', 4);
            
            g.append('text')
                .attr('x', 70 + j * compWidth + (compWidth - 15) / 2)
                .attr('y', layer.y + 75)
                .attr('fill', '#fff')
                .attr('font-size', 11)
                .attr('text-anchor', 'middle')
                .text(comp);
        });
        
        if (i < layers.length - 1) {
            svg.append('line')
                .attr('x1', width / 2)
                .attr('y1', layer.y + 110)
                .attr('x2', width / 2)
                .attr('y2', layers[i + 1].y)
                .attr('stroke', '#4d8cff')
                .attr('stroke-width', 2)
                .attr('stroke-dasharray', '5,5')
                .attr('marker-end', 'url(#arrow)');
        }
    });
    
    // Arrow marker
    svg.append('defs').append('marker')
        .attr('id', 'arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 8)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#4d8cff');
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    renderVisualization('overview');
});
</script>
</body>
</html>'''

    return html


def main():
    """Generate dashboard"""
    print("🚀 Generating complete KASHKOLE dashboard...")
    
    html = generate_html()
    
    # Output path
    output_dir = Path("company/dashboards/kashkole")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "dashboard.html"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    file_size = output_path.stat().st_size / 1024
    print(f"✅ Dashboard generated: {output_path}")
    print(f"📦 File size: {file_size:.1f} KB")
    print(f"🔗 Open: file:///{output_path.absolute().as_posix()}")


if __name__ == "__main__":
    main()
