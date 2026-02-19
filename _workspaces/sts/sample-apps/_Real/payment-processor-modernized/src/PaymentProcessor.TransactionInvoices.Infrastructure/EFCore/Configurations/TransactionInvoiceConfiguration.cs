using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using PaymentProcessor.TransactionInvoices.Core.Entities;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Configurations;

/// <summary>
/// EF Core entity configuration for TransactionInvoice.
/// Defines table schema, relationships, and constraints.
/// </summary>
public class TransactionInvoiceConfiguration : IEntityTypeConfiguration<TransactionInvoice>
{
    public void Configure(EntityTypeBuilder<TransactionInvoice> builder)
    {
        // Table mapping
        builder.ToTable("TransactionInvoice");

        // Primary key
        builder.HasKey(f => f.InvoiceId);

        // Properties
        builder.Property(f => f.InvoiceId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(f => f.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(f => f.AccountCategoryId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(f => f.InvoiceNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(f => f.Amount)
            .HasColumnType("decimal(18,2)")
            .IsRequired();

        builder.Property(f => f.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Pending");

        builder.Property(f => f.Description)
            .HasMaxLength(500);

        builder.Property(f => f.InvoiceDate)
            .IsRequired();

        builder.Property(f => f.DueDate);

        // Audit fields
        builder.Property(f => f.CreatedBy)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(f => f.CreatedDate)
            .IsRequired()
            .HasDefaultValueSql("GETUTCDATE()");

        builder.Property(f => f.ModifiedBy)
            .HasMaxLength(100);

        builder.Property(f => f.ModifiedDate);

        // Relationships
        builder.HasOne(f => f.TransactionBatch)
            .WithMany(b => b.TransactionInvoices)
            .HasForeignKey(f => f.BatchId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        builder.HasOne(f => f.AccountCategory)
            .WithMany(s => s.TransactionInvoices)
            .HasForeignKey(f => f.AccountCategoryId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        // Indexes (already defined in DbContext, but can also be defined here)
        builder.HasIndex(f => f.BatchId)
            .HasDatabaseName("IX_TransactionInvoice_BatchId");

        builder.HasIndex(f => f.AccountCategoryId)
            .HasDatabaseName("IX_TransactionInvoice_AccountCategoryId");

        builder.HasIndex(f => new { f.Status, f.InvoiceDate })
            .HasDatabaseName("IX_TransactionInvoice_Status_InvoiceDate");
    }
}
