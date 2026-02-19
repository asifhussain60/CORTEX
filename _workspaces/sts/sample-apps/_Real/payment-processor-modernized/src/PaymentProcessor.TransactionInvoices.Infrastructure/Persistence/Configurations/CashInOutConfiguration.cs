using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using PaymentProcessor.TransactionInvoices.Core.Entities;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Configurations;

/// <summary>
/// Entity type configuration for CashInOut entity.
/// Defines precise database schema mapping using Fluent API.
/// </summary>
public class CashInOutConfiguration : IEntityTypeConfiguration<CashInOut>
{
    public void Configure(EntityTypeBuilder<CashInOut> builder)
    {
        // Table mapping
        builder.ToTable("CashInOut");

        // Primary key
        builder.HasKey(e => e.TransactionId);
        builder.Property(e => e.TransactionId)
            .HasMaxLength(50)
            .IsRequired();

        // Properties
        builder.Property(e => e.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.TransactionType)
            .HasMaxLength(20)
            .IsRequired();

        builder.Property(e => e.Amount)
            .HasColumnType("decimal(18,2)")
            .IsRequired();

        builder.Property(e => e.TransactionDate)
            .IsRequired();

        builder.Property(e => e.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Pending");

        builder.Property(e => e.ReferenceNumber)
            .HasMaxLength(100);

        builder.Property(e => e.Description)
            .HasMaxLength(500);

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
            .WithMany(b => b.CashTransactions)
            .HasForeignKey(e => e.BatchId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        // Indexes for performance
        builder.HasIndex(e => e.BatchId)
            .HasDatabaseName("IX_CashInOut_BatchId");

        builder.HasIndex(e => e.TransactionType)
            .HasDatabaseName("IX_CashInOut_TransactionType");

        builder.HasIndex(e => e.TransactionDate)
            .HasDatabaseName("IX_CashInOut_TransactionDate");

        builder.HasIndex(e => e.Status)
            .HasDatabaseName("IX_CashInOut_Status");

        builder.HasIndex(e => e.ReferenceNumber)
            .HasDatabaseName("IX_CashInOut_ReferenceNumber");
    }
}
