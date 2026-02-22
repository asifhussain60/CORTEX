// ✅ SMELL-1 FIXED: Parameterized queries — no string interpolation
// ✅ SMELL-6 FIXED: Pagination on GET /accounts
// ✅ SMELL-11 FIXED: ILogger<T> structured logging
// ✅ SMELL-14 FIXED: DB transfer wrapped in SQLite transaction — atomic operation
// ✅ SMELL-17 FIXED: DI via constructor injection
// ✅ SMELL-19 FIXED: Transfer validation via IValidationService

using CortexLabs.FinTrack.Application.Interfaces;
using CortexLabs.FinTrack.Domain.Entities;
using CortexLabs.FinTrack.Domain.Enums;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.Logging;

namespace CortexLabs.FinTrack.Application.Services;

/// <summary>
/// Manages account operations. The TransferAsync method uses a SQLite transaction
/// so partial failures are automatically rolled back (SMELL-14 fix — atomicity).
/// </summary>
public sealed class AccountService : IAccountService
{
    private readonly string _connectionString;
    private readonly IValidationService _validationService;
    private readonly ILogger<AccountService> _logger;

    public AccountService(
        IConfiguration configuration,
        IValidationService validationService,
        ILogger<AccountService> logger)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("DefaultConnection is required.");
        _validationService = validationService;
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<IEnumerable<Account>> GetAccountsAsync(int page = 1, int pageSize = 25)
    {
        var offset = (page - 1) * pageSize;
        var accounts = new List<Account>();

        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        // ✅ SMELL-6 FIXED: Paginated
        cmd.CommandText = "SELECT Id, accountName, Balance, user_id, account_type FROM Accounts LIMIT @limit OFFSET @offset";
        cmd.Parameters.AddWithValue("@limit", pageSize);
        cmd.Parameters.AddWithValue("@offset", offset);

        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            accounts.Add(MapAccount(reader));
        }

        return accounts;
    }

    /// <inheritdoc/>
    public async Task<Account?> GetByIdAsync(int id)
    {
        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        var cmd = conn.CreateCommand();
        cmd.CommandText = "SELECT Id, accountName, Balance, user_id, account_type FROM Accounts WHERE Id = @id";
        cmd.Parameters.AddWithValue("@id", id);

        await using var reader = await cmd.ExecuteReaderAsync();
        return await reader.ReadAsync() ? MapAccount(reader) : null;
    }

    /// <inheritdoc/>
    public async Task<TransferResult> TransferAsync(int fromId, int toId, decimal amount, int requestedBy)
    {
        // 1. Fetch current balance for validation
        var sourceAccount = await GetByIdAsync(fromId);
        if (sourceAccount is null)
            return new TransferResult(false, $"Source account {fromId} not found.");

        // 2. Validate via single canonical service (SMELL-10 fixed)
        var validation = _validationService.ValidateTransfer(fromId, toId, amount, sourceAccount.Balance);
        if (!validation.IsValid)
            return new TransferResult(false, validation.Error);

        // 3. Execute atomically in a SQLite transaction (SMELL-14 fix)
        await using var conn = new SqliteConnection(_connectionString);
        await conn.OpenAsync();
        await using var txn = conn.BeginTransaction();
        try
        {
            var debit = conn.CreateCommand();
            debit.Transaction = txn;
            // ✅ SMELL-1 FIXED: Parameterized
            debit.CommandText = "UPDATE Accounts SET Balance = Balance - @amount WHERE Id = @id";
            debit.Parameters.AddWithValue("@amount", (double)amount);
            debit.Parameters.AddWithValue("@id", fromId);
            await debit.ExecuteNonQueryAsync();

            var credit = conn.CreateCommand();
            credit.Transaction = txn;
            credit.CommandText = "UPDATE Accounts SET Balance = Balance + @amount WHERE Id = @id";
            credit.Parameters.AddWithValue("@amount", (double)amount);
            credit.Parameters.AddWithValue("@id", toId);
            await credit.ExecuteNonQueryAsync();

            await txn.CommitAsync();
            _logger.LogInformation("Transfer {Amount:C} from account {From} to {To} by user {User}",
                amount, fromId, toId, requestedBy);
            return new TransferResult(true);
        }
        catch (Exception ex)
        {
            await txn.RollbackAsync();
            _logger.LogError(ex, "Transfer failed from {From} to {To}", fromId, toId);
            return new TransferResult(false, "Transfer failed due to a database error.");
        }
    }

    private static Account MapAccount(SqliteDataReader r) => new()
    {
        Id = r.GetInt32(0),
        Name = r.IsDBNull(1) ? string.Empty : r.GetString(1),
        Balance = (decimal)r.GetDouble(2),
        UserId = r.GetInt32(3),
        Type = Enum.TryParse<AccountType>(r.IsDBNull(4) ? "Checking" : r.GetString(4), out var t)
            ? t : AccountType.Checking
    };
}
