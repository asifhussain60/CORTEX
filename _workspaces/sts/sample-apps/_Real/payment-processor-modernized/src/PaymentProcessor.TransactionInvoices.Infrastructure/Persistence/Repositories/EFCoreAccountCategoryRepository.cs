using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Core.Interfaces;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Repositories;

/// <summary>
/// EF Core implementation of IAccountCategoryRepository.
/// Provides database-backed CRUD operations for AccountCategory entities.
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
            .Include(s => s.TransactionInvoices)
            .ToListAsync();
    }

    public async Task<AccountCategory?> GetByAccountNumberAsync(string accountNumber)
    {
        return await _context.AccountCategorys
            .Include(s => s.TransactionInvoices)
            .FirstOrDefaultAsync(s => s.AccountNumber == accountNumber);
    }

    public async Task<IEnumerable<AccountCategory>> GetByCustomerIdAsync(string customerId)
    {
        return await _context.AccountCategorys
            .Where(s => s.CustomerId == customerId)
            .ToListAsync();
    }

    public async Task<IEnumerable<AccountCategory>> GetByAccountTypeAsync(string accountType)
    {
        return await _context.AccountCategorys
            .Where(s => s.AccountType == accountType)
            .ToListAsync();
    }

    public async Task<IEnumerable<AccountCategory>> GetByStatusAsync(string status)
    {
        return await _context.AccountCategorys
            .Where(s => s.Status == status)
            .ToListAsync();
    }

    public async Task<AccountCategory> CreateAsync(AccountCategory account_category)
    {
        _context.AccountCategorys.Add(account_category);
        await _context.SaveChangesAsync();
        return account_category;
    }

    public async Task<AccountCategory> UpdateAsync(AccountCategory account_category)
    {
        _context.Entry(account_category).State = EntityState.Modified;
        await _context.SaveChangesAsync();
        return account_category;
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

    public async Task<int> CountAsync()
    {
        return await _context.AccountCategorys.CountAsync();
    }
}
