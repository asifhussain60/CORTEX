using CleanSolidApp.Domain.Entities;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace CleanSolidApp.Application.Interfaces
{
    public interface ITaskRepository
    {
        Task<IEnumerable<TaskItem>> GetAllAsync(string? filter = null);
        Task<TaskItem?> GetByIdAsync(int id);
        Task<TaskItem> AddAsync(TaskItem item);
        Task UpdateAsync(TaskItem item);
        Task DeleteAsync(int id);
    }
}
