"""
Threat Modeler Agent

Enhanced security threat analysis agent using STRIDE framework with:
- Feature-specific threat templates
- OWASP Top 10 mapping
- Auto-mitigation strategies with code examples
- Risk rating with context awareness

Author: CORTEX Development Team
Version: 2.0
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.workflows.stages.threat_modeler import ThreatCategory, Threat

logger = logging.getLogger(__name__)


class RiskRating(Enum):
    """Enhanced risk ratings"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class OWASPCategory(Enum):
    """OWASP Top 10 2021 Categories"""
    A01 = "A01:2021 - Broken Access Control"
    A02 = "A02:2021 - Cryptographic Failures"
    A03 = "A03:2021 - Injection"
    A04 = "A04:2021 - Insecure Design"
    A05 = "A05:2021 - Security Misconfiguration"
    A06 = "A06:2021 - Vulnerable and Outdated Components"
    A07 = "A07:2021 - Identification and Authentication Failures"
    A08 = "A08:2021 - Software and Data Integrity Failures"
    A09 = "A09:2021 - Security Logging and Monitoring Failures"
    A10 = "A10:2021 - Server-Side Request Forgery (SSRF)"


@dataclass
class MitigationStrategy:
    """Structured mitigation strategy with implementation details"""
    name: str
    description: str
    implementation_steps: List[str]
    code_example: str
    language: str
    effort_hours: float
    effectiveness_percent: int
    tools: List[str] = field(default_factory=list)
    testing_guidance: str = ""
    references: List[str] = field(default_factory=list)


@dataclass
class EnhancedThreat:
    """Enhanced threat with OWASP mapping and detailed mitigations"""
    category: ThreatCategory
    name: str
    description: str
    attack_scenario: str
    likelihood: str
    impact: str
    risk_rating: RiskRating
    owasp_categories: List[OWASPCategory]
    mitigation_strategies: List[MitigationStrategy]
    keywords_matched: List[str] = field(default_factory=list)
    
    @property
    def risk_score(self) -> int:
        """Calculate numeric risk score (1-10)"""
        likelihood_map = {"low": 1, "medium": 2, "high": 3}
        impact_map = {"low": 1, "medium": 3, "high": 4}
        return likelihood_map[self.likelihood] * impact_map[self.impact]


@dataclass
class ThreatReport:
    """Comprehensive threat analysis report"""
    feature_name: str
    feature_type: str
    threats: List[EnhancedThreat]
    timestamp: datetime
    risk_level: RiskRating
    stride_summary: Dict[str, int]
    owasp_coverage: Dict[str, int]
    recommendations: List[str]
    
    @property
    def critical_threats(self) -> List[EnhancedThreat]:
        """Get critical threats only"""
        return [t for t in self.threats if t.risk_rating == RiskRating.CRITICAL]
    
    @property
    def high_threats(self) -> List[EnhancedThreat]:
        """Get high risk threats"""
        return [t for t in self.threats if t.risk_rating == RiskRating.HIGH]


class ThreatModelerAgent(BaseAgent):
    """
    Enhanced threat modeling agent using STRIDE framework.
    
    Features:
    - Feature-specific threat templates (auth, api, data, upload, payment)
    - OWASP Top 10 2021 mapping
    - Structured mitigation strategies with code examples
    - Context-aware risk rating
    - Semantic threat detection (100+ keywords)
    """
    
    def __init__(self):
        super().__init__(agent_name="ThreatModeler")
        self._init_threat_templates()
        self._init_mitigation_database()
        self._init_keyword_expansion()
    
    def _init_threat_templates(self):
        """Initialize feature-specific threat templates"""
        self.threat_templates = {
            'authentication': [
                {
                    'name': 'Brute Force Attacks',
                    'stride': [ThreatCategory.SPOOFING],
                    'owasp': [OWASPCategory.A07],
                    'description': 'Attacker attempts multiple login combinations to guess user credentials',
                    'attack_scenario': 'Automated bot sends thousands of login requests with common passwords',
                    'likelihood': 'high',
                    'impact': 'high',
                    'keywords': ['login', 'authenticate', 'signin', 'password', 'credentials']
                },
                {
                    'name': 'Session Hijacking',
                    'stride': [ThreatCategory.SPOOFING, ThreatCategory.ELEVATION_OF_PRIVILEGE],
                    'owasp': [OWASPCategory.A07],
                    'description': 'Attacker steals or predicts session tokens to impersonate legitimate users',
                    'attack_scenario': 'Attacker intercepts session cookie via XSS or network sniffing',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['session', 'token', 'cookie', 'authentication']
                },
                {
                    'name': 'Credential Stuffing',
                    'stride': [ThreatCategory.SPOOFING],
                    'owasp': [OWASPCategory.A07],
                    'description': 'Attacker uses leaked credentials from other breaches to access accounts',
                    'attack_scenario': 'Attacker obtains leaked passwords from data breach and tries them on your system',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['login', 'password', 'account', 'user']
                },
                {
                    'name': 'Insufficient MFA Protection',
                    'stride': [ThreatCategory.SPOOFING],
                    'owasp': [OWASPCategory.A07],
                    'description': 'Lack of multi-factor authentication allows single-factor compromise',
                    'attack_scenario': 'Attacker compromises password but no second factor blocks access',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['auth', 'authentication', 'login', 'mfa', '2fa']
                }
            ],
            
            'api': [
                {
                    'name': 'SQL Injection',
                    'stride': [ThreatCategory.TAMPERING, ThreatCategory.INFORMATION_DISCLOSURE],
                    'owasp': [OWASPCategory.A03],
                    'description': 'Attacker injects malicious SQL commands to manipulate database queries',
                    'attack_scenario': 'Attacker sends crafted input that breaks out of SQL query context',
                    'likelihood': 'high',
                    'impact': 'high',
                    'keywords': ['query', 'database', 'sql', 'data', 'search', 'filter']
                },
                {
                    'name': 'Broken Object Level Authorization',
                    'stride': [ThreatCategory.ELEVATION_OF_PRIVILEGE, ThreatCategory.INFORMATION_DISCLOSURE],
                    'owasp': [OWASPCategory.A01],
                    'description': 'API endpoints do not properly verify user authorization for object access',
                    'attack_scenario': 'Attacker modifies object IDs in API requests to access other users\' data',
                    'likelihood': 'high',
                    'impact': 'high',
                    'keywords': ['api', 'endpoint', 'resource', 'id', 'get', 'fetch']
                },
                {
                    'name': 'Mass Assignment',
                    'stride': [ThreatCategory.TAMPERING, ThreatCategory.ELEVATION_OF_PRIVILEGE],
                    'owasp': [OWASPCategory.A04],
                    'description': 'API allows modification of object properties that should be restricted',
                    'attack_scenario': 'Attacker sends additional fields in API request to modify admin flags',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['update', 'create', 'post', 'put', 'patch', 'api']
                },
                {
                    'name': 'Rate Limiting Bypass',
                    'stride': [ThreatCategory.DENIAL_OF_SERVICE],
                    'owasp': [OWASPCategory.A04],
                    'description': 'Lack of rate limiting allows resource exhaustion or data scraping',
                    'attack_scenario': 'Attacker sends thousands of API requests to overwhelm system',
                    'likelihood': 'medium',
                    'impact': 'medium',
                    'keywords': ['api', 'endpoint', 'service', 'request']
                }
            ],
            
            'data_storage': [
                {
                    'name': 'Unauthorized Data Access',
                    'stride': [ThreatCategory.INFORMATION_DISCLOSURE, ThreatCategory.ELEVATION_OF_PRIVILEGE],
                    'owasp': [OWASPCategory.A01],
                    'description': 'Insufficient access controls allow unauthorized data retrieval',
                    'attack_scenario': 'Attacker accesses database records without proper authorization checks',
                    'likelihood': 'high',
                    'impact': 'high',
                    'keywords': ['database', 'store', 'save', 'persist', 'data']
                },
                {
                    'name': 'Data Exfiltration',
                    'stride': [ThreatCategory.INFORMATION_DISCLOSURE],
                    'owasp': [OWASPCategory.A02],
                    'description': 'Sensitive data copied or transmitted without authorization',
                    'attack_scenario': 'Attacker extracts large amounts of data through bulk queries or exports',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['export', 'bulk', 'data', 'download', 'extract']
                },
                {
                    'name': 'Insufficient Encryption',
                    'stride': [ThreatCategory.INFORMATION_DISCLOSURE],
                    'owasp': [OWASPCategory.A02],
                    'description': 'Sensitive data stored without encryption or weak encryption',
                    'attack_scenario': 'Attacker gains database access and reads plaintext sensitive data',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['password', 'sensitive', 'personal', 'pii', 'confidential']
                },
                {
                    'name': 'Backup Exposure',
                    'stride': [ThreatCategory.INFORMATION_DISCLOSURE],
                    'owasp': [OWASPCategory.A05],
                    'description': 'Database backups stored insecurely or unencrypted',
                    'attack_scenario': 'Attacker finds publicly accessible backup files containing sensitive data',
                    'likelihood': 'low',
                    'impact': 'high',
                    'keywords': ['backup', 'archive', 'snapshot', 'restore']
                }
            ],
            
            'file_upload': [
                {
                    'name': 'Malicious File Upload',
                    'stride': [ThreatCategory.TAMPERING, ThreatCategory.ELEVATION_OF_PRIVILEGE],
                    'owasp': [OWASPCategory.A04],
                    'description': 'Attacker uploads malicious files (malware, webshells, scripts)',
                    'attack_scenario': 'Attacker uploads PHP webshell disguised as image to gain server control',
                    'likelihood': 'high',
                    'impact': 'high',
                    'keywords': ['upload', 'file', 'attachment', 'document']
                },
                {
                    'name': 'Path Traversal',
                    'stride': [ThreatCategory.INFORMATION_DISCLOSURE, ThreatCategory.TAMPERING],
                    'owasp': [OWASPCategory.A01],
                    'description': 'Attacker manipulates file paths to access unauthorized files',
                    'attack_scenario': 'Attacker uses ../ sequences to access files outside upload directory',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['upload', 'file', 'path', 'directory']
                },
                {
                    'name': 'XML External Entity (XXE)',
                    'stride': [ThreatCategory.INFORMATION_DISCLOSURE, ThreatCategory.DENIAL_OF_SERVICE],
                    'owasp': [OWASPCategory.A03],
                    'description': 'XML parser processes external entities leading to data exposure',
                    'attack_scenario': 'Attacker uploads XML file with external entity references to read local files',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['upload', 'xml', 'parse', 'document']
                },
                {
                    'name': 'Resource Exhaustion',
                    'stride': [ThreatCategory.DENIAL_OF_SERVICE],
                    'owasp': [OWASPCategory.A04],
                    'description': 'Large file uploads exhaust storage or processing resources',
                    'attack_scenario': 'Attacker uploads massive files repeatedly to fill disk space',
                    'likelihood': 'medium',
                    'impact': 'medium',
                    'keywords': ['upload', 'file', 'large', 'size']
                }
            ],
            
            'payment': [
                {
                    'name': 'Payment Amount Manipulation',
                    'stride': [ThreatCategory.TAMPERING],
                    'owasp': [OWASPCategory.A04],
                    'description': 'Attacker modifies payment amounts or prices',
                    'attack_scenario': 'Attacker intercepts request and changes $100 to $1 before submission',
                    'likelihood': 'high',
                    'impact': 'high',
                    'keywords': ['payment', 'price', 'amount', 'total', 'checkout']
                },
                {
                    'name': 'Payment Replay Attack',
                    'stride': [ThreatCategory.REPUDIATION, ThreatCategory.TAMPERING],
                    'owasp': [OWASPCategory.A08],
                    'description': 'Attacker replays captured payment requests for fraudulent transactions',
                    'attack_scenario': 'Attacker captures valid payment request and replays it multiple times',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['payment', 'transaction', 'order', 'purchase']
                },
                {
                    'name': 'PCI DSS Non-Compliance',
                    'stride': [ThreatCategory.INFORMATION_DISCLOSURE],
                    'owasp': [OWASPCategory.A02],
                    'description': 'Payment card data handled insecurely violating PCI DSS',
                    'attack_scenario': 'System logs or stores full credit card numbers in plaintext',
                    'likelihood': 'medium',
                    'impact': 'high',
                    'keywords': ['payment', 'card', 'credit', 'billing']
                },
                {
                    'name': 'Insufficient Payment Logging',
                    'stride': [ThreatCategory.REPUDIATION],
                    'owasp': [OWASPCategory.A09],
                    'description': 'Payment transactions not properly logged for audit trail',
                    'attack_scenario': 'Fraudulent transaction occurs but insufficient logs prevent investigation',
                    'likelihood': 'low',
                    'impact': 'medium',
                    'keywords': ['payment', 'transaction', 'billing']
                }
            ]
        }
    
    def _init_mitigation_database(self):
        """Initialize comprehensive mitigation strategies database"""
        self.mitigation_database = {
            'brute_force': MitigationStrategy(
                name="Account Lockout with Progressive Delays",
                description="Implement account lockout after failed attempts with increasing delays",
                implementation_steps=[
                    "Track failed login attempts per account",
                    "Implement lockout after 5 failed attempts",
                    "Add progressive delays (1s, 2s, 5s, 15s, 30s)",
                    "Notify user and admin of lockout",
                    "Provide secure account recovery mechanism"
                ],
                code_example='''// ASP.NET Core Identity Configuration
services.Configure<IdentityOptions>(options =>
{
    // Lockout settings
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.Lockout.AllowedForNewUsers = true;
    
    // Password settings
    options.Password.RequireDigit = true;
    options.Password.RequiredLength = 12;
    options.Password.RequireNonAlphanumeric = true;
    options.Password.RequireUppercase = true;
    options.Password.RequireLowercase = true;
});''',
                language="csharp",
                effort_hours=2.0,
                effectiveness_percent=85,
                tools=["ASP.NET Core Identity", "Redis (for distributed lockout)"],
                testing_guidance="Test with automated attacks, verify lockout triggers, test unlock mechanism",
                references=["https://docs.microsoft.com/en-us/aspnet/core/security/authentication/identity-configuration"]
            ),
            
            'sql_injection': MitigationStrategy(
                name="Parameterized Queries with ORM",
                description="Use parameterized queries through Entity Framework to prevent SQL injection",
                implementation_steps=[
                    "Replace all string concatenation queries",
                    "Use Entity Framework LINQ queries",
                    "For raw SQL, use SqlParameter objects",
                    "Enable query logging in development",
                    "Add input validation as defense-in-depth"
                ],
                code_example='''// VULNERABLE (DO NOT USE)
string sql = $"SELECT * FROM Users WHERE Email = '{userEmail}'";

// SECURE (Parameterized Query)
var user = await _context.Users
    .Where(u => u.Email == userEmail)
    .FirstOrDefaultAsync();

// SECURE (Raw SQL with Parameters)
var user = await _context.Users
    .FromSqlRaw("SELECT * FROM Users WHERE Email = {0}", userEmail)
    .FirstOrDefaultAsync();''',
                language="csharp",
                effort_hours=4.0,
                effectiveness_percent=99,
                tools=["Entity Framework Core", "LINQ"],
                testing_guidance="Use SQL injection testing tools (sqlmap), verify all queries parameterized",
                references=["https://docs.microsoft.com/en-us/ef/core/querying/sql-queries"]
            ),
            
            'session_hijacking': MitigationStrategy(
                name="Secure Session Management",
                description="Implement HttpOnly, Secure, and SameSite cookie flags with short timeouts",
                implementation_steps=[
                    "Enable HttpOnly flag (prevent XSS access)",
                    "Enable Secure flag (HTTPS only)",
                    "Set SameSite=Strict (prevent CSRF)",
                    "Implement 15-minute session timeout",
                    "Regenerate session on privilege change"
                ],
                code_example='''// ASP.NET Core Startup Configuration
services.ConfigureApplicationCookie(options =>
{
    options.Cookie.HttpOnly = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    options.Cookie.SameSite = SameSiteMode.Strict;
    options.ExpireTimeSpan = TimeSpan.FromMinutes(15);
    options.SlidingExpiration = true;
});

// Additional HTTPS enforcement
services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
    options.HttpsPort = 443;
});''',
                language="csharp",
                effort_hours=1.5,
                effectiveness_percent=90,
                tools=["ASP.NET Core", "HTTPS"],
                testing_guidance="Verify cookie flags in browser dev tools, test session timeout, attempt XSS cookie theft",
                references=["https://docs.microsoft.com/en-us/aspnet/core/security/authentication/cookie"]
            ),
            
            'broken_authorization': MitigationStrategy(
                name="Resource-Level Authorization Checks",
                description="Implement authorization checks on every resource access",
                implementation_steps=[
                    "Create authorization policies per resource type",
                    "Implement IAuthorizationHandler for custom rules",
                    "Check authorization before every data access",
                    "Log authorization failures",
                    "Use authorization attributes on controllers"
                ],
                code_example='''// Authorization Handler
public class ResourceOwnerHandler : AuthorizationHandler<ResourceOwnerRequirement, Resource>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        ResourceOwnerRequirement requirement,
        Resource resource)
    {
        var userId = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        
        if (userId == resource.OwnerId || context.User.IsInRole("Admin"))
        {
            context.Succeed(requirement);
        }
        
        return Task.CompletedTask;
    }
}

// Controller Usage
[HttpGet("{id}")]
public async Task<IActionResult> GetResource(int id)
{
    var resource = await _context.Resources.FindAsync(id);
    
    // Authorization check BEFORE returning data
    var authResult = await _authorizationService
        .AuthorizeAsync(User, resource, "ResourceOwnerPolicy");
    
    if (!authResult.Succeeded)
    {
        return Forbid();
    }
    
    return Ok(resource);
}''',
                language="csharp",
                effort_hours=6.0,
                effectiveness_percent=95,
                tools=["ASP.NET Core Authorization", "Policy-based authorization"],
                testing_guidance="Test with different user roles, attempt cross-user data access, verify logging",
                references=["https://docs.microsoft.com/en-us/aspnet/core/security/authorization/resourcebased"]
            ),
            
            'file_upload_malware': MitigationStrategy(
                name="Multi-Layer File Upload Validation",
                description="Validate file type, scan for malware, store outside webroot",
                implementation_steps=[
                    "Validate file extension whitelist",
                    "Verify file magic numbers (not just extension)",
                    "Scan files with antivirus (ClamAV)",
                    "Store files outside web-accessible directory",
                    "Generate random filenames",
                    "Limit file sizes"
                ],
                code_example='''// File Upload Validation
public async Task<IActionResult> Upload(IFormFile file)
{
    // Size validation
    if (file.Length > 10 * 1024 * 1024) // 10MB
        return BadRequest("File too large");
    
    // Extension whitelist
    var allowedExtensions = new[] { ".jpg", ".jpeg", ".png", ".pdf" };
    var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
    if (!allowedExtensions.Contains(extension))
        return BadRequest("Invalid file type");
    
    // Magic number verification
    using var stream = file.OpenReadStream();
    var header = new byte[8];
    await stream.ReadAsync(header, 0, 8);
    
    if (!IsValidImageHeader(header))
        return BadRequest("File content does not match extension");
    
    // Generate secure filename
    var secureFilename = $"{Guid.NewGuid()}{extension}";
    var uploadPath = Path.Combine(_secureUploadPath, secureFilename);
    
    using (var fileStream = new FileStream(uploadPath, FileMode.Create))
    {
        await file.CopyToAsync(fileStream);
    }
    
    // Scan with antivirus (async)
    _ = Task.Run(() => ScanFileAsync(uploadPath));
    
    return Ok(new { filename = secureFilename });
}''',
                language="csharp",
                effort_hours=4.0,
                effectiveness_percent=85,
                tools=["ClamAV", "File magic number libraries"],
                testing_guidance="Test with malicious files, verify magic number checking, test size limits",
                references=["https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload"]
            ),
            
            'payment_manipulation': MitigationStrategy(
                name="Server-Side Price Calculation with Idempotency",
                description="Calculate prices server-side and implement idempotency keys for transactions",
                implementation_steps=[
                    "Never trust client-side prices",
                    "Recalculate totals on server before processing",
                    "Use idempotency keys to prevent replay",
                    "Implement transaction signing",
                    "Log all payment attempts"
                ],
                code_example='''// Payment Processing with Idempotency
[HttpPost("checkout")]
public async Task<IActionResult> ProcessPayment(
    [FromBody] PaymentRequest request,
    [FromHeader(Name = "Idempotency-Key")] string idempotencyKey)
{
    // Check idempotency key (prevent replay)
    if (await _cache.ExistsAsync(idempotencyKey))
    {
        return BadRequest("Duplicate transaction");
    }
    
    // SERVER-SIDE price calculation (never trust client)
    var cart = await _context.Carts
        .Include(c => c.Items)
        .ThenInclude(i => i.Product)
        .FirstOrDefaultAsync(c => c.Id == request.CartId);
    
    decimal serverCalculatedTotal = cart.Items.Sum(i => 
        i.Product.CurrentPrice * i.Quantity);
    
    // Verify prices match (tolerance for rounding)
    if (Math.Abs(serverCalculatedTotal - request.Amount) > 0.01m)
    {
        _logger.LogWarning("Price manipulation attempt: Expected {Expected}, Got {Received}",
            serverCalculatedTotal, request.Amount);
        return BadRequest("Price mismatch");
    }
    
    // Store idempotency key (24 hour expiration)
    await _cache.SetAsync(idempotencyKey, "1", TimeSpan.FromHours(24));
    
    // Process payment with Stripe
    var chargeOptions = new ChargeCreateOptions
    {
        Amount = (long)(serverCalculatedTotal * 100), // cents
        Currency = "usd",
        Source = request.PaymentToken,
        IdempotencyKey = idempotencyKey
    };
    
    var charge = await _stripeService.Charges.CreateAsync(chargeOptions);
    
    return Ok(new { transactionId = charge.Id });
}''',
                language="csharp",
                effort_hours=3.0,
                effectiveness_percent=95,
                tools=["Stripe", "Redis (idempotency cache)"],
                testing_guidance="Test with modified prices, test replay attacks, verify logging",
                references=["https://stripe.com/docs/api/idempotent_requests"]
            ),
            
            'encryption_at_rest': MitigationStrategy(
                name="Transparent Data Encryption",
                description="Enable database encryption for sensitive data at rest",
                implementation_steps=[
                    "Enable SQL Server Transparent Data Encryption (TDE)",
                    "Encrypt sensitive columns with Always Encrypted",
                    "Use Data Protection API for configuration secrets",
                    "Implement key rotation policy",
                    "Encrypt database backups"
                ],
                code_example='''-- Enable Transparent Data Encryption
USE master;
GO

-- Create master key
CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<strong_password>';
GO

-- Create certificate
CREATE CERTIFICATE TDECert WITH SUBJECT = 'TDE Certificate';
GO

-- Create database encryption key
USE YourDatabase;
GO

CREATE DATABASE ENCRYPTION KEY
WITH ALGORITHM = AES_256
ENCRYPTION BY SERVER CERTIFICATE TDECert;
GO

-- Enable encryption
ALTER DATABASE YourDatabase
SET ENCRYPTION ON;
GO

-- Verify encryption status
SELECT db.name, db.is_encrypted
FROM sys.databases db
WHERE db.name = 'YourDatabase';''',
                language="sql",
                effort_hours=2.0,
                effectiveness_percent=90,
                tools=["SQL Server TDE", "Azure Key Vault"],
                testing_guidance="Verify encryption with sys.databases, test backup encryption, test key rotation",
                references=["https://docs.microsoft.com/en-us/sql/relational-databases/security/encryption/transparent-data-encryption"]
            ),
            
            'rate_limiting': MitigationStrategy(
                name="Distributed Rate Limiting with Redis",
                description="Implement rate limiting per user/IP with Redis for distributed systems",
                implementation_steps=[
                    "Install AspNetCoreRateLimit package",
                    "Configure Redis as distributed cache",
                    "Set rate limits per endpoint",
                    "Implement sliding window algorithm",
                    "Return 429 Too Many Requests with Retry-After"
                ],
                code_example='''// Startup.cs - Rate Limiting Configuration
services.AddMemoryCache();
services.Configure<IpRateLimitOptions>(options =>
{
    options.EnableEndpointRateLimiting = true;
    options.StackBlockedRequests = false;
    options.HttpStatusCode = 429;
    options.RealIpHeader = "X-Real-IP";
    options.GeneralRules = new List<RateLimitRule>
    {
        new RateLimitRule
        {
            Endpoint = "POST:/api/login",
            Period = "1m",
            Limit = 5
        },
        new RateLimitRule
        {
            Endpoint = "*",
            Period = "1s",
            Limit = 10
        },
        new RateLimitRule
        {
            Endpoint = "*",
            Period = "1m",
            Limit = 200
        }
    };
});

services.AddSingleton<IIpPolicyStore, DistributedCacheIpPolicyStore>();
services.AddSingleton<IRateLimitCounterStore, DistributedCacheRateLimitCounterStore>();
services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();

// In Configure method
app.UseIpRateLimiting();''',
                language="csharp",
                effort_hours=2.5,
                effectiveness_percent=80,
                tools=["AspNetCoreRateLimit", "Redis", "StackExchange.Redis"],
                testing_guidance="Test with load testing tools (k6, JMeter), verify 429 responses, test distributed scenarios",
                references=["https://github.com/stefanprodan/AspNetCoreRateLimit"]
            )
        }
    
    def _init_keyword_expansion(self):
        """Initialize expanded keyword dictionary (100+ terms)"""
        self.expanded_keywords = {
            ThreatCategory.SPOOFING: [
                'login', 'signin', 'sign-in', 'auth', 'authenticate', 'authentication',
                'password', 'credentials', 'token', 'session', 'cookie', 'jwt',
                'oauth', 'saml', 'sso', 'single sign-on', 'mfa', '2fa', 'biometric',
                'fingerprint', 'face recognition', 'register', 'signup', 'sign-up',
                'identity', 'user', 'account'
            ],
            ThreatCategory.TAMPERING: [
                'update', 'modify', 'edit', 'change', 'delete', 'remove',
                'alter', 'patch', 'put', 'post', 'insert', 'create',
                'import', 'sync', 'synchronize', 'merge', 'bulk', 'batch',
                'mass', 'modify', 'write', 'save', 'persist'
            ],
            ThreatCategory.REPUDIATION: [
                'transaction', 'payment', 'order', 'purchase', 'submit',
                'admin action', 'administrative', 'privilege', 'critical action',
                'data access', 'sensitive operation', 'config change', 'setting',
                'audit', 'log', 'track', 'record'
            ],
            ThreatCategory.INFORMATION_DISCLOSURE: [
                'export', 'download', 'share', 'api', 'email', 'send',
                'log', 'error', 'exception', 'debug', 'trace', 'report',
                'print', 'display', 'show', 'view', 'read', 'get',
                'fetch', 'retrieve', 'query', 'search', 'list', 'personal',
                'pii', 'sensitive', 'confidential', 'private', 'secret'
            ],
            ThreatCategory.DENIAL_OF_SERVICE: [
                'upload', 'import', 'process', 'calculate', 'generate',
                'query', 'search', 'list', 'recursive', 'loop', 'batch',
                'bulk', 'mass', 'large', 'compute', 'aggregate', 'analyze',
                'parse', 'transform', 'convert', 'compile', 'build'
            ],
            ThreatCategory.ELEVATION_OF_PRIVILEGE: [
                'admin', 'administrator', 'permission', 'role', 'access',
                'privilege', 'sudo', 'grant', 'delegate', 'impersonate',
                'escalate', 'elevate', 'authorize', 'authorization', 'rbac',
                'acl', 'security', 'rights', 'capability'
            ]
        }
    
    async def process(self, feature_requirements: str, feature_type: str = 'general',
                     context: Optional[Dict[str, Any]] = None) -> ThreatReport:
        """
        Main processing method for threat analysis.
        
        Args:
            feature_requirements: Description of feature to analyze
            feature_type: Type of feature (auth, api, data_storage, file_upload, payment, general)
            context: Optional context (project patterns, previous threats, etc.)
        
        Returns:
            ThreatReport with identified threats and mitigations
        """
        self._start_execution()
        
        try:
            self.logger.info(f"Analyzing threats for {feature_type} feature")
            
            # Detect feature type if not provided
            if feature_type == 'general':
                feature_type = self._detect_feature_type(feature_requirements)
            
            # Identify threats using templates and keywords
            threats = self._identify_threats_enhanced(feature_requirements, feature_type, context)
            
            # Calculate risk ratings
            for threat in threats:
                threat.risk_rating = self._calculate_risk_rating_enhanced(
                    threat, feature_type, context
                )
            
            # Sort threats by risk score
            threats.sort(key=lambda t: t.risk_score, reverse=True)
            
            # Generate STRIDE summary
            stride_summary = self._generate_stride_summary(threats)
            
            # Generate OWASP coverage
            owasp_coverage = self._generate_owasp_coverage(threats)
            
            # Generate recommendations
            recommendations = self._generate_recommendations_enhanced(threats, feature_type)
            
            # Determine overall risk level
            risk_level = self._calculate_overall_risk(threats)
            
            report = ThreatReport(
                feature_name=self._extract_feature_name(feature_requirements),
                feature_type=feature_type,
                threats=threats,
                timestamp=datetime.now(),
                risk_level=risk_level,
                stride_summary=stride_summary,
                owasp_coverage=owasp_coverage,
                recommendations=recommendations
            )
            
            self._end_execution(success=True)
            self.logger.info(f"Threat analysis complete: {len(threats)} threats, risk={risk_level.value}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Threat modeling failed: {e}")
            self._end_execution(success=False, error=str(e))
            raise
    
    def _detect_feature_type(self, requirements: str) -> str:
        """
        Auto-detect feature type from requirements.
        
        Args:
            requirements: Feature requirements text
        
        Returns:
            Feature type (auth, api, data_storage, file_upload, payment, general)
        """
        requirements_lower = requirements.lower()
        
        # Score each feature type
        scores = {
            'authentication': 0,
            'api': 0,
            'data_storage': 0,
            'file_upload': 0,
            'payment': 0
        }
        
        # Keyword matching with weights
        type_keywords = {
            'authentication': (['login', 'auth', 'password', 'signin', 'signup', 'register', 'mfa', '2fa'], 2.0),
            'api': (['api', 'endpoint', 'rest', 'graphql', 'service', 'request'], 1.5),
            'data_storage': (['database', 'save', 'store', 'persist', 'crud', 'data'], 1.0),
            'file_upload': (['upload', 'file', 'attachment', 'document', 'image'], 3.0),
            'payment': (['payment', 'checkout', 'billing', 'transaction', 'stripe', 'purchase'], 3.0)
        }
        
        for feature_type, (keywords, weight) in type_keywords.items():
            for keyword in keywords:
                if keyword in requirements_lower:
                    scores[feature_type] += weight
        
        # Return highest scoring type or 'general'
        max_score = max(scores.values())
        if max_score == 0:
            return 'general'
        
        return max(scores, key=scores.get)
    
    def _identify_threats_enhanced(self, requirements: str, feature_type: str,
                                  context: Optional[Dict[str, Any]]) -> List[EnhancedThreat]:
        """
        Identify threats using feature-specific templates and keyword matching.
        
        Args:
            requirements: Feature requirements text
            feature_type: Detected or provided feature type
            context: Optional context for threat detection
        
        Returns:
            List of enhanced threats
        """
        threats = []
        requirements_lower = requirements.lower()
        
        # Get templates for feature type
        templates = self.threat_templates.get(feature_type, [])
        
        # Add general threats if feature type is unknown
        if feature_type == 'general':
            templates.extend(self._get_general_threats())
        
        for template in templates:
            # Check if threat keywords match requirements
            keywords_matched = [kw for kw in template['keywords'] 
                              if kw in requirements_lower]
            
            if keywords_matched:
                # Get mitigation strategies
                mitigation_key = template['name'].lower().replace(' ', '_')
                mitigations = [self.mitigation_database.get(mitigation_key)] if mitigation_key in self.mitigation_database else []
                
                # If no specific mitigation, create generic one
                if not mitigations:
                    mitigations = [self._create_generic_mitigation(template)]
                
                threat = EnhancedThreat(
                    category=template['stride'][0],  # Primary STRIDE category
                    name=template['name'],
                    description=template['description'],
                    attack_scenario=template['attack_scenario'],
                    likelihood=template['likelihood'],
                    impact=template['impact'],
                    risk_rating=RiskRating.MEDIUM,  # Will be recalculated
                    owasp_categories=template['owasp'],
                    mitigation_strategies=mitigations,
                    keywords_matched=keywords_matched
                )
                
                threats.append(threat)
        
        return threats
    
    def _create_generic_mitigation(self, template: Dict[str, Any]) -> MitigationStrategy:
        """Create generic mitigation strategy when specific one not in database"""
        return MitigationStrategy(
            name=f"Mitigate {template['name']}",
            description=f"Implement controls to address {template['name']}",
            implementation_steps=["Review security best practices", "Implement appropriate controls"],
            code_example="// See documentation for implementation examples",
            language="text",
            effort_hours=3.0,
            effectiveness_percent=70,
            tools=[],
            testing_guidance="Verify control effectiveness with security testing"
        )
    
    def _get_general_threats(self) -> List[Dict[str, Any]]:
        """Get general threats when feature type cannot be determined"""
        return [
            {
                'name': 'Input Validation Failure',
                'stride': [ThreatCategory.TAMPERING, ThreatCategory.INFORMATION_DISCLOSURE],
                'owasp': [OWASPCategory.A03],
                'description': 'Insufficient input validation allows malicious input',
                'attack_scenario': 'Attacker sends crafted input to exploit parsing or processing logic',
                'likelihood': 'medium',
                'impact': 'medium',
                'keywords': ['input', 'form', 'field', 'data', 'submit']
            },
            {
                'name': 'Insufficient Logging',
                'stride': [ThreatCategory.REPUDIATION],
                'owasp': [OWASPCategory.A09],
                'description': 'Critical actions not logged for security monitoring',
                'attack_scenario': 'Attacker performs malicious actions without detection',
                'likelihood': 'low',
                'impact': 'medium',
                'keywords': ['action', 'operation', 'function', 'process']
            }
        ]
    
    def _calculate_risk_rating_enhanced(self, threat: EnhancedThreat, feature_type: str,
                                       context: Optional[Dict[str, Any]]) -> RiskRating:
        """
        Calculate risk rating with context awareness.
        
        Args:
            threat: Threat to rate
            feature_type: Feature type for context multiplier
            context: Additional context (compliance requirements, etc.)
        
        Returns:
            Risk rating (CRITICAL, HIGH, MEDIUM, LOW)
        """
        base_score = threat.risk_score
        
        # Context multipliers
        feature_multipliers = {
            'payment': 1.5,
            'authentication': 1.3,
            'file_upload': 1.2,
            'api': 1.1,
            'data_storage': 1.1
        }
        
        multiplier = feature_multipliers.get(feature_type, 1.0)
        adjusted_score = base_score * multiplier
        
        # Apply compliance multipliers if context provided
        if context and context.get('requires_pci_dss') and feature_type == 'payment':
            adjusted_score *= 1.2
        
        if context and context.get('handles_pii'):
            adjusted_score *= 1.15
        
        # Determine rating
        if adjusted_score >= 11:
            return RiskRating.CRITICAL
        elif adjusted_score >= 8:
            return RiskRating.HIGH
        elif adjusted_score >= 5:
            return RiskRating.MEDIUM
        else:
            return RiskRating.LOW
    
    def _calculate_overall_risk(self, threats: List[EnhancedThreat]) -> RiskRating:
        """Calculate overall risk level from all threats"""
        if not threats:
            return RiskRating.LOW
        
        # If any critical, overall is critical
        if any(t.risk_rating == RiskRating.CRITICAL for t in threats):
            return RiskRating.CRITICAL
        
        # Count high/medium/low
        high_count = len([t for t in threats if t.risk_rating == RiskRating.HIGH])
        
        if high_count >= 3:
            return RiskRating.HIGH
        elif high_count >= 1:
            return RiskRating.HIGH
        elif len(threats) >= 3:
            return RiskRating.MEDIUM
        else:
            return RiskRating.LOW
    
    def _generate_stride_summary(self, threats: List[EnhancedThreat]) -> Dict[str, int]:
        """Generate summary of threats by STRIDE category"""
        summary = {category.value: 0 for category in ThreatCategory}
        
        for threat in threats:
            summary[threat.category.value] += 1
        
        return summary
    
    def _generate_owasp_coverage(self, threats: List[EnhancedThreat]) -> Dict[str, int]:
        """Generate summary of threats by OWASP category"""
        coverage = {}
        
        for threat in threats:
            for owasp in threat.owasp_categories:
                key = owasp.value.split(' - ')[0]  # Extract A01, A02, etc.
                coverage[key] = coverage.get(key, 0) + 1
        
        return coverage
    
    def _generate_recommendations_enhanced(self, threats: List[EnhancedThreat],
                                         feature_type: str) -> List[str]:
        """Generate actionable recommendations based on threats"""
        recommendations = []
        
        critical_threats = [t for t in threats if t.risk_rating == RiskRating.CRITICAL]
        high_threats = [t for t in threats if t.risk_rating == RiskRating.HIGH]
        
        if critical_threats:
            recommendations.append(
                f"⚠️ CRITICAL: {len(critical_threats)} critical threats identified - address before deployment"
            )
            for threat in critical_threats[:3]:  # Top 3
                recommendations.append(f"  • {threat.name}: {threat.mitigation_strategies[0].name}")
        
        if high_threats:
            recommendations.append(
                f"🔴 HIGH: {len(high_threats)} high-risk threats - address in current sprint"
            )
        
        # Feature-specific recommendations
        if feature_type == 'authentication':
            recommendations.append("Consider implementing MFA for enhanced security")
        elif feature_type == 'payment':
            recommendations.append("Ensure PCI DSS compliance requirements are met")
        elif feature_type == 'file_upload':
            recommendations.append("Implement malware scanning for all uploaded files")
        
        # General recommendations
        if len(threats) >= 5:
            recommendations.append("Multiple threats identified - schedule security review with team")
        
        recommendations.append("Write security-focused tests for each identified threat")
        
        return recommendations
    
    def _extract_feature_name(self, requirements: str) -> str:
        """Extract feature name from requirements (first line or first 50 chars)"""
        first_line = requirements.split('\n')[0].strip()
        if len(first_line) > 50:
            return first_line[:47] + "..."
        return first_line


# Factory function for backward compatibility with workflow stages
def create_agent() -> ThreatModelerAgent:
    """Create threat modeler agent instance"""
    return ThreatModelerAgent()
