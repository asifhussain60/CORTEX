// ❌ SMELL-5: Circular dependency — UserService depends on TransactionService
// ❌ SMELL-14: No retry/circuit breaker — raw HttpClient calls
// ❌ SMELL-17: No DI — services instantiate each other directly

using CortexLabs.FinTrack.Models;

namespace CortexLabs.FinTrack.Services;

// ❌ SMELL-3: Service is also a God class — does auth, email, reporting, analytics
public class UserService
{
    // ❌ SMELL-5: Circular dependency — UserService creates TransactionService
    private TransactionService _transactionService;
    // ❌ SMELL-14: No retry policy, no circuit breaker, no timeout
    private HttpClient _httpClient = new HttpClient();

    public UserService()
    {
        // ❌ SMELL-17: Direct instantiation instead of DI
        _transactionService = new TransactionService();
    }

    // ❌ SMELL-1: SQL injection via string concatenation
    public string BuildUserQuery(string username)
    {
        return $"SELECT * FROM Users WHERE user_name = '{username}'"; // SQL INJECTION!
    }

    // ❌ SMELL-10: Duplicate validation — same logic exists in Program.cs endpoints
    public bool ValidateEmail(string email)
    {
        if (string.IsNullOrEmpty(email)) return false;
        if (!email.Contains("@")) return false;
        if (email.Length < 5) return false; // ❌ SMELL-15: Magic number
        if (email.Length > 100) return false; // ❌ SMELL-15: Magic number
        return true;
    }

    // ❌ SMELL-8: Dead code — this method is never called anywhere
    public void SendWelcomeEmail(string email)
    {
        // TODO: implement email sending
        Console.WriteLine($"Welcome email sent to {email}"); // ❌ SMELL-11: Console.WriteLine instead of ILogger
    }

    // ❌ SMELL-8: Another dead method
    public void ExportUserData(int userId, string format)
    {
        // This was planned for Q3 2023 but never implemented
        throw new NotImplementedException();
    }

    // ❌ SMELL-14: No retry, no timeout, no error handling on HTTP call
    public async Task<string> GetUserCreditScore(int userId)
    {
        var response = await _httpClient.GetAsync($"https://api.creditcheck.fake/score/{userId}");
        return await response.Content.ReadAsStringAsync();
    }

    // ❌ SMELL-4: Business logic that should be in a domain service
    public decimal CalculateUserNetWorth(List<Account> accounts, List<Transaction> transactions)
    {
        decimal total = 0;
        foreach (var account in accounts)
        {
            total += account.Balance;
        }
        foreach (var tx in transactions)
        {
            if (tx.Type == "expense")
                total -= tx.Amount;
            else if (tx.Type == "income")
                total += tx.Amount;
            // ❌ SMELL-15: Magic strings "expense", "income" — should be enum
        }
        return total;
    }
}

public class TransactionService
{
    // ❌ SMELL-5: Circular dependency — TransactionService creates UserService
    private UserService _userService;

    public TransactionService()
    {
        // ❌ SMELL-17: Direct instantiation — will cause stack overflow if both constructed!
        // In "production" this is "avoided" by lazy initialization... poorly
        // _userService = new UserService(); // Commented out to avoid immediate crash
    }

    public void SetUserService(UserService us)
    {
        _userService = us;
    }

    // ❌ SMELL-1: SQL injection
    public string BuildTransactionQuery(string category, string dateFrom)
    {
        return $"SELECT * FROM Transactions WHERE category_name = '{category}' AND Date >= '{dateFrom}'";
    }

    // ❌ SMELL-6: No pagination — returns ALL transactions
    public string GetAllTransactionsQuery()
    {
        return "SELECT * FROM Transactions"; // No LIMIT, no OFFSET, no WHERE
    }

    // ❌ SMELL-10: Duplicate validation — same email check as UserService
    public bool IsValidEmail(string email)
    {
        if (string.IsNullOrEmpty(email)) return false;
        if (!email.Contains("@")) return false;
        if (email.Length < 5) return false; // ❌ SMELL-15: Same magic numbers duplicated
        if (email.Length > 100) return false;
        return true;
    }

    // ❌ SMELL-8: Dead code — never invoked
    public void ArchiveOldTransactions()
    {
        // Planned for Phase 2, never implemented
        Console.WriteLine("Archiving..."); // ❌ SMELL-11: No structured logging
    }

    // ❌ SMELL-4: Business logic embedded in service — should be domain model
    public string CategorizeTransaction(decimal amount, string description)
    {
        if (amount > 10000) return "large_purchase"; // ❌ SMELL-15: Magic number
        if (amount > 1000) return "medium_purchase"; // ❌ SMELL-15: Magic number
        if (description.ToLower().Contains("grocery")) return "food"; // ❌ SMELL-15: Magic string
        if (description.ToLower().Contains("gas")) return "transport";
        if (description.ToLower().Contains("netflix")) return "entertainment";
        return "other";
    }
}

// ❌ SMELL-8: Entire class is dead code — was planned for "Phase 3" but never used
public class NotificationService
{
    private static readonly string API_KEY = "ntfy-12345-abcde"; // ❌ SMELL-2: Hardcoded API key

    public void SendPushNotification(string userId, string message)
    {
        Console.WriteLine($"Push to {userId}: {message}"); // ❌ SMELL-11: Console.WriteLine
    }

    public void SendSms(string phoneNumber, string body)
    {
        Console.WriteLine($"SMS to {phoneNumber}: {body}");
    }

    public void SendSlackAlert(string channel, string text)
    {
        Console.WriteLine($"Slack #{channel}: {text}");
    }
}

// ❌ SMELL-8: Another dead class — ReportGenerator never called from any endpoint
public class ReportGenerator
{
    // ❌ SMELL-15: Magic numbers for report thresholds
    private const int MAX_ROWS = 99999;
    private const int TIMEOUT_MS = 300000;

    // ❌ SMELL-6: No pagination, loads everything
    public List<Transaction> GetAllDataForReport()
    {
        // In a real app this would query the DB with no limit
        return AppCache.RecentTransactions.ToList();
    }

    public string GenerateCSV(List<Transaction> data)
    {
        var csv = "Id,Description,Amount,Category,Type,Date,UserId\n";
        foreach (var t in data)
        {
            // ❌ SMELL-18: No escaping — CSV injection possible
            csv += $"{t.Id},{t.description},{t.Amount},{t.category_name},{t.Type},{t.Date},{t.UserId}\n";
        }
        return csv;
    }
}
