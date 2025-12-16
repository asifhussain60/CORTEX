using Microsoft.EntityFrameworkCore;
using RA.FundingInvoices.Core.Entities;

namespace RA.FundingInvoices.Infrastructure.EFCore;

/// <summary>
/// Entity Framework Core DbContext for RA Funding Invoices domain.
/// Manages database schema, relationships, and change tracking.
/// </summary>
public class FundingInvoicesDbContext : DbContext
{
    public FundingInvoicesDbContext(DbContextOptions<FundingInvoicesDbContext> options)
        : base(options)
    {
    }

    /// <summary>
    /// Funding invoices table.
    /// </summary>
    public DbSet<FundingInvoice> FundingInvoices => Set<FundingInvoice>();

    /// <summary>
    /// Funding batches table.
    /// </summary>
    public DbSet<FundingBatch> FundingBatches => Set<FundingBatch>();

    /// <summary>
    /// Subaccounts (member reimbursement accounts) table.
    /// </summary>
    public DbSet<Subaccount> Subaccounts => Set<Subaccount>();

    /// <summary>
    /// Cash in/out transactions table.
    /// </summary>
    public DbSet<CashInOut> CashTransactions => Set<CashInOut>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply entity configurations
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(FundingInvoicesDbContext).Assembly);

        // Global query filters for soft deletes (if needed in future)
        // modelBuilder.Entity<FundingInvoice>().HasQueryFilter(e => !e.IsDeleted);

        // Configure audit fields default values
        ConfigureAuditFields(modelBuilder);

        // Configure indexes for performance
        ConfigureIndexes(modelBuilder);
    }

    private void ConfigureAuditFields(ModelBuilder modelBuilder)
    {
        // Set default values for audit timestamps
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            var createdDateProperty = entityType.FindProperty("CreatedDate");
            if (createdDateProperty != null)
            {
                createdDateProperty.SetDefaultValueSql("GETUTCDATE()");
            }
        }
    }

    private void ConfigureIndexes(ModelBuilder modelBuilder)
    {
        // FundingInvoice indexes
        modelBuilder.Entity<FundingInvoice>()
            .HasIndex(f => f.BatchId)
            .HasDatabaseName("IX_FundingInvoice_BatchId");

        modelBuilder.Entity<FundingInvoice>()
            .HasIndex(f => f.SubaccountId)
            .HasDatabaseName("IX_FundingInvoice_SubaccountId");

        modelBuilder.Entity<FundingInvoice>()
            .HasIndex(f => new { f.Status, f.InvoiceDate })
            .HasDatabaseName("IX_FundingInvoice_Status_InvoiceDate");

        // FundingBatch indexes
        modelBuilder.Entity<FundingBatch>()
            .HasIndex(b => b.Status)
            .HasDatabaseName("IX_FundingBatch_Status");

        modelBuilder.Entity<FundingBatch>()
            .HasIndex(b => b.BatchDate)
            .HasDatabaseName("IX_FundingBatch_BatchDate");

        // Subaccount indexes
        modelBuilder.Entity<Subaccount>()
            .HasIndex(s => s.MemberId)
            .HasDatabaseName("IX_Subaccount_MemberId");

        modelBuilder.Entity<Subaccount>()
            .HasIndex(s => s.AccountNumber)
            .IsUnique()
            .HasDatabaseName("IX_Subaccount_AccountNumber_Unique");

        modelBuilder.Entity<Subaccount>()
            .HasIndex(s => new { s.AccountType, s.Status })
            .HasDatabaseName("IX_Subaccount_AccountType_Status");

        // CashInOut indexes
        modelBuilder.Entity<CashInOut>()
            .HasIndex(c => c.BatchId)
            .HasDatabaseName("IX_CashInOut_BatchId");

        modelBuilder.Entity<CashInOut>()
            .HasIndex(c => new { c.TransactionType, c.TransactionDate })
            .HasDatabaseName("IX_CashInOut_TransactionType_TransactionDate");
    }

    /// <summary>
    /// Override SaveChanges to automatically update audit fields.
    /// </summary>
    public override int SaveChanges()
    {
        UpdateAuditFields();
        return base.SaveChanges();
    }

    /// <summary>
    /// Override SaveChangesAsync to automatically update audit fields.
    /// </summary>
    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateAuditFields();
        return base.SaveChangesAsync(cancellationToken);
    }

    private void UpdateAuditFields()
    {
        var entries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Added || e.State == EntityState.Modified);

        foreach (var entry in entries)
        {
            if (entry.State == EntityState.Added)
            {
                // Set CreatedBy and CreatedDate for new entities
                if (entry.Property("CreatedBy").CurrentValue == null || 
                    string.IsNullOrEmpty(entry.Property("CreatedBy").CurrentValue?.ToString()))
                {
                    entry.Property("CreatedBy").CurrentValue = "System"; // TODO: Get from IHttpContextAccessor
                }
                
                if (entry.Property("CreatedDate").CurrentValue == null ||
                    (DateTime)entry.Property("CreatedDate").CurrentValue == DateTime.MinValue)
                {
                    entry.Property("CreatedDate").CurrentValue = DateTime.UtcNow;
                }
            }

            if (entry.State == EntityState.Modified)
            {
                // Set ModifiedBy and ModifiedDate for updated entities
                entry.Property("ModifiedBy").CurrentValue = "System"; // TODO: Get from IHttpContextAccessor
                entry.Property("ModifiedDate").CurrentValue = DateTime.UtcNow;
            }
        }
    }
}
