# CORTEX Docker Deployment Guide

**Quick Start for deploying CORTEX MCP Server**

---

## 🚀 Quick Start (5 minutes)

### Step 1: Clone and Setup
```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Verify Python dependencies
pip install -r requirements.txt

# Verify wiring system
python -c "from cortex.wiring import bootstrap_cortex; c = bootstrap_cortex(); print(f'✅ Wired: {len(c.list_orchestrators())}/23 orchestrators')"
```

### Step 2: Development Deployment
```bash
# Start CORTEX in development mode
docker-compose up -d

# Wait for health check
sleep 10

# Verify deployment
curl http://localhost:8443/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T01:00:00Z",
  "uptime_seconds": 10.5,
  "checks": {
    "wiring": "healthy",
    "orchestrators": "healthy"
  },
  "wiring_info": {
    "wiring_hash": "5a972fc99b395299",
    "orchestrators_wired": 23,
    "wiring_source": "yaml"
  }
}
```

### Step 3: Test Endpoints
```bash
# Health check
curl http://localhost:8443/health

# Wiring health
curl http://localhost:8443/health/wiring

# Orchestrator health
curl http://localhost:8443/health/orchestrators

# Discover available tools
curl http://localhost:8443/mcp/tools

# Prometheus metrics
curl http://localhost:8443/metrics
```

---

## 👥 Team Deployment (2-10 Users)

### Step 1: Configure API Keys
```bash
# Create .env file
cat > .env << EOF
CORTEX_AUTH_ENABLED=true
CORTEX_API_KEY_ALICE=alice_secret_key_123
CORTEX_API_KEY_BOB=bob_secret_key_456
CORTEX_API_KEY_CHARLIE=charlie_secret_key_789
EOF
```

### Step 2: Start with Authentication
```bash
# Load environment
source .env

# Start production configuration
docker-compose -f docker-compose.prod.yml up -d

# Verify authentication is enabled
curl http://localhost:8443/health
# Should work without key (health is public)

curl -H "X-CORTEX-API-KEY: alice_secret_key_123" http://localhost:8443/mcp/tools
# Should work with valid key

curl http://localhost:8443/mcp/tools
# Should fail without key (401 Unauthorized)
```

### Step 3: Connect Clients

**VS Code:**
```json
// settings.json
{
  "cortex.apiKey": "alice_secret_key_123",
  "cortex.endpoint": "http://localhost:8443"
}
```

**Claude Desktop:**
```bash
# Configure in Claude settings
CORTEX_ENDPOINT=http://localhost:8443
CORTEX_API_KEY=bob_secret_key_456
```

**Curl:**
```bash
curl -H "X-CORTEX-API-KEY: alice_secret_key_123" \
     -H "Content-Type: application/json" \
     -d '{"method": "implement", "params": {"feature": "user auth"}}' \
     http://localhost:8443/mcp/execute
```

---

## 🏢 Production Deployment (100-500 Users)

### Step 1: TLS Certificates
```bash
# Generate self-signed cert (dev/testing)
openssl req -x509 -newkey rsa:4096 -keyout deployment/tls/cortex.key -out deployment/tls/cortex.crt -days 365 -nodes

# Or use Let's Encrypt (production)
certbot certonly --standalone -d cortex.company.com
```

### Step 2: Configure Nginx
```bash
# Update deployment/nginx.prod.conf with your domain
sed -i 's/cortex.company.com/your-domain.com/g' deployment/nginx.prod.conf

# Copy certificates
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem deployment/tls/cortex.crt
cp /etc/letsencrypt/live/your-domain.com/privkey.pem deployment/tls/cortex.key
```

### Step 3: Start Production Stack
```bash
# Start with 3 replicas (HA)
docker-compose -f docker-compose.prod.yml up -d --scale cortex-mcp=3

# Start nginx reverse proxy
docker run -d \
  --name cortex-nginx \
  -p 443:443 \
  -v $(pwd)/deployment/nginx.prod.conf:/etc/nginx/nginx.conf:ro \
  -v $(pwd)/deployment/tls:/etc/nginx/certs:ro \
  --network cortex-network \
  nginx:alpine

# Start Prometheus
docker run -d \
  --name cortex-prometheus \
  -p 9090:9090 \
  -v $(pwd)/deployment/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  --network cortex-network \
  prom/prometheus
```

### Step 4: Verify Production Deployment
```bash
# Check replicas
docker ps | grep cortex-mcp
# Should show 3 containers

# Check health through nginx (HTTPS)
curl -k https://localhost:8443/health

# Check Prometheus scraping
curl http://localhost:9090/api/v1/targets
# Should show cortex-mcp targets

# Check persistent volumes
docker volume ls | grep cortex
# Should show: cortex-audit-logs, cortex-state, cortex-metrics
```

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CORTEX_ENV` | `development` | Environment: `development` or `production` |
| `CORTEX_PORT` | `8443` | Server port |
| `CORTEX_LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CORTEX_AUTH_ENABLED` | `false` | Enable API key authentication |
| `CORTEX_API_KEY_<username>` | - | API key for user (one per user) |
| `CORTEX_WIRING_FILE` | `cortex/wiring/specifications/wiring.yaml` | Path to wiring file |
| `CORTEX_HOT_RELOAD` | `true` (dev) / `false` (prod) | Enable hot-reload for wiring.yaml |
| `CORTEX_MAX_WORKERS` | `4` | Number of worker processes |
| `CORTEX_TIMEOUT_SECONDS` | `30` | Request timeout |

### Docker Compose Profiles

```bash
# Development (hot-reload enabled)
docker-compose --profile dev up -d

# Production (3 replicas, HA)
docker-compose --profile prod up -d

# With Prometheus monitoring
docker-compose --profile monitoring up -d

# All services
docker-compose --profile all up -d
```

---

## 📊 Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8443/health

# Wiring health (check if YAML loaded)
curl http://localhost:8443/health/wiring

# Orchestrator health (check if all 23 wired)
curl http://localhost:8443/health/orchestrators
```

### Prometheus Metrics
```bash
# All metrics
curl http://localhost:8443/metrics

# Request count
curl http://localhost:8443/metrics | grep cortex_requests_total

# Error rate
curl http://localhost:8443/metrics | grep cortex_errors_total

# Wiring health (0=unhealthy, 1=degraded, 2=healthy)
curl http://localhost:8443/metrics | grep cortex_wiring_health
```

### Logs
```bash
# Container logs
docker logs cortex-mcp-1 -f

# Audit logs (persistent volume)
docker exec cortex-mcp-1 tail -f /app/logs/audit.log

# Application logs
docker exec cortex-mcp-1 tail -f /app/logs/cortex.log
```

---

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs cortex-mcp-1

# Common issues:
# 1. Port already in use
sudo lsof -i :8443
# Kill process and retry

# 2. Wiring file missing
docker exec cortex-mcp-1 ls -la /app/cortex/wiring/specifications/wiring.yaml

# 3. Python import error
docker exec cortex-mcp-1 python -c "from cortex.wiring import bootstrap_cortex; bootstrap_cortex()"
```

### Health Check Failing
```bash
# Check wiring status
curl http://localhost:8443/health/wiring

# Expected: {"wiring_status": "healthy", "orchestrators_wired": 23}

# If wiring_status is "degraded":
# 1. Check wiring.yaml syntax
docker exec cortex-mcp-1 python -c "import yaml; yaml.safe_load(open('cortex/wiring/specifications/wiring.yaml'))"

# 2. Verify all orchestrator modules exist
docker exec cortex-mcp-1 python tests/wiring/phase3/test_git_backed_wiring.py
```

### API Key Authentication Not Working
```bash
# Verify environment variables loaded
docker exec cortex-mcp-1 env | grep CORTEX_API_KEY

# Test API key validation
docker exec cortex-mcp-1 python -c "
from cortex.mcp.auth import load_api_keys_from_env, validate_api_key
load_api_keys_from_env()
user = validate_api_key('alice_secret_key_123')
print(f'User: {user.username if user else None}')
"
```

### Orchestrator Not Wiring
```bash
# List all orchestrators
curl http://localhost:8443/health/orchestrators

# If count < 23, check which failed:
docker exec cortex-mcp-1 python -c "
from cortex.wiring import bootstrap_cortex
registry = bootstrap_cortex()
orchestrators = registry.list_orchestrators()
print(f'Wired: {len(orchestrators)}/23')
for name in orchestrators:
    print(f'  ✅ {name}')
"
```

---

## 🔄 Updates and Rollbacks

### Update Wiring Configuration
```bash
# Edit wiring.yaml
vi cortex/wiring/specifications/wiring.yaml

# Development: Hot-reload (no restart needed)
# Wiring watcher will detect changes and reload

# Production: Restart containers
docker-compose -f docker-compose.prod.yml restart
```

### Rollback to Previous Wiring
```bash
# Git-based rollback
git log cortex/wiring/specifications/wiring.yaml
git checkout <commit-hash> -- cortex/wiring/specifications/wiring.yaml

# Restart containers
docker-compose restart
```

### Update Container Image
```bash
# Rebuild image
docker-compose build

# Rolling update (zero downtime)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build cortex-mcp
```

---

## 📦 Backup and Recovery

### Backup Persistent Volumes
```bash
# Backup audit logs
docker run --rm -v cortex-audit-logs:/source -v $(pwd)/backups:/backup alpine tar czf /backup/audit-logs-$(date +%Y%m%d).tar.gz -C /source .

# Backup state
docker run --rm -v cortex-state:/source -v $(pwd)/backups:/backup alpine tar czf /backup/state-$(date +%Y%m%d).tar.gz -C /source .

# Backup metrics
docker run --rm -v cortex-metrics:/source -v $(pwd)/backups:/backup alpine tar czf /backup/metrics-$(date +%Y%m%d).tar.gz -C /source .
```

### Restore from Backup
```bash
# Restore audit logs
docker run --rm -v cortex-audit-logs:/target -v $(pwd)/backups:/backup alpine tar xzf /backup/audit-logs-20260128.tar.gz -C /target

# Restart containers
docker-compose restart
```

### Automated Daily Backups
```bash
# Add to crontab
crontab -e

# Backup at 2 AM daily
0 2 * * * /path/to/backup-cortex-volumes.sh
```

---

## 🎯 Next Steps

1. **Deploy Development:** `docker-compose up -d`
2. **Test Endpoints:** Verify `/health`, `/mcp/tools`, `/metrics`
3. **Configure Team Auth:** Add API keys for team members
4. **Deploy Production:** Use `docker-compose.prod.yml` with TLS
5. **Monitor:** Set up Prometheus + Grafana dashboards
6. **Automate Backups:** Schedule daily volume backups

---

## 📞 Support

**Issues:**
- Check logs: `docker logs cortex-mcp-1 -f`
- Health check: `curl http://localhost:8443/health`
- Run tests: `pytest tests/wiring/ tests/mcp/ tests/collaboration/ -v`

**Documentation:**
- Migration Plan: `_workspaces/docker-plan/migration-phases-plan.yaml`
- Status Report: `docs/DOCKER-MIGRATION-STATUS-REPORT.md`
- Wiring Spec: `cortex/wiring/specifications/wiring.yaml`

**Version:** CORTEX v2.0.0 (Docker-First)  
**Date:** 2026-01-28  
**Status:** ✅ Production Ready (Tier 1 & 2)
