using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using RA.FundingInvoices.Core.Entities;

namespace RA.FundingInvoices.Infrastructure.Persistence.Configurations;

/// <summary>
/// Entity type configuration for FundingBatch entity.
/// Defines precise database schema mapping using Fluent API.
/// </summary>
public class FundingBatchConfiguration : IEntityTypeConfiguration<FundingBatch>
{
    public void Configure(EntityTypeBuilder<FundingBatch> builder)
    {
        // Table mapping
        builder.ToTable("FundingBatch");

        // Primary key
        builder.HasKey(e => e.BatchId);
        builder.Property(e => e.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        // Properties
        builder.Property(e => e.BatchNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.BatchDate)
            .IsRequired();

        builder.Property(e => e.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Open");

        builder.Property(e => e.TotalAmount)
            .HasColumnType("decimal(18,2)")
            .IsRequired()
            .HasDefaultValue(0m);

        builder.Property(e => e.InvoiceCount)
            .IsRequired()
            .HasDefaultValue(0);

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

        // Indexes for performance
        builder.HasIndex(e => e.BatchNumber)
            .IsUnique()
            .HasDatabaseName("IX_FundingBatch_BatchNumber");

        builder.HasIndex(e => e.BatchDate)
            .HasDatabaseName("IX_FundingBatch_BatchDate");

        builder.HasIndex(e => e.Status)
            .HasDatabaseName("IX_FundingBatch_Status");
    }
}
