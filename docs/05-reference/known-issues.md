# Known Issues & Workarounds

Track known issues and recommended workarounds.

## Performance

### Issue: Knowledge queries are slow
**Symptom**: `Domain Brain query timeout` in logs  
**Root Cause**: Large knowledge base without proper indexing  
**Workaround**:
```bash
# Reindex knowledge repository
cortex admin reindex-knowledge --parallel 4
```
**Fix**: Upgrade to next version with query optimization

---

### Issue: High memory usage in production
**Symptom**: CORTEX process uses >4GB RAM  
**Root Cause**: Unbounded in-memory cache  
**Workaround**:
```yaml
# In cortex-config.yaml
cache:
  max_size: 1000
  ttl: 3600
```

---

## Operational

### Issue: Audit trail database locked
**Symptom**: `governance.db is locked` error  
**Root Cause**: Multiple CORTEX instances writing simultaneously  
**Workaround**: Ensure only one writer instance  
**Fix**: Use PostgreSQL backend for multi-instance setup

---

### Issue: Orchestrator timeout during knowledge retrieval
**Symptom**: Orchestrator fails with timeout after 30s  
**Root Cause**: Knowledge Brain is slow  
**Workaround**:
```yaml
# Increase timeout in orchestrator context
timeout: 60  # seconds
```

---

## Integration

### Issue: REST API returns 401 even with valid token
**Symptom**: `Unauthorized` from valid JWT token  
**Root Cause**: Token clock skew  
**Workaround**: Sync system clocks across infrastructure

---

## Documentation

For detailed troubleshooting, see [Troubleshooting Guide](../04-guides/operations/4-troubleshooting.md).
