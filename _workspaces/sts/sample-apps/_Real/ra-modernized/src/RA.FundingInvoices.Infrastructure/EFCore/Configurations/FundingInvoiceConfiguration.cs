using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using RA.FundingInvoices.Core.Entities;

namespace RA.FundingInvoices.Infrastructure.EFCore.Configurations;

/// <summary>
/// EF Core entity configuration for FundingInvoice.
/// Defines table schema, relationships, and constraints.
/// </summary>
public class FundingInvoiceConfiguration : IEntityTypeConfiguration<FundingInvoice>
{
    public void Configure(EntityTypeBuilder<FundingInvoice> builder)
    {
        // Table mapping
        builder.ToTable("FundingInvoice");

        // Primary key
        builder.HasKey(f => f.InvoiceId);

        // Properties
        builder.Property(f => f.InvoiceId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(f => f.BatchId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(f => f.SubaccountId)
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
        builder.HasOne(f => f.FundingBatch)
            .WithMany(b => b.FundingInvoices)
            .HasForeignKey(f => f.BatchId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        builder.HasOne(f => f.Subaccount)
            .WithMany(s => s.FundingInvoices)
            .HasForeignKey(f => f.SubaccountId)
            .OnDelete(DeleteBehavior.Restrict); // Prevent cascade delete

        // Indexes (already defined in DbContext, but can also be defined here)
        builder.HasIndex(f => f.BatchId)
            .HasDatabaseName("IX_FundingInvoice_BatchId");

        builder.HasIndex(f => f.SubaccountId)
            .HasDatabaseName("IX_FundingInvoice_SubaccountId");

        builder.HasIndex(f => new { f.Status, f.InvoiceDate })
            .HasDatabaseName("IX_FundingInvoice_Status_InvoiceDate");
    }
}
