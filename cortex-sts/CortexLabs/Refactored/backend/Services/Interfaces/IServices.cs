// ✅ CORTEX Refactored — Service Interfaces
// ✅ SMELL-17 RESOLVED: Interface-based dependency injection

namespace CortexLabs.FinTrack.Services.Interfaces;

public interface IUserService
{
    Task<UserDto?> GetByIdAsync(int id);
    Task<IEnumerable<UserDto>> GetAllAsync(int page = 1, int pageSize = 20);
    Task<UserDto?> GetByUsernameAsync(string username);
    Task<UserDto> CreateAsync(CreateUserDto dto);
    Task<bool> UpdateAsync(int id, UpdateUserDto dto);
    Task<bool> DeleteAsync(int id);
}

public interface ITransactionService
{
    Task<TransactionDto?> GetByIdAsync(int id);
    Task<IEnumerable<TransactionDto>> GetAllAsync(int page = 1, int pageSize = 50);
    Task<IEnumerable<TransactionDto>> SearchAsync(string? category, DateTime? fromDate);
    Task<TransactionDto> CreateAsync(CreateTransactionDto dto);
    Task<bool> DeleteAsync(int id);
    Task<DashboardSummary> GetDashboardSummaryAsync(int userId);
}

public interface IAccountService
{
    Task<AccountDto?> GetByIdAsync(int id);
    Task<IEnumerable<AccountDto>> GetByUserIdAsync(int userId);
    Task<AccountDto> CreateAsync(CreateAccountDto dto);
    Task<bool> TransferAsync(int fromAccountId, int toAccountId, decimal amount);
}

public interface IValidationService
{
    ValidationResult ValidateEmail(string email);
    ValidationResult ValidateTransaction(CreateTransactionDto dto);
    ValidationResult ValidateUser(CreateUserDto dto);
}

public interface IAuthService
{
    Task<AuthTokenDto> LoginAsync(string username, string password);
    Task<AuthTokenDto> RefreshTokenAsync(string refreshToken);
}

public interface IReportService
{
    Task<IEnumerable<ReportDto>> GetAllAsync(int page = 1, int pageSize = 20);
    Task<ReportDto?> GetByIdAsync(int id);
    Task<ReportDto> GenerateAsync(GenerateReportDto dto);
}

public interface IAnalyticsService
{
    Task<AnalyticsSummaryDto> GetSummaryAsync(int? userId = null);
    Task<IEnumerable<CategoryBreakdown>> GetCategoryBreakdownAsync(int? userId = null, DateTime? fromDate = null);
}

// DTOs
public record UserDto(int Id, string UserName, string Email, string Role, bool IsActive);
public record CreateUserDto(string UserName, string Email, string Password, string Role = "user");
public record UpdateUserDto(string? Email, string? Role, bool? IsActive);

public record TransactionDto(int Id, string Description, decimal Amount, string Category, string Type, DateTime Date, int UserId);
public record CreateTransactionDto(string Description, decimal Amount, string Category, string Type, int UserId);

public record AccountDto(int Id, string Name, decimal Balance, int UserId, string AccountType);
public record CreateAccountDto(string Name, decimal InitialBalance, int UserId, string AccountType);

public record DashboardSummary(decimal TotalIncome, decimal TotalExpenses, decimal NetPosition, string HealthScore, IEnumerable<CategoryBreakdown> Categories);
public record CategoryBreakdown(string Name, decimal Amount, decimal Percentage);

public record ValidationResult(bool IsValid, IEnumerable<string> Errors);
