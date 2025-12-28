# Generate Remaining Category Pages
# Author: Asif Hussain
# Generates HTML category pages for CORTEX Knowledge Library

$categories = @(
    @{
        file = "messaging.html"
        domain = "Backend & APIs"
        icon = "📨"
        title = "Messaging & Events"
        subtitle = "Message queues, event-driven architecture, pub/sub patterns"
        stats = @("4", "70+", "3")
        statLabels = @("Knowledge Files", "Patterns", "Protocols")
        nav = @("api-design.html|🌐|API Design", "microservices.html|🔷|Microservices", "messaging.html|📨|Messaging|active")
        files = @(
            @{icon="📬"; title="Message Queues"; subtitle="RabbitMQ, Azure Service Bus"; badge="18 rules"},
            @{icon="🎯"; title="Event-Driven Architecture"; subtitle="Event sourcing, CQRS"; badge="22 rules"},
            @{icon="🔄"; title="Apache Kafka"; subtitle="Topics, partitions, consumers"; badge="20 rules"},
            @{icon="🐰"; title="RabbitMQ Patterns"; subtitle="Exchanges, routing, bindings"; badge="16 rules"}
        )
        mermaid = @"
graph LR
    P[Publisher] --> MB[Message Broker]
    MB --> Q1[Queue/Topic 1]
    MB --> Q2[Queue/Topic 2]
    Q1 --> C1[Consumer 1]
    Q1 --> C2[Consumer 2]
    Q2 --> C3[Consumer 3]
    style MB fill:#00d4ff,stroke:#7b61ff,stroke-width:2px
"@
    },
    @{
        file = "database.html"
        domain = "Data & Storage"
        icon = "🗄️"
        title = "Database Design"
        subtitle = "SQL, NoSQL, schema design, query optimization"
        stats = @("3", "75+", "5")
        statLabels = @("Knowledge Files", "Patterns", "Database Types")
        nav = @("database.html|🗄️|Database|active", "performance.html|⚡|Performance")
        files = @(
            @{icon="📊"; title="SQL Best Practices"; subtitle="PostgreSQL, MySQL, indexes"; badge="28 rules"},
            @{icon="🍃"; title="NoSQL Patterns"; subtitle="MongoDB, Cassandra, Redis"; badge="24 rules"},
            @{icon="📐"; title="Schema Design"; subtitle="Normalization, denormalization"; badge="20 rules"}
        )
        mermaid = @"
graph TD
    A[Databases] --> B[Relational]
    A --> C[NoSQL]
    B --> D[PostgreSQL]
    B --> E[MySQL]
    C --> F[Document: MongoDB]
    C --> G[Wide Column: Cassandra]
    C --> H[Key-Value: Redis]
    style A fill:#00d4ff,stroke:#7b61ff,stroke-width:2px
"@
    },
    @{
        file = "performance.html"
        domain = "Data & Storage"
        icon = "⚡"
        title = "Performance Optimization"
        subtitle = "Caching, query optimization, load testing"
        stats = @("3", "60+", "4")
        statLabels = @("Knowledge Files", "Techniques", "Cache Strategies")
        nav = @("database.html|🗄️|Database", "performance.html|⚡|Performance|active")
        files = @(
            @{icon="💾"; title="Caching Strategies"; subtitle="Redis, Memcached, CDN"; badge="18 rules"},
            @{icon="🚀"; title="Query Optimization"; subtitle="Indexes, execution plans"; badge="22 rules"},
            @{icon="📈"; title="Load Testing"; subtitle="k6, JMeter, performance budgets"; badge="16 rules"}
        )
        mermaid = @"
graph TD
    A[Request] --> B[CDN Cache]
    B --> C[Application Cache]
    C --> D[Database Cache]
    D --> E[Database]
    style B fill:#4ecdc4,stroke:#fff,stroke-width:2px
    style C fill:#00d4ff,stroke:#fff,stroke-width:2px
    style D fill:#7b61ff,stroke:#fff,stroke-width:2px
"@
    },
    @{
        file = "cloud.html"
        domain = "Infrastructure & Cloud"
        icon = "☁️"
        title = "Cloud Architecture"
        subtitle = "AWS, Azure, GCP best practices and patterns"
        stats = @("3", "90+", "3")
        statLabels = @("Knowledge Files", "Patterns", "Major Providers")
        nav = @("cloud.html|☁️|Cloud|active", "containers.html|🐳|Containers", "devops.html|🔧|DevOps")
        files = @(
            @{icon="🟠"; title="AWS Best Practices"; subtitle="EC2, S3, Lambda, VPC"; badge="30 rules"; exists=$true},
            @{icon="🔵"; title="Azure Patterns"; subtitle="App Service, Cosmos DB, Functions"; badge="28 rules"},
            @{icon="🟡"; title="GCP Architecture"; subtitle="Compute Engine, Cloud Storage"; badge="25 rules"}
        )
        mermaid = @"
graph TD
    A[Cloud Platform] --> B[Compute]
    A --> C[Storage]
    A --> D[Database]
    A --> E[Networking]
    A --> F[Security]
    B --> G[VMs/Containers/Serverless]
    C --> H[Object/Block/File]
    D --> I[SQL/NoSQL]
    style A fill:#00d4ff,stroke:#7b61ff,stroke-width:2px
"@
    }
)

Write-Host "🚀 Generating category pages..." -ForegroundColor Cyan

foreach ($cat in $categories) {
    $navHtml = ""
    foreach ($navItem in $cat.nav) {
        $parts = $navItem -split '\|'
        $href = $parts[0]
        $icon = $parts[1]
        $label = $parts[2]
        $activeClass = if ($parts.Count -gt 3 -and $parts[3] -eq "active") { " active" } else { "" }
        
        $navHtml += "            <a href=`"$href`" class=`"category-nav-link$activeClass`">$icon $label</a>`n"
    }
    
    $filesHtml = ""
    foreach ($file in $cat.files) {
        $existsNote = if ($file.exists) { 
            "                <p>Comprehensive AWS cloud best practices covering EC2, S3, Lambda, VPC, and more.</p>
                <a href=`"cloud/aws-best-practices.html`" class=`"btn-link`">View Full Documentation →</a>" 
        } else { 
            "                <p>$($file.subtitle) patterns and best practices.</p>
                <p><em>📝 Knowledge file coming soon</em></p>" 
        }
        
        $contentId = $file.title.ToLower() -replace '[^a-z]+', '-'
        $filesHtml += @"
                        <div class="accordion-item">
                            <button class="accordion-header" aria-expanded="false" aria-controls="$contentId-content">
                                <span class="accordion-icon">$($file.icon)</span>
                                <div class="accordion-title-group">
                                    <h3 class="accordion-title">$($file.title)</h3>
                                    <p class="accordion-subtitle">$($file.subtitle)</p>
                                </div>
                                <span class="badge">$($file.badge)</span>
                                <svg class="accordion-chevron" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="6 9 12 15 18 9"></polyline></svg>
                            </button>
                            <div id="$contentId-content" class="accordion-content" hidden>
$existsNote
                            </div>
                        </div>

"@
    }
    
    $bottomNavHtml = ""
    foreach ($navItem in $cat.nav) {
        $parts = $navItem -split '\|'
        $href = $parts[0]
        $icon = $parts[1]
        $label = $parts[2]
        $activeClass = if ($parts.Count -gt 3 -and $parts[3] -eq "active") { " active" } else { "" }
        
        $bottomNavHtml += @"
        <a href="$href" class="bottom-nav-link$activeClass">
            <span class="bottom-nav-icon">$icon</span>
            <span class="bottom-nav-label">$label</span>
        </a>

"@
    }
    
    $html = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="$($cat.title) - $($cat.subtitle)">
    <meta name="author" content="Asif Hussain">
    <title>$($cat.title) - CORTEX Knowledge</title>
    <link rel="icon" type="image/png" href="../assets/images/CORTEX-logo.png">
    <link rel="stylesheet" href="../assets/css/main.css">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <nav class="breadcrumb-container sticky-nav" aria-label="Breadcrumb">
        <button class="back-button" onclick="history.back()" aria-label="Go back">← Back</button>
        <ol class="breadcrumb">
            <li><a href="../index.html">Home</a></li>
            <li><a href="index.html">Knowledge Library</a></li>
            <li><a href="index.html#$(($cat.domain -replace ' & ', '-' -replace ' ', '-').ToLower())">$($cat.domain)</a></li>
            <li aria-current="page">$($cat.icon) $($cat.title -replace ' & ', ' ' -replace '(?<=[A-Z])[A-Z]+', '')</li>
        </ol>
    </nav>

    <section class="hero" id="main-content">
        <div class="logo-header">
            <img src="../assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="page-logo">
        </div>
        <h1 class="hero-title">$($cat.icon) $($cat.title)</h1>
        <p class="hero-subtitle">$($cat.subtitle)</p>
    </section>

    <aside class="category-sidebar" aria-label="Category navigation">
        <h3>$($cat.domain)</h3>
        <nav class="category-nav">
$navHtml        </nav>
    </aside>

    <section class="section category-content">
        <div class="container">
            <div class="tabs-container">
                <div class="tabs-nav" role="tablist" aria-label="Category sections">
                    <button class="tab-button active" role="tab" aria-selected="true" aria-controls="overview-tab" id="overview-btn" data-tab="overview">Overview</button>
                    <button class="tab-button" role="tab" aria-selected="false" aria-controls="files-tab" id="files-btn" data-tab="files">Knowledge Files</button>
                    <button class="tab-button" role="tab" aria-selected="false" aria-controls="resources-tab" id="resources-btn" data-tab="resources">Learning Resources</button>
                    <button class="tab-button" role="tab" aria-selected="false" aria-controls="usage-tab" id="usage-btn" data-tab="usage">CORTEX Usage</button>
                </div>

                <div class="tab-content active" id="overview-tab" role="tabpanel" aria-labelledby="overview-btn">
                    <div class="glass-card">
                        <h2>Overview</h2>
                        <p>$($cat.subtitle)</p>

                        <h3>Category Statistics</h3>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value">$($cat.stats[0])</div>
                                <div class="stat-label">$($cat.statLabels[0])</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">$($cat.stats[1])</div>
                                <div class="stat-label">$($cat.statLabels[1])</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">$($cat.stats[2])</div>
                                <div class="stat-label">$($cat.statLabels[2])</div>
                            </div>
                        </div>
                    </div>

                    <div class="glass-card">
                        <h2>Concept Map</h2>
                        <div class="mermaid">
$($cat.mermaid)
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="files-tab" role="tabpanel" aria-labelledby="files-btn" hidden>
                    <div class="glass-card">
                        <h2>Knowledge Files</h2>
                        <p>Explore $($cat.title.ToLower()) patterns:</p>
                    </div>

                    <div class="knowledge-files-accordion">
$filesHtml                    </div>
                </div>

                <div class="tab-content" id="resources-tab" role="tabpanel" aria-labelledby="resources-btn" hidden>
                    <div class="glass-card">
                        <h2>Learning Resources</h2>
                        <p><em>Curated resources coming soon</em></p>
                    </div>
                </div>

                <div class="tab-content" id="usage-tab" role="tabpanel" aria-labelledby="usage-btn" hidden>
                    <div class="glass-card">
                        <h2>How CORTEX Uses $($cat.title) Knowledge</h2>
                        <p><em>Usage patterns coming soon</em></p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <nav class="bottom-nav" aria-label="Category navigation">
$bottomNavHtml    </nav>

    <script src="../assets/js/category-page.js"></script>
    <script>
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {
                primaryColor: '#00d4ff',
                primaryTextColor: '#fff',
                primaryBorderColor: '#7b61ff',
                lineColor: '#00d4ff',
                secondaryColor: '#7b61ff',
                tertiaryColor: '#1a1f3a'
            }
        });
    </script>
</body>
</html>
"@
    
    $outputPath = Join-Path "d:\PROJECTS\CORTEX\docs\knowledge" $cat.file
    $html | Out-File -FilePath $outputPath -Encoding UTF8
    Write-Host "✅ Created $($cat.file)" -ForegroundColor Green
}

Write-Host "`n✨ Category pages generated successfully!" -ForegroundColor Green
