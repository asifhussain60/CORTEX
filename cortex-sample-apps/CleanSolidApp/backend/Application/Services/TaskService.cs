using CleanSolidApp.Application.Interfaces;
using CleanSolidApp.Domain.Entities;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace CleanSolidApp.Application.Services
{
    public interface ITaskService
    {
        Task<IEnumerable<TaskItem>> GetTasksAsync(string? filter = null);
        Task<TaskItem?> GetTaskAsync(int id);
        Task<TaskItem> CreateTaskAsync(string title);
        Task CompleteTaskAsync(int id, bool isCompleted);
        Task DeleteTaskAsync(int id);
    }

    public class TaskService : ITaskService
    {
        private readonly ITaskRepository _repo;

        public TaskService(ITaskRepository repo)
        {
            _repo = repo;
        }

        public Task<IEnumerable<TaskItem>> GetTasksAsync(string? filter = null)
            => _repo.GetAllAsync(filter);

        public Task<TaskItem?> GetTaskAsync(int id)
            => _repo.GetByIdAsync(id);

        public async Task<TaskItem> CreateTaskAsync(string title)
        {
            var task = new TaskItem { Title = title, IsCompleted = false };
            return await _repo.AddAsync(task);
        }

        public async Task CompleteTaskAsync(int id, bool isCompleted)
        {
            var task = await _repo.GetByIdAsync(id);
            if (task == null) throw new KeyNotFoundException($"Task {id} not found");

            task.IsCompleted = isCompleted;
            await _repo.UpdateAsync(task);
        }

        public Task DeleteTaskAsync(int id)
            => _repo.DeleteAsync(id);
    }
}
