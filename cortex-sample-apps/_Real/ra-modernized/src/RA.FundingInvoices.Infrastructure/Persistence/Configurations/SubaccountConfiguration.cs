using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using RA.FundingInvoices.Core.Entities;

namespace RA.FundingInvoices.Infrastructure.Persistence.Configurations;

/// <summary>
/// Entity type configuration for Subaccount entity.
/// Defines precise database schema mapping using Fluent API.
/// </summary>
public class SubaccountConfiguration : IEntityTypeConfiguration<Subaccount>
{
    public void Configure(EntityTypeBuilder<Subaccount> builder)
    {
        // Table mapping
        builder.ToTable("Subaccount");

        // Primary key
        builder.HasKey(e => e.SubaccountId);
        builder.Property(e => e.SubaccountId)
            .HasMaxLength(50)
            .IsRequired();

        // Properties
        builder.Property(e => e.AccountNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.AccountType)
            .HasMaxLength(20)
            .IsRequired();

        builder.Property(e => e.MemberId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.Balance)
            .HasColumnType("decimal(18,2)")
            .IsRequired()
            .HasDefaultValue(0m);

        builder.Property(e => e.Status)
            .HasMaxLength(20)
            .IsRequired()
            .HasDefaultValue("Active");

        builder.Property(e => e.OpenedDate)
            .IsRequired();

        builder.Property(e => e.ClosedDate);

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
        builder.HasIndex(e => e.AccountNumber)
            .IsUnique()
            .HasDatabaseName("IX_Subaccount_AccountNumber");

        builder.HasIndex(e => e.MemberId)
            .HasDatabaseName("IX_Subaccount_MemberId");

        builder.HasIndex(e => e.AccountType)
            .HasDatabaseName("IX_Subaccount_AccountType");

        builder.HasIndex(e => e.Status)
            .HasDatabaseName("IX_Subaccount_Status");
    }
}
