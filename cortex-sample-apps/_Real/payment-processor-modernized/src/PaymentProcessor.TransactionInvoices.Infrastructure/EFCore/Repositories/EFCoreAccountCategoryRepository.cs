using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of IAccountCategoryRepository.
/// Provides database-backed CRUD operations for account_categorys.
/// </summary>
public class EFCoreAccountCategoryRepository : IAccountCategoryRepository
{
    private readonly TransactionInvoicesDbContext _context;

    public EFCoreAccountCategoryRepository(TransactionInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<AccountCategory?> GetByIdAsync(string account_categoryId)
    {
        return await _context.AccountCategorys
            .Include(s => s.TransactionInvoices)
            .FirstOrDefaultAsync(s => s.AccountCategoryId == account_categoryId);
    }

    public async Task<IEnumerable<AccountCategory>> GetAllAsync()
    {
        return await _context.AccountCategorys
            .ToListAsync();
    }

    public async Task<IEnumerable<AccountCategory>> GetByEmployerIdAsync(string employerId)
    {
        // Note: employerId mapping needs clarification based on actual schema
        // Assuming it's stored in a field (adjust as needed)
        return await _context.AccountCategorys
            .Where(s => s.Status == "Active") // Placeholder filter
            .ToListAsync();
    }

    public async Task<IEnumerable<AccountCategory>> GetByAccountTypeAsync(string accountType)
    {
        return await _context.AccountCategorys
            .Where(s => s.AccountType == accountType)
            .OrderBy(s => s.AccountNumber)
            .ToListAsync();
    }

    public async Task<IEnumerable<AccountCategory>> SearchAsync(string searchTerm)
    {
        return await _context.AccountCategorys
            .Where(s => s.CustomerId.Contains(searchTerm) || 
                       s.AccountNumber.Contains(searchTerm))
            .OrderBy(s => s.AccountNumber)
            .ToListAsync();
    }

    public async Task<AccountCategory> CreateAsync(AccountCategory account_category)
    {
        if (string.IsNullOrEmpty(account_category.AccountCategoryId))
        {
            account_category.AccountCategoryId = Guid.NewGuid().ToString();
        }

        _context.AccountCategorys.Add(account_category);
        await _context.SaveChangesAsync();
        
        return account_category;
    }

    public async Task<AccountCategory> UpdateAsync(AccountCategory account_category)
    {
        var existing = await _context.AccountCategorys.FindAsync(account_category.AccountCategoryId);
        if (existing == null)
        {
            throw new InvalidOperationException($"AccountCategory {account_category.AccountCategoryId} not found.");
        }

        _context.Entry(existing).CurrentValues.SetValues(account_category);
        await _context.SaveChangesAsync();
        
        return existing;
    }

    public async Task<bool> DeleteAsync(string account_categoryId)
    {
        var account_category = await _context.AccountCategorys.FindAsync(account_categoryId);
        if (account_category == null)
        {
            return false;
        }

        _context.AccountCategorys.Remove(account_category);
        await _context.SaveChangesAsync();
        
        return true;
    }
}
