using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using PaymentProcessor.TransactionInvoices.Core.Entities;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Configurations;

/// <summary>
/// Entity type configuration for TransactionInvoice entity.
/// Defines precise database schema mapping using Fluent API.
/// </summary>
public class TransactionInvoiceConfiguration : IEntityTypeConfiguration<TransactionInvoice>
{
    public void Configure(EntityTypeBuilder<TransactionInvoice> builder)
    {
        // Table mapping
        builder.ToTable("TransactionInvoice");

        // Primary key
        builder.HasKey(e => e.InvoiceId);
        builder.Property(e => e.InvoiceId)
            .HasMaxLength(50)
            .IsRequired();

        // Properties
        builder.Property(e => e.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.AccountCategoryId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.InvoiceNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.Amount)
            .HasColumnType("decimal(18,2)")
            .IsRequired();

        builder.Property(e => e.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Pending");

        builder.Property(e => e.Description)
            .HasMaxLength(500);

        builder.Property(e => e.InvoiceDate)
            .IsRequired();

        builder.Property(e => e.DueDate);

        // Audit fields
        builder.Property(e => e.CreatedBy)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(e => e.CreatedDate)
            .IsRequired();

        builder.Property(e => e.ModifiedBy)
            .HasMaxLength(100);

        builder.Property(e => e.ModifiedDate);

        // Relationships
        builder.HasOne(e => e.TransactionBatch)
            .WithMany(b => b.TransactionInvoices)
            .HasForeignKey(e => e.BatchId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        builder.HasOne(e => e.AccountCategory)
            .WithMany(s => s.TransactionInvoices)
            .HasForeignKey(e => e.AccountCategoryId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        // Indexes for performance
        builder.HasIndex(e => e.BatchId)
            .HasDatabaseName("IX_TransactionInvoice_BatchId");

        builder.HasIndex(e => e.AccountCategoryId)
            .HasDatabaseName("IX_TransactionInvoice_AccountCategoryId");

        builder.HasIndex(e => e.InvoiceNumber)
            .IsUnique()
            .HasDatabaseName("IX_TransactionInvoice_InvoiceNumber");

        builder.HasIndex(e => e.Status)
            .HasDatabaseName("IX_TransactionInvoice_Status");

        builder.HasIndex(e => e.InvoiceDate)
            .HasDatabaseName("IX_TransactionInvoice_InvoiceDate");
    }
}
