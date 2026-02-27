// ❌ SMELL-19: No validation attributes on any model
// ❌ SMELL-20: No audit fields (CreatedAt, ModifiedBy, Version)
// ❌ SMELL-7: Mixed naming conventions (PascalCase + camelCase + snake_case in same file)

namespace CortexLabs.FinTrack.Models;

// ❌ SMELL-19: No [Required], [Range], [StringLength] attributes — accepts any garbage
public class Transaction
{
    public int Id { get; set; }
    public string description { get; set; } // ❌ SMELL-7: camelCase instead of PascalCase
    public decimal Amount { get; set; }
    public string category_name { get; set; } // ❌ SMELL-7: snake_case in C#
    public string Type { get; set; } // No enum — accepts any string including "HACKED"
    public DateTime Date { get; set; }
    public int UserId { get; set; }
    // ❌ SMELL-20: Missing CreatedAt, CreatedBy, ModifiedAt, ModifiedBy, IsDeleted, Version
}

public class User
{
    public int Id { get; set; }
    public string user_name { get; set; } // ❌ SMELL-7: snake_case
    public string Email { get; set; }
    public string password_hash { get; set; } // ❌ SMELL-7: snake_case + stored as plain text despite name
    public string Role { get; set; }
    public bool is_active { get; set; } // ❌ SMELL-7: snake_case
    // ❌ SMELL-20: No audit trail
}

public class Account
{
    public int Id { get; set; }
    public string accountName { get; set; } // ❌ SMELL-7: camelCase
    public decimal Balance { get; set; }
    public int user_id { get; set; } // ❌ SMELL-7: snake_case
    public string account_type { get; set; } // ❌ SMELL-7: snake_case — no enum
    // ❌ SMELL-20: No LastModified, no optimistic concurrency token
}

public class Report
{
    public int Id { get; set; }
    public string title { get; set; } // ❌ SMELL-7: camelCase
    public string Content { get; set; }
    public int generated_by { get; set; } // ❌ SMELL-7: snake_case
    public DateTime generated_at { get; set; } // ❌ SMELL-7: snake_case
}

// ❌ SMELL-16: Global mutable state — static list used as in-memory cache
public static class AppCache
{
    public static List<Transaction> RecentTransactions = new List<Transaction>();
    public static Dictionary<string, object> Settings = new Dictionary<string, object>();
    public static int TotalRequestCount = 0;
    public static DateTime? LastError = null;
    public static string LastErrorMessage = "";
}
