using System.Collections.Concurrent;
using RA.FundingInvoices.Core.Interfaces;

namespace RA.FundingInvoices.Infrastructure.Mock;

/// <summary>
/// In-memory mock implementation of IFundingBatchRepository.
/// Thread-safe batch state management for testing.
/// </summary>
public class MockFundingBatchRepository : IFundingBatchRepository
{
    private readonly ConcurrentDictionary<string, FundingBatch> _batches = new();

    public Task<FundingBatch?> GetByIdAsync(string batchId)
    {
        _batches.TryGetValue(batchId, out var batch);
        return Task.FromResult(batch);
    }

    public Task<IEnumerable<FundingBatch>> GetAllAsync()
    {
        return Task.FromResult(_batches.Values.AsEnumerable());
    }

    public Task<IEnumerable<FundingBatch>> GetByStatusAsync(string status)
    {
        var batches = _batches.Values.Where(b => b.Status == status);
        return Task.FromResult(batches);
    }

    public Task<IEnumerable<FundingBatch>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
    {
        var batches = _batches.Values.Where(b => 
            b.CreatedDate >= startDate && b.CreatedDate <= endDate);
        return Task.FromResult(batches);
    }

    public Task<FundingBatch> CreateAsync(FundingBatch batch)
    {
        if (string.IsNullOrEmpty(batch.BatchId))
        {
            batch.BatchId = $"BATCH-{Guid.NewGuid():N}";
        }

        batch.CreatedDate = DateTime.UtcNow;

        if (!_batches.TryAdd(batch.BatchId, batch))
        {
            throw new InvalidOperationException($"Batch with ID {batch.BatchId} already exists");
        }

        return Task.FromResult(batch);
    }

    public Task<FundingBatch> UpdateAsync(FundingBatch batch)
    {
        if (!_batches.ContainsKey(batch.BatchId))
        {
            throw new KeyNotFoundException($"Batch with ID {batch.BatchId} not found");
        }

        _batches[batch.BatchId] = batch;
        return Task.FromResult(batch);
    }

    public Task<FundingBatch> UpdateStatusAsync(string batchId, string newStatus)
    {
        if (!_batches.TryGetValue(batchId, out var batch))
        {
            throw new KeyNotFoundException($"Batch with ID {batchId} not found");
        }

        batch.Status = newStatus;
        if (newStatus == "Completed")
        {
            batch.ProcessedDate = DateTime.UtcNow;
        }

        return Task.FromResult(batch);
    }

    public Task<bool> DeleteAsync(string batchId)
    {
        return Task.FromResult(_batches.TryRemove(batchId, out _));
    }

    internal void Seed(FundingBatch batch)
    {
        _batches.TryAdd(batch.BatchId, batch);
    }

    internal void Clear()
    {
        _batches.Clear();
    }
}
