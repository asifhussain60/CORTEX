using CleanSolidApp.Application.Interfaces;
using CleanSolidApp.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace CleanSolidApp.Infrastructure.Data
{
    public class TaskRepository : ITaskRepository
    {
        private readonly AppDbContext _ctx;

        public TaskRepository(AppDbContext ctx)
        {
            _ctx = ctx;
        }

        public async Task<IEnumerable<TaskItem>> GetAllAsync(string? filter = null)
        {
            var query = _ctx.Tasks.AsQueryable();
            if (!string.IsNullOrWhiteSpace(filter))
            {
                query = query.Where(t => t.Title.Contains(filter));
            }
            return await query.AsNoTracking().ToListAsync();
        }

        public Task<TaskItem?> GetByIdAsync(int id)
            => _ctx.Tasks.AsNoTracking().FirstOrDefaultAsync(t => t.Id == id)!;

        public async Task<TaskItem> AddAsync(TaskItem item)
        {
            _ctx.Tasks.Add(item);
            await _ctx.SaveChangesAsync();
            return item;
        }

        public async Task UpdateAsync(TaskItem item)
        {
            _ctx.Tasks.Update(item);
            await _ctx.SaveChangesAsync();
        }

        public async Task DeleteAsync(int id)
        {
            var existing = await _ctx.Tasks.FindAsync(id);
            if (existing != null)
            {
                _ctx.Tasks.Remove(existing);
                await _ctx.SaveChangesAsync();
            }
        }
    }
}
