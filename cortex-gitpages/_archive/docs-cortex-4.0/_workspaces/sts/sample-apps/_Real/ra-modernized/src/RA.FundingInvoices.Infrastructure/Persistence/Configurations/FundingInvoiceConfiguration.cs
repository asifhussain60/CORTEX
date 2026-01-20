using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using RA.FundingInvoices.Core.Entities;

namespace RA.FundingInvoices.Infrastructure.Persistence.Configurations;

/// <summary>
/// Entity type configuration for FundingInvoice entity.
/// Defines precise database schema mapping using Fluent API.
/// </summary>
public class FundingInvoiceConfiguration : IEntityTypeConfiguration<FundingInvoice>
{
    public void Configure(EntityTypeBuilder<FundingInvoice> builder)
    {
        // Table mapping
        builder.ToTable("FundingInvoice");

        // Primary key
        builder.HasKey(e => e.InvoiceId);
        builder.Property(e => e.InvoiceId)
            .HasMaxLength(50)
            .IsRequired();

        // Properties
        builder.Property(e => e.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.SubaccountId)
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
        builder.HasOne(e => e.FundingBatch)
            .WithMany(b => b.FundingInvoices)
            .HasForeignKey(e => e.BatchId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        builder.HasOne(e => e.Subaccount)
            .WithMany(s => s.FundingInvoices)
            .HasForeignKey(e => e.SubaccountId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        // Indexes for performance
        builder.HasIndex(e => e.BatchId)
            .HasDatabaseName("IX_FundingInvoice_BatchId");

        builder.HasIndex(e => e.SubaccountId)
            .HasDatabaseName("IX_FundingInvoice_SubaccountId");

        builder.HasIndex(e => e.InvoiceNumber)
            .IsUnique()
            .HasDatabaseName("IX_FundingInvoice_InvoiceNumber");

        builder.HasIndex(e => e.Status)
            .HasDatabaseName("IX_FundingInvoice_Status");

        builder.HasIndex(e => e.InvoiceDate)
            .HasDatabaseName("IX_FundingInvoice_InvoiceDate");
    }
}
