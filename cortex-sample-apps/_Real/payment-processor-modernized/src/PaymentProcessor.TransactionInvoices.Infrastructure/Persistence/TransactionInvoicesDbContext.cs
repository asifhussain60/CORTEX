using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;
using PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Configurations;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence;

/// <summary>
/// Entity Framework Core database context for PaymentProcessor Transaction Invoices.
/// Manages database connections, entity mapping, and change tracking.
/// </summary>
public class TransactionInvoicesDbContext : DbContext
{
    public TransactionInvoicesDbContext(DbContextOptions<TransactionInvoicesDbContext> options)
        : base(options)
    {
    }

    /// <summary>
    /// Transaction invoices entity set.
    /// </summary>
    public DbSet<TransactionInvoice> TransactionInvoices { get; set; } = null!;

    /// <summary>
    /// Transaction batches entity set.
    /// </summary>
    public DbSet<TransactionBatch> TransactionBatches { get; set; } = null!;

    /// <summary>
    /// AccountCategorys entity set.
    /// </summary>
    public DbSet<AccountCategory> AccountCategorys { get; set; } = null!;

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
        modelBuilder.ApplyConfiguration(new TransactionInvoiceConfiguration());
        modelBuilder.ApplyConfiguration(new TransactionBatchConfiguration());
        modelBuilder.ApplyConfiguration(new AccountCategoryConfiguration());
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
    /// GDPR compliance: Track all changes to PII-containing records.
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
                // Set ModifiedBy to system user (in production, use actual user from requests)
                modifiedByProp.SetValue(entry.Entity, "SYSTEM");
                modifiedDateProp.SetValue(entry.Entity, DateTime.UtcNow);
            }
        }
    }
}
