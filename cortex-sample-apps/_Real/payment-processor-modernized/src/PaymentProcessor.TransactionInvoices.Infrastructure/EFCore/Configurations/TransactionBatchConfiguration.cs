using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using PaymentProcessor.TransactionInvoices.Core.Entities;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Configurations;

/// <summary>
/// EF Core entity configuration for TransactionBatch.
/// Defines table schema, relationships, and constraints.
/// </summary>
public class TransactionBatchConfiguration : IEntityTypeConfiguration<TransactionBatch>
{
    public void Configure(EntityTypeBuilder<TransactionBatch> builder)
    {
        // Table mapping
        builder.ToTable("TransactionBatch");

        // Primary key
        builder.HasKey(b => b.BatchId);

        // Properties
        builder.Property(b => b.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(b => b.BatchNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(b => b.BatchDate)
            .IsRequired();

        builder.Property(b => b.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Open");

        builder.Property(b => b.TotalAmount)
            .HasColumnType("decimal(18,2)")
            .HasDefaultValue(0m);

        builder.Property(b => b.InvoiceCount)
            .HasDefaultValue(0);

        builder.Property(b => b.Description)
            .HasMaxLength(500);

        // Audit fields
        builder.Property(b => b.CreatedBy)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(b => b.CreatedDate)
            .IsRequired()
            .HasDefaultValueSql("GETUTCDATE()");

        builder.Property(b => b.ModifiedBy)
            .HasMaxLength(100);

        builder.Property(b => b.ModifiedDate);

        // Relationships
        builder.HasMany(b => b.TransactionInvoices)
            .WithOne(f => f.TransactionBatch)
            .HasForeignKey(f => f.BatchId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(b => b.CashTransactions)
            .WithOne(c => c.TransactionBatch)
            .HasForeignKey(c => c.BatchId)
            .OnDelete(DeleteBehavior.Restrict);

        // Indexes
        builder.HasIndex(b => b.Status)
            .HasDatabaseName("IX_TransactionBatch_Status");

        builder.HasIndex(b => b.BatchDate)
            .HasDatabaseName("IX_TransactionBatch_BatchDate");

        builder.HasIndex(b => b.BatchNumber)
            .IsUnique()
            .HasDatabaseName("IX_TransactionBatch_BatchNumber_Unique");
    }
}
