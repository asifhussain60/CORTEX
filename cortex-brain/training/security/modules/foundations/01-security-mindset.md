# Module 01: Security Mindset

**Track:** Foundations  
**Duration:** 30 minutes  
**Difficulty:** Beginner  
**Prerequisites:** None

---

## 🎯 Learning Objectives

After completing this module, you will:
- Understand the security-first mindset
- Recognize common threat actors and motivations
- Apply defense-in-depth principles
- Think like an attacker to build better defenses

---

## 📚 Content

### 1. The Security-First Mindset

Security isn't a feature—it's a fundamental property of quality software. Every line of code you write can be a potential attack vector.

```mermaid
mindmap
  root((Security<br/>Mindset))
    Trust Nothing
      Validate All Input
      Verify All Users
      Question All Data
    Defense in Depth
      Multiple Layers
      No Single Point of Failure
      Assume Breach
    Least Privilege
      Minimal Permissions
      Need-to-Know Basis
      Time-Limited Access
    Secure by Default
      Safe Defaults
      Opt-in Risk
      Fail Secure
```

### 2. Threat Landscape

Understanding who attacks systems and why:

| Threat Actor | Motivation | Typical Targets | Sophistication |
|--------------|------------|-----------------|----------------|
| **Script Kiddies** | Curiosity, bragging rights | Low-hanging fruit | Low |
| **Hacktivists** | Ideological | High-visibility orgs | Low-Medium |
| **Cybercriminals** | Financial gain | Any valuable data | Medium-High |
| **Competitors** | Industrial espionage | IP, trade secrets | Medium-High |
| **Nation States** | Strategic advantage | Critical infrastructure | Very High |
| **Insiders** | Revenge, financial | Internal systems | Varies |

### 3. The CIA Triad

The foundation of information security:

```mermaid
flowchart TB
    subgraph CIA[CIA Triad]
        C[🔒 Confidentiality<br/>Protecting data from<br/>unauthorized access]
        I[✅ Integrity<br/>Ensuring data is<br/>accurate and unaltered]
        A[🔄 Availability<br/>Ensuring systems are<br/>accessible when needed]
    end
    
    C --- I
    I --- A
    A --- C
```

**Confidentiality Threats:**
- Data breaches
- Unauthorized access
- Information disclosure

**Integrity Threats:**
- Data tampering
- Man-in-the-middle attacks
- SQL injection

**Availability Threats:**
- DDoS attacks
- Ransomware
- System failures

### 4. Defense in Depth

Never rely on a single security control:

```mermaid
flowchart LR
    subgraph External
        A[🌐 Internet]
    end
    
    subgraph Perimeter["Layer 1: Perimeter"]
        B[🔥 Firewall]
        C[🛡️ WAF]
    end
    
    subgraph Network["Layer 2: Network"]
        D[📡 IDS/IPS]
        E[🔒 Network Segmentation]
    end
    
    subgraph Application["Layer 3: Application"]
        F[🔐 Authentication]
        G[✅ Authorization]
        H[📝 Validation]
    end
    
    subgraph Data["Layer 4: Data"]
        I[🔑 Encryption]
        J[📊 Audit Logs]
    end
    
    A --> B --> D --> F --> I
    B --> C
    D --> E
    F --> G --> H
    I --> J
```

### 5. Think Like an Attacker

Security professionals must understand attack methodology:

```mermaid
flowchart LR
    R[1. Reconnaissance<br/>Gather information] --> S[2. Scanning<br/>Find vulnerabilities]
    S --> E[3. Exploitation<br/>Gain access]
    E --> M[4. Maintain Access<br/>Establish persistence]
    M --> C[5. Cover Tracks<br/>Remove evidence]
```

**For Each Feature You Build, Ask:**
1. What data does this handle?
2. Who should have access?
3. What happens if input is malicious?
4. How could an attacker abuse this?
5. What's the worst-case scenario?

---

## 🧪 Exercises

### Exercise 1: Threat Analysis

Consider a simple login form. List at least 5 ways an attacker might try to abuse it:

<details>
<summary>Click for Answer</summary>

1. **Brute Force:** Try many password combinations
2. **Credential Stuffing:** Use leaked credentials from other sites
3. **SQL Injection:** `' OR '1'='1' --` in username field
4. **Timing Attack:** Measure response time to enumerate users
5. **Session Hijacking:** Steal session token after successful login
6. **CSRF:** Trick logged-in user into performing actions
7. **Account Lockout DoS:** Lock out legitimate users
8. **Password Reset Abuse:** Exploit password reset functionality

</details>

### Exercise 2: Security Design

You're building a file upload feature. Design security controls for each layer:

| Layer | Security Control | Purpose |
|-------|-----------------|---------|
| Perimeter | ? | ? |
| Network | ? | ? |
| Application | ? | ? |
| Data | ? | ? |

<details>
<summary>Click for Answer</summary>

| Layer | Security Control | Purpose |
|-------|-----------------|---------|
| **Perimeter** | Rate limiting | Prevent upload DoS |
| **Network** | Dedicated storage zone | Isolate uploaded files |
| **Application** | File type validation, size limits, virus scan | Prevent malicious uploads |
| **Data** | Encryption at rest, randomized filenames | Protect stored files |

</details>

---

## 📝 Knowledge Check

1. What does the "I" in CIA stand for?
   - [ ] Intelligence
   - [ ] Integration
   - [x] Integrity
   - [ ] Infrastructure

2. Which threat actor is typically motivated by financial gain?
   - [ ] Script Kiddies
   - [ ] Hacktivists
   - [x] Cybercriminals
   - [ ] Nation States

3. Defense in depth means:
   - [ ] Using the strongest possible firewall
   - [x] Using multiple layers of security controls
   - [ ] Defending your code with unit tests
   - [ ] Hiring more security staff

4. When thinking like an attacker, the first step is:
   - [ ] Exploitation
   - [x] Reconnaissance
   - [ ] Privilege Escalation
   - [ ] Exfiltration

---

## 🎓 Key Takeaways

1. **Security is everyone's responsibility**—not just the security team
2. **Trust nothing**—validate all inputs, verify all users
3. **Defense in depth**—never rely on a single control
4. **Think like an attacker**—anticipate how features can be abused
5. **Secure by default**—unsafe options should require opt-in

---

## 📖 Further Reading

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Microsoft SDL](https://www.microsoft.com/en-us/securityengineering/sdl)

---

## ⏭️ Next Module

Continue to [02 - Secure Coding Basics](./02-secure-coding-basics.md)
