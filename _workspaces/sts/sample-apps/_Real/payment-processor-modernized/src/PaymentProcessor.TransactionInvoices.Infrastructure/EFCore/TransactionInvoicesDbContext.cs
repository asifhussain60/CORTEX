using Microsoft.EntityFrameworkCore;
using PaymentProcessor.TransactionInvoices.Core.Entities;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore;

/// <summary>
/// Entity Framework Core DbContext for PaymentProcessor Transaction Invoices domain.
/// Manages database schema, relationships, and change tracking.
/// </summary>
public class TransactionInvoicesDbContext : DbContext
{
    public TransactionInvoicesDbContext(DbContextOptions<TransactionInvoicesDbContext> options)
        : base(options)
    {
    }

    /// <summary>
    /// Transaction invoices table.
    /// </summary>
    public DbSet<TransactionInvoice> TransactionInvoices => Set<TransactionInvoice>();

    /// <summary>
    /// Transaction batches table.
    /// </summary>
    public DbSet<TransactionBatch> TransactionBatches => Set<TransactionBatch>();

    /// <summary>
    /// AccountCategorys (customer payment accounts) table.
    /// </summary>
    public DbSet<AccountCategory> AccountCategorys => Set<AccountCategory>();

    /// <summary>
    /// Cash in/out transactions table.
    /// </summary>
    public DbSet<CashInOut> CashTransactions => Set<CashInOut>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply entity configurations
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(TransactionInvoicesDbContext).Assembly);

        // Global query filters for soft deletes (if needed in future)
        // modelBuilder.Entity<TransactionInvoice>().HasQueryFilter(e => !e.IsDeleted);

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
        // TransactionInvoice indexes
        modelBuilder.Entity<TransactionInvoice>()
            .HasIndex(f => f.BatchId)
            .HasDatabaseName("IX_TransactionInvoice_BatchId");

        modelBuilder.Entity<TransactionInvoice>()
            .HasIndex(f => f.AccountCategoryId)
            .HasDatabaseName("IX_TransactionInvoice_AccountCategoryId");

        modelBuilder.Entity<TransactionInvoice>()
            .HasIndex(f => new { f.Status, f.InvoiceDate })
            .HasDatabaseName("IX_TransactionInvoice_Status_InvoiceDate");

        // TransactionBatch indexes
        modelBuilder.Entity<TransactionBatch>()
            .HasIndex(b => b.Status)
            .HasDatabaseName("IX_TransactionBatch_Status");

        modelBuilder.Entity<TransactionBatch>()
            .HasIndex(b => b.BatchDate)
            .HasDatabaseName("IX_TransactionBatch_BatchDate");

        // AccountCategory indexes
        modelBuilder.Entity<AccountCategory>()
            .HasIndex(s => s.CustomerId)
            .HasDatabaseName("IX_AccountCategory_CustomerId");

        modelBuilder.Entity<AccountCategory>()
            .HasIndex(s => s.AccountNumber)
            .IsUnique()
            .HasDatabaseName("IX_AccountCategory_AccountNumber_Unique");

        modelBuilder.Entity<AccountCategory>()
            .HasIndex(s => new { s.AccountType, s.Status })
            .HasDatabaseName("IX_AccountCategory_AccountType_Status");

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
