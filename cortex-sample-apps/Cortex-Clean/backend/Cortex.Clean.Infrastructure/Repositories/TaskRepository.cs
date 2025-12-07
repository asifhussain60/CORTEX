using Cortex.Clean.Domain.Entities;
using Cortex.Clean.Domain.Interfaces;
using Cortex.Clean.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace Cortex.Clean.Infrastructure.Repositories;

public class TaskRepository : ITaskRepository
{
    private readonly ApplicationDbContext _context;

    public TaskRepository(ApplicationDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<TaskEntity> AddAsync(TaskEntity task, CancellationToken cancellationToken = default)
    {
        if (task == null) throw new ArgumentNullException(nameof(task));
        
        await _context.Tasks.AddAsync(task, cancellationToken);
        return task;
    }

    public async Task<IEnumerable<TaskEntity>> GetAllAsync(string? filter = null, CancellationToken cancellationToken = default)
    {
        var query = _context.Tasks.AsQueryable();

        if (!string.IsNullOrWhiteSpace(filter))
        {
            query = query.Where(t => t.Title.Contains(filter));
        }

        return await query
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public async Task<TaskEntity?> GetByIdAsync(int id, CancellationToken cancellationToken = default)
    {
        return await _context.Tasks
            .FirstOrDefaultAsync(t => t.Id == id, cancellationToken);
    }

    public Task UpdateAsync(TaskEntity task, CancellationToken cancellationToken = default)
    {
        if (task == null) throw new ArgumentNullException(nameof(task));
        
        _context.Tasks.Update(task);
        return Task.CompletedTask;
    }

    public async Task<bool> DeleteAsync(int id, CancellationToken cancellationToken = default)
    {
        var task = await _context.Tasks.FirstOrDefaultAsync(t => t.Id == id, cancellationToken);
        
        if (task == null)
        {
            return false;
        }
        
        _context.Tasks.Remove(task);
        return true;
    }

    public async Task SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        await _context.SaveChangesAsync(cancellationToken);
    }
}
