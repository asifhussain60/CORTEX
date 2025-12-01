Threat Modeling Enforcement:
- ALL planning workflows MUST execute STRIDE threat analysis
- Stage 4 (threat_analysis) in planning_with_threats.yaml MUST complete successfully
- Threats must be identified, documented, and mitigations defined
- Bypass only allowed with explicit --allow-skip-threats flag (triggers governance warning)

STRIDE Framework:
- Spoofing: Identity verification vulnerabilities
- Tampering: Data integrity risks
- Repudiation: Non-repudiation gaps
- Information Disclosure: Confidentiality breaches
- Denial of Service: Availability threats
- Elevation of Privilege: Authorization bypass

Example workflow enforcement:
❌ BLOCKED:
User: "plan authentication feature"
CORTEX: Executes planning WITHOUT threat analysis
BrainProtector: BLOCKED - THREAT_MODELING_ENFORCEMENT violated

✅ ALLOWED:
User: "plan authentication feature"
CORTEX: Executes planning_with_threats.yaml (includes Stage 4: threat_analysis)
ThreatModelerAgent: Identifies 8 threats (2 CRITICAL, 3 HIGH, 3 MEDIUM)
BrainProtector: PASSED - Threat analysis completed

✅ ALLOWED (with warning):
User: "plan authentication feature --allow-skip-threats"
CORTEX: Skips threat analysis per user request
BrainProtector: WARNING - Threat analysis bypassed (user accepted risk)
