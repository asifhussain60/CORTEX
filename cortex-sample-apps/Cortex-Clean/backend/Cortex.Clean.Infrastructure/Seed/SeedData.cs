using Cortex.Clean.Domain.Entities;
using Cortex.Clean.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace Cortex.Clean.Infrastructure.Seed;

public static class SeedData
{
    public static async Task SeedAsync(ApplicationDbContext context)
    {
        // Only seed if database is empty
        if (await context.Tasks.AnyAsync())
        {
            return;
        }

        var tasks = new[]
        {
            new TaskEntity("Review Clean Architecture documentation"),
            new TaskEntity("Set up CI/CD pipeline"),
            new TaskEntity("Write integration tests for API endpoints"),
            new TaskEntity("Configure Serilog for structured logging"),
            new TaskEntity("Implement authentication middleware")
        };

        // Mark first two as completed
        tasks[0].ToggleCompletion();
        tasks[1].ToggleCompletion();

        await context.Tasks.AddRangeAsync(tasks);
        await context.SaveChangesAsync();
    }
}
