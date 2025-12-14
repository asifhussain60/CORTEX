# Admin Guide

**Generated**:   
**Version**: 

This guide covers administrative tasks for CORTEX 3.0, including system maintenance, monitoring, and troubleshooting.

## System Administration

### Daily Operations

#### Health Monitoring

Run health checks daily:

```bash
python -m src.epm.health_check
```

Review output for:
- ✓ All services running
- ✓ No critical errors
- ✓ Memory usage within limits
- ✓ Disk space available

#### Log Review

Check logs for anomalies:

```bash
# Recent errors
grep "ERROR" logs/**/*.log | tail -20

# Recent operations
tail -f logs/operations/operations.log
```

#### Backup Verification

Verify backups are being created:

```bash
ls -lh *-backup-* | tail -5
```

### Weekly Operations

#### Knowledge Graph Cleanup

Review and clean stale knowledge:

```bash
python -m src.epm.knowledge_cleanup --dry-run
python -m src.epm.knowledge_cleanup
```

#### Performance Review

Check performance metrics:

```bash
python -m src.epm.metrics_report --period=week
```

#### Conversation Archive

Archive old conversations:

```bash
python -m src.epm.conversation_archiver --days=30
```

### Monthly Operations

#### Full System Health Check

Comprehensive health assessment:

```bash
python -m src.epm.health_check --comprehensive
```

#### Documentation Update

Regenerate documentation after major changes:

```bash
# Always dry-run first
python -m src.epm.doc_generator --dry-run

# Review output, then execute
python -m src.epm.doc_generator
```

#### Backup Rotation

Clean old backups (keep last 5):

```bash
python -m src.epm.backup_manager --rotate=5
```

## Entry Point Modules (EPMs)

### Documentation Generator

**When to Run**: After major code changes, new features, or architectural updates

**Preparation**:
1. Ensure all YAML files are valid
2. Update templates if needed
3. Review source mappings
4. Commit current work

**Execution**:
```bash
# 1. Dry-run to preview
python -m src.epm.doc_generator --dry-run

# 2. Review output carefully
# 3. Execute
python -m src.epm.doc_generator

# 4. Verify output
mkdocs serve

# 5. Review in browser
# http://localhost:8000
```

**Post-execution**:
- Review generated pages
- Check for broken links
- Verify diagrams render correctly
- Commit generated documentation

### Health Check

**When to Run**: Daily, or after system changes

```bash
python -m src.epm.health_check
```

**What it checks**:
- Brain structure integrity
- Configuration validity
- Agent status
- Tier data health
- System resources

### Cleanup Manager

**When to Run**: When disk space is low, or for maintenance

```bash
# Preview cleanup
python -m src.epm.cleanup_manager --dry-run

# Execute cleanup
python -m src.epm.cleanup_manager
```

**What it cleans**:
- Old conversation logs
- Temporary files
- Expired metrics
- Stale cache

## Monitoring

### Key Metrics

Monitor these metrics:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate | < 1% | Investigate if higher |
| Response time | < 2s | Optimize if slower |
| Memory usage | < 80% | Scale if higher |
| Disk usage | < 90% | Clean up if higher |
| Knowledge graph size | < 100MB | Archive if larger |

### Alerting

Set up alerts for critical events:

```yaml
# alerts.yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 0.01
    action: notify_admin
  
  - name: low_disk_space
    condition: disk_usage > 0.90
    action: trigger_cleanup
  
  - name: agent_failure
    condition: agent_status == "failed"
    action: restart_agent
```

### Log Analysis

Key logs to monitor:

```bash
# Operations log
tail -f logs/operations/operations.log

# Error log
tail -f logs/errors/errors.log

# Agent log
tail -f logs/agents/agents.log
```

## Troubleshooting

### Common Issues

#### EPM Fails with Validation Error

**Symptom**: Pre-flight validation fails

**Solution**:
1. Check validation output for specific error
2. Fix the issue (missing file, invalid YAML, etc.)
3. Re-run EPM

#### Documentation Generator Produces Broken Links

**Symptom**: Cross-reference builder reports broken links

**Solution**:
1. Review `page-definitions.yaml`
2. Check template link syntax
3. Verify target pages exist
4. Re-run generator

#### Knowledge Graph Grows Too Large

**Symptom**: Slow performance, high memory usage

**Solution**:
```bash
# Archive old patterns
python -m src.epm.knowledge_archiver --age=90

# Optimize graph
python -m src.epm.knowledge_optimizer
```

#### Agent Not Responding

**Symptom**: Agent operations time out

**Solution**:
1. Check agent logs
2. Verify agent configuration
3. Restart agent:
```bash
python -m src.agents.restart --agent=code_executor
```

### Getting Help

If you can't resolve an issue:

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review [GitHub Issues](/issues)
3. Check logs for detailed error messages
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Log excerpts
   - System info

## Security

### Brain Protection

The cortex-brain is protected by multiple layers:

1. **File-level protection**: Rules in `brain-protection-rules.yaml`
2. **Operation validation**: Pre-flight checks
3. **Backup system**: Automatic backups before changes
4. **Audit logging**: All brain modifications logged

### Access Control

Limit access to sensitive operations:

```yaml
# access-control.yaml
roles:
  admin:
    - run_epm
    - modify_brain
    - access_logs
  
  developer:
    - read_brain
    - run_operations
    - access_logs
  
  viewer:
    - read_brain
```

### Audit Trail

Review audit logs regularly:

```bash
# Brain modifications
grep "brain_modify" logs/audit/audit.log

# EPM executions
grep "epm_execute" logs/audit/audit.log
```

## Maintenance Schedule

### Recommended Schedule

| Task | Frequency | Time Required |
|------|-----------|---------------|
| Health check | Daily | 5 min |
| Log review | Daily | 10 min |
| Backup verification | Daily | 5 min |
| Knowledge cleanup | Weekly | 15 min |
| Performance review | Weekly | 20 min |
| Documentation update | Monthly | 30 min |
| Full health check | Monthly | 1 hour |
| Backup rotation | Monthly | 10 min |

## Best Practices

1. **Always use dry-run first**: Preview EPM operations before executing
2. **Keep backups**: Never skip backup creation
3. **Monitor logs**: Set up log monitoring and alerting
4. **Document changes**: Update documentation after major changes
5. **Test on branches**: Run destructive operations on feature branches
6. **Review regularly**: Schedule regular health checks
7. **Archive proactively**: Don't wait for disk space issues
8. **Version control**: Keep brain files in git

## Advanced Topics

### Custom EPM Development

See [EPM Guide](entry-point-modules.md#creating-a-new-epm) for creating custom EPMs.

### Performance Tuning

Optimize CORTEX performance:

1. **Tier caching**: Adjust tier cache sizes
2. **Agent pooling**: Configure agent pool size
3. **Knowledge graph**: Optimize graph structure
4. **Metrics retention**: Reduce metrics history

### Disaster Recovery

If the brain is corrupted:

1. Stop all operations
2. Restore from latest backup:
```bash
python -m src.epm.restore_backup --backup=backup-timestamp
```
3. Verify restoration:
```bash
python -m src.epm.health_check --comprehensive
```
4. Resume operations

## Related Documentation

- [Operations Overview](../operations/overview.md)
- [EPM Guide](../operations/entry-point-modules.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Architecture Overview](../architecture/overview.md)

---

*This page was automatically generated by the CORTEX Documentation Generator.*