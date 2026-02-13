using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;
using RA.FundingInvoices.Infrastructure.Persistence.Configurations;

namespace RA.FundingInvoices.Infrastructure.Persistence;

/// <summary>
/// Entity Framework Core database context for RA Funding Invoices.
/// Manages database connections, entity mapping, and change tracking.
/// </summary>
public class FundingInvoicesDbContext : DbContext
{
    public FundingInvoicesDbContext(DbContextOptions<FundingInvoicesDbContext> options)
        : base(options)
    {
    }

    /// <summary>
    /// Funding invoices entity set.
    /// </summary>
    public DbSet<FundingInvoice> FundingInvoices { get; set; } = null!;

    /// <summary>
    /// Funding batches entity set.
    /// </summary>
    public DbSet<FundingBatch> FundingBatches { get; set; } = null!;

    /// <summary>
    /// Subaccounts entity set.
    /// </summary>
    public DbSet<Subaccount> Subaccounts { get; set; } = null!;

    /// <summary>
    /// Cash in/out transactions entity set.
    /// </summary>
    public DbSet<CashInOut> CashTransactions { get; set; } = null!;

    /// <summary>
    /// Configure entity mappings using Fluent API for precise control over database schema.
    /// </summary>
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply entity type configurations
        modelBuilder.ApplyConfiguration(new FundingInvoiceConfiguration());
        modelBuilder.ApplyConfiguration(new FundingBatchConfiguration());
        modelBuilder.ApplyConfiguration(new SubaccountConfiguration());
        modelBuilder.ApplyConfiguration(new CashInOutConfiguration());
    }

    /// <summary>
    /// Override SaveChanges to automatically update audit fields (ModifiedBy, ModifiedDate).
    /// </summary>
    public override int SaveChanges()
    {
        UpdateAuditFields();
        return base.SaveChanges();
    }

    /// <summary>
    /// Override SaveChangesAsync to automatically update audit fields (ModifiedBy, ModifiedDate).
    /// </summary>
    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateAuditFields();
        return base.SaveChangesAsync(cancellationToken);
    }

    /// <summary>
    /// Automatically set ModifiedBy and ModifiedDate for modified entities.
    /// HIPAA compliance: Track all changes to PHI-containing records.
    /// </summary>
    private void UpdateAuditFields()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Modified);

        foreach (var entry in entries)
        {
            // Get ModifiedBy and ModifiedDate properties via reflection
            var modifiedByProp = entry.Entity.GetType().GetProperty("ModifiedBy");
            var modifiedDateProp = entry.Entity.GetType().GetProperty("ModifiedDate");

            if (modifiedByProp != null && modifiedDateProp != null)
            {
                // Set ModifiedBy to system user (in production, use actual user from claims)
                modifiedByProp.SetValue(entry.Entity, "SYSTEM");
                modifiedDateProp.SetValue(entry.Entity, DateTime.UtcNow);
            }
        }
    }
}
