using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using RA.FundingInvoices.Core.Entities;

namespace RA.FundingInvoices.Infrastructure.EFCore.Configurations;

/// <summary>
/// EF Core entity configuration for Subaccount.
/// Defines table schema, relationships, and constraints.
/// </summary>
public class SubaccountConfiguration : IEntityTypeConfiguration<Subaccount>
{
    public void Configure(EntityTypeBuilder<Subaccount> builder)
    {
        // Table mapping
        builder.ToTable("Subaccount");

        // Primary key
        builder.HasKey(s => s.SubaccountId);

        // Properties
        builder.Property(s => s.SubaccountId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(s => s.AccountNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(s => s.AccountType)
            .HasMaxLength(20)
            .IsRequired();

        builder.Property(s => s.MemberId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(s => s.Balance)
            .HasColumnType("decimal(18,2)")
            .HasDefaultValue(0m);

        builder.Property(s => s.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Active");

        builder.Property(s => s.OpenedDate)
            .IsRequired();

        builder.Property(s => s.ClosedDate);

        // Audit fields
        builder.Property(s => s.CreatedBy)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(s => s.CreatedDate)
            .IsRequired()
            .HasDefaultValueSql("GETUTCDATE()");

        builder.Property(s => s.ModifiedBy)
            .HasMaxLength(100);

        builder.Property(s => s.ModifiedDate);

        // Relationships
        builder.HasMany(s => s.FundingInvoices)
            .WithOne(f => f.Subaccount)
            .HasForeignKey(f => f.SubaccountId)
            .OnDelete(DeleteBehavior.Restrict);

        // Indexes
        builder.HasIndex(s => s.MemberId)
            .HasDatabaseName("IX_Subaccount_MemberId");

        builder.HasIndex(s => s.AccountNumber)
            .IsUnique()
            .HasDatabaseName("IX_Subaccount_AccountNumber_Unique");

        builder.HasIndex(s => new { s.AccountType, s.Status })
            .HasDatabaseName("IX_Subaccount_AccountType_Status");
    }
}
