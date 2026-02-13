namespace PaymentProcessor.TransactionInvoices.Core.Interfaces;

/// <summary>
/// Repository interface for AccountCategory entity.
/// Manages account_category lookup and filtering operations.
/// </summary>
public interface IAccountCategoryRepository
{
    /// <summary>
    /// Retrieves a account_category by its unique identifier.
    /// </summary>
    /// <param name="account_categoryId">The unique account_category identifier.</param>
    /// <returns>The account_category if found; otherwise, null.</returns>
    Task<AccountCategory?> GetByIdAsync(string account_categoryId);

    /// <summary>
    /// Retrieves all account_categorys.
    /// </summary>
    /// <returns>Collection of all account_categorys.</returns>
    Task<IEnumerable<AccountCategory>> GetAllAsync();

    /// <summary>
    /// Retrieves account_categorys by employer identifier.
    /// </summary>
    /// <param name="employerId">The employer identifier.</param>
    /// <returns>Collection of account_categorys for the specified employer.</returns>
    Task<IEnumerable<AccountCategory>> GetByEmployerIdAsync(string employerId);

    /// <summary>
    /// Retrieves account_categorys by account type.
    /// </summary>
    /// <param name="accountType">The account type (e.g., "AccountTypeA", "AccountTypeB", "AccountTypeC").</param>
    /// <returns>Collection of account_categorys with the specified type.</returns>
    Task<IEnumerable<AccountCategory>> GetByAccountTypeAsync(string accountType);

    /// <summary>
    /// Searches account_categorys by customer identifier or name (partial match).
    /// </summary>
    /// <param name="searchTerm">The search term.</param>
    /// <returns>Collection of matching account_categorys.</returns>
    Task<IEnumerable<AccountCategory>> SearchAsync(string searchTerm);

    /// <summary>
    /// Creates a new account_category.
    /// </summary>
    /// <param name="account_category">The account_category to create.</param>
    /// <returns>The created account_category.</returns>
    Task<AccountCategory> CreateAsync(AccountCategory account_category);

    /// <summary>
    /// Updates an existing account_category.
    /// </summary>
    /// <param name="account_category">The account_category with updated values.</param>
    /// <returns>The updated account_category.</returns>
    Task<AccountCategory> UpdateAsync(AccountCategory account_category);

    /// <summary>
    /// Deletes a account_category by its identifier.
    /// </summary>
    /// <param name="account_categoryId">The account_category identifier to delete.</param>
    /// <returns>True if deleted; otherwise, false.</returns>
    Task<bool> DeleteAsync(string account_categoryId);
}

// TODO: Phase 2 - Define AccountCategory entity class
public class AccountCategory
{
    public string AccountCategoryId { get; set; } = string.Empty;
    public string EmployerId { get; set; } = string.Empty;
    public string CustomerId { get; set; } = string.Empty;
    public string CustomerName { get; set; } = string.Empty;
    public string AccountType { get; set; } = string.Empty;
    public decimal Balance { get; set; }
    public DateTime CreatedDate { get; set; }
}
