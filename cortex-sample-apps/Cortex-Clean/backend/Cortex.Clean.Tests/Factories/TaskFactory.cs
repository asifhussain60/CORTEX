using Cortex.Clean.Domain.Entities;
using AutoFixture;

namespace Cortex.Clean.Tests.Factories;

/// <summary>
/// Factory for creating test Task entities with valid data.
/// </summary>
public static class TaskFactory
{
    private static readonly Fixture _fixture = new();

    /// <summary>
    /// Creates a valid task entity for testing.
    /// </summary>
    public static TaskEntity CreateValid(string? title = null, bool isCompleted = false)
    {
        var task = new TaskEntity(title ?? _fixture.Create<string>()[..50]);
        if (isCompleted)
        {
            task.ToggleCompletion();
        }
        return task;
    }

    /// <summary>
    /// Creates multiple valid task entities.
    /// </summary>
    public static List<TaskEntity> CreateMany(int count)
    {
        return Enumerable.Range(1, count)
            .Select(i => CreateValid($"Task {i}"))
            .ToList();
    }
}
