using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.EFCore.Repositories;

/// <summary>
/// EF Core implementation of ISubaccountRepository.
/// Provides database-backed CRUD operations for subaccounts.
/// </summary>
public class EFCoreSubaccountRepository : ISubaccountRepository
{
    private readonly FundingInvoicesDbContext _context;

    public EFCoreSubaccountRepository(FundingInvoicesDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<Subaccount?> GetByIdAsync(string subaccountId)
    {
        return await _context.Subaccounts
            .Include(s => s.FundingInvoices)
            .FirstOrDefaultAsync(s => s.SubaccountId == subaccountId);
    }

    public async Task<IEnumerable<Subaccount>> GetAllAsync()
    {
        return await _context.Subaccounts
            .ToListAsync();
    }

    public async Task<IEnumerable<Subaccount>> GetByEmployerIdAsync(string employerId)
    {
        // Note: employerId mapping needs clarification based on actual schema
        // Assuming it's stored in a field (adjust as needed)
        return await _context.Subaccounts
            .Where(s => s.Status == "Active") // Placeholder filter
            .ToListAsync();
    }

    public async Task<IEnumerable<Subaccount>> GetByAccountTypeAsync(string accountType)
    {
        return await _context.Subaccounts
            .Where(s => s.AccountType == accountType)
            .OrderBy(s => s.AccountNumber)
            .ToListAsync();
    }

    public async Task<IEnumerable<Subaccount>> SearchAsync(string searchTerm)
    {
        return await _context.Subaccounts
            .Where(s => s.MemberId.Contains(searchTerm) || 
                       s.AccountNumber.Contains(searchTerm))
            .OrderBy(s => s.AccountNumber)
            .ToListAsync();
    }

    public async Task<Subaccount> CreateAsync(Subaccount subaccount)
    {
        if (string.IsNullOrEmpty(subaccount.SubaccountId))
        {
            subaccount.SubaccountId = Guid.NewGuid().ToString();
        }

        _context.Subaccounts.Add(subaccount);
        await _context.SaveChangesAsync();
        
        return subaccount;
    }

    public async Task<Subaccount> UpdateAsync(Subaccount subaccount)
    {
        var existing = await _context.Subaccounts.FindAsync(subaccount.SubaccountId);
        if (existing == null)
        {
            throw new InvalidOperationException($"Subaccount {subaccount.SubaccountId} not found.");
        }

        _context.Entry(existing).CurrentValues.SetValues(subaccount);
        await _context.SaveChangesAsync();
        
        return existing;
    }

    public async Task<bool> DeleteAsync(string subaccountId)
    {
        var subaccount = await _context.Subaccounts.FindAsync(subaccountId);
        if (subaccount == null)
        {
            return false;
        }

        _context.Subaccounts.Remove(subaccount);
        await _context.SaveChangesAsync();
        
        return true;
    }
}
