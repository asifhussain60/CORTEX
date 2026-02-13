using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.Persistence.Repositories;

/// <summary>
/// EF Core implementation of ISubaccountRepository.
/// Provides database-backed CRUD operations for Subaccount entities.
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
            .Include(s => s.FundingInvoices)
            .ToListAsync();
    }

    public async Task<Subaccount?> GetByAccountNumberAsync(string accountNumber)
    {
        return await _context.Subaccounts
            .Include(s => s.FundingInvoices)
            .FirstOrDefaultAsync(s => s.AccountNumber == accountNumber);
    }

    public async Task<IEnumerable<Subaccount>> GetByMemberIdAsync(string memberId)
    {
        return await _context.Subaccounts
            .Where(s => s.MemberId == memberId)
            .ToListAsync();
    }

    public async Task<IEnumerable<Subaccount>> GetByAccountTypeAsync(string accountType)
    {
        return await _context.Subaccounts
            .Where(s => s.AccountType == accountType)
            .ToListAsync();
    }

    public async Task<IEnumerable<Subaccount>> GetByStatusAsync(string status)
    {
        return await _context.Subaccounts
            .Where(s => s.Status == status)
            .ToListAsync();
    }

    public async Task<Subaccount> CreateAsync(Subaccount subaccount)
    {
        _context.Subaccounts.Add(subaccount);
        await _context.SaveChangesAsync();
        return subaccount;
    }

    public async Task<Subaccount> UpdateAsync(Subaccount subaccount)
    {
        _context.Entry(subaccount).State = EntityState.Modified;
        await _context.SaveChangesAsync();
        return subaccount;
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

    public async Task<int> CountAsync()
    {
        return await _context.Subaccounts.CountAsync();
    }
}
