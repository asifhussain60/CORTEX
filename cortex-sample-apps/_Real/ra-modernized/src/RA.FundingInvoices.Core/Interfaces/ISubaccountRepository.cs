namespace RA.FundingInvoices.Core.Interfaces;

/// <summary>
/// Repository interface for Subaccount entity.
/// Manages subaccount lookup and filtering operations.
/// </summary>
public interface ISubaccountRepository
{
    /// <summary>
    /// Retrieves a subaccount by its unique identifier.
    /// </summary>
    /// <param name="subaccountId">The unique subaccount identifier.</param>
    /// <returns>The subaccount if found; otherwise, null.</returns>
    Task<Subaccount?> GetByIdAsync(string subaccountId);

    /// <summary>
    /// Retrieves all subaccounts.
    /// </summary>
    /// <returns>Collection of all subaccounts.</returns>
    Task<IEnumerable<Subaccount>> GetAllAsync();

    /// <summary>
    /// Retrieves subaccounts by employer identifier.
    /// </summary>
    /// <param name="employerId">The employer identifier.</param>
    /// <returns>Collection of subaccounts for the specified employer.</returns>
    Task<IEnumerable<Subaccount>> GetByEmployerIdAsync(string employerId);

    /// <summary>
    /// Retrieves subaccounts by account type.
    /// </summary>
    /// <param name="accountType">The account type (e.g., "HSA", "FSA", "HRA").</param>
    /// <returns>Collection of subaccounts with the specified type.</returns>
    Task<IEnumerable<Subaccount>> GetByAccountTypeAsync(string accountType);

    /// <summary>
    /// Searches subaccounts by member identifier or name (partial match).
    /// </summary>
    /// <param name="searchTerm">The search term.</param>
    /// <returns>Collection of matching subaccounts.</returns>
    Task<IEnumerable<Subaccount>> SearchAsync(string searchTerm);

    /// <summary>
    /// Creates a new subaccount.
    /// </summary>
    /// <param name="subaccount">The subaccount to create.</param>
    /// <returns>The created subaccount.</returns>
    Task<Subaccount> CreateAsync(Subaccount subaccount);

    /// <summary>
    /// Updates an existing subaccount.
    /// </summary>
    /// <param name="subaccount">The subaccount with updated values.</param>
    /// <returns>The updated subaccount.</returns>
    Task<Subaccount> UpdateAsync(Subaccount subaccount);

    /// <summary>
    /// Deletes a subaccount by its identifier.
    /// </summary>
    /// <param name="subaccountId">The subaccount identifier to delete.</param>
    /// <returns>True if deleted; otherwise, false.</returns>
    Task<bool> DeleteAsync(string subaccountId);
}

// TODO: Phase 2 - Define Subaccount entity class
public class Subaccount
{
    public string SubaccountId { get; set; } = string.Empty;
    public string EmployerId { get; set; } = string.Empty;
    public string MemberId { get; set; } = string.Empty;
    public string MemberName { get; set; } = string.Empty;
    public string AccountType { get; set; } = string.Empty;
    public decimal Balance { get; set; }
    public DateTime CreatedDate { get; set; }
}
