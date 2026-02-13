using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using RA.FundingInvoices.Core.Entities;

namespace RA.FundingInvoices.Infrastructure.EFCore.Configurations;

/// <summary>
/// EF Core entity configuration for CashInOut.
/// Defines table schema, relationships, and constraints.
/// </summary>
public class CashInOutConfiguration : IEntityTypeConfiguration<CashInOut>
{
    public void Configure(EntityTypeBuilder<CashInOut> builder)
    {
        // Table mapping
        builder.ToTable("CashInOut");

        // Primary key
        builder.HasKey(c => c.TransactionId);

        // Properties
        builder.Property(c => c.TransactionId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(c => c.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(c => c.TransactionType)
            .HasMaxLength(20)
            .IsRequired();

        builder.Property(c => c.Amount)
            .HasColumnType("decimal(18,2)")
            .IsRequired();

        builder.Property(c => c.TransactionDate)
            .IsRequired();

        builder.Property(c => c.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Pending");

        builder.Property(c => c.ReferenceNumber)
            .HasMaxLength(100);

        builder.Property(c => c.Description)
            .HasMaxLength(500);

        // Audit fields
        builder.Property(c => c.CreatedBy)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(c => c.CreatedDate)
            .IsRequired()
            .HasDefaultValueSql("GETUTCDATE()");

        builder.Property(c => c.ModifiedBy)
            .HasMaxLength(100);

        builder.Property(c => c.ModifiedDate);

        // Relationships
        builder.HasOne(c => c.FundingBatch)
            .WithMany(b => b.CashTransactions)
            .HasForeignKey(c => c.BatchId)
            .OnDelete(DeleteBehavior.Restrict);

        // Indexes
        builder.HasIndex(c => c.BatchId)
            .HasDatabaseName("IX_CashInOut_BatchId");

        builder.HasIndex(c => new { c.TransactionType, c.TransactionDate })
            .HasDatabaseName("IX_CashInOut_TransactionType_TransactionDate");

        builder.HasIndex(c => c.ReferenceNumber)
            .HasDatabaseName("IX_CashInOut_ReferenceNumber");
    }
}
