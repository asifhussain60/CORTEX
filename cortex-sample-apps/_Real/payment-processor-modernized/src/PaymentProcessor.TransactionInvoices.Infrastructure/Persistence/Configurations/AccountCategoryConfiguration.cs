using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using PaymentProcessor.TransactionInvoices.Core.Entities;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.Persistence.Configurations;

/// <summary>
/// Entity type configuration for AccountCategory entity.
/// Defines precise database schema mapping using Fluent API.
/// </summary>
public class AccountCategoryConfiguration : IEntityTypeConfiguration<AccountCategory>
{
    public void Configure(EntityTypeBuilder<AccountCategory> builder)
    {
        // Table mapping
        builder.ToTable("AccountCategory");

        // Primary key
        builder.HasKey(e => e.AccountCategoryId);
        builder.Property(e => e.AccountCategoryId)
            .HasMaxLength(50)
            .IsRequired();

        // Properties
        builder.Property(e => e.AccountNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(e => e.AccountType)
            .HasMaxLength(20)
            .IsRequired();

        builder.Property(e => e.CustomerId)
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
            .HasDatabaseName("IX_AccountCategory_AccountNumber");

        builder.HasIndex(e => e.CustomerId)
            .HasDatabaseName("IX_AccountCategory_CustomerId");

        builder.HasIndex(e => e.AccountType)
            .HasDatabaseName("IX_AccountCategory_AccountType");

        builder.HasIndex(e => e.Status)
            .HasDatabaseName("IX_AccountCategory_Status");
    }
}
