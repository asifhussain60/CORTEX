using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using PaymentProcessor.TransactionInvoices.Core.Entities;

namespace PaymentProcessor.TransactionInvoices.Infrastructure.EFCore.Configurations;

/// <summary>
/// EF Core entity configuration for AccountCategory.
/// Defines table schema, relationships, and constraints.
/// </summary>
public class AccountCategoryConfiguration : IEntityTypeConfiguration<AccountCategory>
{
    public void Configure(EntityTypeBuilder<AccountCategory> builder)
    {
        // Table mapping
        builder.ToTable("AccountCategory");

        // Primary key
        builder.HasKey(s => s.AccountCategoryId);

        // Properties
        builder.Property(s => s.AccountCategoryId)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(s => s.AccountNumber)
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(s => s.AccountType)
            .HasMaxLength(20)
            .IsRequired();

        builder.Property(s => s.CustomerId)
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
        builder.HasMany(s => s.TransactionInvoices)
            .WithOne(f => f.AccountCategory)
            .HasForeignKey(f => f.AccountCategoryId)
            .OnDelete(DeleteBehavior.Restrict);

        // Indexes
        builder.HasIndex(s => s.CustomerId)
            .HasDatabaseName("IX_AccountCategory_CustomerId");

        builder.HasIndex(s => s.AccountNumber)
            .IsUnique()
            .HasDatabaseName("IX_AccountCategory_AccountNumber_Unique");

        builder.HasIndex(s => new { s.AccountType, s.Status })
            .HasDatabaseName("IX_AccountCategory_AccountType_Status");
    }
}
