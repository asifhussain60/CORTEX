// ✅ CORTEX Refactored — DbContext

using Microsoft.EntityFrameworkCore;
using CortexLabs.FinTrack.Models;

namespace CortexLabs.FinTrack.Repositories;

/// <summary>
/// Entity Framework DbContext for FinTrack
/// </summary>
public class FinTrackDbContext : DbContext
{
    public FinTrackDbContext(DbContextOptions<FinTrackDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users => Set<User>();
    public DbSet<Transaction> Transactions => Set<Transaction>();
    public DbSet<Account> Accounts => Set<Account>();
    public DbSet<Report> Reports => Set<Report>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // User configuration
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.UserName).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
        });

        // Transaction configuration
        modelBuilder.Entity<Transaction>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.UserId);
            entity.HasIndex(e => e.Category);
            entity.HasIndex(e => e.Date);
        });

        // Account configuration
        modelBuilder.Entity<Account>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.UserId);
            entity.Property(e => e.Version).IsConcurrencyToken();
        });

        // Report configuration
        modelBuilder.Entity<Report>(entity =>
        {
            entity.HasKey(e => e.Id);
        });

        // Seed data
        modelBuilder.Entity<User>().HasData(
            new User 
            { 
                Id = 1, 
                UserName = "admin", 
                Email = "admin@cortexlabs.com",
                PasswordHash = "$2a$11$dummy.hash.for.seeding", // Replace in production
                Role = "admin",
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            },
            new User 
            { 
                Id = 2, 
                UserName = "john.doe", 
                Email = "john@cortexlabs.com",
                PasswordHash = "$2a$11$dummy.hash.for.seeding",
                Role = "user",
                IsActive = true,
                CreatedAt = DateTime.UtcNow
            }
        );
    }
}
