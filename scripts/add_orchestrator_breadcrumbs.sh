#!/bin/bash

# Script to add breadcrumb navigation to all orchestrator HTML files
# Author: Asif Hussain

ORCHESTRATORS_DIR="/Users/asifhussain/PROJECTS/CORTEX/docs/technical/orchestrators"

# Define orchestrator files and their display names
declare -A ORCHESTRATORS=(
    ["tdd-orchestrator.html"]="TDD Orchestrator"
    ["ado-planning.html"]="ADO Planning"
    ["maintenance-orchestrator.html"]="System Maintenance"
    ["code-sanitization.html"]="Code Sanitization"
    ["system-integrity.html"]="System Integrity"
    ["refinement-orchestrator.html"]="Refinement"
    ["cleanup-orchestrator.html"]="Cleanup"
    ["git-checkpoint.html"]="Git Checkpoint"
    ["architectural-review.html"]="Architectural Review"
    ["cortex-lens.html"]="CORTEX Lens v3"
    ["intelligent-dashboard.html"]="Intelligent Dashboard"
    ["debug-orchestrator.html"]="Debug"
    ["rollback-orchestrator.html"]="Rollback"
    ["autonomous-execution.html"]="Autonomous Execution"
    ["pre-flight-orchestrator.html"]="Pre-Flight"
)

# Breadcrumb CSS to be added (before the closing </style> tag)
read -r -d '' BREADCRUMB_CSS << 'EOF'
        
        /* Breadcrumb Navigation */
        .breadcrumb {
            background: rgba(30, 41, 59, 0.8);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(124, 58, 237, 0.3);
            margin-bottom: 2rem;
        }
        
        .breadcrumb a {
            color: var(--planning-primary, #2196F3);
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .breadcrumb a:hover {
            color: var(--planning-secondary, #1976D2);
            text-decoration: underline;
        }
        
        .breadcrumb-separator {
            color: #64748b;
            margin: 0 0.5rem;
        }
        
        .breadcrumb-current {
            color: #e2e8f0;
        }
EOF

# Function to add breadcrumbs to a file
add_breadcrumbs() {
    local file="$1"
    local display_name="$2"
    local filepath="${ORCHESTRATORS_DIR}/${file}"
    
    echo "Processing: $file -> $display_name"
    
    # Check if file exists
    if [ ! -f "$filepath" ]; then
        echo "  ❌ File not found: $filepath"
        return 1
    fi
    
    # Check if breadcrumb already exists
    if grep -q "class=\"breadcrumb\"" "$filepath"; then
        echo "  ⏭️  Breadcrumb already exists, skipping"
        return 0
    fi
    
    # Create temporary file
    local temp_file="${filepath}.tmp"
    
    # Read the file and add breadcrumbs
    awk -v css="$BREADCRUMB_CSS" -v name="$display_name" '
    BEGIN { 
        in_style = 0
        in_media_query = 0
        css_added = 0
        breadcrumb_added = 0
    }
    
    # Track when we are in <style> tag
    /<style>/ { in_style = 1 }
    
    # Track media queries (usually near end of style block)
    /@media \(max-width: 768px\)/ { in_media_query = 1 }
    
    # Add CSS before closing style tag (but after media queries if present)
    /<\/style>/ && in_style && !css_added {
        if (in_media_query) {
            # Add breadcrumb-specific media query adjustments if needed
            print "        "
            print "            .breadcrumb {"
            print "                padding: 0.75rem 1rem;"
            print "                font-size: 0.9rem;"
            print "            }"
        }
        print css
        css_added = 1
        in_style = 0
    }
    
    # Add breadcrumb HTML after <body> tag
    /<body>/ && !breadcrumb_added {
        print $0
        print "    <!-- Breadcrumb -->"
        print "    <nav class=\"breadcrumb\">"
        print "        <a href=\"../../index.html\">Home</a>"
        print "        <span class=\"breadcrumb-separator\">›</span>"
        print "        <a href=\"../../features/orchestrators.html\">Orchestrators</a>"
        print "        <span class=\"breadcrumb-separator\">›</span>"
        print "        <a href=\"index.html\">Technical Documentation</a>"
        print "        <span class=\"breadcrumb-separator\">›</span>"
        print "        <span class=\"breadcrumb-current\">" name "</span>"
        print "    </nav>"
        print "    "
        breadcrumb_added = 1
        next
    }
    
    # Print all other lines
    { print }
    ' "$filepath" > "$temp_file"
    
    # Check if awk succeeded
    if [ $? -eq 0 ] && [ -s "$temp_file" ]; then
        mv "$temp_file" "$filepath"
        echo "  ✅ Breadcrumb added successfully"
    else
        echo "  ❌ Failed to add breadcrumb"
        rm -f "$temp_file"
        return 1
    fi
}

# Main execution
echo "🧠 CORTEX Breadcrumb Navigation Installer"
echo "=========================================="
echo ""

success_count=0
skip_count=0
fail_count=0

for file in "${!ORCHESTRATORS[@]}"; do
    add_breadcrumbs "$file" "${ORCHESTRATORS[$file]}"
    case $? in
        0) ((skip_count++)) ;;
        1) ((fail_count++)) ;;
        *) ((success_count++)) ;;
    esac
    echo ""
done

echo "=========================================="
echo "📊 Summary:"
echo "  ✅ Successfully added: $success_count"
echo "  ⏭️  Already existed: $skip_count"
echo "  ❌ Failed: $fail_count"
echo ""
echo "✅ Breadcrumb installation complete!"
