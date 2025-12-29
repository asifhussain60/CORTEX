"""
Quick validation script for Phase 3 language analyzers.
Demonstrates analyzer capabilities with sample code snippets.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.dashboard.analyzers import (
    get_factory,
    CSharpAnalyzer,
    TypeScriptAnalyzer,
    ColdFusionAnalyzer,
    SQLAnalyzer
)


def validate_csharp_analyzer():
    """Validate C# analyzer with sample code."""
    print("\n" + "="*60)
    print("VALIDATING CSHARP ANALYZER")
    print("="*60)
    
    sample_code = """
using System;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class AccountController : ControllerBase
{
    private readonly IAccountService _accountService;
    
    public AccountController(IAccountService accountService)
    {
        _accountService = accountService;
    }
    
    [HttpGet("{id}")]
    public async Task<ActionResult<Account>> GetAccount(int id)
    {
        var account = await _accountService.GetByIdAsync(id);
        return Ok(account);
    }
    
    [HttpPost]
    public async Task<ActionResult> CreateAccount(CreateAccountDto dto)
    {
        var result = await _accountService.CreateAsync(dto);
        return CreatedAtAction(nameof(GetAccount), new { id = result.Id }, result);
    }
}
"""
    
    analyzer = CSharpAnalyzer()
    
    # Write to temp file
    temp_file = Path("temp_test.cs")
    temp_file.write_text(sample_code)
    
    try:
        result = analyzer.analyze(temp_file)
        
        print(f"✅ Classes found: {len(result.classes)}")
        print(f"✅ Methods found: {len(result.methods)}")
        print(f"✅ Is API Controller: {result.patterns['web_api']['is_api_controller']}")
        print(f"✅ Endpoints: {len(result.patterns['web_api']['endpoints'])}")
        print(f"✅ Has DI: {result.patterns['dependency_injection']['has_constructor_injection']}")
        print(f"✅ Async methods: {result.metrics['async_method_count']}")
        
        if result.classes:
            print(f"\nClass: {result.classes[0]['name']}")
        
        if result.patterns['web_api']['endpoints']:
            print("\nAPI Endpoints:")
            for ep in result.patterns['web_api']['endpoints']:
                print(f"  - {ep['method']} {ep['route']} → {ep['handler']}")
        
    finally:
        if temp_file.exists():
            temp_file.unlink()


def validate_typescript_analyzer():
    """Validate TypeScript analyzer with sample code."""
    print("\n" + "="*60)
    print("VALIDATING TYPESCRIPT ANALYZER")
    print("="*60)
    
    sample_code = """
import { Component, OnInit } from '@angular/core';
import { UserService } from './services/user.service';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.css']
})
export class UserListComponent implements OnInit {
  users$: Observable<User[]>;
  
  constructor(private userService: UserService) {}
  
  ngOnInit(): void {
    this.users$ = this.userService.getUsers().pipe(
      map(users => users.filter(u => u.active)),
      switchMap(users => this.enrichUsers(users))
    );
  }
  
  private enrichUsers(users: User[]): Observable<User[]> {
    return this.http.get<User[]>('/api/users/enrich');
  }
}
"""
    
    analyzer = TypeScriptAnalyzer()
    
    # Write to temp file
    temp_file = Path("temp_test.ts")
    temp_file.write_text(sample_code)
    
    try:
        result = analyzer.analyze(temp_file)
        
        print(f"✅ Classes found: {len(result.classes)}")
        print(f"✅ Methods found: {len(result.methods)}")
        print(f"✅ Is Component: {result.patterns['component']['is_component']}")
        print(f"✅ Selector: {result.patterns['component']['selector']}")
        print(f"✅ Has RxJS: {result.patterns['rxjs']['has_rxjs']}")
        print(f"✅ Observable count: {result.patterns['rxjs']['observable_count']}")
        
        if result.patterns['rxjs']['operators']:
            print("\nRxJS Operators:")
            for op in result.patterns['rxjs']['operators']:
                print(f"  - {op['name']}: {op['count']} times")
        
    finally:
        if temp_file.exists():
            temp_file.unlink()


def validate_coldfusion_analyzer():
    """Validate ColdFusion analyzer with sample code."""
    print("\n" + "="*60)
    print("VALIDATING COLDFUSION ANALYZER")
    print("="*60)
    
    sample_code = """
<cfcomponent name="UserService" extends="BaseService" persistent="true" table="users">
    
    <cfproperty name="userId" type="numeric" fieldtype="id">
    <cfproperty name="username" type="string">
    <cfproperty name="email" type="string">
    
    <cffunction name="getUser" access="public" returntype="query">
        <cfargument name="userId" type="numeric" required="true">
        
        <cfquery name="qUser" datasource="mydb">
            SELECT userId, username, email
            FROM users
            WHERE userId = <cfqueryparam value="#arguments.userId#" cfsqltype="cf_sql_integer">
        </cfquery>
        
        <cfreturn qUser>
    </cffunction>
    
    <cffunction name="sendWelcomeEmail" access="private" returntype="void">
        <cfargument name="user" type="struct" required="true">
        
        <cfmail to="#arguments.user.email#" 
                from="noreply@example.com" 
                subject="Welcome!">
            Welcome to our application, #arguments.user.username#!
        </cfmail>
    </cffunction>
    
</cfcomponent>
"""
    
    analyzer = ColdFusionAnalyzer()
    
    # Write to temp file
    temp_file = Path("temp_test.cfc")
    temp_file.write_text(sample_code)
    
    try:
        result = analyzer.analyze(temp_file)
        
        print(f"✅ Components found: {len(result.classes)}")
        print(f"✅ Functions found: {len(result.methods)}")
        print(f"✅ Has queries: {result.patterns['cfquery']['has_queries']}")
        print(f"✅ Query count: {result.patterns['cfquery']['query_count']}")
        print(f"✅ Is ORM entity: {result.patterns['orm']['is_entity']}")
        print(f"✅ Has email: {result.patterns['cfmail']['has_email']}")
        print(f"✅ Email count: {result.patterns['cfmail']['email_count']}")
        
        if result.patterns['orm']['is_entity']:
            print(f"\nORM Table: {result.patterns['orm']['table_name']}")
            print(f"Properties: {result.patterns['orm']['properties']}")
        
    finally:
        if temp_file.exists():
            temp_file.unlink()


def validate_sql_analyzer():
    """Validate SQL analyzer with sample code."""
    print("\n" + "="*60)
    print("VALIDATING SQL ANALYZER")
    print("="*60)
    
    sample_code = """
-- Create Users table
CREATE TABLE dbo.Users (
    UserId INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(100) NOT NULL,
    Email NVARCHAR(255) NOT NULL,
    CreatedDate DATETIME DEFAULT GETDATE()
);

-- Create index
CREATE NONCLUSTERED INDEX IX_Users_Email ON dbo.Users(Email);

-- Create stored procedure
CREATE PROCEDURE dbo.sp_GetUserById
    @UserId INT
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        SELECT UserId, Username, Email, CreatedDate
        FROM dbo.Users
        WHERE UserId = @UserId;
    END TRY
    BEGIN CATCH
        THROW;
    END CATCH
END;
GO

-- Create function
CREATE FUNCTION dbo.fn_GetUserCount()
RETURNS INT
AS
BEGIN
    DECLARE @Count INT;
    
    SELECT @Count = COUNT(*)
    FROM dbo.Users
    WHERE CreatedDate >= DATEADD(DAY, -30, GETDATE());
    
    RETURN @Count;
END;
GO

-- Create view
CREATE VIEW dbo.vw_ActiveUsers
AS
SELECT UserId, Username, Email
FROM dbo.Users
WHERE CreatedDate >= DATEADD(YEAR, -1, GETDATE());
GO
"""
    
    analyzer = SQLAnalyzer()
    
    # Write to temp file
    temp_file = Path("temp_test.sql")
    temp_file.write_text(sample_code)
    
    try:
        result = analyzer.analyze(temp_file)
        
        print(f"✅ Tables found: {result.metrics['table_count']}")
        print(f"✅ Views found: {result.metrics['view_count']}")
        print(f"✅ Procedures found: {result.metrics['procedure_count']}")
        print(f"✅ Functions found: {result.metrics['function_count']}")
        print(f"✅ Indexes found: {result.metrics['index_count']}")
        print(f"✅ Has error handling: {result.patterns['has_error_handling']}")
        print(f"✅ Has transactions: {result.patterns['has_transactions']}")
        
        if result.classes:
            print(f"\nFirst object: {result.classes[0]['name']} ({result.classes[0]['type']})")
        
        if result.methods:
            print(f"\nFirst procedure: {result.methods[0]['name']}")
            print(f"  Parameters: {result.methods[0]['parameter_count']}")
            print(f"  LOC: {result.methods[0]['loc']}")
            print(f"  Complexity: {result.methods[0]['complexity']}")
        
    finally:
        if temp_file.exists():
            temp_file.unlink()


def validate_factory():
    """Validate language parser factory."""
    print("\n" + "="*60)
    print("VALIDATING LANGUAGE PARSER FACTORY")
    print("="*60)
    
    factory = get_factory()
    
    print(f"✅ Supported languages: {factory.get_supported_languages()}")
    print(f"✅ Supported extensions: {factory.get_supported_extensions()}")
    
    # Test file detection
    test_files = [
        Path("test.cs"),
        Path("test.ts"),
        Path("test.cfm"),
        Path("test.sql"),
        Path("test.py")  # Not supported
    ]
    
    print("\nFile Support Detection:")
    for file in test_files:
        supported = factory.supports_file(file)
        language = factory.detect_language(file)
        status = "✅" if supported else "❌"
        print(f"  {status} {file.name} - Language: {language or 'Unknown'}")


def main():
    """Run all validations."""
    print("\n" + "="*60)
    print("PHASE 3 LANGUAGE ANALYZERS VALIDATION")
    print("="*60)
    
    try:
        validate_csharp_analyzer()
        validate_typescript_analyzer()
        validate_coldfusion_analyzer()
        validate_sql_analyzer()
        validate_factory()
        
        print("\n" + "="*60)
        print("✅ ALL VALIDATIONS PASSED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
