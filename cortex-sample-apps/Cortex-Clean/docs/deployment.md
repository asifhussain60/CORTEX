# Deployment Guide: Cortex-Clean

## Prerequisites

- .NET 8 Runtime/SDK
- SQL Server 2019+ or Azure SQL
- Node.js 18+ (for frontend build)
- IIS 10+ or Linux with Nginx (optional)

---

## Backend Deployment

### 1. Publish Application

```powershell
cd backend
dotnet publish Cortex.Clean.API/Cortex.Clean.API.csproj -c Release -o ./publish
```

**Output:** `./publish` folder with compiled application

---

### 2. Configure Production Settings

**appsettings.Production.json:**
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.EntityFrameworkCore": "Error"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Server=PRODUCTION_SERVER;Database=CortexCleanDb;User Id=APP_USER;Password=STRONG_PASSWORD;Encrypt=True;TrustServerCertificate=False;"
  },
  "AllowedHosts": "yourdomain.com"
}
```

⚠️ **Security:** Never commit production connection strings to source control

---

### 3. Database Setup

**Option A: Auto-Migration (Development/Staging)**
```powershell
# Application auto-migrates on startup via DatabaseInitializer
# No manual steps required
```

**Option B: Manual Migration (Production)**
```powershell
# Generate SQL script
dotnet ef migrations script -o migration.sql --project Cortex.Clean.Infrastructure --startup-project Cortex.Clean.API

# Review script, then apply via SQL Server Management Studio
```

**Seed Data:**
```sql
-- Disable auto-seeding in production
-- Remove or comment out SeedData.SeedAsync() call in DatabaseInitializer
```

---

### 4. IIS Deployment (Windows)

**Install Prerequisites:**
```powershell
# Install .NET 8 Hosting Bundle
# Download from: https://dotnet.microsoft.com/download/dotnet/8.0
```

**IIS Configuration:**
1. Open IIS Manager
2. Add New Website:
   - Site Name: `CortexCleanAPI`
   - Physical Path: `C:\inetpub\wwwroot\cortex-clean-api\`
   - Binding: HTTPS, Port 443, SSL Certificate
3. Application Pool:
   - .NET CLR Version: No Managed Code
   - Managed Pipeline Mode: Integrated
4. Copy publish folder contents to physical path
5. Update `appsettings.Production.json` connection string
6. Restart application pool

**web.config (auto-generated):**
```xml
<configuration>
  <system.webServer>
    <handlers>
      <add name="aspNetCore" path="*" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified" />
    </handlers>
    <aspNetCore processPath="dotnet" arguments=".\Cortex.Clean.API.dll" stdoutLogEnabled="false" stdoutLogFile=".\logs\stdout" hostingModel="inprocess" />
  </system.webServer>
</configuration>
```

---

### 5. Linux Deployment (Systemd Service)

**Copy Files:**
```bash
sudo mkdir -p /var/www/cortex-clean-api
sudo cp -r ./publish/* /var/www/cortex-clean-api/
sudo chown -R www-data:www-data /var/www/cortex-clean-api
```

**Create Service File:**
```bash
sudo nano /etc/systemd/system/cortex-clean-api.service
```

**cortex-clean-api.service:**
```ini
[Unit]
Description=Cortex Clean API
After=network.target

[Service]
WorkingDirectory=/var/www/cortex-clean-api
ExecStart=/usr/bin/dotnet /var/www/cortex-clean-api/Cortex.Clean.API.dll
Restart=always
RestartSec=10
SyslogIdentifier=cortex-clean-api
User=www-data
Environment=ASPNETCORE_ENVIRONMENT=Production
Environment=DOTNET_PRINT_TELEMETRY_MESSAGE=false

[Install]
WantedBy=multi-user.target
```

**Start Service:**
```bash
sudo systemctl enable cortex-clean-api
sudo systemctl start cortex-clean-api
sudo systemctl status cortex-clean-api
```

**Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection keep-alive;
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Frontend Deployment

### 1. Build for Production

```powershell
cd frontend
npm install
npm run build --configuration=production
```

**Output:** `dist/frontend/` folder with optimized bundle

---

### 2. Update Environment

**environment.prod.ts:**
```typescript
export const environment = {
  production: true,
  apiBaseUrl: 'https://api.yourdomain.com'
};
```

---

### 3. Static Hosting Options

**Option A: IIS (Windows)**
1. Copy `dist/frontend/*` to `C:\inetpub\wwwroot\cortex-clean\`
2. Add web.config for SPA routing:

```xml
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Angular Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

**Option B: Nginx (Linux)**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    root /var/www/cortex-clean;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Option C: Azure Static Web Apps**
```bash
# Install Azure CLI
az login
az staticwebapp create --name cortex-clean --resource-group MyResourceGroup --location eastus

# Deploy
az staticwebapp deploy --name cortex-clean --app-location ./dist/frontend
```

**Option D: Netlify**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd dist/frontend
netlify deploy --prod
```

---

## Database Migration Strategy

### Development → Staging → Production

**Step 1: Generate Migration Script**
```powershell
dotnet ef migrations script --idempotent -o migration-v1.0.0.sql
```

**Step 2: Review & Test in Staging**
```sql
-- Execute migration-v1.0.0.sql in staging database
-- Verify schema changes
-- Test application connectivity
```

**Step 3: Backup Production**
```sql
BACKUP DATABASE CortexCleanDb 
TO DISK = 'C:\Backups\CortexCleanDb_PreMigration.bak'
WITH FORMAT, INIT, COMPRESSION;
```

**Step 4: Execute in Production**
```sql
-- Execute migration-v1.0.0.sql during maintenance window
-- Monitor for errors
-- Verify application startup
```

---

## Monitoring & Health Checks

### Application Insights (Azure)

**Install Package:**
```powershell
dotnet add package Microsoft.ApplicationInsights.AspNetCore
```

**Configure (Program.cs):**
```csharp
builder.Services.AddApplicationInsightsTelemetry(
    builder.Configuration["ApplicationInsights:ConnectionString"]);
```

**appsettings.Production.json:**
```json
{
  "ApplicationInsights": {
    "ConnectionString": "InstrumentationKey=YOUR_KEY;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/"
  }
}
```

---

### Health Checks

**Add Endpoint (Program.cs):**
```csharp
builder.Services.AddHealthChecks()
    .AddDbContextCheck<ApplicationDbContext>();

app.MapHealthChecks("/health");
```

**Monitor:**
```bash
curl https://api.yourdomain.com/health
# Response: Healthy
```

---

## Security Checklist

- [ ] HTTPS enforced (SSL certificate installed)
- [ ] Connection strings in secure configuration (Azure Key Vault, env vars)
- [ ] CORS restricted to frontend domain only
- [ ] Serilog not logging sensitive data (PII)
- [ ] Error responses don't expose stack traces in production
- [ ] SQL Server firewall rules allow only application IP
- [ ] Application pool/service account has minimum permissions
- [ ] Regular security updates applied (dotnet, dependencies)

---

## Rollback Plan

### Backend Rollback

1. Stop IIS/systemd service
2. Restore previous publish folder
3. Rollback database migration:
   ```sql
   RESTORE DATABASE CortexCleanDb 
   FROM DISK = 'C:\Backups\CortexCleanDb_PreMigration.bak' 
   WITH REPLACE;
   ```
4. Restart service

### Frontend Rollback

1. Replace dist folder with previous version
2. Clear browser cache / CDN cache if applicable
3. Verify application loads

---

## Performance Optimization

**Backend:**
- Enable response compression (Gzip/Brotli)
- Add output caching for GET endpoints
- Database connection pooling (default in EF Core)
- Consider Redis for distributed caching

**Frontend:**
- Enable Angular production optimizations (default with `--prod`)
- Use CDN for static assets
- Enable HTTP/2
- Implement service worker for offline support

---

## Continuous Deployment (CI/CD)

### Azure DevOps Pipeline Example

**azure-pipelines.yml:**
```yaml
trigger:
  - main

pool:
  vmImage: 'windows-latest'

steps:
- task: UseDotNet@2
  inputs:
    version: '8.x'

- task: DotNetCoreCLI@2
  displayName: 'Build Backend'
  inputs:
    command: 'publish'
    publishWebProjects: true
    arguments: '-c Release -o $(Build.ArtifactStagingDirectory)/backend'

- task: NodeTool@0
  inputs:
    versionSpec: '18.x'

- script: |
    cd frontend
    npm install
    npm run build --prod
  displayName: 'Build Frontend'

- task: PublishBuildArtifacts@1
  inputs:
    PathtoPublish: '$(Build.ArtifactStagingDirectory)'
    ArtifactName: 'drop'
```

---

## Support & Troubleshooting

**Common Issues:**

1. **Database Connection Failed**
   - Check connection string
   - Verify SQL Server firewall rules
   - Test connection with SQL Server Management Studio

2. **CORS Errors**
   - Verify `AllowAngular` policy includes production frontend URL
   - Check browser developer console for exact error

3. **404 on Angular Routes**
   - Verify URL rewrite rules in IIS/Nginx
   - Check `<base href="/">` in index.html

4. **Slow Performance**
   - Enable Application Insights
   - Check database query performance (SQL Profiler)
   - Review Serilog logs for bottlenecks

---

**Last Updated:** December 7, 2025  
**Maintainer:** Asif Hussain
