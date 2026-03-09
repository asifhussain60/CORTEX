# Video Prompt 05 — What Is CORTEX? (Security Engineers)

---
**Series:** CORTEX — The Governed AI Engineering Partner
**Video:** 05 of 07 (Role Series)
**Title:** What Is CORTEX? For Security Engineers
**Subtitle:** Five-Layer Defence-in-Depth, STRIDE + OWASP Enforcement, and Tamper-Evident Evidence
**Audience:** Security engineers, AppSec teams, penetration testers, compliance architects, DevSecOps practitioners
**Duration:** 7–10 minutes
**Narrator:** 🎙️ Female (VBP-017 — odd-numbered video)
**Generator:** Google Gemini Video Generator / NotebookLM Video Editor
**Last Updated:** 2026-03-08
**VBP Rules Applied:** VBP-001 through VBP-019 (full compliance)
**Content Sources:** `01-platform`, `03-governance`, `07-security`, `09-lifecycle`
**Series Context:** Video 01 introduced the CORTEX platform and its three mission pillars. This video does NOT repeat that introduction — it goes deep on security-specific capabilities: the five-layer defence model, STRIDE threat modelling with full six-category analysis, OWASP Top 10 release gate, secret sanitisation before commit, and the hash-chain tamper-evident audit trail.

---

## 🎯 Learning Objective

Security engineers understand that CORTEX implements defence-in-depth as a structural property of the development process — five security layers, STRIDE threat modelling across all six categories with DREAD risk scoring, OWASP Top 10 enforced at every release gate, automatic secret sanitisation before commit, and a cryptographic hash-chain audit trail that makes tampering structurally detectable.

---

## 🎬 MANDATORY Hero Intro Slide (VBP-014 — 5 seconds)

**Scene:** Full-screen `#0a0e27` deep space navy. Floating red (`#ff4444`) and cyan particles drift at 4% opacity — subtle threat-awareness aesthetic.

**Centre frame:**
- `cortex-logo-512.png` — large, hero-scale, pulsing cyan glow
- **Above logo:** "What Is CORTEX?" — Space Grotesk Bold, `#ffffff`, 48px
- **Below logo:** "For Security Engineers — Defence-in-Depth as Development Infrastructure" — Inter Regular, `#a0a6c0`, 20px, typewriter reveal

**Hold 5 seconds → logo to watermark → Scene 1 fades in.**

---

## Scene 1 — The Hook: Where Security Fails (0:05 – 0:40)

**Visual (VBP-006 — pain before solution):**

A timeline bar labelled "Traditional Development Lifecycle":

```
[Requirements] → [Design] → [Implementation] → [Code Review] → [QA] → [Security Scan] → [Production]
```

A red skull icon appears only at "Security Scan" and "Production". Text below: `"Security enters here — too late."` — `#ff4444`.

Beneath the timeline: four incident cards, staggered reveal:

```
💀  Secret committed 6 weeks ago — now in production logs
💀  OWASP injection vulnerability — passed three code reviews
💀  Dependency CVE — published 3 weeks before anyone noticed
💀  Tampered audit record — no mechanism to detect modification
```

**Narration:**
> "In most organisations, security enters the development lifecycle at the end — a scan before release, a review before production. By that point, a secret committed six weeks ago has propagated through the build system, the CI logs, and the container registry. An injection vulnerability has survived three code reviews. A dependency CVE has been active in production for three weeks before the scanner ran. And a tampered audit record is indistinguishable from a genuine one. CORTEX moves security to where these things cost nothing to fix — the very beginning."

**VBP-002:** Hook at 0:07.
**VBP-011:** 2s silence after the four incident cards.

---

## Scene 2 — Five Security Layers: Defence-in-Depth (0:40 – 1:25)

**Visual:**
A shield wall — five translucent shields stacked in depth perspective, front to back, each a darker shade from `rgba(0,212,255,0.3)` to `rgba(0,212,255,0.05)`. Each shield glows as narrated:

| Shield | Layer | What It Blocks |
|--------|-------|---------------|
| Shield 1 (front) | Before Commit | Secrets, PII, credentials — blocked before version control |
| Shield 2 | Governance Rules | Bare exception catches, missing type hints, WAL enforcement |
| Shield 3 | Code Intelligence (LENS) | SQL injection, XSS, credential exposure, known vulnerability patterns |
| Shield 4 | Static Analysis + CVE | SAST scan, dependency database, CVE scoring |
| Shield 5 (back) | Release Gate | OWASP Top 10 + STRIDE threat model review |

A cyan "clean commit" particle travels through all five shields → exits as `#00ff88` green.
A red "malicious commit" particle hits Shield 1 → bounces back with red flash + shake.
A second red particle bypasses Shield 1 → blocked by Shield 3 → bounces back.

**Narration:**
> "CORTEX implements security at five distinct layers — because no single layer needs to be perfect. The combination is what makes it robust. A vulnerability that evades the code intelligence layer is caught by static analysis. One that passes static analysis is stopped at the release gate. A secret that slips through pattern matching is caught by the SAST scan. Defence-in-depth means the system remains secure even when individual layers are imperfect — because the combination covers the gaps."

**VBP-010 (Analogy):** "Like a facility with perimeter fence, locked entry, access cards, CCTV, and motion detection — no single control is sufficient; the combination is what protects." Dark pill.

---

## Scene 3 — Secret Sanitisation: Before Commit, Before History (1:25 – 2:05)

**Visual:**
A VS Code editor simulation (dark glass). A developer stages a config file. A pre-commit hook fires:

```
CORTEX Pre-Commit Security Gate — Layer 1
──────────────────────────────────────────
🔍 Scanning staged files... (312 patterns active)
❌ SECRET DETECTED
   File:     config/settings.py (line 47)
   Pattern:  AWS_ACCESS_KEY_ID = "AKIA..."
   Severity: CRITICAL
   Action:   COMMIT BLOCKED — remove secret before staging

❌ SECRET DETECTED
   File:     tests/fixtures/test_data.py (line 83)
   Pattern:  api_key = "sk-abc..."
   Severity: CRITICAL
   Action:   COMMIT BLOCKED
```

Red border glow. The commit is rejected.

Below: the log redaction layer:
```
# Raw log entry (before redaction):
"Authenticating user with token=sk-abc123def456ghi789..."

# Sanitised output (after redaction):
"Authenticating user with token=[REDACTED]"
```

**Narration:**
> "Before any code enters version control, CORTEX's secret detection engine scans every staged file against 312 detection patterns — AWS keys, GitHub tokens, private key PEMs, database credentials, API secrets across every major provider. A commit containing any detected secret is blocked immediately. The same sanitisation engine runs through every log output: tokens, PII, and credentials are automatically redacted before they can appear in debug traces, error reports, or structured logging. Your git history never contains a secret — because the commit never reaches it."

**VBP-016:** Bold: **"blocked immediately"**, **"312 patterns"**, **"history never contains a secret"** in `#ff4444`.

---

## Scene 4 — STRIDE Threat Modelling: All Six Categories (2:05 – 2:50)

**Visual:**
A STRIDE matrix card (glassmorphism, red left-border). Each row reveals with a slide-in from left, then a DREAD score card animates beside it:

```
STRIDE Threat Model — /api/auth/login
──────────────────────────────────────────────────────────────────────────────
Category          Threat                                    DREAD   Severity
──────────────────────────────────────────────────────────────────────────────
S  Spoofing       Session fixation via predictable tokens   8.2     CRITICAL
T  Tampering      JWT payload modification without re-sign  7.8     HIGH
R  Repudiation    Missing structured audit log on auth fail 5.1     MEDIUM
I  Info Disclosure Error message reveals valid username      4.9     MEDIUM
D  Denial of Svc  No rate limiting on login endpoint        7.3     HIGH
E  Elevation      Admin role assigned without 2FA check     9.1     CRITICAL
```

Each DREAD score bar fills left to right in `#ff4444` for CRITICAL, `#ffa500` for HIGH, `#fbbf24` for MEDIUM.

**Narration:**
> "CORTEX's Threat Model Engine applies the full STRIDE classification to any entry point, data flow, or trust boundary in your codebase. Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege — all six categories assessed and scored. Each threat receives a DREAD risk score: Damage potential, Reproducibility, Exploitability, Affected users, Discoverability. The output is a ranked threat catalogue with mitigations — reproducible on demand, not just at release, and auditable as evidence of your security assessment process."

**VBP-018:** STRIDE and DREAD expanded on first use.
**VBP-009 (Signaling):** Each STRIDE row glows as narrated; prior rows dim to 40%.

---

## Scene 5 — OWASP Top 10 Release Gate (2:50 – 3:30)

**Visual:**
A release gate card (glassmorphism, red-to-cyan gradient top border). Ten OWASP categories listed with gate status:

```
OWASP Top 10 Release Gate — Sprint 47
──────────────────────────────────────────────────────────
A01 Broken Access Control          ✅ PASS  — role enforcement verified
A02 Cryptographic Failures         ✅ PASS  — TLS 1.3, no weak ciphers
A03 Injection                      ✅ PASS  — parameterised queries enforced
A04 Insecure Design                ✅ PASS  — threat model completed
A05 Security Misconfiguration      ✅ PASS  — defaults reviewed
A06 Vulnerable/Outdated Components ✅ PASS  — CVE scan clean
A07 ID & Auth Failures             ⚠️ WARN  — session timeout below 30 min
A08 Software & Data Integrity      ✅ PASS  — hash-chain verified
A09 Logging & Monitoring Failures  ✅ PASS  — structured logging + traces
A10 SSRF                           ✅ PASS  — external URL allowlist enforced

Gate result: 9/10 PASS | 1 ADVISORY
Action required: Review session timeout (A07) before release
```

**Narration:**
> "Every release in CORTEX passes through an OWASP Top 10 gate — not as documentation, but as a structural check against the codebase as it exists at release time. Each of the ten categories is evaluated against live code analysis: injection patterns, cryptographic choices, access control enforcement, dependency CVE status, SSRF protections. An advisory finding blocks release until acknowledged. A failing check blocks release until resolved. No release certificate is issued until the gate is satisfied."

---

## Scene 6 — Tamper-Evident Audit Trail: Hash-Chain Integrity (3:30 – 4:10)

**Visual:**
An audit trail visualised as a chain of linked record blocks:

```
Record 001 →[sha256:a3f9…]→ Record 002 →[sha256:b7c2…]→ Record 003 →[sha256:d4e1…]→ ...
[2026-03-08 14:22:07]        [2026-03-08 14:22:31]        [2026-03-08 14:23:15]
[governance: PASS]           [security: PASS]             [tdd: PASS]
[operator: TDDOrchestrator]  [operator: SecurityGate]     [operator: ReviewOrchestrator]
```

A tamper simulation: Record 002 is highlighted red — "modified externally". The hash arrow from Record 001 to Record 002 breaks — red crack animation. A tamper alert card:
```
🚨 CHAIN INTEGRITY VIOLATION
   Record 002 hash mismatch
   Expected: sha256:b7c2...4a19
   Actual:   sha256:f2d8...99c3
   Status:   TAMPER DETECTED — record modified after write
```

Below: an evidence bundle card (glassmorphism, green border):
```
🎖️ Evidence Bundle — Sprint 47 Release
  Tests:        ✅ All passed (hash: sha256:e8f1...2b44)
  Governance:   ✅ 60+ rules satisfied
  OWASP Gate:   ✅ 10/10 categories passed
  STRIDE Model: ✅ Completed (6 categories, 12 findings, 12 mitigated)
  Secrets:      ✅ Zero detected across 847 commits
  Chain hash:   sha256:a3f9...7c21 — verified
```

**Narration:**
> "Every CORTEX operation writes to a tamper-evident audit trail using cryptographic hash chaining. Each record includes the hash of the previous record — forming a chain where any modification to any historical record breaks every subsequent link. You do not need a blockchain: the chain itself is the proof. When an auditor asks whether a governance check was performed seven months ago, CORTEX retrieves the record in under one second and proves it has not been modified. Evidence is not assembled retroactively — it accumulates continuously, verified at every link."

**VBP-013 (Business Book):** Callout: *"In God we trust. All others must bring data."* — W. Edwards Deming. Dark pill.

---

## Scene 7 — Security in the Delivery Lifecycle: Three Gates (4:10 – 4:50)

**Visual:**
The seven-phase lifecycle pipeline (red-tinted domain colour):

```
[Requirements] → [Design] → [Implementation] → [Code Review]
→ [Integration] → [Security Assessment] → [Release Readiness]
```

Three red shield gate icons mark security-specific checkpoints:

- **Requirements:** `"Threat surface identified — STRIDE scope defined"`
- **Code Review:** `"Layer 3 (LENS) + Layer 4 (SAST) active — secrets and CVEs scanned"`
- **Security Assessment:** `"Layer 5 — OWASP Top 10 + STRIDE + CVE complete"`

At Release Readiness: the release certificate card includes a `Security: ✅ 5 layers satisfied` line.

**Narration:**
> "Security in CORTEX is not a phase — it is a gate at every phase. At requirements, the threat surface of the proposed feature is identified and the STRIDE scope is defined before design begins. During implementation, Layers 3 and 4 run continuously — LENS security analysis and SAST scanning surface findings in real time while context is fresh. At the security assessment phase, the full OWASP gate and STRIDE model review run — blocking release until both are satisfied. The release certificate documents which layers ran, what they found, and that all findings were resolved."

---

## Scene 8 — DevSecOps Integration: Where CORTEX Sits (4:50 – 5:25)

**Visual:**
A DevSecOps pipeline diagram with CORTEX overlaid at each stage:

```
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor
  │       │       │       │       │         │        │        │
STRIDE  Secret  SAST   OWASP  Gate    Evidence  Alerts  Traces
scope   scan    +LENS  gate   cert    bundle    Prom.   OTEL
```

A comparison card:
```
Traditional DevSecOps:      CORTEX Security:
  Security tool added at    Security as structural property
  each stage manually       of every stage — automatic
  Evidence assembled        Evidence accumulated
  at audit time             continuously
  Finding = ticket          Finding = immediate block or
  in backlog                ADVISORY requiring acknowledgement
```

**Narration:**
> "CORTEX does not replace your DevSecOps pipeline — it makes every stage of it security-aware by default. No manual tool configuration at each stage. No evidence assembly at audit time. No findings that silently enter a backlog. Every security finding is either an immediate block — commit rejected, gate failed — or an advisory requiring acknowledged resolution before the release certificate is issued. The security posture of your codebase is always visible, always current, and always evidenced."

---

## Scene 9 — Vision: Security as a Structural Property (5:25 – 5:55)

**Visual:**
Full-screen dark navy. A quote card — glassmorphism, red-to-cyan gradient top border:

> *"Security is not a product, but a process."*
> — Bruce Schneier, **Secrets and Lies**

Below: a second card:

> **"In CORTEX, security is not a process either — it is a structural property of every commit, every review, every release."**

**AUDIO: Strategic Silence — 2 seconds.**

**Narration:**
> "The most effective security is the security that requires no discipline to maintain — because it is enforced by the structure of the system. CORTEX builds security into every layer of the development process, where it is automatic, continuous, and evidenced. Not because your team is disciplined. Because the system is built that way."

---

## Scene 10 — Call to Action (5:55 – 6:10)

**Visual:**
Single centred card, glassmorphism, red-to-cyan gradient border:

> **"Five layers. STRIDE + DREAD. OWASP Top 10. Hash-chain evidence. Security that enforces itself."**

Below: `→ Explore the CORTEX security model for DevSecOps teams` in `#00d4ff`.
Breadcrumb (bottom): `05/07 — Security Engineers | 06 → Quality Engineers →`

**Narration:**
> "CORTEX is security infrastructure — not a security tool. The difference is that infrastructure does not require configuration or discipline to be active. It simply is."

---

## 🎬 Closing Title Card

`cortex-logo-512.png` hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Incident cards Scene 1, 0:07 |
| VBP-003 Narration ≠ slide text | ✅ Narration interprets; slides show data |
| VBP-004 Progressive disclosure | ✅ STRIDE rows reveal sequentially; OWASP gate line-by-line |
| VBP-005 Z/F pattern | ✅ Shield wall left-to-right; lifecycle pipeline left-to-right |
| VBP-006 Contrast storytelling | ✅ Traditional DevSecOps vs CORTEX Scene 8 |
| VBP-007 2-min visual cycles | ✅ New concept every scene |
| VBP-008 Title + duration + chapters | ✅ Intro slide + pipeline breadcrumbs |
| VBP-009 Signaling | ✅ STRIDE rows highlight sequentially; OWASP items tick in |
| VBP-010 Analogy | ✅ Physical facility security layers Scene 2; dark pill |
| VBP-011 Strategic silence | ✅ 2s after four incident cards Scene 1; 2s after Schneier quote Scene 9 |
| VBP-012 Consistent visual language | ✅ Red → cyan security domain gradient throughout |
| VBP-013 Business Book | ✅ Deming Scene 6; Schneier Scene 9 |
| VBP-014 Hero intro slide | ✅ `cortex-logo-512.png`, 5 seconds |
| VBP-015 Breadcrumb | ✅ Lifecycle pipeline Scene 7; shield layers Scene 2 |
| VBP-016 Bold key words | ✅ Red highlights on critical security terms |
| VBP-017 Female narrator | ✅ Odd-numbered video |
| VBP-018 No unexpanded acronyms | ✅ STRIDE, DREAD, OWASP, SAST, CVE, PII, TLS, SSRF, WAL, AC, VBP all expanded |
| VBP-019 Strategic colour | ✅ Red (`#ff4444`) → Cyan (`#00d4ff`) security domain |

---

## 🎵 Audio Direction

- **Background:** Low-frequency tense ambient pad — security operations room feel. Slow pulse, measured.
- **Incident cards (Scene 1):** Soft alarm-tone pulse per card — building tension; 2s absolute silence after last card
- **Shield clean pass (Scene 2):** Smooth chime cascade across 5 shields — ascending pitch
- **Shield block (Scene 2):** Sharp low-frequency thud + red flash
- **Pre-commit block (Scene 3):** Distinctive block-tone — unmistakable rejection signal
- **STRIDE row reveals (Scene 4):** Descending severity tone: CRITICAL = deep alert, MEDIUM = neutral
- **DREAD score bars (Scene 4):** Ascending fill sound per bar proportional to score
- **OWASP gate items (Scene 5):** Clean tick per PASS; warning tone on ADVISORY
- **Hash chain break (Scene 6):** Sharp metallic crack — tamper alert
- **Evidence bundle complete (Scene 6):** Ascending certified chime
- **Schneier quote silence (Scene 9):** Absolute silence — 2 full seconds, no music, no FX
- **Narration style:** Precise, measured, authoritative. 132 wpm. Zero hyperbole — security audiences require evidence, not claims.


**Visual (VBP-006 — pain before solution):**

A timeline bar labelled "Traditional Development Lifecycle":

```
[Requirements] → [Design] → [Implementation] → [Code Review] → [QA] → [Security Scan] → [Production]
```

A red skull icon appears at "Security Scan" and "Production" only. Text below: `"Security enters here."` — `#ff4444`.

Beneath the timeline: three incident cards, staggered reveal:

```
💀  Secret committed 6 weeks ago — exposed in production
💀  OWASP injection vulnerability — passed every code review
💀  Dependency CVE — published 3 weeks before anyone noticed
```

**Narration:**
> "In most organisations, security enters the development lifecycle at the end — a scan before release, a review before production. By that point, a secret committed six weeks ago has propagated through the build system. An injection vulnerability has survived three code reviews. A dependency CVE has been sitting in production for weeks before anyone noticed. CORTEX moves security to where it costs nothing to fix — the very beginning."

**VBP-002:** Hook at 0:07.
**VBP-011:** 1.5s silence after the three incident cards.

---

## Scene 2 — Five Security Layers: Defence-in-Depth (0:28 – 1:10)

**Visual:**
A shield wall — five translucent shields stacked in depth perspective, front to back, each a darker shade from `rgba(0,212,255,0.3)` to `rgba(0,212,255,0.05)`. Each shield glows as narrated:

| Shield | Layer | What It Blocks |
|--------|-------|---------------|
| Shield 1 (front) | Before Commit | Secrets, PII, credentials — blocked before version control |
| Shield 2 | Governance Rules | Bare exception catches, WAL enforcement, plan-first requirements |
| Shield 3 | Code Intelligence | SQL injection, XSS, credential exposure, known patterns |
| Shield 4 | Static Analysis + CVE | SAST, dependency vulnerability database, CVE scanning |
| Shield 5 (back) | Release Gate | OWASP Top 10 + STRIDE threat model review |

A cyan "clean commit" particle travels through all five shields smoothly → exits as `#00ff88` green.
A red "malicious commit" particle hits Shield 1 → bounces back with a red flash + shake animation.

**Breadcrumb bar (VBP-015, bottom):** `[Layer 1] → [Layer 2] → [Layer 3] → [Layer 4] → [Layer 5]` — current layer cyan.

**Narration:**
> "CORTEX implements security at five distinct layers — because no single layer needs to be perfect. The combination is what makes it secure. A vulnerability missed by the code intelligence layer is caught by static analysis. One that passes static analysis is stopped at the release gate by the OWASP Top 10 check. A clean commit travels through all five shields. A threat is stopped at the first one it fails."

**VBP-010 (Analogy):** "Like a building's security — perimeter fence, locked door, key card, CCTV, alarm. No single layer is enough; the combination is what protects." Dark pill.

---

## Scene 3 — Before Commit: Secret Sanitisation (1:10 – 1:40)

**Visual:**
A VS Code editor simulation (dark glass). A developer stages a file. A pre-commit hook fires:

```
CORTEX Pre-Commit Security Gate
─────────────────────────────────
🔍 Scanning staged files...
❌ SECRET DETECTED: API key in config/settings.py (line 47)
   Pattern: AWS_ACCESS_KEY_ID = "AKIA..."
   Severity: CRITICAL
   Action: COMMIT BLOCKED — remove secret before staging
```

Red border glow on the terminal card. The commit is rejected with a `git status` showing unstaged.

Below: a separate panel showing the secret redaction in the logging layer:
```python
# Before redaction:  "token=sk-abc123def456"
# After redaction:   "token=[REDACTED]"
```

**Narration:**
> "Before code enters version control, CORTEX's sanitisation engine scans every staged file for secrets — API keys, credentials, private keys, tokens — across hundreds of detection patterns. A commit containing any detected secret is blocked immediately. The same redaction engine runs through every log output, ensuring sensitive data cannot appear in debug traces, error reports, or observability tooling. Secrets never reach your git history."

**VBP-016:** Bold: **"BLOCKED"**, **"never reach your git history"** in `#ff4444` and `#00d4ff`.

---

## Scene 4 — STRIDE Threat Modelling: On Demand (1:40 – 2:10)

**Visual:**
A STRIDE matrix card (glassmorphism, red left-border), entries animated in row by row:

```
STRIDE Threat Model — /api/auth/login
──────────────────────────────────────────────────────
S  Spoofing          Session fixation via predictable tokens     CRITICAL
T  Tampering         JWT payload modification without re-sign    HIGH
R  Repudiation       Missing structured audit log on auth fail   MEDIUM
I  Info Disclosure   Error message reveals valid username        MEDIUM
D  Denial of Service No rate limiting on login endpoint          HIGH
E  Elevation         Admin role assigned without 2FA check       CRITICAL
```

Each row reveals with a slide-in from left. Severity badges colour-coded: `#ff4444` CRITICAL, `#ffa500` HIGH, `#fbbf24` MEDIUM.

**Narration:**
> "CORTEX includes a Threat Model Engine that applies STRIDE classification — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege — to any entry point, data flow, or trust boundary in your codebase. On demand, not just at release. The output is a ranked threat catalogue with risk scores and recommended mitigations. Your security assessment becomes evidence-based, reproducible, and auditable."

**VBP-018:** STRIDE expanded on first use.
**VBP-009 (Signaling):** Each STRIDE row glows as narrated; prior rows dim to 40%.

---

## Scene 5 — Security in the Delivery Lifecycle (2:10 – 2:40)

**Visual:**
The seven-phase lifecycle pipeline (red-tinted domain colour, `rgba(255,68,68,0.1)` background):

```
[Requirements] → [Design] → [Implementation] → [Code Review]
→ [Integration] → [Security Assessment] → [Release Readiness]
```

Red shield icons mark three "security gate" points:
- Requirements: `"Threat surface identified"`
- Code Review: `"Security pass included"`
- Security Assessment: `"OWASP Top 10 + STRIDE + CVE"`

**Narration:**
> "Security in CORTEX is not a phase that happens before release. It is a gate at every phase. During requirements, CORTEX identifies the threat surface of the proposed feature. During design, architectural choices are validated against security-by-design principles. During implementation, the security analyser runs on the code being written — findings surface immediately, while the context is fresh. During code review, a dedicated security pass scans for secrets, PII, and vulnerability patterns. At release, the complete OWASP check and threat model review run before any deployment proceeds."

---

## Scene 6 — Tamper-Evident Audit Trail (2:40 – 3:10)

**Visual:**
An audit trail visualised as a chain — each record linked by a cryptographic hash arrow:

```
Record 001  →[hash]→  Record 002  →[hash]→  Record 003  →[hash]→  ...
[timestamp]            [timestamp]            [timestamp]
[operation]            [operation]            [operation]
[governance: PASS]     [governance: PASS]     [governance: PASS]
```

A tamper attempt is simulated: Record 002 is highlighted red — "modified". The chain breaks at the hash arrow. A red alert card: `"Chain integrity violation detected at Record 002."`.

Below: an evidence bundle card (glassmorphism, green border):
```
🎖️ Evidence Bundle — Sprint 47 Release
  Tests:      ✅ All passed (hash verified)
  Governance: ✅ 60+ rules satisfied
  Security:   ✅ OWASP + STRIDE complete
  Secrets:    ✅ Zero detected
  Hash:       sha256:a3f9...7c21
```

**Narration:**
> "Every CORTEX operation writes to a tamper-evident audit trail using cryptographic hash chaining. Each record links to the previous one — any modification to historical records breaks the chain, providing proof of tampering without requiring a blockchain. Evidence bundles package validation results — test outcomes, governance checks, security findings — into hash-verified packages your auditor can verify independently."

**VBP-013 (Business Book):** Callout: *"Trust, but verify."* — Ronald Reagan (popularised in security contexts). Dark pill.

---

## Scene 7 — Call to Action (3:10 – 3:25)

**Visual:**
Single centred card, glassmorphism, red-to-cyan gradient border:

> **"Five layers. STRIDE modelling. Tamper-evident audit trail. Secret sanitisation. Security that proves itself."**

Below: `→ Explore the CORTEX security architecture` in `#00d4ff`.
Breadcrumb (bottom): `05/07 — Security Engineers | 06 → Quality Engineers →`

**Narration:**
> "CORTEX is designed so security teams can answer the hardest audit questions — not with assertions, but with evidence. The audit trail proves it happened. The hash chain proves it wasn't modified. The evidence bundle proves every gate passed. Security is not bolted on at the end. It is structurally unavoidable."

---

## 🎬 Closing Title Card (3:25 – 3:30)

CORTEX logo hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Skull icons on timeline at 0:08 |
| VBP-003 Narration ≠ slide text | ✅ |
| VBP-004 Progressive disclosure | ✅ STRIDE rows animate sequentially |
| VBP-005 Z/F pattern | ✅ Shield wall front-to-back depth |
| VBP-006 Contrast storytelling | ✅ Incident cards before shield wall |
| VBP-007 2-min visual cycles | ✅ |
| VBP-008 Title + duration + chapters | ✅ |
| VBP-009 Signaling | ✅ Active shield glows; others dim |
| VBP-010 Analogy | ✅ Building security analogy, dark pill |
| VBP-011 Strategic silence | ✅ 1.5s after incident cards |
| VBP-012 Consistent visual language | ✅ Red-to-cyan security domain colours |
| VBP-013 Business Book | ✅ "Trust, but verify" dark pill |
| VBP-014 Hero intro slide | ✅ |
| VBP-015 Breadcrumb | ✅ Shield layers Scene 2 |
| VBP-016 Bold key words | ✅ BLOCKED, critical terms |
| VBP-017 Female narrator | ✅ Odd-numbered video |
| VBP-018 No unexpanded acronyms | ✅ STRIDE, OWASP, SAST, PII, CVE, WAL, XSS expanded |
| VBP-019 Strategic colour | ✅ Red (`#ff4444`) → Cyan (`#00d4ff`) security domain gradient |

---

## 🎵 Audio Direction

- **Background:** Tense ambient pad — low-frequency hum with slow pulse, security-operations-room feel
- **Red incident cards (Scene 1):** Soft alarm-tone pulse per item — building tension
- **Shield particle (clean, Scene 2):** Smooth pass-through chime cascade across 5 shields
- **Shield block (red, Scene 2):** Sharp low-frequency thud + red flash
- **Pre-commit block (Scene 3):** Distinctive block-tone — unmistakable rejection signal
- **STRIDE row reveals (Scene 4):** Descending severity tone: CRITICAL = deep alert, MEDIUM = neutral tone
- **Hash chain break (Scene 6):** Sharp metallic crack sound — tamper alert
- **Evidence bundle complete (Scene 6):** Ascending certified chime
- **Narration style:** Precise, measured, authoritative. 135 wpm. Zero hyperbole — security audiences require evidence, not claims.
