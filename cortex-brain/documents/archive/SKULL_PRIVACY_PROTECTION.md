SKULL-006: Privacy Protection

Real incident (2025-11-12):
- User runs publish script
- Discovers .coverage.AHHOME.12345.XgvxuuYx in publish/CORTEX/
- 7 coverage files with machine name exposed
- logs/ambient_capture.log contains C:\Windows\Temp paths
- cortex.config.json contains AHHOME machine paths
- health-reports/ has user-specific diagnostic data

Impact:
- Privacy violation (machine names, usernames exposed)
- Distribution bloat (unnecessary test artifacts)
- Professionalism degradation (dev artifacts in user package)

SKULL-006 prevents this by:
1. Scanning published files for machine-specific patterns
2. Requiring publish script exclude logs, coverage, health data
3. Blocking publish if privacy leaks detected
4. Enforcing template configs instead of real paths

Implementation:
- Add EXCLUDE_PATTERNS to publish script (logs, coverage, health)
- Create test_publish_privacy.py that scans for leaks
- Add pre-publish hook that runs privacy scan
- Use cortex.config.template.json instead of cortex.config.json
