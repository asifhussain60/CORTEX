using CleanSolidApp.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace CleanSolidApp.Infrastructure.Data
{
    public class AppDbContext : DbContext
    {
        public DbSet<TaskItem> Tasks => Set<TaskItem>();

        public AppDbContext(DbContextOptions<AppDbContext> options)
            : base(options)
        {
        }
    }
}
